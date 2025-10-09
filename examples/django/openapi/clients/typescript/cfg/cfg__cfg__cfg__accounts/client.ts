import * as Models from "./models";


/**
 * API endpoints for Cfg Accounts.
 */
export class CfgAccountsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
   * Request OTP code to email or phone.
   */
  async cfgAccountsOtpRequestCreate(data: Models.OTPRequestRequest): Promise<Models.OTPRequestResponse> {
    const response = await this.client.request('POST', "/cfg/accounts/otp/request/", { body: data });
    return response;
  }

  /**
   * Verify OTP code and return JWT tokens.
   */
  async cfgAccountsOtpVerifyCreate(data: Models.OTPVerifyRequest): Promise<Models.OTPVerifyResponse> {
    const response = await this.client.request('POST', "/cfg/accounts/otp/verify/", { body: data });
    return response;
  }

}