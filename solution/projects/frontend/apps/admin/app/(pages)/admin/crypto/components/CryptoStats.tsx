import { Card, CardContent, CardHeader, CardTitle } from '@djangocfg/ui-nextjs';
import { DollarSign, TrendingUp, Bitcoin } from 'lucide-react';
import type { CoinStats } from '@/api/generated/crypto/_utils/schemas/CoinStats.schema';

interface CryptoStatsProps {
  stats: CoinStats | undefined;
}

export function CryptoStatsComponent({ stats }: CryptoStatsProps) {
  if (!stats) return null;

  const statsData = [
    {
      title: 'Total Coins',
      value: stats.total_coins,
      icon: Bitcoin,
      description: 'Listed cryptocurrencies'
    },
    {
      title: 'Market Cap',
      value: `$${Number(stats.total_market_cap_usd).toLocaleString()}`,
      icon: DollarSign,
      description: 'Total market value'
    },
    {
      title: '24h Volume',
      value: `$${Number(stats.total_volume_24h_usd).toLocaleString()}`,
      icon: TrendingUp,
      description: 'Trading volume'
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-3">
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
