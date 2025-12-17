/**
 * Crypto Context
 *
 * Provides cryptocurrency data and wallet management functionality.
 */

import React, { createContext, ReactNode, useContext } from 'react';

import { cryptoClient } from '@/api/BaseClient';

import {
    useCryptoCoinsList, useCryptoCoinsStatsRetrieve, useCryptoExchangesList, useCryptoWalletsList
} from '../../api/generated/crypto/_utils/hooks';

import type { API } from '../../api/generated/crypto';
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
