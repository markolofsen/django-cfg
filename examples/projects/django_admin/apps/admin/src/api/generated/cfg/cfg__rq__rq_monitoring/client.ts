import * as Models from "./models";


/**
 * API endpoints for RQ Monitoring.
 */
export class CfgRqMonitoring {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get RQ configuration
   * 
   * Returns current RQ configuration from django-cfg.
   */
  async rqMonitorConfigRetrieve(): Promise<Models.RQConfig> {
    const response = await this.client.request('GET', "/cfg/rq/monitor/config/");
    return response;
  }

  /**
   * Health check
   * 
   * Returns RQ cluster health status including worker count and queue
   * status.
   */
  async rqMonitorHealthRetrieve(): Promise<Models.HealthCheck> {
    const response = await this.client.request('GET', "/cfg/rq/monitor/health/");
    return response;
  }

  /**
   * Prometheus metrics
   * 
   * Returns Prometheus metrics for RQ queues and workers.
   */
  async rqMonitorMetricsRetrieve(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/rq/monitor/metrics/");
    return response;
  }

}