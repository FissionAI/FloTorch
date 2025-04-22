-- Switch to database
USE flotorch;
-- ====================================================
-- DEVOPS VIEWS
-- ====================================================

-- DevOps: System Health Dashboard
CREATE VIEW IF NOT EXISTS v_devops_system_health AS
SELECT
    toStartOfHour(timestamp) AS hour,
    countIf(status = 'success') AS successful_requests,
    countIf(status = 'error') AS failed_requests,
    countIf(status = 'timeout') AS timeout_requests,
    round(countIf(status != 'success') * 100.0 / count(), 2) AS error_rate_percent,
    round(avg(latencyMs), 2) AS avg_latency_ms,
    max(latencyMs) AS max_latency_ms,
    quantile(0.95)(latencyMs) AS p95_latency_ms,
    quantile(0.99)(latencyMs) AS p99_latency_ms,
    count() AS total_requests
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 7 DAY
GROUP BY hour
ORDER BY hour DESC;

-- DevOps: Error Monitoring
CREATE VIEW IF NOT EXISTS v_devops_error_monitoring AS
SELECT
    toStartOfHour(timestamp) AS hour,
    errorCode,
    count() AS error_count,
    avgIf(latencyMs, latencyMs > 0) AS avg_latency_ms,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    providerName,
    model
FROM request_logs
WHERE status = 'error'
  AND timestamp >= toStartOfDay(now()) - INTERVAL 7 DAY
GROUP BY hour, errorCode, providerName, model
ORDER BY hour DESC, error_count DESC;

-- DevOps: Provider Reliability
CREATE VIEW IF NOT EXISTS v_devops_provider_reliability AS
SELECT
    toStartOfDay(timestamp) AS day,
    providerName,
    count() AS total_requests,
    countIf(status = 'success') AS successful_requests,
    round(countIf(status = 'success') * 100.0 / count(), 2) AS success_rate_percent,
    round(avg(latencyMs), 2) AS avg_latency_ms,
    quantile(0.95)(latencyMs) AS p95_latency_ms,
    quantile(0.99)(latencyMs) AS p99_latency_ms,
    countIf(isRetry) AS retry_count,
    countIf(isFallback) AS fallback_count,
    round(avgIf(latencyMs, isRetry = false), 2) AS avg_latency_no_retry_ms
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, providerName
ORDER BY day DESC, total_requests DESC;

-- DevOps: Request Pipeline Performance
CREATE VIEW IF NOT EXISTS v_devops_request_pipeline AS
SELECT
    rt.requestUid,
    rl.workspaceUid,
    rl.model,
    rl.providerName,
    rl.status AS overall_status,
    rl.latencyMs AS total_latency_ms,
    rt.stage,
    rt.latencyMs AS stage_latency_ms,
    round(rt.latencyMs * 100.0 / nullIf(rl.latencyMs, 0), 2) AS stage_latency_percent,
    rt.status AS stage_status,
    rt.errorCode AS stage_error_code
FROM request_traces rt
JOIN request_logs rl ON rt.requestUid = rl.requestUid
WHERE rt.timestamp >= toStartOfDay(now()) - INTERVAL 7 DAY
ORDER BY rt.timestamp DESC, rt.sequence;

-- DevOps: Pipeline Stage Performance
CREATE VIEW IF NOT EXISTS v_devops_pipeline_stage_performance AS
SELECT
    toStartOfHour(timestamp) AS hour,
    stage,
    count() AS stage_count,
    round(avg(latencyMs), 2) AS avg_latency_ms,
    max(latencyMs) AS max_latency_ms,
    quantile(0.95)(latencyMs) AS p95_latency_ms,
    countIf(status = 'error') AS error_count
FROM request_traces
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 7 DAY
GROUP BY hour, stage
ORDER BY hour DESC, avg_latency_ms DESC;

-- ====================================================
-- DEVELOPER VIEWS
-- ====================================================

-- Developers: API Usage Patterns
CREATE VIEW IF NOT EXISTS v_developer_api_usage AS
SELECT
    toStartOfDay(timestamp) AS day,
    workspaceUid,
    groupId,
    subGroupId,
    count() AS total_requests,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    round(avg(latencyMs), 2) AS avg_latency_ms,
    max(latencyMs) AS max_latency_ms
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, workspaceUid, groupId, subGroupId
ORDER BY day DESC, total_requests DESC;

