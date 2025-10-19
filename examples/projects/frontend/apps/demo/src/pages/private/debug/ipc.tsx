/**
 * IPC Debug Page
 *
 * Interactive page for testing WebSocket RPC communication with Django backend.
 * Allows sending RPC commands and viewing real-time responses.
 */

import { DebugIPCView } from '@/views/debug_ipc';
import { PageWithConfig } from "@/types";

const View: PageWithConfig = () => {
  return <DebugIPCView />;
};

View.pageConfig = {
  title: 'IPC Debug',
  description: 'Debug WebSocket RPC communication with Django backend',
};

export default View;

