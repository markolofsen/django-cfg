import { Card, CardContent, CardHeader, CardTitle } from '@djangocfg/ui-nextjs';
import { Terminal, Activity, Clock } from 'lucide-react';
import type { TerminalSessionList } from '@/api/generated/terminal/_utils/schemas/TerminalSessionList.schema';

interface SessionStatsProps {
  sessions: TerminalSessionList[];
  activeSessions: TerminalSessionList[];
}

export function SessionStats({ sessions, activeSessions }: SessionStatsProps) {
  const stats = [
    {
      title: 'Total Sessions',
      value: sessions.length,
      icon: Terminal,
      description: 'All terminal sessions',
    },
    {
      title: 'Active Sessions',
      value: activeSessions.length,
      icon: Activity,
      description: 'Currently running',
    },
    {
      title: 'Inactive',
      value: sessions.length - activeSessions.length,
      icon: Clock,
      description: 'Closed sessions',
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {stats.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
            <stat.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stat.value}</div>
            <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
