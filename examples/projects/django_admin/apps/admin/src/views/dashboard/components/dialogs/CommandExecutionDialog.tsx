/**
 * Command Execution Dialog
 *
 * Dialog for executing Django management commands with real-time streaming output
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  Button,
  ScrollArea,
  Badge,
} from '@djangocfg/ui/components';
import { useToast } from '@djangocfg/ui/hooks';
import { Terminal, X, CheckCircle, AlertCircle, Loader2, Copy } from 'lucide-react';
import { useDashboardCommandsContext, type CommandExecutionEvent } from '@/contexts/dashboard';
import { APIError } from '@/api/BaseClient';

export interface CommandExecutionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  commandName: string;
  commandArgs?: string[];
  commandOptions?: Record<string, any>;
}

type ExecutionStatus = 'idle' | 'running' | 'success' | 'error';

export const CommandExecutionDialog: React.FC<CommandExecutionDialogProps> = ({
  open,
  onOpenChange,
  commandName,
  commandArgs = [],
  commandOptions = {},
}) => {
  const { executeCommand } = useDashboardCommandsContext();
  const { toast } = useToast();

  const [status, setStatus] = useState<ExecutionStatus>('idle');
  const [output, setOutput] = useState<string[]>([]);
  const [executionTime, setExecutionTime] = useState<number>(0);
  const [returnCode, setReturnCode] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const outputEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new output arrives
  useEffect(() => {
    if (outputEndRef.current) {
      outputEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [output]);

  // Auto-execute when dialog opens
  useEffect(() => {
    if (open && status === 'idle') {
      handleExecute();
    }
  }, [open]);

  const handleExecute = async () => {
    setStatus('running');
    setOutput([]);
    setExecutionTime(0);
    setReturnCode(null);

    try {
      await executeCommand(
        {
          command: commandName,
          args: commandArgs,
          options: commandOptions,
        },
        handleEvent
      );
    } catch (error) {
      setStatus('error');

      let errorMessage = 'Failed to execute command';
      if (error instanceof APIError) {
        if (error.isPermissionError) {
          errorMessage = 'Permission denied - only superusers can execute commands';
        } else if (error.isAuthError) {
          errorMessage = 'Authentication required';
        } else {
          errorMessage = error.errorMessage || errorMessage;
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }

      setOutput((prev) => [...prev, '', `❌ Error: ${errorMessage}`]);

      toast({
        title: 'Execution Failed',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  const handleEvent = (event: CommandExecutionEvent) => {
    switch (event.type) {
      case 'start':
        setOutput([
          `🚀 Executing: ${event.command}`,
          `📋 Arguments: ${event.args.length > 0 ? event.args.join(' ') : '(none)'}`,
          '',
        ]);
        break;

      case 'output':
        setOutput((prev) => [...prev, event.line]);
        break;

      case 'complete':
        setStatus(event.return_code === 0 ? 'success' : 'error');
        setReturnCode(event.return_code);
        setExecutionTime(event.execution_time);

        const icon = event.return_code === 0 ? '✅' : '❌';
        const message = event.return_code === 0 ? 'Success' : 'Failed';

        setOutput((prev) => [
          ...prev,
          '',
          `${icon} Command ${message.toLowerCase()} (exit code: ${event.return_code}, time: ${event.execution_time}s)`,
        ]);

        if (event.return_code === 0) {
          toast({
            title: 'Command Completed',
            description: `${commandName} executed successfully in ${event.execution_time}s`,
          });
        }
        break;

      case 'error':
        setStatus('error');
        setOutput((prev) => [...prev, '', `❌ Error: ${event.error}`]);
        if (event.execution_time) {
          setExecutionTime(event.execution_time);
        }

        toast({
          title: 'Command Failed',
          description: event.error,
          variant: 'destructive',
        });
        break;
    }
  };

  const handleClose = () => {
    if (status === 'running') {
      toast({
        title: 'Command still running',
        description: 'Please wait for the command to finish',
        variant: 'destructive',
      });
      return;
    }

    onOpenChange(false);

    // Reset state after animation
    setTimeout(() => {
      setStatus('idle');
      setOutput([]);
      setExecutionTime(0);
      setReturnCode(null);
    }, 300);
  };

  const handleCopyOutput = () => {
    const text = output.join('\n');
    navigator.clipboard.writeText(text);
    toast({
      title: 'Copied',
      description: 'Command output copied to clipboard',
    });
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'running':
        return (
          <Badge variant="default" className="gap-1.5">
            <Loader2 className="h-3 w-3 animate-spin" />
            Running
          </Badge>
        );
      case 'success':
        return (
          <Badge variant="default" className="gap-1.5 bg-green-500">
            <CheckCircle className="h-3 w-3" />
            Success
          </Badge>
        );
      case 'error':
        return (
          <Badge variant="destructive" className="gap-1.5">
            <AlertCircle className="h-3 w-3" />
            Error
          </Badge>
        );
      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="max-w-4xl max-h-[85vh] flex flex-col">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Terminal className="h-5 w-5" />
              <div>
                <DialogTitle>Command Execution</DialogTitle>
                <DialogDescription className="mt-1">
                  <code className="text-xs font-mono bg-muted px-1.5 py-0.5 rounded">
                    python manage.py {commandName} {commandArgs.join(' ')}
                  </code>
                </DialogDescription>
              </div>
            </div>
            {getStatusBadge()}
          </div>
        </DialogHeader>

        {/* Output Terminal */}
        <div className="flex-1 min-h-0 border rounded-lg bg-slate-950 text-slate-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800 bg-slate-900">
            <div className="flex items-center gap-2">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <span className="text-xs text-slate-400 font-mono">Terminal Output</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopyOutput}
              disabled={output.length === 0}
              className="h-7 text-xs"
            >
              <Copy className="h-3 w-3 mr-1.5" />
              Copy
            </Button>
          </div>

          <ScrollArea className="h-[400px]">
            <div className="p-4 font-mono text-sm space-y-1" ref={scrollRef}>
              {output.length === 0 && status === 'idle' && (
                <div className="text-slate-500 italic">Waiting to execute...</div>
              )}

              {output.map((line, index) => (
                <div
                  key={index}
                  className={`whitespace-pre-wrap break-all ${
                    line.startsWith('❌') || line.includes('Error')
                      ? 'text-red-400'
                      : line.startsWith('✅')
                      ? 'text-green-400'
                      : line.startsWith('🚀') || line.startsWith('📋')
                      ? 'text-blue-400'
                      : 'text-slate-200'
                  }`}
                >
                  {line || '\u00A0'}
                </div>
              ))}

              <div ref={outputEndRef} />
            </div>
          </ScrollArea>
        </div>

        {/* Footer with stats */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            {executionTime > 0 && (
              <span>
                ⏱️ {executionTime}s
              </span>
            )}
            {returnCode !== null && (
              <span>
                Exit Code: <code className="font-mono">{returnCode}</code>
              </span>
            )}
            {output.length > 0 && (
              <span>
                {output.length} lines
              </span>
            )}
          </div>

          <Button onClick={handleClose} disabled={status === 'running'}>
            {status === 'running' ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <X className="h-4 w-4 mr-2" />
                Close
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
