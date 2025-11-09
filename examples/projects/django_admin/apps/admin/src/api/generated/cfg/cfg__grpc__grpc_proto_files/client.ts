import * as Models from "./models";


/**
 * API endpoints for Grpc Proto Files.
 */
export class CfgGrpcProtoFiles {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * List all proto files
   * 
   * Returns list of all available proto files with metadata.
   */
  async list(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/grpc/proto-files/");
    return response;
  }

  /**
   * Download proto file
   * 
   * Download specific proto file by app label.
   */
  async retrieve(id: string, pk: string): Promise<any> {
    const response = await this.client.request('GET', `/cfg/grpc/proto-files/${id}/`);
    return response;
  }

  /**
   * Download all proto files
   * 
   * Download all proto files as a .zip archive.
   */
  async downloadAllRetrieve(): Promise<any> {
    const response = await this.client.request('GET', "/cfg/grpc/proto-files/download-all/");
    return response;
  }

  /**
   * Generate proto files
   * 
   * Trigger proto file generation for specified apps.
   */
  async generateCreate(data: Models.ProtoGenerateRequestRequest): Promise<Models.ProtoGenerateResponse> {
    const response = await this.client.request('POST', "/cfg/grpc/proto-files/generate/", { body: data });
    return response;
  }

}