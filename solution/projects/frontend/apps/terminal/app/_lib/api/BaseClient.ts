/**
 * BaseClient for Terminal App API
 */

import { API as TerminalAPI, LocalStorageAdapter as TerminalStorage } from '@api/generated/terminal';

// Get base URL from environment
const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7301';

// Create singleton Terminal API instance
const terminalApi = new TerminalAPI(baseUrl, { storage: new TerminalStorage() });

export { terminalApi as terminalClient };