-- Developers: Session Analysis
CREATE VIEW IF NOT EXISTS v_developer_session_analysis AS
SELECT
    toStartOfDay(timestamp) AS day,
    workspaceUid,
    sessionUid,
    min(timestamp) AS session_start,
    max(timestamp) AS session_end,
    count() AS request_count,
    round(avg(latencyMs), 2) AS avg_latency_ms,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    sum(totalCost) AS total_session_cost
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, workspaceUid, sessionUid
ORDER BY day DESC, request_count DESC;

-- Developers: Error Diagnostic
CREATE VIEW IF NOT EXISTS v_developer_error_diagnostic AS
SELECT
    requestUid,
    timestamp,
    workspaceUid,
    model,
    providerName,
    status,
    errorCode,
    latencyMs,
    inputTokens,
    outputTokens,
    toString(request),
    toString(response),
    toString(metadata)
FROM request_logs
WHERE status = 'error'
  AND timestamp >= toStartOfDay(now()) - INTERVAL 7 DAY
ORDER BY timestamp DESC;

-- Developers: Request Trace Analysis
CREATE VIEW IF NOT EXISTS v_developer_request_traces AS
WITH ranked_requests AS (
    SELECT
        requestUid,
        timestamp,
        latencyMs,
        ROW_NUMBER() OVER (PARTITION BY toStartOfDay(timestamp) ORDER BY latencyMs DESC) AS latency_rank
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 7 DAY
)
SELECT
    rt.requestUid,
    rt.timestamp,
    rt.stage,
    rt.status AS stage_status,
    rt.errorCode AS stage_error,
    rt.latencyMs AS stage_latency_ms,
    rt.startTime,
    rt.endTime,
    rt.sequence,
    toString(rt.inputBody),
    toString(rt.outputBody)
FROM request_traces rt
JOIN ranked_requests rr ON rt.requestUid = rr.requestUid
WHERE rr.latency_rank <= 100  -- Focus on top 100 slowest requests per day
ORDER BY rt.requestUid, rt.sequence;

-- ====================================================
-- AI ENGINEER VIEWS
-- ====================================================

-- AI Engineers: Model Performance Comparison
CREATE VIEW IF NOT EXISTS v_ai_engineer_model_performance AS
SELECT
    toStartOfDay(timestamp) AS day,
    model,
    providerName,
    providerModelName,
    count() AS request_count,
    round(avg(latencyMs), 2) AS avg_latency_ms,
    quantile(0.95)(latencyMs) AS p95_latency_ms,
    quantile(0.99)(latencyMs) AS p99_latency_ms,
    round(avg(inputTokens), 2) AS avg_input_tokens,
    round(avg(outputTokens), 2) AS avg_output_tokens,
    round(avg(totalCost), 6) AS avg_request_cost,
    round(sum(totalCost), 2) AS total_cost,
    countIf(status = 'success') / count() AS success_rate
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, model, providerName, providerModelName
ORDER BY day DESC, request_count DESC;

-- AI Engineers: Guardrail Effectiveness
-- AI Engineers: Guardrail Effectiveness
CREATE VIEW IF NOT EXISTS v_ai_engineer_guardrail_effectiveness AS
WITH workspace_requests AS (
    SELECT
        workspaceUid,
        count(DISTINCT requestUid) AS total_workspace_requests
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
    GROUP BY workspaceUid
),
guardrail_stats AS (
    SELECT
        toStartOfDay(gl.timestamp) AS day,
        gl.workspaceUid,
        gl.guardrailUid,
        gl.hook,
        gl.action,
        gl.severity,
        count() AS trigger_count,
        count(DISTINCT gl.requestUid) AS affected_requests
    FROM guardrail_logs gl
    WHERE gl.timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
    GROUP BY day, gl.workspaceUid, gl.guardrailUid, gl.hook, gl.action, gl.severity
)
SELECT
    gs.day,
    gs.workspaceUid,
    gs.guardrailUid,
    gs.hook,
    gs.action,
    gs.severity,
    gs.trigger_count,
    gs.affected_requests,
    round(gs.affected_requests * 100.0 / nullIf(wr.total_workspace_requests, 0), 2) AS percent_of_all_requests
