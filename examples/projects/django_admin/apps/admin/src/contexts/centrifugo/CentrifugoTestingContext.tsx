/**
 * Centrifugo Testing Context
 *
 * Manages Centrifugo testing operations
 *
 * Features:
 * - Connection token generation
 * - Test message publishing
 * - Publishing with database logging
 * - Manual ACK sending
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useCreateCentrifugoAdminApiTestingConnectionTokenCreate,
  useCreateCentrifugoAdminApiTestingPublishTestCreate,
  useCreateCentrifugoAdminApiTestingPublishWithLoggingCreate,
  useCreateCentrifugoAdminApiTestingSendAckCreate,
} from '@/api/generated/cfg/_utils/hooks/cfg__centrifugo__centrifugo_testing';
import type { API } from '@/api/generated/cfg';
import type {
  ConnectionTokenRequestRequest,
  ConnectionTokenResponse,
  PublishTestRequestRequest,
  PublishTestResponse,
  ManualAckRequestRequest,
  ManualAckResponse,
} from '@/api/generated/cfg/_utils/schemas';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface CentrifugoTestingContextValue {
  // Connection token generation
  generateConnectionToken: (data: ConnectionTokenRequestRequest) => Promise<ConnectionTokenResponse>;

  // Publishing
  publishTest: (data: PublishTestRequestRequest) => Promise<PublishTestResponse>;
  publishWithLogging: (data: PublishTestRequestRequest) => Promise<PublishTestResponse>;

  // Manual ACK
  sendAck: (data: ManualAckRequestRequest) => Promise<ManualAckResponse>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const CentrifugoTestingContext = createContext<CentrifugoTestingContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function CentrifugoTestingProvider({ children }: { children: ReactNode }) {
  // Mutation hooks
  const generateTokenMutation = useCreateCentrifugoAdminApiTestingConnectionTokenCreate();
  const publishTestMutation = useCreateCentrifugoAdminApiTestingPublishTestCreate();
  const publishWithLoggingMutation = useCreateCentrifugoAdminApiTestingPublishWithLoggingCreate();
  const sendAckMutation = useCreateCentrifugoAdminApiTestingSendAckCreate();

  // Generate JWT token for WebSocket connection
  const generateConnectionToken = async (data: ConnectionTokenRequestRequest): Promise<ConnectionTokenResponse> => {
    return await generateTokenMutation(data, api as unknown as API);
  };

  // Publish test message to Centrifugo
  const publishTest = async (data: PublishTestRequestRequest): Promise<PublishTestResponse> => {
    return await publishTestMutation(data, api as unknown as API);
  };

  // Publish message with database logging
  const publishWithLogging = async (data: PublishTestRequestRequest): Promise<PublishTestResponse> => {
    return await publishWithLoggingMutation(data, api as unknown as API);
  };

  // Send manual ACK for a message
  const sendAck = async (data: ManualAckRequestRequest): Promise<ManualAckResponse> => {
    return await sendAckMutation(data, api as unknown as API);
  };

  const value: CentrifugoTestingContextValue = {
    generateConnectionToken,
    publishTest,
    publishWithLogging,
    sendAck,
  };

  return (
    <CentrifugoTestingContext.Provider value={value}>
      {children}
    </CentrifugoTestingContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useCentrifugoTestingContext(): CentrifugoTestingContextValue {
  const context = useContext(CentrifugoTestingContext);
  if (!context) {
    throw new Error('useCentrifugoTestingContext must be used within CentrifugoTestingProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  ConnectionTokenRequestRequest,
  ConnectionTokenResponse,
  PublishTestRequestRequest,
  PublishTestResponse,
  ManualAckRequestRequest,
  ManualAckResponse,
};
