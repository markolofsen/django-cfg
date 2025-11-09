import * as Models from "./models";


/**
 * API endpoints for Grpc Testing.
 */
export class CfgGrpcTesting {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Call gRPC method
   * 
   * Interactive gRPC method calling using dynamic invocation. Uses gRPC
   * Reflection API to discover and call methods without compiled stubs.
   */
  async grpcTestCallCreate(data: Models.GRPCCallRequestRequest): Promise<Models.GRPCCallResponse> {
    const response = await this.client.request('POST', "/cfg/grpc/test/call/", { body: data });
    return response;
  }

  async grpcTestExamplesRetrieve(method?: string, service?: string): Promise<Models.GRPCExamplesList[]>;
  async grpcTestExamplesRetrieve(params?: { method?: string; service?: string }): Promise<Models.GRPCExamplesList[]>;

  /**
   * Get example payloads
   * 
   * Returns example payloads for testing gRPC methods.
   */
  async grpcTestExamplesRetrieve(...args: any[]): Promise<Models.GRPCExamplesList[]> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { method: args[0], service: args[1] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/test/examples/", { params });
    return (response as any).results || response;
  }

  async grpcTestLogsRetrieve(method?: string, service?: string, status?: string): Promise<Models.GRPCTestLog>;
  async grpcTestLogsRetrieve(params?: { method?: string; service?: string; status?: string }): Promise<Models.GRPCTestLog>;

  /**
   * Get test logs
   * 
   * Returns logs from test gRPC calls. Uses standard DRF pagination.
   */
  async grpcTestLogsRetrieve(...args: any[]): Promise<Models.GRPCTestLog> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { method: args[0], service: args[1], status: args[2] };
    }
    const response = await this.client.request('GET', "/cfg/grpc/test/logs/", { params });
    return response;
  }

}