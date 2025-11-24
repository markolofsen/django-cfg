import { Card, CardContent, Badge } from '@djangocfg/ui';
import { Wallet as WalletIcon, Lock } from 'lucide-react';
import type { Wallet } from '@/api/generated/crypto/crypto__api__crypto/models';

interface WalletCardProps {
  wallet: Wallet;
}

export function WalletCardComponent({ wallet }: WalletCardProps) {
  const coinInfo = wallet.coin_info as any;

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
                <span className="font-semibold">
                  {coinInfo?.symbol || `Coin #${wallet.coin}`}
                </span>
                {coinInfo?.name && (
                  <span className="text-sm text-muted-foreground">{coinInfo.name}</span>
                )}
              </div>
              {wallet.address && (
                <div className="text-xs text-muted-foreground mt-1 font-mono">
                  {wallet.address.slice(0, 8)}...{wallet.address.slice(-6)}
                </div>
              )}
            </div>
          </div>

          <div className="text-right">
            <div className="font-semibold">${wallet.value_usd}</div>
            <div className="text-xs text-muted-foreground">
              {wallet.total_balance} {coinInfo?.symbol || ''}
            </div>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Available:</span>
            <span className="font-medium">{wallet.balance || '0'}</span>
          </div>
          {wallet.locked_balance !== '0' && (
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
