import * as Models from "./models";


/**
 * API endpoints for Grpc Services.
 */
export class CfgGrpcServices {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async list(hours?: number, page?: number, page_size?: number): Promise<Models.PaginatedServiceSummaryList>;
  async list(params?: { hours?: number; page?: number; page_size?: number }): Promise<Models.PaginatedServiceSummaryList>;

  /**
   * List all services
   * 
   * Returns paginated list of all registered gRPC services with basic
   * statistics.
   */
  async list(...args: any[]): Promise<Models.PaginatedServiceSummaryList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { hours: args[0], page: args[1], page_size: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/services/", { params });
    return response;
  }

  /**
   * Get service details
   * 
   * Returns detailed information about a specific gRPC service.
   */
  async retrieve(id: string, pk: string): Promise<Models.ServiceDetail> {
    const response = await this.client.request('GET', `/cfg/grpc/services/${id}/`);
    return response;
  }

  /**
   * Get service methods
   * 
   * Returns list of methods for a specific service with statistics.
   */
  async methodsRetrieve(id: string, pk: string): Promise<Models.ServiceMethods> {
    const response = await this.client.request('GET', `/cfg/grpc/services/${id}/methods/`);
    return response;
  }

}