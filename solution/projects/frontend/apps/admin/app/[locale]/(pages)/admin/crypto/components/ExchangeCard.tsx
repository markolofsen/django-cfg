import { Building2, Check, TrendingUp } from 'lucide-react';

import { Badge, Card, CardContent } from '@djangocfg/ui-nextjs';

import type { Exchange } from '@/api/generated/crypto/_utils/schemas/Exchange.schema';

interface ExchangeCardProps {
  exchange: Exchange;
}

export function ExchangeCardComponent({ exchange }: ExchangeCardProps) {
  const volumeFormatted = exchange.volume_24h_usd
    ? `$${Number(exchange.volume_24h_usd).toLocaleString()}`
    : null;
  const rankLabel = exchange.rank ? `#${exchange.rank}` : null;
  const hasFees = exchange.maker_fee_percent || exchange.taker_fee_percent;
  const feesFormatted = hasFees
    ? `${exchange.maker_fee_percent}% / ${exchange.taker_fee_percent}%`
    : null;

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    e.currentTarget.style.display = 'none';
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {exchange.logo_url ? (
              <img
                src={exchange.logo_url}
                alt={exchange.name}
                className="w-10 h-10 rounded-full"
                onError={handleImageError}
              />
            ) : (
              <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                <Building2 className="h-5 w-5" />
              </div>
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{exchange.name}</span>
                {exchange.is_verified && (
                  <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
                )}
                {rankLabel && (
                  <Badge variant="secondary" className="text-xs">
                    {rankLabel}
                  </Badge>
                )}
              </div>
              <div className="text-sm text-muted-foreground">{exchange.code}</div>
            </div>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t space-y-2">
          {volumeFormatted && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">24h Volume:</span>
              <span className="font-medium">{volumeFormatted}</span>
            </div>
          )}
          {exchange.num_markets && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Markets:</span>
              <span className="font-medium">{exchange.num_markets}</span>
            </div>
          )}
          {feesFormatted && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Fees:</span>
              <span className="font-medium">{feesFormatted}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
