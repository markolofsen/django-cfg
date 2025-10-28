/**
 * Private Provider for CFG Demo
 *
 * Base provider for authenticated routes (WSRPC)
 * Specific context providers are wrapped around individual views
 */
import { ReactNode } from 'react';
import { WSRPCProvider } from '@/rpc';

export const PrivateProvider = ({ children }: { children: ReactNode }) => {
  return (
    <WSRPCProvider autoConnect={true}>
      {children}
    </WSRPCProvider>
  );
};
