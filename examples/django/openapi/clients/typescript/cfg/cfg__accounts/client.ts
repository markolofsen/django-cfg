import * as Models from "./models";


/**
 * API endpoints for Accounts.
 */
export class CfgAccountsAPI {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  /**
 * Request OTP code to email or phone.
 */
async otpRequestCreate(data: Models.OTPRequestRequest): Promise<Models.OTPRequestResponse> {
  const response = await this.client.request<Models.OTPRequestResponse>('POST', "/django_cfg_accounts/otp/request/", { body: data });
  return response;
}

  /**
 * Verify OTP code and return JWT tokens.
 */
async otpVerifyCreate(data: Models.OTPVerifyRequest): Promise<Models.OTPVerifyResponse> {
  const response = await this.client.request<Models.OTPVerifyResponse>('POST', "/django_cfg_accounts/otp/verify/", { body: data });
  return response;
}

}