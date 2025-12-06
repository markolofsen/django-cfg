import Link from 'next/link';
import { Card, CardContent, Badge, Button } from '@djangocfg/ui-nextjs';
import { Terminal, Circle, X, FolderOpen, Monitor, ExternalLink } from 'lucide-react';
import type { TerminalSessionList } from '@lib/api/generated/terminal/_utils/schemas/TerminalSessionList.schema';

interface SessionCardProps {
  session: TerminalSessionList;
  onClose?: (id: string) => void;
  onSelect?: (id: string) => void;
}

export function SessionCard({ session, onClose, onSelect }: SessionCardProps) {
  const terminalUrl = `/${session.id}`;
  const isAlive = session.is_alive;

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
              <Terminal className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{session.display_name}</span>
                <Badge variant={isAlive ? 'default' : 'secondary'} className="text-xs">
                  <Circle
                    className={`h-2 w-2 mr-1 ${isAlive ? 'fill-green-500 text-green-500' : 'fill-gray-400 text-gray-400'}`}
                  />
                  {isAlive ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              {session.name && (
                <div className="text-sm text-muted-foreground">{session.name}</div>
              )}
            </div>
          </div>

          <div className="flex gap-1">
            {isAlive && (
              <Button variant="ghost" size="icon" asChild>
                <Link href={terminalUrl}>
                  <ExternalLink className="h-4 w-4" />
                </Link>
              </Button>
            )}
            {onSelect && isAlive && (
              <Button variant="ghost" size="icon" onClick={() => onSelect(session.id)}>
                <Monitor className="h-4 w-4" />
              </Button>
            )}
            {onClose && isAlive && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onClose(session.id)}
                className="text-destructive hover:text-destructive"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>

        <div className="mt-3 pt-3 border-t space-y-2">
          {session.working_directory && (
            <div className="flex items-center gap-2 text-xs">
              <FolderOpen className="h-3 w-3 text-muted-foreground" />
              <span className="text-muted-foreground font-mono truncate">
                {session.working_directory}
              </span>
            </div>
          )}
          {session.shell && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Shell:</span>
              <span className="font-medium">{session.shell}</span>
            </div>
          )}
          {session.electron_hostname && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Host:</span>
              <span className="font-medium">{session.electron_hostname}</span>
            </div>
          )}
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Created:</span>
            <span className="font-medium">
              {new Date(session.created_at).toLocaleString()}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
