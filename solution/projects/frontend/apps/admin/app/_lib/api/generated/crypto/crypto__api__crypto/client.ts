import * as Models from "./models";


/**
 * API endpoints for Crypto.
 */
export class CryptoCrypto {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async coinsList(ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedCoinListList>;
  async coinsList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedCoinListList>;

  /**
   * List coins
   * 
   * ViewSet for cryptocurrency coins.
   */
  async coinsList(...args: any[]): Promise<Models.PaginatedCoinListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/api/crypto/coins/", { params });
    return response;
  }

  /**
   * Get coin details
   * 
   * ViewSet for cryptocurrency coins.
   */
  async coinsRetrieve(id: number): Promise<Models.Coin> {
    const response = await this.client.request('GET', `/api/crypto/coins/${id}/`);
    return response;
  }

  /**
   * Get coin statistics
   * 
   * Get cryptocurrency statistics.
   */
  async coinsStatsRetrieve(): Promise<Models.CoinStats> {
    const response = await this.client.request('GET', "/api/crypto/coins/stats/");
    return response;
  }

  async exchangesList(ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedExchangeList>;
  async exchangesList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedExchangeList>;

  /**
   * List exchanges
   * 
   * ViewSet for cryptocurrency exchanges.
   */
  async exchangesList(...args: any[]): Promise<Models.PaginatedExchangeList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/api/crypto/exchanges/", { params });
    return response;
  }

  /**
   * Get exchange details
   * 
   * ViewSet for cryptocurrency exchanges.
   */
  async exchangesRetrieve(slug: string): Promise<Models.Exchange> {
    const response = await this.client.request('GET', `/api/crypto/exchanges/${slug}/`);
    return response;
  }

  async walletsList(ordering?: string, page?: number, page_size?: number, search?: string): Promise<Models.PaginatedWalletList>;
  async walletsList(params?: { ordering?: string; page?: number; page_size?: number; search?: string }): Promise<Models.PaginatedWalletList>;

  /**
   * List wallets
   * 
   * ViewSet for user wallets.
   */
  async walletsList(...args: any[]): Promise<Models.PaginatedWalletList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { ordering: args[0], page: args[1], page_size: args[2], search: args[3] };
    }
    const response = await this.client.request('GET', "/api/crypto/wallets/", { params });
    return response;
  }

  /**
   * Get wallet details
   * 
   * ViewSet for user wallets.
   */
  async walletsRetrieve(id: string): Promise<Models.Wallet> {
    const response = await this.client.request('GET', `/api/crypto/wallets/${id}/`);
    return response;
  }

}