FROM guardrail_stats gs
JOIN workspace_requests wr ON gs.workspaceUid = wr.workspaceUid
ORDER BY gs.day DESC, gs.trigger_count DESC;

-- AI Engineers: Model Error Analysis
-- AI Engineers: Model Error Analysis
CREATE VIEW IF NOT EXISTS v_ai_engineer_model_errors AS
WITH model_totals AS (
    SELECT
        model,
        count() AS total_requests
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
    GROUP BY model
),
error_data AS (
    SELECT
        toStartOfDay(timestamp) AS day,
        model,
        providerName,
        errorCode,
        count() AS error_count,
        round(avg(latencyMs), 2) AS avg_latency_ms,
        -- Extract common error patterns from responses
        JSONExtractString(arrayJoin(
            JSONExtractArrayRaw(
                JSONExtractRaw(response, 'error')
            )
        ), 'message') AS error_message
    FROM request_logs
    WHERE status = 'error'
      AND timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
    GROUP BY day, model, providerName, errorCode, error_message
)
SELECT
    ed.day,
    ed.model,
    ed.providerName,
    ed.errorCode,
    ed.error_count,
    ed.error_count / mt.total_requests AS error_rate,
    ed.avg_latency_ms,
    ed.error_message
FROM error_data ed
JOIN model_totals mt ON ed.model = mt.model
ORDER BY ed.day DESC, ed.error_count DESC;

-- AI Engineers: Token Usage Patterns
CREATE VIEW IF NOT EXISTS v_ai_engineer_token_usage AS
SELECT
    toStartOfDay(timestamp) AS day,
    model,
    workspaceUid,
    groupId,
    count() AS request_count,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    round(avg(inputTokens), 2) AS avg_input_tokens,
    round(avg(outputTokens), 2) AS avg_output_tokens,
    round(max(inputTokens), 2) AS max_input_tokens,
    round(max(outputTokens), 2) AS max_output_tokens,
    round(sum(inputCost), 4) AS total_input_cost,
    round(sum(outputCost), 4) AS total_output_cost
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, model, workspaceUid, groupId
ORDER BY day DESC, total_input_tokens + total_output_tokens DESC;

-- ====================================================
-- BUSINESS USER VIEWS
-- ====================================================

-- Business Users: AI Usage Dashboard
CREATE VIEW IF NOT EXISTS v_business_user_ai_usage AS
SELECT
    toStartOfDay(timestamp) AS day,
    workspaceUid,
    groupId,
    count() AS request_count,
    count(DISTINCT sessionUid) AS session_count,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    round(avg(latencyMs) / 1000, 2) AS avg_response_time_seconds,
    countIf(status = 'success') / count() AS success_rate
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, workspaceUid, groupId
ORDER BY day DESC, request_count DESC;

-- Business Users: Application Performance
CREATE VIEW IF NOT EXISTS v_business_user_application_performance AS
SELECT
    toStartOfHour(timestamp) AS hour,
    workspaceUid,
    groupId,
    count() AS request_count,
    countIf(status = 'success') AS successful_requests,
    countIf(status = 'error') AS failed_requests,
    round(avgIf(latencyMs, status = 'success') / 1000, 2) AS avg_success_time_seconds,
    round(quantile(0.95)(latencyMs) / 1000, 2) AS p95_response_time_seconds
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 7 DAY
GROUP BY hour, workspaceUid, groupId
ORDER BY hour DESC, request_count DESC;

-- ====================================================
-- PRODUCT MANAGER VIEWS
-- ====================================================

-- Product Managers: Feature Usage Analytics
CREATE VIEW IF NOT EXISTS v_product_manager_feature_usage AS
SELECT
    toStartOfDay(timestamp) AS day,
    workspaceUid,
    groupId,
    subGroupId, -- Can represent different features or product areas
    model,
    count() AS request_count,
    count(DISTINCT sessionUid) AS unique_sessions,
    round(avg(latencyMs) / 1000, 2) AS avg_response_time_seconds,
    countIf(status = 'success') / count() AS success_rate
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, workspaceUid, groupId, subGroupId, model
ORDER BY day DESC, request_count DESC;

