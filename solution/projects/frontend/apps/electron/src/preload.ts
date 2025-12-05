// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { exposeTerminalAPI } from './features/terminal/ipc/preload';

// Expose terminal API to renderer
exposeTerminalAPI();
