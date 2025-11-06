/**
 * React hook for subscribing to Centrifugo channels.
 *
 * Automatically handles subscription lifecycle (mount/unmount).
 *
 * @example
 * // Subscribe to bot heartbeat
 * useSubscription('bot#bot-123#heartbeat', (data) => {
 *   console.log('Heartbeat:', data);
 *   updateMetrics(data);
 * });
 *
 * @example
 * // Conditional subscription
 * useSubscription(
 *   'bot#bot-123#status',
 *   (data) => console.log('Status:', data),
 *   { enabled: isMonitoring }
 * );
 */

import { useEffect, useRef } from 'react';
import { useWSRPC } from './context';

export interface useSubscriptionOptions {
  /**
   * Enable/disable subscription.
   * Defaults to true.
   */
  enabled?: boolean;
}

/**
 * Hook for subscribing to a Centrifugo channel.
 *
 * @param channel - Channel name (e.g., 'bot#bot-123#heartbeat'). Set to null to disable.
 * @param callback - Callback function for received messages
 * @param options - Subscription options
 *
 * @example
 * ```tsx
 * function BotMonitor({ botId }: { botId: string }) {
 *   const [heartbeat, setHeartbeat] = useState(null);
 *
 *   useSubscription(`bot#${botId}#heartbeat`, (data) => {
 *     setHeartbeat(data);
 *   });
 *
 *   return <div>CPU: {heartbeat?.cpu_usage}%</div>;
 * }
 * ```
 */
export function useSubscription<T = any>(
  channel: string | null,
  callback: (data: T) => void,
  options: useSubscriptionOptions = {}
) {
  const { baseClient, isConnected } = useWSRPC();
  const callbackRef = useRef(callback);
  const { enabled = true } = options;

  // Keep callback ref updated (avoid stale closures)
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    // Don't subscribe if disabled, not connected, or no channel
    if (!enabled || !isConnected || !baseClient || !channel) {
      return;
    }

    console.log(`🎣 useSubscription: Subscribing to ${channel}`);

    // Subscribe with stable callback wrapper
    const unsubscribe = baseClient.subscribe(channel, (data) => {
      callbackRef.current(data);
    });

    // Cleanup on unmount or channel change
    return () => {
      console.log(`🎣 useSubscription: Unsubscribing from ${channel}`);
      unsubscribe();
    };
  }, [channel, enabled, isConnected, baseClient]);
}
