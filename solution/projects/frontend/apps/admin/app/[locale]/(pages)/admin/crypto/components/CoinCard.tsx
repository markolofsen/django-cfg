import { TrendingDown, TrendingUp } from 'lucide-react';

import { Badge, Card, CardContent } from '@djangocfg/ui-nextjs';

import type { CoinList } from '@/api/generated/crypto/_utils/schemas/CoinList.schema';

interface CoinCardProps {
  coin: CoinList;
}

export function CoinCardComponent({ coin }: CoinCardProps) {
  const isPriceUp = coin.is_price_up_24h === true;
  const priceChange = coin.price_change_24h_percent ? parseFloat(String(coin.price_change_24h_percent)) : 0;
  const hasPriceChange = priceChange !== 0;

  const currentPrice = coin.current_price_usd
    ? `$${Number(coin.current_price_usd).toLocaleString()}`
    : '$0.00';
  const priceChangeFormatted = `${Math.abs(priceChange).toFixed(2)}%`;
  const marketCapFormatted = coin.market_cap_usd
    ? `Market Cap: $${Number(coin.market_cap_usd).toLocaleString()}`
    : null;
  const rankLabel = coin.rank ? `#${coin.rank}` : null;

  const TrendIcon = isPriceUp ? TrendingUp : TrendingDown;
  const priceChangeClass = isPriceUp
    ? 'flex items-center gap-1 text-sm text-green-600 dark:text-green-400'
    : 'flex items-center gap-1 text-sm text-red-600 dark:text-red-400';

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    e.currentTarget.style.display = 'none';
  };

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
                onError={handleImageError}
              />
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{coin.symbol}</span>
                {rankLabel && (
                  <Badge variant="secondary" className="text-xs">
                    {rankLabel}
                  </Badge>
                )}
              </div>
              <div className="text-sm text-muted-foreground">{coin.name}</div>
            </div>
          </div>

          <div className="text-right">
            <div className="font-semibold">{currentPrice}</div>
            {hasPriceChange && (
              <div className={priceChangeClass}>
                <TrendIcon className="h-3 w-3" />
                {priceChangeFormatted}
              </div>
            )}
          </div>
        </div>

        {marketCapFormatted && (
          <div className="mt-3 pt-3 border-t text-xs text-muted-foreground">
            {marketCapFormatted}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
