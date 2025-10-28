import { useState, useCallback, useEffect, useRef } from 'react';
import { Socket } from 'socket.io-client';

const ROUTER_URL = process.env.NEXT_PUBLIC_ROUTER_API_URL || 'http://localhost:8083';
const API_KEY = process.env.NEXT_PUBLIC_ROUTER_API_KEY || 'ReformsClaude';

interface MessageChunkEvent {
  session_id: string;
  content: string;
  finished: boolean;
  role: 'assistant';
}

export interface Session {
  id: string;
  name: string;
  working_dir: string;
  model: string;
  status: 'active' | 'idle' | 'stopped';
  created_at: string;
  last_active?: string;
  message_count: number;
  tokens_used: number;
  metadata?: Record<string, any>;
}

export interface Message {
  id: number;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tokens_prompt?: number;
  tokens_completion?: number;
}

interface SessionCreateInput {
  name: string;
  working_dir?: string;
  model?: 'sonnet' | 'opus' | 'claude-sonnet-4-5-20250929' | 'claude-opus-4-20250514';
  metadata?: Record<string, any>;
}

export function useSessionChat(socket: Socket | null, workspaceId: string) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const streamingMessageRef = useRef<Message | null>(null);
  const currentSessionIdRef = useRef<string | null>(null);
  const workspaceIdRef = useRef<string>(workspaceId);

  // Update refs when values change
  useEffect(() => {
    currentSessionIdRef.current = currentSession?.id || null;
    workspaceIdRef.current = workspaceId;
  }, [currentSession, workspaceId]);

  // Debug: Track messages changes
  // useEffect(() => {
  //   console.log('[useSessionChat] Messages state changed:', messages.length, 'messages:', JSON.stringify(messages.map(m => ({ id: m.id, role: m.role, content: m.content.substring(0, 50) })), null, 2));
  // }, [messages]);

  // Fetch sessions
  const fetchSessions = useCallback(async () => {
    try {
      // Always use workspace-scoped endpoint (no legacy fallback)
      const endpoint = `${ROUTER_URL}/workspaces/${workspaceIdRef.current}/sessions`;

      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch sessions: ${response.statusText}`);
      }

      const data = await response.json();

      // Deduplicate sessions by ID
      const uniqueSessions = Array.from(
        new Map(data.map((s: Session) => [s.id, s])).values()
      ) as Session[];

      setSessions(uniqueSessions);
    } catch (err) {
      console.error('Error fetching sessions:', err);
      setError(err instanceof Error ? err : new Error('Unknown error'));
    }
  }, []);

  // Create session
  const createSession = useCallback(async (input: SessionCreateInput) => {
    try {
      // Always use workspace-scoped endpoint (no legacy fallback)
      const endpoint = `${ROUTER_URL}/workspaces/${workspaceIdRef.current}/sessions`;

      const payload = {
        workspace_id: workspaceIdRef.current,
        name: input.name,
        working_dir: input.working_dir || '.',
        model: input.model || 'sonnet',
        metadata: input.metadata,
      };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.statusText}`);
      }

      const session: Session = await response.json();

      // Add session to local state
      setSessions(prev => {
        // Check if already exists (avoid duplicates from WebSocket)
        if (prev.some(s => s.id === session.id)) {
          return prev;
        }
        return [...prev, session];
      });

      setCurrentSession(session);
      setMessages([]);

      return session;
    } catch (err) {
      console.error('Error creating session:', err);
      setError(err instanceof Error ? err : new Error('Unknown error'));
      throw err;
    }
  }, []);

  // Select session and load messages
  const selectSession = useCallback(async (sessionId: string) => {
    try {
      // Clear streaming state when switching sessions
      streamingMessageRef.current = null;
      setIsLoading(false);
      setError(null);

      // Fetch session details
      const sessionResponse = await fetch(`${ROUTER_URL}/sessions/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
        },
      });

      if (!sessionResponse.ok) {
        throw new Error(`Failed to fetch session: ${sessionResponse.statusText}`);
      }

      const session: Session = await sessionResponse.json();
      setCurrentSession(session);

      // Fetch session messages
      const messagesResponse = await fetch(`${ROUTER_URL}/sessions/${sessionId}/messages`, {
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
        },
      });

      if (!messagesResponse.ok) {
        throw new Error(`Failed to fetch messages: ${messagesResponse.statusText}`);
      }

      const messageData = await messagesResponse.json();
      setMessages(messageData);
    } catch (err) {
      console.error('Error selecting session:', err);
      setError(err instanceof Error ? err : new Error('Unknown error'));
    }
  }, []);

  // Send message (response will come via WebSocket)
  const sendMessage = useCallback(async (content: string) => {
    if (!currentSession) {
      throw new Error('No session selected');
    }

    const userMessage: Message = {
      id: Date.now(),
      session_id: currentSession.id,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    // console.log('[sendMessage] Adding user message ID:', userMessage.id, 'content:', content.substring(0, 50));

    // Add user message immediately
    setMessages(prev => {
      const updated = [...prev, userMessage];
      // console.log('[sendMessage] Messages after adding user message:', JSON.stringify(updated.map(m => ({ id: m.id, role: m.role, content: m.content.substring(0, 50) })), null, 2));
      return updated;
    });
    setIsLoading(true);
    setError(null);

    try {
      // Send message - response will stream via WebSocket
      const response = await fetch(
        `${ROUTER_URL}/sessions/${currentSession.id}/messages`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`,
          },
          body: JSON.stringify({
            content,
            auto_start: true,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Response chunks will arrive via WebSocket 'message:chunk' events
      // No need to process response body here
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      setIsLoading(false);
      console.error('Chat error:', error);
    }
  }, [currentSession]);

  // Delete session
  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`${ROUTER_URL}/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${API_KEY}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete session: ${response.statusText}`);
      }

      setSessions(prev => prev.filter(s => s.id !== sessionId));

      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Error deleting session:', err);
      setError(err instanceof Error ? err : new Error('Unknown error'));
    }
  }, [currentSession]);

  // WebSocket message chunk listener
  useEffect(() => {
    if (!socket) return;

    const listenerId = Math.random().toString(36).substring(7);
    // console.log(`[useSessionChat ${listenerId}] Setting up message:chunk listener`);

    const handleMessageChunk = (data: MessageChunkEvent) => {
      // console.log(`[useSessionChat ${listenerId}] Received chunk:`, {
      //   session_id: data.session_id,
      //   current_session: currentSessionIdRef.current,
      //   content_len: data.content.length,
      //   finished: data.finished
      // });

      // Only handle chunks for current session
      if (!currentSessionIdRef.current || data.session_id !== currentSessionIdRef.current) {
        // console.log(`[useSessionChat ${listenerId}] Ignoring chunk for different session`);
        return;
      }

      if (!streamingMessageRef.current) {
        // Create new streaming message
        streamingMessageRef.current = {
          id: Date.now() + 1,
          session_id: data.session_id,
          role: 'assistant',
          content: data.content,
          timestamp: new Date().toISOString(),
        };
        // console.log(`[useSessionChat ${listenerId}] Creating new streaming message ID:`, streamingMessageRef.current.id);
        setMessages(prev => {
          const updated = [...prev, streamingMessageRef.current!];
          // console.log(`[useSessionChat ${listenerId}] Messages after adding streaming:`, JSON.stringify(updated.map(m => ({ id: m.id, role: m.role, content: m.content.substring(0, 50) })), null, 2));
          return updated;
        });
      } else {
        // Append to existing streaming message (only if content is not empty)
        if (data.content) {
          streamingMessageRef.current.content += data.content;
          // console.log(`[useSessionChat ${listenerId}] Appending to streaming message ID:`, streamingMessageRef.current.id);
          setMessages(prev => {
            const newMessages = [...prev];
            const lastIndex = newMessages.findIndex(
              m => m.id === streamingMessageRef.current?.id
            );
            // console.log(`[useSessionChat ${listenerId}] Found streaming message at index:`, lastIndex);
            if (lastIndex >= 0) {
              newMessages[lastIndex] = { ...streamingMessageRef.current! };
            }
            // console.log(`[useSessionChat ${listenerId}] Messages after updating streaming:`, JSON.stringify(newMessages.map(m => ({ id: m.id, role: m.role, content: m.content.substring(0, 50) })), null, 2));
            return newMessages;
          });
        } else {
          // console.log(`[useSessionChat ${listenerId}] Skipping empty content chunk (finished signal)`);
        }
      }

      // Clear ref when finished
      if (data.finished) {
        // console.log(`[useSessionChat ${listenerId}] FINISHED! Final assistant message content:`, streamingMessageRef.current?.content);
        streamingMessageRef.current = null;
        setIsLoading(false);

        // Refresh session stats only (don't reload messages to avoid visual jump)
        if (currentSessionIdRef.current) {
          fetch(`${ROUTER_URL}/sessions/${currentSessionIdRef.current}`, {
            headers: { 'Authorization': `Bearer ${API_KEY}` },
          })
            .then(res => res.json())
            .then(session => setCurrentSession(session))
            .catch(err => console.error('Failed to refresh session stats:', err));
        }
      }
    };

    socket.on('message_chunk', handleMessageChunk);

    return () => {
      // console.log(`[useSessionChat ${listenerId}] Cleaning up message_chunk listener`);
      socket.off('message_chunk', handleMessageChunk);
    };
  }, [socket]);

  // Initial load
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return {
    sessions,
    currentSession,
    messages,
    isLoading,
    error,
    createSession,
    selectSession,
    sendMessage,
    deleteSession,
    refreshSessions: fetchSessions,
  };
}