-- Product Managers: User Satisfaction Metrics
CREATE VIEW IF NOT EXISTS v_product_manager_user_satisfaction AS
SELECT
    toStartOfDay(timestamp) AS day,
    workspaceUid,
    groupId,
    count() AS total_requests,
    countIf(status = 'success' AND latencyMs < 3000) AS fast_successful_requests, -- Under 3 seconds
    countIf(status = 'success' AND latencyMs >= 3000 AND latencyMs < 10000) AS medium_successful_requests, -- 3-10 seconds
    countIf(status = 'success' AND latencyMs >= 10000) AS slow_successful_requests, -- Over 10 seconds
    countIf(status = 'error') AS failed_requests,
    round(countIf(status = 'success' AND latencyMs < 3000) * 100.0 / count(), 2) AS fast_success_rate,
    round(avgIf(latencyMs, status = 'success') / 1000, 2) AS avg_success_time_seconds
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, workspaceUid, groupId
ORDER BY day DESC, total_requests DESC;

-- Product Managers: Model Usage Trends
CREATE VIEW IF NOT EXISTS v_product_manager_model_usage_trends AS
SELECT
    toStartOfDay(timestamp) AS day,
    model,
    count() AS request_count,
    count(DISTINCT workspaceUid) AS unique_workspaces,
    count(DISTINCT sessionUid) AS unique_sessions,
    round(avg(latencyMs) / 1000, 2) AS avg_response_time_seconds,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 90 DAY
GROUP BY day, model
ORDER BY day DESC, request_count DESC;

-- Product Managers: User Adoption
CREATE VIEW IF NOT EXISTS v_product_manager_user_adoption AS
WITH daily_active AS (
    SELECT
        toStartOfDay(timestamp) AS day,
        workspaceUid,
        count(DISTINCT sessionUid) AS daily_sessions,
        count() AS daily_requests
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 90 DAY
    GROUP BY day, workspaceUid
),
weekly_active AS (
    SELECT
        toStartOfWeek(timestamp) AS week,
        workspaceUid,
        count(DISTINCT sessionUid) AS weekly_sessions,
        count() AS weekly_requests
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 90 DAY
    GROUP BY week, workspaceUid
),
monthly_active AS (
    SELECT
        toStartOfMonth(timestamp) AS month,
        workspaceUid,
        count(DISTINCT sessionUid) AS monthly_sessions,
        count() AS monthly_requests
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 90 DAY
    GROUP BY month, workspaceUid
)
SELECT
    d.day,
    count(DISTINCT d.workspaceUid) AS daily_active_workspaces,
    sum(d.daily_sessions) AS total_daily_sessions,
    sum(d.daily_requests) AS total_daily_requests,
    w.week,
    count(DISTINCT w.workspaceUid) AS weekly_active_workspaces,
    sum(w.weekly_sessions) AS total_weekly_sessions,
    sum(w.weekly_requests) AS total_weekly_requests,
    m.month,
    count(DISTINCT m.workspaceUid) AS monthly_active_workspaces,
    sum(m.monthly_sessions) AS total_monthly_sessions,
    sum(m.monthly_requests) AS total_monthly_requests
FROM daily_active d
LEFT JOIN weekly_active w ON d.workspaceUid = w.workspaceUid AND w.week = toStartOfWeek(d.day)
LEFT JOIN monthly_active m ON d.workspaceUid = m.workspaceUid AND m.month = toStartOfMonth(d.day)
GROUP BY d.day, w.week, m.month
ORDER BY d.day DESC;

-- ====================================================
-- PROJECT MANAGER VIEWS
-- ====================================================

-- Project Managers: Project Usage Metrics
CREATE VIEW IF NOT EXISTS v_project_manager_usage_metrics AS
SELECT
    toStartOfDay(timestamp) AS day,
    workspaceUid,
    groupId AS project_id,
    subGroupId AS sub_project_id,
    count() AS request_count,
    count(DISTINCT sessionUid) AS unique_sessions,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    sum(totalCost) AS total_cost,
    round(avg(latencyMs) / 1000, 2) AS avg_response_time_seconds,
    countIf(status = 'success') / count() AS success_rate
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, workspaceUid, groupId, subGroupId
ORDER BY day DESC, total_cost DESC;

