import { Card, CardContent, CardHeader, CardTitle } from '@djangocfg/ui';
import { DollarSign, TrendingUp, Target, Award } from 'lucide-react';
import type { Portfolio, PortfolioStats } from '@/api/generated/trading/trading__api__trading/models';

interface PortfolioStatsProps {
  portfolio: Portfolio | undefined;
  stats: PortfolioStats | undefined;
}

export function PortfolioStatsComponent({ portfolio, stats }: PortfolioStatsProps) {
  if (!portfolio) return null;

  const statsData = [
    {
      title: 'Total Balance',
      value: `$${portfolio.total_balance_usd || '0.00'}`,
      icon: DollarSign,
      description: 'Portfolio value'
    },
    {
      title: 'Total Trades',
      value: portfolio.total_trades || 0,
      icon: TrendingUp,
      description: `${portfolio.winning_trades || 0} winning`
    },
    {
      title: 'Win Rate',
      value: `${portfolio.win_rate || '0'}%`,
      icon: Target,
      description: 'Success rate'
    },
    {
      title: 'Profit/Loss',
      value: `$${portfolio.total_profit_loss || '0.00'}`,
      icon: Award,
      description: 'Total P/L'
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-4">
      {statsData.map((stat) => (
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
