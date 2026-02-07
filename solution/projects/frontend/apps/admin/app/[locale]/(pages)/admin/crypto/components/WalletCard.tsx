import { Lock, Wallet as WalletIcon } from 'lucide-react';

import { Badge, Card, CardContent } from '@djangocfg/ui-nextjs';

import type { Wallet } from '@/api/generated/crypto/_utils/schemas/Wallet.schema';

interface WalletCardProps {
  wallet: Wallet;
}

export function WalletCardComponent({ wallet }: WalletCardProps) {
  const coinInfo = wallet.coin_info as any;

  const coinSymbol = coinInfo?.symbol || `Coin #${wallet.coin}`;
  const coinName = coinInfo?.name || null;
  const addressShort = wallet.address
    ? `${wallet.address.slice(0, 8)}...${wallet.address.slice(-6)}`
    : null;
  const balanceWithSymbol = `${wallet.total_balance} ${coinInfo?.symbol || ''}`.trim();
  const availableBalance = wallet.balance || '0';
  const hasLockedBalance = wallet.locked_balance !== '0';

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
              <WalletIcon className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{coinSymbol}</span>
                {coinName && (
                  <span className="text-sm text-muted-foreground">{coinName}</span>
                )}
              </div>
              {addressShort && (
                <div className="text-xs text-muted-foreground mt-1 font-mono">
                  {addressShort}
                </div>
              )}
            </div>
          </div>

          <div className="text-right">
            <div className="font-semibold">${wallet.value_usd}</div>
            <div className="text-xs text-muted-foreground">{balanceWithSymbol}</div>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Available:</span>
            <span className="font-medium">{availableBalance}</span>
          </div>
          {hasLockedBalance && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground flex items-center gap-1">
                <Lock className="h-3 w-3" />
                Locked:
              </span>
              <span className="font-medium">{wallet.locked_balance}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