-- Project Managers: Project Health
CREATE VIEW IF NOT EXISTS v_project_manager_project_health AS
SELECT
    toStartOfDay(timestamp) AS day,
    workspaceUid,
    groupId AS project_id,
    count() AS total_requests,
    countIf(status = 'success') AS successful_requests,
    countIf(status = 'error') AS failed_requests,
    round(countIf(status = 'error') * 100.0 / count(), 2) AS error_rate_percent,
    round(avg(latencyMs) / 1000, 2) AS avg_response_time_seconds,
    sum(totalCost) AS total_cost,
    arrayJoin(groupArray(DISTINCT model)) AS models_used,
    count() OVER (PARTITION BY workspaceUid, groupId, model) AS model_requests
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY day, workspaceUid, groupId, model
ORDER BY day DESC, total_requests DESC;


-- Project Managers: Guardrail Impact
CREATE VIEW IF NOT EXISTS v_project_manager_guardrail_impact AS
WITH project_requests AS (
    SELECT
        workspaceUid,
        groupId,
        count(DISTINCT requestUid) AS total_project_requests
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
    GROUP BY workspaceUid, groupId
),
guardrail_stats AS (
    SELECT
        toStartOfDay(gl.timestamp) AS day,
        rl.workspaceUid AS workspaceUid,  -- Explicit column alias
        rl.groupId AS project_id,
        gl.action AS action,              -- Explicit column alias
        gl.severity AS severity,          -- Explicit column alias
        count() AS guardrail_triggers,
        count(DISTINCT gl.requestUid) AS affected_requests
    FROM guardrail_logs gl
    JOIN request_logs rl ON gl.requestUid = rl.requestUid
    WHERE gl.timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
    GROUP BY day, rl.workspaceUid, rl.groupId, gl.action, gl.severity
)
SELECT
    gs.day,
    gs.workspaceUid,
    gs.project_id,
    gs.action,
    gs.severity,
    gs.guardrail_triggers,
    gs.affected_requests,
    round(gs.affected_requests * 100.0 / nullIf(pr.total_project_requests, 0), 2) AS percent_of_project_requests
FROM guardrail_stats gs
JOIN project_requests pr ON gs.workspaceUid = pr.workspaceUid AND gs.project_id = pr.groupId
ORDER BY gs.day DESC, gs.guardrail_triggers DESC;

-- ====================================================
-- FINANCE VIEWS
-- ====================================================

-- Finance: Cost Analysis
CREATE VIEW IF NOT EXISTS v_finance_cost_analysis AS
SELECT
    toStartOfDay(timestamp) AS day,
    workspaceUid,
    model,
    providerName,
    count() AS request_count,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    sum(inputCost) AS total_input_cost,
    sum(outputCost) AS total_output_cost,
    sum(totalCost) AS total_cost,
    round(avg(totalCost), 6) AS avg_request_cost
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 90 DAY
GROUP BY day, workspaceUid, model, providerName
ORDER BY day DESC, total_cost DESC;

-- Finance: Budget Tracking
-- Finance: Budget Tracking (Compatible Version)
CREATE VIEW IF NOT EXISTS v_finance_budget_tracking AS
WITH daily_costs AS (
    SELECT
        toStartOfDay(timestamp) AS day,
        workspaceUid,
        sum(totalCost) AS daily_cost
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 90 DAY
    GROUP BY day, workspaceUid
),
workspace_monthly_costs AS (
    SELECT
        toStartOfMonth(day) AS month,
        workspaceUid,
        sum(daily_cost) AS monthly_cost
    FROM daily_costs
    GROUP BY month, workspaceUid
),
-- Create a running total instead of using window functions
running_totals AS (
    SELECT
        a.month,
        a.workspaceUid,
        a.monthly_cost,
        sum(b.monthly_cost) AS cumulative_cost
    FROM workspace_monthly_costs a
    JOIN workspace_monthly_costs b 
    ON a.workspaceUid = b.workspaceUid AND b.month <= a.month
    GROUP BY a.month, a.workspaceUid, a.monthly_cost
)
SELECT
    month,
    workspaceUid,
    monthly_cost,
    cumulative_cost
