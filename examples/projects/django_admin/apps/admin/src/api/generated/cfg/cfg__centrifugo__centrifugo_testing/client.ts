import * as Models from "./models";


/**
 * API endpoints for Centrifugo Testing.
 */
export class CfgCentrifugoTesting {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Publish test message
   * 
   * Publish test message to Centrifugo via wrapper with optional ACK
   * tracking.
   */
  async publishTestCreate(data: Models.PublishTestRequestRequest): Promise<Models.PublishTestResponse> {
    const response = await this.client.request('POST', "/cfg/centrifugo/testing/publish-test/", { body: data });
    return response;
  }

  /**
   * Publish with database logging
   * 
   * Publish message using CentrifugoClient with database logging. This will
   * create CentrifugoLog records.
   */
  async publishWithLoggingCreate(data: Models.PublishTestRequestRequest): Promise<Models.PublishTestResponse> {
    const response = await this.client.request('POST', "/cfg/centrifugo/testing/publish-with-logging/", { body: data });
    return response;
  }

  /**
   * Send manual ACK
   * 
   * Manually send ACK for a message to the wrapper. Pass message_id in
   * request body.
   */
  async sendAckCreate(data: Models.ManualAckRequestRequest): Promise<Models.ManualAckResponse> {
    const response = await this.client.request('POST', "/cfg/centrifugo/testing/send-ack/", { body: data });
    return response;
  }

}