/**
 * SWR Hooks for Crypto
 *
 * React hooks powered by SWR for data fetching with automatic caching,
 * revalidation, and optimistic updates.
 *
 * Usage:
 * ```typescript
 * // Query hooks (GET)
 * const { data, error, isLoading } = useUsers({ page: 1 })
 *
 * // Mutation hooks (POST/PUT/PATCH/DELETE)
 * const createUser = useCreateUser()
 * await createUser({ name: 'John', email: 'john@example.com' })
 * ```
 */
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/crypto__api__crypto'
import type { API } from '../../index'
import type { Coin } from '../schemas/Coin.schema'
import type { CoinStats } from '../schemas/CoinStats.schema'
import type { Exchange } from '../schemas/Exchange.schema'
import type { PaginatedCoinListList } from '../schemas/PaginatedCoinListList.schema'
import type { PaginatedExchangeList } from '../schemas/PaginatedExchangeList.schema'
import type { PaginatedWalletList } from '../schemas/PaginatedWalletList.schema'
import type { Wallet } from '../schemas/Wallet.schema'

/**
 * List coins
 *
 * @method GET
 * @path /api/crypto/coins/
 */
export function useCryptoCoinsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedCoinListList>> {
  return useSWR<PaginatedCoinListList>(
    params ? ['crypto-coins', params] : 'crypto-coins',
    () => Fetchers.getCryptoCoinsList(params, client)
  )
}


/**
 * Get coin details
 *
 * @method GET
 * @path /api/crypto/coins/{id}/
 */
export function useCryptoCoinsRetrieve(id: number, client?: API): ReturnType<typeof useSWR<Coin>> {
  return useSWR<Coin>(
    ['crypto-coin', id],
    () => Fetchers.getCryptoCoinsRetrieve(id, client)
  )
}


/**
 * Get coin statistics
 *
 * @method GET
 * @path /api/crypto/coins/stats/
 */
export function useCryptoCoinsStatsRetrieve(client?: API): ReturnType<typeof useSWR<CoinStats>> {
  return useSWR<CoinStats>(
    'crypto-coins-stat',
    () => Fetchers.getCryptoCoinsStatsRetrieve(client)
  )
}


/**
 * List exchanges
 *
 * @method GET
 * @path /api/crypto/exchanges/
 */
export function useCryptoExchangesList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedExchangeList>> {
  return useSWR<PaginatedExchangeList>(
    params ? ['crypto-exchanges', params] : 'crypto-exchanges',
    () => Fetchers.getCryptoExchangesList(params, client)
  )
}


/**
 * Get exchange details
 *
 * @method GET
 * @path /api/crypto/exchanges/{slug}/
 */
export function useCryptoExchangesRetrieve(slug: string, client?: API): ReturnType<typeof useSWR<Exchange>> {
  return useSWR<Exchange>(
    ['crypto-exchange', slug],
    () => Fetchers.getCryptoExchangesRetrieve(slug, client)
  )
}


/**
 * List wallets
 *
 * @method GET
 * @path /api/crypto/wallets/
 */
export function useCryptoWalletsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedWalletList>> {
  return useSWR<PaginatedWalletList>(
    params ? ['crypto-wallets', params] : 'crypto-wallets',
    () => Fetchers.getCryptoWalletsList(params, client)
  )
}


/**
 * Get wallet details
 *
 * @method GET
 * @path /api/crypto/wallets/{id}/
 */
export function useCryptoWalletsRetrieve(id: string, client?: API): ReturnType<typeof useSWR<Wallet>> {
  return useSWR<Wallet>(
    ['crypto-wallet', id],
    () => Fetchers.getCryptoWalletsRetrieve(id, client)
  )
}