FROM running_totals
ORDER BY month DESC, monthly_cost DESC;

-- Finance: Cost Breakdown by Project
CREATE VIEW IF NOT EXISTS v_finance_cost_by_project AS
SELECT
    toStartOfMonth(timestamp) AS month,
    workspaceUid,
    groupId AS project_id,
    sum(totalCost) AS total_cost,
    sum(inputCost) AS input_cost,
    sum(outputCost) AS output_cost,
    count() AS request_count,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    round(sum(totalCost) / count(), 6) AS avg_request_cost
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 90 DAY
GROUP BY month, workspaceUid, groupId
ORDER BY month DESC, total_cost DESC;

-- Finance: Provider Cost Comparison
CREATE VIEW IF NOT EXISTS v_finance_provider_cost_comparison AS
SELECT
    toStartOfMonth(timestamp) AS month,
    providerName,
    model,
    count() AS request_count,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    sum(totalCost) AS total_cost,
    round(sum(totalCost) / sum(inputTokens + outputTokens) * 1000, 6) AS cost_per_1k_tokens,
    round(avg(totalCost), 6) AS avg_request_cost
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 90 DAY
GROUP BY month, providerName, model
ORDER BY month DESC, total_cost DESC;

-- ====================================================
-- CROSS-FUNCTIONAL VIEWS
-- ====================================================

-- Cross-Functional: Executive Dashboard
CREATE VIEW IF NOT EXISTS v_executive_dashboard AS
WITH daily_metrics AS (
    SELECT
        toStartOfDay(timestamp) AS day,
        count() AS request_count,
        countIf(status = 'success') AS successful_requests,
        countIf(status = 'error') AS failed_requests,
        count(DISTINCT workspaceUid) AS active_workspaces,
        count(DISTINCT sessionUid) AS unique_sessions,
        sum(totalCost) AS total_cost,
        sum(inputTokens) AS total_input_tokens,
        sum(outputTokens) AS total_output_tokens,
        avg(latencyMs) AS avg_latency_ms
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
    GROUP BY day
),
previous_period AS (
    SELECT
        sum(request_count) AS prev_request_count,
        sum(successful_requests) AS prev_successful_requests,
        sum(failed_requests) AS prev_failed_requests,
        avg(active_workspaces) AS prev_active_workspaces,
        sum(unique_sessions) AS prev_unique_sessions,
        sum(total_cost) AS prev_total_cost,
        sum(total_input_tokens) AS prev_total_input_tokens,
        sum(total_output_tokens) AS prev_total_output_tokens,
        avg(avg_latency_ms) AS prev_avg_latency_ms
    FROM daily_metrics
    WHERE day BETWEEN toStartOfDay(now()) - INTERVAL 60 DAY AND toStartOfDay(now()) - INTERVAL 31 DAY
),
current_period AS (
    SELECT
        sum(request_count) AS curr_request_count,
        sum(successful_requests) AS curr_successful_requests,
        sum(failed_requests) AS curr_failed_requests,
        avg(active_workspaces) AS curr_active_workspaces,
        sum(unique_sessions) AS curr_unique_sessions,
        sum(total_cost) AS curr_total_cost,
        sum(total_input_tokens) AS curr_total_input_tokens,
        sum(total_output_tokens) AS curr_total_output_tokens,
        avg(avg_latency_ms) AS curr_avg_latency_ms
    FROM daily_metrics
    WHERE day BETWEEN toStartOfDay(now()) - INTERVAL 30 DAY AND toStartOfDay(now())
)
SELECT
    curr_request_count,
    round((curr_request_count - prev_request_count) * 100.0 / nullIf(prev_request_count, 0), 2) AS request_growth_percent,
    curr_successful_requests,
    curr_failed_requests,
    round(curr_failed_requests * 100.0 / nullIf(curr_request_count, 0), 2) AS error_rate_percent,
    round(curr_active_workspaces) AS active_workspaces,
    round((curr_active_workspaces - prev_active_workspaces) * 100.0 / nullIf(prev_active_workspaces, 0), 2) AS workspace_growth_percent,
    curr_unique_sessions,
    round((curr_unique_sessions - prev_unique_sessions) * 100.0 / nullIf(prev_unique_sessions, 0), 2) AS session_growth_percent,
    round(curr_total_cost, 2) AS total_cost,
    round((curr_total_cost - prev_total_cost) * 100.0 / nullIf(prev_total_cost, 0), 2) AS cost_growth_percent,
    curr_total_input_tokens + curr_total_output_tokens AS total_tokens,
    round(curr_avg_latency_ms / 1000, 2) AS avg_response_time_seconds,
    round((curr_avg_latency_ms - prev_avg_latency_ms) * 100.0 / nullIf(prev_avg_latency_ms, 0), 2) AS latency_change_percent
