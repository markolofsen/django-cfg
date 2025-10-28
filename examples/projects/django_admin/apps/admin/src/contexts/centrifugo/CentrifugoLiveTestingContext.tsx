/**
 * Centrifugo Live Testing Context
 *
 * Provides WebSocket client for real-time Centrifugo testing
 *
 * Features:
 * - Connect/disconnect to Centrifugo server
 * - Subscribe to channels in real-time
 * - Publish messages with live feedback
 * - Track events and connection state
 * - Quick test scenarios
 */

'use client';

import React, { createContext, useContext, useState, useCallback, useRef, type ReactNode } from 'react';
import { Centrifuge, Subscription } from 'centrifuge';
import { toast } from '@djangocfg/ui';
import { useCentrifugoTestingContext } from './CentrifugoTestingContext';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface CentrifugoEvent {
  id: string;
  timestamp: Date;
  type: 'connected' | 'disconnected' | 'subscribed' | 'unsubscribed' | 'publication' | 'error' | 'info';
  channel?: string;
  data?: any;
  message: string;
}

export interface ActiveSubscription {
  channel: string;
  subscription: Subscription;
  lastMessage?: any;
  messageCount: number;
}

export interface QuickScenario {
  id: string;
  name: string;
  description: string;
  channel: string;
  icon: string;
  color: string;
  action: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface CentrifugoLiveTestingContextValue {
  // Connection state
  isConnected: boolean;
  isConnecting: boolean;
  connectionError: string | null;
  connectionTime: Date | null;

  // Client
  centrifuge: Centrifuge | null;

  // Connection methods
  connect: () => Promise<void>;
  disconnect: () => void;

  // Subscription management
  subscriptions: Map<string, ActiveSubscription>;
  subscribe: (channel: string) => Promise<void>;
  unsubscribe: (channel: string) => void;
  unsubscribeAll: () => void;

  // Publishing
  publish: (channel: string, data: any) => Promise<void>;

  // Events
  events: CentrifugoEvent[];
  clearEvents: () => void;

  // Metrics
  totalMessagesReceived: number;

  // Quick scenarios
  quickScenarios: QuickScenario[];
  runScenario: (scenarioId: string) => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const CentrifugoLiveTestingContext = createContext<CentrifugoLiveTestingContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function CentrifugoLiveTestingProvider({ children }: { children: ReactNode }) {
  const { generateConnectionToken, publishTest } = useCentrifugoTestingContext();

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [connectionTime, setConnectionTime] = useState<Date | null>(null);
  const [events, setEvents] = useState<CentrifugoEvent[]>([]);
  const [subscriptions, setSubscriptions] = useState<Map<string, ActiveSubscription>>(new Map());
  const [totalMessagesReceived, setTotalMessagesReceived] = useState(0);

  const centrifugeRef = useRef<Centrifuge | null>(null);
  const eventIdCounter = useRef(0);

  // Add event to log
  const addEvent = useCallback((event: Omit<CentrifugoEvent, 'id' | 'timestamp'>) => {
    setEvents((prev) => [
      {
        ...event,
        id: `event-${eventIdCounter.current++}`,
        timestamp: new Date(),
      },
      ...prev,
    ].slice(0, 100)); // Keep last 100 events
  }, []);

  // Connect to Centrifugo
  const connect = useCallback(async () => {
    if (centrifugeRef.current || isConnecting) {
      return;
    }

    setIsConnecting(true);
    setConnectionError(null);

    try {
      // Generate connection token
      const tokenResponse = await generateConnectionToken({
        user_id: 'test-user',
        channels: [],
      });

      // Use WebSocket URL from API response (configured in django-cfg)
      const wsUrl = tokenResponse.centrifugo_url;

      // Create Centrifuge client
      const client = new Centrifuge(wsUrl, {
        token: tokenResponse.token,
      });

      // Connection events
      client.on('connected', (ctx) => {
        console.log('✅ Connected to Centrifugo:', ctx);
        setIsConnected(true);
        setIsConnecting(false);
        setConnectionTime(new Date());
        addEvent({
          type: 'connected',
          message: 'Connected to Centrifugo server',
          data: ctx,
        });
      });

      client.on('disconnected', (ctx) => {
        console.warn('⚠️ Disconnected from Centrifugo:', ctx);
        setIsConnected(false);
        setIsConnecting(false);
        setConnectionTime(null);
        setTotalMessagesReceived(0);
        addEvent({
          type: 'disconnected',
          message: `Disconnected: ${ctx.reason}`,
          data: ctx,
        });
      });

      client.on('error', (ctx) => {
        console.error('❌ Centrifugo error:', ctx);
        setConnectionError(ctx.error.message);
        addEvent({
          type: 'error',
          message: `Error: ${ctx.error.message}`,
          data: ctx,
        });
      });

      // Connect
      client.connect();
      centrifugeRef.current = client;

      addEvent({
        type: 'info',
        message: 'Connecting to Centrifugo...',
      });
    } catch (error: any) {
      console.error('Failed to connect:', error);
      setIsConnecting(false);
      setConnectionError(error.message);

      addEvent({
        type: 'error',
        message: `Connection failed: ${error.message}`,
      });
    }
  }, [isConnecting, generateConnectionToken, addEvent]);

  // Disconnect
  const disconnect = useCallback(() => {
    if (centrifugeRef.current) {
      // Unsubscribe from all channels
      subscriptions.forEach((sub) => {
        sub.subscription.unsubscribe();
      });
      setSubscriptions(new Map());

      centrifugeRef.current.disconnect();
      centrifugeRef.current = null;
      setIsConnected(false);

      addEvent({
        type: 'info',
        message: 'Disconnected from Centrifugo',
      });
    }
  }, [subscriptions, addEvent]);

  // Subscribe to channel
  const subscribe = useCallback(
    async (channel: string) => {
      const client = centrifugeRef.current;
      if (!client || !isConnected) {
        throw new Error('Not connected to Centrifugo');
      }

      if (subscriptions.has(channel)) {
        addEvent({
          type: 'info',
          channel,
          message: `Already subscribed to ${channel}`,
        });
        return;
      }

      const sub = client.newSubscription(channel);

      sub.on('subscribed', (ctx) => {
        console.log(`✅ Subscribed to ${channel}:`, ctx);
        addEvent({
          type: 'subscribed',
          channel,
          message: `Subscribed to ${channel}`,
          data: ctx,
        });
      });

      sub.on('unsubscribed', (ctx) => {
        console.log(`⚠️ Unsubscribed from ${channel}:`, ctx);
        addEvent({
          type: 'unsubscribed',
          channel,
          message: `Unsubscribed from ${channel}`,
          data: ctx,
        });
      });

      sub.on('publication', (ctx) => {
        console.log(`📩 Message on ${channel}:`, ctx.data);

        setTotalMessagesReceived((prev) => prev + 1);

        setSubscriptions((prev) => {
          const updated = new Map(prev);
          const existing = updated.get(channel);
          if (existing) {
            existing.lastMessage = ctx.data;
            existing.messageCount++;
          }
          return updated;
        });

        addEvent({
          type: 'publication',
          channel,
          message: `Received message on ${channel}`,
          data: ctx.data,
        });
      });

      sub.on('error', (ctx) => {
        console.error(`❌ Subscription error on ${channel}:`, ctx);
        addEvent({
          type: 'error',
          channel,
          message: `Subscription error: ${ctx.error.message}`,
          data: ctx,
        });
      });

      sub.subscribe();

      setSubscriptions((prev) => {
        const updated = new Map(prev);
        updated.set(channel, {
          channel,
          subscription: sub,
          messageCount: 0,
        });
        return updated;
      });
    },
    [isConnected, subscriptions, addEvent]
  );

  // Unsubscribe from channel
  const unsubscribe = useCallback(
    (channel: string) => {
      const sub = subscriptions.get(channel);
      if (sub) {
        sub.subscription.unsubscribe();
        setSubscriptions((prev) => {
          const updated = new Map(prev);
          updated.delete(channel);
          return updated;
        });

        addEvent({
          type: 'info',
          channel,
          message: `Unsubscribed from ${channel}`,
        });
      }
    },
    [subscriptions, addEvent]
  );

  // Unsubscribe from all channels
  const unsubscribeAll = useCallback(() => {
    subscriptions.forEach((sub) => {
      sub.subscription.unsubscribe();
    });
    setSubscriptions(new Map());

    addEvent({
      type: 'info',
      message: 'Unsubscribed from all channels',
    });
  }, [subscriptions, addEvent]);

  // Publish message
  const publish = useCallback(
    async (channel: string, data: any) => {
      if (!isConnected) {
        throw new Error('Not connected to Centrifugo');
      }

      await publishTest({
        channel,
        data,
        wait_for_ack: false,
        ack_timeout: 5,
      });

      addEvent({
        type: 'info',
        channel,
        message: `Published message to ${channel}`,
        data,
      });
    },
    [isConnected, publishTest, addEvent]
  );

  // Clear events
  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  // Quick scenarios
  const quickScenarios: QuickScenario[] = [
    {
      id: 'simple-notification',
      name: 'Simple Notification',
      description: 'Fire-and-forget notification to user#test-123',
      channel: 'user#test-123',
      icon: 'notifications',
      color: 'blue',
      action: async () => {
        await subscribe('user#test-123');
        await publish('user#test-123', {
          type: 'notification',
          title: 'Test Notification',
          message: 'This is a simple test notification',
        });
      },
    },
    {
      id: 'ack-notification',
      name: 'ACK Required',
      description: 'Message with acknowledgment tracking',
      channel: 'user#test-123',
      icon: 'check_circle',
      color: 'green',
      action: async () => {
        await subscribe('user#test-123');
        await publishTest({
          channel: 'user#test-123',
          data: {
            type: 'notification',
            title: 'ACK Test',
            message: 'Please acknowledge this message',
          },
          wait_for_ack: true,
          ack_timeout: 10,
        });
      },
    },
    {
      id: 'broadcast',
      name: 'Team Broadcast',
      description: 'Broadcast to team#developers channel',
      channel: 'team#developers',
      icon: 'campaign',
      color: 'orange',
      action: async () => {
        await subscribe('team#developers');
        await publish('team#developers', {
          type: 'announcement',
          title: 'Team Update',
          message: 'New deployment is ready!',
        });
      },
    },
  ];

  const runScenario = useCallback(
    async (scenarioId: string) => {
      if (!isConnected) {
        toast({
          title: 'Not Connected',
          description: 'Please connect to Centrifugo first',
          variant: 'destructive',
        });
        return;
      }

      const scenario = quickScenarios.find((s) => s.id === scenarioId);
      if (!scenario) {
        toast({
          title: 'Scenario Not Found',
          description: `Scenario not found: ${scenarioId}`,
          variant: 'destructive',
        });
        return;
      }

      addEvent({
        type: 'info',
        message: `Running scenario: ${scenario.name}`,
      });

      await scenario.action();
    },
    [isConnected, addEvent, quickScenarios]
  );

  const value: CentrifugoLiveTestingContextValue = {
    isConnected,
    isConnecting,
    connectionError,
    connectionTime,
    centrifuge: centrifugeRef.current,
    connect,
    disconnect,
    subscriptions,
    subscribe,
    unsubscribe,
    unsubscribeAll,
    publish,
    events,
    clearEvents,
    totalMessagesReceived,
    quickScenarios,
    runScenario,
  };

  return (
    <CentrifugoLiveTestingContext.Provider value={value}>
      {children}
    </CentrifugoLiveTestingContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useCentrifugoLiveTestingContext() {
  const context = useContext(CentrifugoLiveTestingContext);
  if (!context) {
    throw new Error('useCentrifugoLiveTestingContext must be used within CentrifugoLiveTestingProvider');
  }
  return context;
}
