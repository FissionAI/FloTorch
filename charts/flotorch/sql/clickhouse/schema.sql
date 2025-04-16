-- Create database if not exists
CREATE DATABASE IF NOT EXISTS flotorch;

-- Switch to database
USE flotorch;
SET enable_json_type = 1;

-- Request logs for basic request-level logging
CREATE TABLE IF NOT EXISTS request_logs (
  timestamp DateTime64(3), -- Use DateTime64 with 3 decimal places for millisecond precision
  gatewayUid UUID,
  groupId String,
  subGroupId String,
  workspaceUid UUID,
  requestUid UUID,
  sessionUid UUID,
  apikeyUid UUID,
  model LowCardinality(String),
  modelUid UUID,
  configUid UUID,
  providerUid UUID,
  providerName LowCardinality(String),
  providerModelName LowCardinality(String),
  type String,
  latencyMs UInt32 CODEC(Delta, ZSTD),
  inputTokens UInt32 CODEC(Delta, ZSTD),
  outputTokens UInt32 CODEC(Delta, ZSTD),
  inputCost Float64,
  outputCost Float64,
  totalCost Float64,
  status LowCardinality(String) DEFAULT 'unknown' NOT NULL,
  errorCode String,
  isRetry Bool DEFAULT false NOT NULL,
  isFallback Bool DEFAULT false NOT NULL,
  routingStrategy String,
  attemptNumber UInt8 DEFAULT 1 NOT NULL,
  metadata JSON CODEC(ZSTD(3)),
  request JSON CODEC(ZSTD(3)),
  response JSON CODEC(ZSTD(3))
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, workspaceUid, requestUid)
TTL toDateTime(timestamp) + INTERVAL 360 DAY
SETTINGS index_granularity = 8192;

-- Add indices with IF NOT EXISTS
ALTER TABLE request_logs ADD INDEX IF NOT EXISTS idx_model (model) TYPE minmax GRANULARITY 1;
ALTER TABLE request_logs ADD INDEX IF NOT EXISTS idx_status (status) TYPE minmax GRANULARITY 1;
ALTER TABLE request_logs ADD INDEX IF NOT EXISTS idx_provider (providerName) TYPE minmax GRANULARITY 1;

-- Add projections for common query patterns with IF NOT EXISTS
ALTER TABLE request_logs ADD PROJECTION IF NOT EXISTS cost_by_model
(
    SELECT
        model,
        toStartOfHour(timestamp) AS hour,
        count() AS request_count,
        sum(inputTokens) AS total_input_tokens,
        sum(outputTokens) AS total_output_tokens,
        sum(totalCost) AS total_cost
    GROUP BY
        model, hour
);

ALTER TABLE request_logs ADD PROJECTION IF NOT EXISTS latency_stats
(
    SELECT
        model,
        toStartOfHour(timestamp) AS hour,
        avg(latencyMs) AS avg_latency,
        min(latencyMs) AS min_latency,
        max(latencyMs) AS max_latency
    GROUP BY
        model, hour
);

-- Materialize the projections - note: MATERIALIZE doesn't support IF NOT EXISTS
-- but will silently do nothing if projection is already materialized
ALTER TABLE request_logs MATERIALIZE PROJECTION cost_by_model;
ALTER TABLE request_logs MATERIALIZE PROJECTION latency_stats;

-- Guardrail logs for policy checks
CREATE TABLE IF NOT EXISTS guardrail_logs (
  timestamp DateTime64(3), -- Use DateTime64 with 3 decimal places for millisecond precision
  workspaceUid UUID,
  requestUid UUID,
  guardrailUid UUID,
  modelGuardrailUid UUID,
  hook String,
  action LowCardinality(String) NOT NULL,
  severity LowCardinality(String) DEFAULT 'info' NOT NULL,
  matched String,
  metadata JSON CODEC(ZSTD(3))
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, workspaceUid, requestUid)
TTL toDateTime(timestamp) + INTERVAL 360 DAY
SETTINGS index_granularity = 8192;

-- Add indices for guardrail_logs
ALTER TABLE guardrail_logs ADD INDEX IF NOT EXISTS idx_action (action) TYPE minmax GRANULARITY 1;
ALTER TABLE guardrail_logs ADD INDEX IF NOT EXISTS idx_severity (severity) TYPE minmax GRANULARITY 1;

-- Add projection for guardrail analysis
ALTER TABLE guardrail_logs ADD PROJECTION IF NOT EXISTS guardrail_summary
(
    SELECT
        action,
        severity,
        toStartOfHour(timestamp) AS hour,
        count() AS check_count
    GROUP BY
        action, severity, hour
);

ALTER TABLE guardrail_logs MATERIALIZE PROJECTION guardrail_summary;

-- Request traces for detailed stage-level logging
CREATE TABLE IF NOT EXISTS request_traces (
  timestamp DateTime64(3), -- Use DateTime64 with 3 decimal places for millisecond precision
  workspaceUid UUID,
  requestUid UUID,
  sessionUid UUID,
  stage Enum8(
    'apikey_validation' = 1,
    'config_resolve' = 2,
    'prompt_transform' = 3,
    'input_guardrail_check' = 4,
    'output_guardrail_check' = 5,
    'provider_selection' = 6,
    'request_transform' = 7,
    'provider_request' = 8,
    'response_transform' = 9,
    'cost_calculation' = 10,
    'error_handling' = 11
  ),
  guardrailUid UUID,
  modelGuardrailUid UUID,
  startTime DateTime64(3), -- Use DateTime64 with 3 decimal places for millisecond precision
  endTime DateTime64(3), -- Use DateTime64 with 3 decimal places for millisecond precision
  latencyMs UInt32 CODEC(Delta, ZSTD),
  status LowCardinality(String) DEFAULT 'unknown' NOT NULL,
  errorCode String,
  errorMessage String,
  inputBody JSON CODEC(ZSTD(3)),
  outputBody JSON CODEC(ZSTD(3)),
  metadata JSON CODEC(ZSTD(3)),
  sequence UInt32 DEFAULT 0 -- Add sequence number for ordering
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (requestUid, sequence, timestamp)
TTL toDateTime(timestamp) + INTERVAL 120 DAY
SETTINGS index_granularity = 8192;

-- Create indices for request traces for better query performance
ALTER TABLE request_traces ADD INDEX IF NOT EXISTS idx_sequence (sequence) TYPE minmax GRANULARITY 1;
ALTER TABLE request_traces ADD INDEX IF NOT EXISTS idx_request_sequence (requestUid, sequence) TYPE minmax GRANULARITY 1;
ALTER TABLE request_traces ADD INDEX IF NOT EXISTS idx_request_timestamp (requestUid, timestamp) TYPE minmax GRANULARITY 1;
ALTER TABLE request_traces ADD INDEX IF NOT EXISTS idx_stage (stage) TYPE minmax GRANULARITY 1;

-- Add projection for stage timing analysis
ALTER TABLE request_traces ADD PROJECTION IF NOT EXISTS stage_timing
(
    SELECT
        stage,
        toStartOfHour(timestamp) AS hour,
        avg(latencyMs) AS avg_stage_latency,
        count() AS stage_count
    GROUP BY
        stage, hour
);

ALTER TABLE request_traces MATERIALIZE PROJECTION stage_timing;
