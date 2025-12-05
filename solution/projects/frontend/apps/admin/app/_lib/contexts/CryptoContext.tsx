/**
 * Crypto Context
 *
 * Provides cryptocurrency data and wallet management functionality.
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { cryptoClient } from '@/api/BaseClient';
import {
  useCryptoCoinsList,
  useCryptoCoinsStatsRetrieve,
  useCryptoExchangesList,
  useCryptoWalletsList
} from '../api/generated/crypto/_utils/hooks';
import type { API } from '../api/generated/crypto';
import type { CoinList } from '../api/generated/crypto/_utils/schemas/CoinList.schema';
import type { CoinStats } from '../api/generated/crypto/_utils/schemas/CoinStats.schema';
import type { Exchange } from '../api/generated/crypto/_utils/schemas/Exchange.schema';
import type { Wallet } from '../api/generated/crypto/_utils/schemas/Wallet.schema';

interface CryptoContextType {
  // Coins data
  coins: CoinList[];
  coinsLoading: boolean;
  coinsError: Error | null;
  coinStats: CoinStats | undefined;

  // Exchanges data
  exchanges: Exchange[];
  exchangesLoading: boolean;
  exchangesError: Error | null;

  // Wallets data
  wallets: Wallet[];
  walletsLoading: boolean;
  walletsError: Error | null;

  // Actions
  refreshCoins: () => Promise<void>;
  refreshExchanges: () => Promise<void>;
  refreshWallets: () => Promise<void>;
}

const CryptoContext = createContext<CryptoContextType | undefined>(undefined);

export function CryptoProvider({ children }: { children: ReactNode }) {
  // Get coins list (SWR)
  const {
    data: coinsData,
    error: coinsError,
    isLoading: coinsLoading,
    isValidating: coinsValidating,
    mutate: mutateCoins
  } = useCryptoCoinsList({ page: 1, page_size: 100 }, cryptoClient as unknown as API);


  // Get coin statistics (SWR)
  const {
    data: coinStats,
    isLoading: statsLoading,
  } = useCryptoCoinsStatsRetrieve(cryptoClient as unknown as API);

  // Get exchanges list (SWR)
  const {
    data: exchangesData,
    error: exchangesError,
    isLoading: exchangesLoading,
    mutate: mutateExchanges
  } = useCryptoExchangesList({ page: 1, page_size: 100 }, cryptoClient as unknown as API);

  // Get wallets list (SWR)
  const {
    data: walletsData,
    error: walletsError,
    isLoading: walletsLoading,
    mutate: mutateWallets
  } = useCryptoWalletsList({ page: 1, page_size: 100 }, cryptoClient as unknown as API);

  const coins = coinsData?.results || [];
  const exchanges = exchangesData?.results || [];
  const wallets = walletsData?.results || [];

  const value: CryptoContextType = {
    coins,
    coinsLoading: coinsLoading || statsLoading,
    coinsError: coinsError as Error | null,
    coinStats,
    exchanges,
    exchangesLoading,
    exchangesError: exchangesError as Error | null,
    wallets,
    walletsLoading,
    walletsError: walletsError as Error | null,
    refreshCoins: async () => {
      await mutateCoins();
    },
    refreshExchanges: async () => {
      await mutateExchanges();
    },
    refreshWallets: async () => {
      await mutateWallets();
    },
  };

  return (
    <CryptoContext.Provider value={value}>
      {children}
    </CryptoContext.Provider>
  );
}

export function useCrypto() {
  const context = useContext(CryptoContext);
  if (context === undefined) {
    throw new Error('useCrypto must be used within a CryptoProvider');
  }
  return context;
}
