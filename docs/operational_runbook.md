# FloTorch Operational Runbook

## 1. Routine Operational Tasks

### 1.1 Daily Monitoring Activities

| Activity | Description | KPI Metrics | Procedure |
|----------|-------------|-------------|------------|
| CloudWatch Log Review | Check for errors and exceptions | Error Rate < 0.5% | Navigate to CloudWatch > Log Groups > Review `/aws/vendedlogs/states/FlotorchStateMachine-*` and ECS container logs for ERROR level entries |
| DynamoDB Metrics Check | Monitor table performance | Read/Write Latency < 100ms | Check `ExperimentQuestionMetrics_*` table metrics in DynamoDB console for consumed capacity and throttled requests |
| OpenSearch Cluster Health | Verify cluster status | Cluster Status = Green | Access OpenSearch dashboard via endpoint URL and verify cluster health indicator is green |

### 1.2 Weekly Maintenance

| Activity | Description | KPI Metrics | Procedure |
|----------|-------------|-------------|------------|
| S3 Storage Audit | Check data bucket usage | Storage Growth < 15% week-over-week | Review `flotorch-data-*` bucket metrics and set up alerts if approaching storage thresholds |
| Cost Analysis | Review AWS resource consumption | Cost vs Budget Variance < 10% | Use AWS Cost Explorer to track ECS, OpenSearch, and Bedrock API usage against forecasts |
| Experiment Performance | Evaluate model performance | Avg. Retrieval Accuracy > 85% | Query `ExperimentQuestionMetrics_*` table to analyze retrieval accuracy metrics by model |

## 2. Troubleshooting Scenarios

### 2.1 Indexing Pipeline Failures

| Issue | KPI Impact | Diagnostic Steps | Resolution |
|-------|------------|-----------------|------------|
| Indexing Task Timeout | Experiment Success Rate < 90% | 1. Check ECS logs for indexing task<br>2. Verify document size isn't exceeding limits<br>3. Check OpenSearch cluster load | 1. For large documents, adjust chunking parameters<br>2. Scale OpenSearch instance if CPU utilization > 80%<br>3. Restart failed tasks via Step Functions console |
| Embedding API Errors | Token Usage Efficiency < Expected | 1. Check CloudTrail for Bedrock API failures<br>2. Verify IAM role permissions<br>3. Examine error messages in logs | 1. Confirm Bedrock model access<br>2. Ensure BedrockRole has correct permissions<br>3. Check for API throttling and implement backoff strategy |

### 2.2 Retrieval Performance Issues

| Issue | KPI Impact | Diagnostic Steps | Resolution |
|-------|------------|-----------------|------------|
| High Retrieval Latency | Query Response Time > 2s | 1. Check OpenSearch metrics<br>2. Verify vector database query patterns<br>3. Check network latency between components | 1. Optimize OpenSearch index settings<br>2. Adjust semantic search parameters<br>3. Consider OpenSearch instance scaling |
| Poor Relevance Scores | Retrieval Accuracy < 80% | 1. Analyze `ExperimentQuestionMetrics_*` table<br>2. Compare across embedding models<br>3. Review document chunking strategy | 1. Adjust vector similarity thresholds<br>2. Test alternative embedding models<br>3. Refine chunking parameters for improved context |

### 2.3 Web UI Issues

| Issue | KPI Impact | Diagnostic Steps | Resolution |
|-------|------------|-----------------|------------|
| AppRunner Service Unavailable | Service Uptime < 99.9% | 1. Check AppRunner health checks<br>2. Review CloudWatch logs<br>3. Verify VPC connectivity | 1. Restart AppRunner service<br>2. Check security group configurations<br>3. Verify network path to backend services |
| Slow UI Response | User Satisfaction Score < 4.5/5 | 1. Check browser console errors<br>2. Analyze API response times<br>3. Verify AppRunner instance size | 1. Optimize frontend code<br>2. Review backend service performance<br>3. Scale AppRunner service if CPU > 80% |

## 3. Escalation Procedures

| Severity | Description | Response Time | Escalation Path |
|----------|-------------|---------------|----------------|
| P1 - Critical | Production service down or major functionality broken | < 30 minutes | 1. On-call Engineer → 2. Engineering Manager → 3. CTO |
| P2 - High | Degraded performance or minor feature unavailable | < 2 hours | 1. Support Team → 2. On-call Engineer → 3. Engineering Manager |
| P3 - Medium | Non-critical feature issue or isolated problem | < 8 hours | 1. Support Team → 2. Product Owner → 3. Development Team |
| P4 - Low | Enhancement request or documentation issue | < 3 days | 1. Support Team → 2. Product Owner |

## 4. KPI Recovery Targets

| KPI Metric | Normal Range | Warning Threshold | Critical Threshold | Recovery Target |
|------------|--------------|-------------------|---------------------|----------------|
| Service Uptime | > 99.9% | 99.5% - 99.9% | < 99.5% | Return to > 99.9% within 4 hours |
| Query Response Time | < 1s | 1s - 3s | > 3s | Return to < 1s within 2 hours |
| Embedding Success Rate | > 98% | 95% - 98% | < 95% | Return to > 98% within 1 hour |
| Retrieval Accuracy | > 85% | 75% - 85% | < 75% | Return to > 85% within 24 hours |

## 5. Common Commands Reference

```bash
# Check ECS service status
aws ecs describe-services --cluster flotorch-cluster-${suffix} --services flotorch-indexing-service

# View recent CloudWatch logs
aws logs get-log-events --log-group-name /aws/ecs/flotorch-indexing --log-stream-name <stream-name> --limit 100

# Query experiment metrics
aws dynamodb query --table-name ExperimentQuestionMetrics_${suffix} --key-condition-expression "experiment_id = :eid" --expression-attribute-values '{":eid":{"S":"<experiment-id>"}}'  

# Restart AppRunner service
aws apprunner start-deployment --service-arn <apprunner-service-arn>
```
