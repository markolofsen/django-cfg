/**
 * Crypto Context
 *
 * Provides cryptocurrency data and wallet management functionality.
 */

import React, { createContext, ReactNode, useContext } from 'react';

import { cryptoClient } from '@/api/BaseClient';

import {
    useCryptoCoinsList, useCryptoCoinsStatsRetrieve, useCryptoExchangesList, useCryptoWalletsList
} from '../../api/generated/_crypto/hooks';

import type { API } from '../../api/generated/_crypto';
import type { CryptoContextType } from './types';

const CryptoContext = createContext<CryptoContextType | undefined>(undefined);

export function CryptoProvider({ children }: { children: ReactNode }) {
  // Get coins list (SWR)
  const {
    data: coinsData,
    error: coinsError,
    isLoading: coinsLoading,
    isValidating: coinsValidating,
    mutate: mutateCoins
  } = useCryptoCoinsList({ query: { page: 1, page_size: 100 } });


  // Get coin statistics (SWR)
  const {
    data: coinStats,
    isLoading: statsLoading,
  } = useCryptoCoinsStatsRetrieve();

  // Get exchanges list (SWR)
  const {
    data: exchangesData,
    error: exchangesError,
    isLoading: exchangesLoading,
    mutate: mutateExchanges
  } = useCryptoExchangesList({ query: { page: 1, page_size: 100 } });

  // Get wallets list (SWR)
  const {
    data: walletsData,
    error: walletsError,
    isLoading: walletsLoading,
    mutate: mutateWallets
  } = useCryptoWalletsList({ query: { page: 1, page_size: 100 } });

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