FROM current_period, previous_period;

-- Cross-Functional: Model/Provider Selection Guide
CREATE VIEW IF NOT EXISTS v_model_selection_guide AS
SELECT
    model,
    providerName,
    providerModelName,
    count() AS total_requests,
    round(avg(latencyMs), 2) AS avg_latency_ms,
    round(quantile(0.95)(latencyMs), 2) AS p95_latency_ms,
    countIf(status = 'success') / count() AS success_rate,
    round(avg(totalCost), 6) AS avg_request_cost,
    round(sum(totalCost) / sum(inputTokens + outputTokens) * 1000, 6) AS cost_per_1k_tokens,
    round(avg(inputTokens), 2) AS avg_input_tokens,
    round(avg(outputTokens), 2) AS avg_output_tokens,
    countIf(isFallback) / count() AS fallback_rate
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY model, providerName, providerModelName
HAVING total_requests >= 100  -- Only include models with sufficient sample size
ORDER BY success_rate DESC, avg_latency_ms ASC;

-- Cross-Functional: Guardrail Effectiveness Summary
CREATE VIEW IF NOT EXISTS v_guardrail_effectiveness_summary AS
SELECT
    gl.guardrailUid,
    gl.hook,
    gl.action,
    gl.severity,
    count() AS trigger_count,
    count(DISTINCT gl.requestUid) AS affected_requests,
    count(DISTINCT gl.workspaceUid) AS affected_workspaces,
    round(avg(rl.latencyMs), 2) AS avg_request_latency_ms,
    min(gl.timestamp) AS first_trigger,
    max(gl.timestamp) AS last_trigger,
    arrayStringConcat(groupArray(DISTINCT gl.matched), ', ') AS triggered_patterns,
    round(count(DISTINCT gl.requestUid) * 100.0 / 
          (SELECT count(DISTINCT requestUid) 
           FROM request_logs 
           WHERE timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY), 2) AS percent_of_all_requests
FROM guardrail_logs gl
JOIN request_logs rl ON gl.requestUid = rl.requestUid
WHERE gl.timestamp >= toStartOfDay(now()) - INTERVAL 30 DAY
GROUP BY gl.guardrailUid, gl.hook, gl.action, gl.severity
ORDER BY trigger_count DESC;

-- Cross-Functional: Workspace Overview
CREATE VIEW IF NOT EXISTS v_workspace_overview AS
SELECT
    workspaceUid,
    min(timestamp) AS first_activity,
    max(timestamp) AS last_activity,
    count() AS total_requests,
    count(DISTINCT sessionUid) AS total_sessions,
    count(DISTINCT toStartOfDay(timestamp)) AS active_days,
    count(DISTINCT groupId) AS total_projects,
    countIf(status = 'success') / count() AS overall_success_rate,
    round(avg(latencyMs), 2) AS avg_latency_ms,
    sum(totalCost) AS total_cost,
    sum(inputTokens) AS total_input_tokens,
    sum(outputTokens) AS total_output_tokens,
    arrayStringConcat(groupArray(DISTINCT model), ', ') AS models_used
FROM request_logs
WHERE timestamp >= toStartOfDay(now()) - INTERVAL 90 DAY
GROUP BY workspaceUid
ORDER BY total_requests DESC;

-- ====================================================
-- REAL-TIME MONITORING VIEWS
-- ====================================================

-- Real-time Request Volume
CREATE VIEW IF NOT EXISTS v_realtime_request_volume AS
SELECT
    toStartOfMinute(timestamp) AS minute,
    count() AS request_count,
    countIf(status = 'success') AS success_count,
    countIf(status = 'error') AS error_count,
    countIf(status = 'timeout') AS timeout_count,
    round(avg(latencyMs), 2) AS avg_latency_ms
