import * as Models from "./models";


/**
 * API endpoints for Grpc Configuration.
 */
export class CfgGrpcConfiguration {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Get gRPC configuration
   * 
   * Returns current gRPC server configuration from Django settings.
   */
  async grpcConfigConfigRetrieve(): Promise<Models.GRPCConfig> {
    const response = await this.client.request('GET', "/cfg/grpc/config/config/");
    return response;
  }

  /**
   * Get server information
   * 
   * Returns detailed information about gRPC server, services, and runtime
   * statistics.
   */
  async grpcConfigServerInfoRetrieve(): Promise<Models.GRPCServerInfo> {
    const response = await this.client.request('GET', "/cfg/grpc/config/server-info/");
    return response;
  }

}