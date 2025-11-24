import { Card, CardContent, Badge } from '@djangocfg/ui';
import { Building2, TrendingUp, Check } from 'lucide-react';
import type { Exchange } from '@/api/generated/crypto/crypto__api__crypto/models';

interface ExchangeCardProps {
  exchange: Exchange;
}

export function ExchangeCardComponent({ exchange }: ExchangeCardProps) {
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
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
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
                {exchange.rank && (
                  <Badge variant="secondary" className="text-xs">
                    #{exchange.rank}
                  </Badge>
                )}
              </div>
              <div className="text-sm text-muted-foreground">{exchange.code}</div>
            </div>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t space-y-2">
          {exchange.volume_24h_usd && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">24h Volume:</span>
              <span className="font-medium">${Number(exchange.volume_24h_usd).toLocaleString()}</span>
            </div>
          )}
          {exchange.num_markets && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Markets:</span>
              <span className="font-medium">{exchange.num_markets}</span>
            </div>
          )}
          {(exchange.maker_fee_percent || exchange.taker_fee_percent) && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Fees:</span>
              <span className="font-medium">
                {exchange.maker_fee_percent}% / {exchange.taker_fee_percent}%
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
