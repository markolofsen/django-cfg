import { Card, CardContent, Badge } from '@djangocfg/ui-nextjs';
import { TerminalSquare, CheckCircle, XCircle, Clock } from 'lucide-react';
import type { CommandHistoryList } from '@lib/api/generated/terminal/_utils/schemas/CommandHistoryList.schema';

interface CommandHistoryCardProps {
  command: CommandHistoryList;
}

export function CommandHistoryCard({ command }: CommandHistoryCardProps) {
  const isSuccess = command.is_success;

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center ${
                isSuccess ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'
              }`}
            >
              {isSuccess ? (
                <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <TerminalSquare className="h-4 w-4 text-muted-foreground" />
                <code className="font-mono text-sm truncate block">{command.command}</code>
              </div>
              {command.output_preview && (
                <div className="text-xs text-muted-foreground mt-1 font-mono truncate">
                  {command.output_preview}
                </div>
              )}
            </div>
          </div>

          <div className="text-right shrink-0">
            <Badge variant={isSuccess ? 'default' : 'destructive'} className="text-xs">
              {command.exit_code !== null ? `Exit: ${command.exit_code}` : 'N/A'}
            </Badge>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t flex items-center justify-between text-xs">
          <div className="flex items-center gap-1 text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{command.duration_ms}ms</span>
          </div>
          <span className="text-muted-foreground">
            {new Date(command.created_at).toLocaleString()}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
