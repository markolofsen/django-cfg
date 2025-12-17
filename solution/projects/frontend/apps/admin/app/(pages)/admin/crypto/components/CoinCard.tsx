import { TrendingDown, TrendingUp } from 'lucide-react';

import { Badge, Card, CardContent } from '@djangocfg/ui-nextjs';

import type { CoinList } from '@/api/generated/crypto/_utils/schemas/CoinList.schema';

interface CoinCardProps {
  coin: CoinList;
}

export function CoinCardComponent({ coin }: CoinCardProps) {
  // Handle is_price_up_24h as either boolean or string
  const isPriceUp = coin.is_price_up_24h === true;
  const priceChange = coin.price_change_24h_percent ? parseFloat(String(coin.price_change_24h_percent)) : 0;

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {coin.logo_url && (
              <img
                src={coin.logo_url}
                alt={coin.name}
                className="w-10 h-10 rounded-full"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
              />
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{coin.symbol}</span>
                {coin.rank && (
                  <Badge variant="secondary" className="text-xs">
                    #{coin.rank}
                  </Badge>
                )}
              </div>
              <div className="text-sm text-muted-foreground">{coin.name}</div>
            </div>
          </div>

          <div className="text-right">
            <div className="font-semibold">
              ${coin.current_price_usd ? Number(coin.current_price_usd).toLocaleString() : '0.00'}
            </div>
            {priceChange !== 0 && (
              <div className={`flex items-center gap-1 text-sm ${isPriceUp ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {isPriceUp ? (
                  <TrendingUp className="h-3 w-3" />
                ) : (
                  <TrendingDown className="h-3 w-3" />
                )}
                {Math.abs(priceChange).toFixed(2)}%
              </div>
            )}
          </div>
        </div>

        {coin.market_cap_usd && (
          <div className="mt-3 pt-3 border-t text-xs text-muted-foreground">
            Market Cap: ${Number(coin.market_cap_usd).toLocaleString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
