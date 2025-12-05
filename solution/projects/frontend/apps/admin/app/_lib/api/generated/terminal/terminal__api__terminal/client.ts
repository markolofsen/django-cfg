import * as Models from "./models";


/**
 * API endpoints for Terminal.
 */
export class TerminalTerminal {
  private client: any;

  constructor(client: any) {
    this.client = client;
  }

  async commandsList(page?: number, page_size?: number, search?: string, session?: string, status?: string): Promise<Models.PaginatedCommandHistoryListList>;
  async commandsList(params?: { page?: number; page_size?: number; search?: string; session?: string; status?: string }): Promise<Models.PaginatedCommandHistoryListList>;

  /**
   * List command history
   * 
   * ViewSet for Terminal Command History (read-only). Query parameters: -
   * session: Filter by session ID - status: Filter by status (SUCCESS,
   * FAILED, etc.) - search: Search in command text
   */
  async commandsList(...args: any[]): Promise<Models.PaginatedCommandHistoryListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1], search: args[2], session: args[3], status: args[4] };
    }
    const response = await this.client.request('GET', "/api/terminal/commands/", { params });
    return response;
  }

  /**
   * Get command details
   * 
   * ViewSet for Terminal Command History (read-only). Query parameters: -
   * session: Filter by session ID - status: Filter by status (SUCCESS,
   * FAILED, etc.) - search: Search in command text
   */
  async commandsRetrieve(id: string): Promise<Models.CommandHistoryDetail> {
    const response = await this.client.request('GET', `/api/terminal/commands/${id}/`);
    return response;
  }

  async sessionsList(page?: number, page_size?: number): Promise<Models.PaginatedTerminalSessionListList>;
  async sessionsList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedTerminalSessionListList>;

  /**
   * List user's terminal sessions
   * 
   * ViewSet for Terminal Session management. Provides REST API for: -
   * Creating/listing/closing terminal sessions - Sending input to terminal -
   * Resizing terminal - Sending signals (SIGINT, SIGTERM, SIGKILL) Real-time
   * output is delivered via Centrifugo WebSocket: - Channel:
   * terminal#session#{session_id} - Events: output, status, error,
   * command_complete
   */
  async sessionsList(...args: any[]): Promise<Models.PaginatedTerminalSessionListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/api/terminal/sessions/", { params });
    return response;
  }

  /**
   * Create new terminal session
   * 
   * Create a new terminal session.
   */
  async sessionsCreate(data: Models.TerminalSessionCreateRequest): Promise<Models.TerminalSessionCreate> {
    const response = await this.client.request('POST', "/api/terminal/sessions/", { body: data });
    return response;
  }

  /**
   * Get session details
   * 
   * ViewSet for Terminal Session management. Provides REST API for: -
   * Creating/listing/closing terminal sessions - Sending input to terminal -
   * Resizing terminal - Sending signals (SIGINT, SIGTERM, SIGKILL) Real-time
   * output is delivered via Centrifugo WebSocket: - Channel:
   * terminal#session#{session_id} - Events: output, status, error,
   * command_complete
   */
  async sessionsRetrieve(id: string): Promise<Models.TerminalSessionDetail> {
    const response = await this.client.request('GET', `/api/terminal/sessions/${id}/`);
    return response;
  }

  /**
   * Close terminal session
   * 
   * Close terminal session.
   */
  async sessionsDestroy(id: string): Promise<void> {
    const response = await this.client.request('DELETE', `/api/terminal/sessions/${id}/`);
    return;
  }

  async sessionsHistoryList(id: string, page?: number, page_size?: number): Promise<Models.PaginatedCommandHistoryListList>;
  async sessionsHistoryList(id: string, params?: { page?: number; page_size?: number }): Promise<Models.PaginatedCommandHistoryListList>;

  /**
   * Get command history for session
   * 
   * Get command history for this session with pagination.
   */
  async sessionsHistoryList(...args: any[]): Promise<Models.PaginatedCommandHistoryListList> {
    const id = args[0];
    const isParamsObject = args.length === 2 && typeof args[1] === 'object' && args[1] !== null && !Array.isArray(args[1]);
    
    let params;
    if (isParamsObject) {
      params = args[1];
    } else {
      params = { page: args[1], page_size: args[2] };
    }
    const response = await this.client.request('GET', `/api/terminal/sessions/${id}/history/`, { params });
    return response;
  }

  /**
   * Send input to terminal
   * 
   * Send input data to terminal session.
   */
  async sessionsInputCreate(id: string, data: Models.TerminalInputRequest): Promise<any> {
    const response = await this.client.request('POST', `/api/terminal/sessions/${id}/input/`, { body: data });
    return response;
  }

  /**
   * Resize terminal
   * 
   * Resize terminal dimensions.
   */
  async sessionsResizeCreate(id: string, data: Models.TerminalResizeRequest): Promise<any> {
    const response = await this.client.request('POST', `/api/terminal/sessions/${id}/resize/`, { body: data });
    return response;
  }

  /**
   * Send signal to terminal
   * 
   * Send signal to terminal process (SIGINT, SIGTERM, SIGKILL).
   */
  async sessionsSignalCreate(id: string, data: Models.TerminalSignalRequest): Promise<any> {
    const response = await this.client.request('POST', `/api/terminal/sessions/${id}/signal/`, { body: data });
    return response;
  }

  async sessionsActiveList(page?: number, page_size?: number): Promise<Models.PaginatedTerminalSessionListList>;
  async sessionsActiveList(params?: { page?: number; page_size?: number }): Promise<Models.PaginatedTerminalSessionListList>;

  /**
   * Get active sessions only
   * 
   * List only active (connected) sessions with pagination.
   */
  async sessionsActiveList(...args: any[]): Promise<Models.PaginatedTerminalSessionListList> {
    const isParamsObject = args.length === 1 && typeof args[0] === 'object' && args[0] !== null && !Array.isArray(args[0]);
    
    let params;
    if (isParamsObject) {
      params = args[0];
    } else {
      params = { page: args[0], page_size: args[1] };
    }
    const response = await this.client.request('GET', "/api/terminal/sessions/active/", { params });
    return response;
  }

}