FROM request_logs
WHERE timestamp >= now() - INTERVAL 6 HOUR
GROUP BY minute
ORDER BY minute DESC;

-- Real-time Error Rate Monitoring
CREATE VIEW IF NOT EXISTS v_realtime_error_rate AS
SELECT
    toStartOfMinute(timestamp) AS minute,
    providerName,
    model,
    count() AS request_count,
    countIf(status = 'error') AS error_count,
    round(countIf(status = 'error') * 100.0 / count(), 2) AS error_rate_percent,
    groupArray(10)(errorCode) AS top_error_codes
FROM request_logs
WHERE timestamp >= now() - INTERVAL 6 HOUR
GROUP BY minute, providerName, model
HAVING request_count >= 5  -- Only include combinations with sufficient sample size
ORDER BY minute DESC, error_rate_percent DESC;

-- Real-time Provider Health
CREATE VIEW IF NOT EXISTS v_realtime_provider_health AS
SELECT
    toStartOfFiveMinute(timestamp) AS five_minute,
    providerName,
    count() AS request_count,
    countIf(status = 'success') AS success_count,
    countIf(status = 'error') AS error_count,
    countIf(status = 'timeout') AS timeout_count,
    round(countIf(status != 'success') * 100.0 / count(), 2) AS error_rate_percent,
    round(avg(latencyMs), 2) AS avg_latency_ms,
    round(quantile(0.95)(latencyMs), 2) AS p95_latency_ms
FROM request_logs
WHERE timestamp >= now() - INTERVAL 6 HOUR
GROUP BY five_minute, providerName
HAVING request_count >= 5  -- Only include providers with sufficient sample size
ORDER BY five_minute DESC, error_rate_percent DESC;

-- ====================================================
-- SUPPLEMENTARY UTILITY VIEWS
-- ====================================================

-- Top N Slowest Requests Today
CREATE VIEW IF NOT EXISTS v_top_slowest_requests AS
SELECT
    requestUid,
    timestamp,
    workspaceUid,
    groupId,
    model,
    providerName,
    latencyMs,
    status,
    errorCode,
    inputTokens,
    outputTokens,
    totalCost,
    isRetry,
    isFallback
FROM request_logs
WHERE timestamp >= toStartOfDay(now())
ORDER BY latencyMs DESC
LIMIT 100;

-- Top N Most Expensive Requests Today
CREATE VIEW IF NOT EXISTS v_top_expensive_requests AS
SELECT
    requestUid,
    timestamp,
    workspaceUid,
    groupId,
    model,
    providerName,
    latencyMs,
    status,
    inputTokens,
    outputTokens,
    totalCost
FROM request_logs
WHERE timestamp >= toStartOfDay(now())
ORDER BY totalCost DESC
LIMIT 100;

-- Request Volume Forecast (Basic Trend Analysis)
CREATE VIEW IF NOT EXISTS v_request_volume_forecast AS
WITH daily_volumes AS (
    SELECT
        toStartOfDay(timestamp) AS day,
        count() AS request_count,
        row_number() OVER (ORDER BY toStartOfDay(timestamp)) AS day_number
    FROM request_logs
    WHERE timestamp >= toStartOfDay(now()) - INTERVAL 60 DAY
    GROUP BY day
)
SELECT
    day,
    request_count,
    avg(request_count) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7day_avg,
    -- Simple linear regression coefficients
    (
        (sum(day_number * request_count) OVER () - sum(day_number) OVER () * sum(request_count) OVER () / count() OVER ()) /
        (sum(day_number * day_number) OVER () - sum(day_number) OVER () * sum(day_number) OVER () / count() OVER ())
    ) AS slope,
    (
        sum(request_count) OVER () / count() OVER () - 
        (sum(day_number * request_count) OVER () - sum(day_number) OVER () * sum(request_count) OVER () / count() OVER ()) /
        (sum(day_number * day_number) OVER () - sum(day_number) OVER () * sum(day_number) OVER () / count() OVER ()) *
        sum(day_number) OVER () / count() OVER ()
    ) AS intercept
FROM daily_volumes
ORDER BY day;
