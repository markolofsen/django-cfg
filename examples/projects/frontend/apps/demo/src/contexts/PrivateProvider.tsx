/**
 * Private Provider for CFG Demo
 *
 * Base providers for authenticated routes (WSRPC and Profile)
 * Specific context providers are wrapped around individual views
 */
import { ReactNode } from 'react';
import { WSRPCProvider } from '@/rpc';
import { ProfileProvider } from './ProfileContext';

export const PrivateProvider = ({ children }: { children: ReactNode }) => {
  return (
    <WSRPCProvider autoConnect={true}>
      <ProfileProvider>
        {children}
      </ProfileProvider>
    </WSRPCProvider>
  );
};
