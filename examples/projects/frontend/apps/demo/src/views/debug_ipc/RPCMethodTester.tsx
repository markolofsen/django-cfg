/**
 * RPC Method Tester Component
 *
 * Interactive form for testing RPC methods with the Django backend.
 * Supports session.message, session.task_status, and session.context_updated methods.
 */

'use client';

import { useState } from 'react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
  Button,
  Label,
  Input,
  Badge,
  useToast,
} from '@djangocfg/ui';
import { useWSRPC } from '@/rpc';
import { Send, Copy, Check, Loader2 } from 'lucide-react';
import type { LogEntry } from './DebugIPCView';

interface RPCMethodTesterProps {
  onLog: (entry: Omit<LogEntry, 'id' | 'timestamp'>) => void;
}

// Predefined RPC methods with templates
const RPC_METHODS = {
  'session.message': {
    label: 'Session Message',
    description: 'Send AI session message (streaming)',
    template: {
      session_id: 'session-123',
      message_id: 'msg-456',
      role: 'user',
      content: 'Hello from debug console!',
      is_streaming: false,
      is_final: true,
      timestamp: new Date().toISOString(),
    },
  },
  'session.task_status': {
    label: 'Task Status',
    description: 'Update AI task status',
    template: {
      task_id: 'task-789',
      status: 'completed',
      progress: 100,
      result: 'Task completed successfully',
      error: null,
      timestamp: new Date().toISOString(),
    },
  },
  'session.context_updated': {
    label: 'Context Updated',
    description: 'Notify session context change',
    template: {
      session_id: 'session-123',
      context: {
        files: ['app.py', 'config.py'],
        variables: { debug: true },
      },
    },
  },
  'workspace.list': {
    label: 'List Workspaces',
    description: 'Get list of workspaces',
    template: {
      user_id: 'user-123',
    },
  },
  'notification.send': {
    label: 'Send Notification',
    description: 'Send notification to user',
    template: {
      user_id: 'user-123',
      title: 'Test Notification',
      message: 'This is a test notification from debug console',
      type: 'info',
    },
  },
};

export function RPCMethodTester({ onLog }: RPCMethodTesterProps) {
  const { client, isConnected } = useWSRPC();
  const { toast } = useToast();
  const [selectedMethod, setSelectedMethod] = useState<string>('session.message');
  const [params, setParams] = useState<string>(
    JSON.stringify(RPC_METHODS['session.message'].template, null, 2)
  );
  const [response, setResponse] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleMethodChange = (method: string) => {
    setSelectedMethod(method);
    const template = RPC_METHODS[method as keyof typeof RPC_METHODS]?.template || {};
    setParams(JSON.stringify(template, null, 2));
    setResponse('');
  };

  const handleSend = async () => {
    if (!isConnected) {
      toast({
        title: 'Not Connected',
        description: 'Please connect to WebSocket first',
        variant: 'destructive',
      });
      return;
    }

    if (!client) {
      toast({
        title: 'Client Error',
        description: 'RPC client not initialized',
        variant: 'destructive',
      });
      return;
    }

    try {
      const parsedParams = JSON.parse(params);
      setIsLoading(true);
      setResponse('');

      onLog({
        type: 'sent',
        method: selectedMethod,
        data: parsedParams,
      });

      // Call RPC method using the appropriate public method
      // Map method name to public method call
      let result: any;
      switch (selectedMethod) {
        case 'session.message':
          result = await client.sessionMessage(parsedParams);
          break;
        case 'session.task_status':
          result = await client.sessionTaskStatus(parsedParams);
          break;
        case 'session.context_updated':
          result = await client.sessionContextUpdated(parsedParams);
          break;
        case 'workspace.file_changed':
          result = await client.workspaceFileChanged(parsedParams);
          break;
        case 'workspace.snapshot_created':
          result = await client.workspaceSnapshotCreated(parsedParams);
          break;
        case 'workspace.state_changed':
          result = await client.workspaceStateChanged(parsedParams);
          break;
        case 'notification.send':
          result = await client.notificationSend(parsedParams);
          break;
        case 'notification.broadcast':
          result = await client.notificationBroadcast(parsedParams);
          break;
        default:
          throw new Error(`Unknown RPC method: ${selectedMethod}`);
      }

      const responseData = JSON.stringify(result, null, 2);
      setResponse(responseData);

      onLog({
        type: 'received',
        method: selectedMethod,
        data: result,
      });

      toast({
        title: 'Success',
        description: `Method ${selectedMethod} executed successfully`,
      });
    } catch (error: any) {
      const errorMessage = error.message || String(error);
      setResponse(JSON.stringify({ error: errorMessage }, null, 2));

      onLog({
        type: 'error',
        method: selectedMethod,
        data: { error: errorMessage },
      });

      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast({
        title: 'Copied',
        description: 'Copied to clipboard',
      });
    } catch (error) {
      toast({
        title: 'Copy Failed',
        description: 'Failed to copy to clipboard',
        variant: 'destructive',
      });
    }
  };

  const methodInfo = RPC_METHODS[selectedMethod as keyof typeof RPC_METHODS];

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Request Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Request</CardTitle>
          <CardDescription>Configure and send RPC method call</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Method Selection */}
          <div className="space-y-2">
            <Label htmlFor="method">RPC Method</Label>
            <Select value={selectedMethod} onValueChange={handleMethodChange}>
              <SelectTrigger id="method">
                <SelectValue placeholder="Select method" />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(RPC_METHODS).map(([key, value]) => (
                  <SelectItem key={key} value={key}>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{value.label}</span>
                      <Badge variant="outline" className="text-xs">
                        {key}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {methodInfo && (
              <p className="text-sm text-muted-foreground">{methodInfo.description}</p>
            )}
          </div>

          {/* Parameters */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="params">Parameters (JSON)</Label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleCopy(params)}
                className="h-7"
              >
                {copied ? (
                  <Check className="h-3 w-3" />
                ) : (
                  <Copy className="h-3 w-3" />
                )}
              </Button>
            </div>
            <Textarea
              id="params"
              value={params}
              onChange={(e) => setParams(e.target.value)}
              className="font-mono text-sm min-h-[300px]"
              placeholder="Enter JSON parameters"
            />
          </div>

          {/* Send Button */}
          <Button
            onClick={handleSend}
            disabled={!isConnected || isLoading}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Send Request
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Response Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Response</CardTitle>
          <CardDescription>Server response from RPC call</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Response Data</Label>
              {response && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopy(response)}
                  className="h-7"
                >
                  {copied ? (
                    <Check className="h-3 w-3" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </Button>
              )}
            </div>
            <div className="rounded-lg border bg-muted/50 p-4 min-h-[300px] max-h-[500px] overflow-auto">
              {response ? (
                <pre className="font-mono text-sm whitespace-pre-wrap break-all">
                  {response}
                </pre>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                  {isLoading ? (
                    <div className="flex flex-col items-center gap-2">
                      <Loader2 className="h-8 w-8 animate-spin" />
                      <p className="text-sm">Waiting for response...</p>
                    </div>
                  ) : (
                    <p className="text-sm">No response yet</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
