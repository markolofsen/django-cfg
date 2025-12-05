'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Tabs, TabsContent, TabsList, TabsTrigger } from '@djangocfg/ui-nextjs';
import { RefreshCw } from 'lucide-react';
import { useCrypto } from '@/contexts';
import { CryptoStats, CoinCard, ExchangeCard, WalletCard } from './components';

export function CryptoView() {
  const {
    coins,
    coinStats,
    coinsLoading,
    coinsError,
    exchanges,
    exchangesLoading,
    exchangesError,
    wallets,
    walletsLoading,
    walletsError,
    refreshCoins,
    refreshExchanges,
    refreshWallets
  } = useCrypto();

  const isLoading = coinsLoading || exchangesLoading || walletsLoading;

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-48 bg-muted rounded" />
          <div className="grid gap-4 md:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 bg-muted rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Cryptocurrency</h1>
          <p className="text-muted-foreground mt-2">
            Explore coins, exchanges, and manage your wallets
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            refreshCoins();
            refreshExchanges();
            refreshWallets();
          }}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Crypto Stats */}
      <CryptoStats stats={coinStats} />

      {/* Tabs for different sections */}
      <Tabs defaultValue="coins" className="space-y-6">
        <TabsList>
          <TabsTrigger value="coins">Coins</TabsTrigger>
          <TabsTrigger value="exchanges">Exchanges</TabsTrigger>
          <TabsTrigger value="wallets">Wallets</TabsTrigger>
        </TabsList>

        <TabsContent value="coins" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cryptocurrencies</CardTitle>
              <CardDescription>
                Browse available cryptocurrencies
              </CardDescription>
            </CardHeader>
            <CardContent>
              {coins.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No coins found
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {coins.map((coin) => (
                    <CoinCard key={coin.id} coin={coin} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="exchanges" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cryptocurrency Exchanges</CardTitle>
              <CardDescription>
                Available trading platforms
              </CardDescription>
            </CardHeader>
            <CardContent>
              {exchanges.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No exchanges found
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {exchanges.map((exchange) => (
                    <ExchangeCard key={exchange.id} exchange={exchange} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="wallets" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Your Wallets</CardTitle>
              <CardDescription>
                Manage your cryptocurrency wallets
              </CardDescription>
            </CardHeader>
            <CardContent>
              {wallets.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No wallets yet. Create your first wallet to get started.
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {wallets.map((wallet) => (
                    <WalletCard key={wallet.id} wallet={wallet} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
