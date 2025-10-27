/**
 * Typed fetchers for Crypto
 *
 * Universal functions that work in any environment:
 * - Next.js (App Router / Pages Router / Server Components)
 * - React Native
 * - Node.js backend
 *
 * These fetchers use Zod schemas for runtime validation.
 *
 * Usage:
 * ```typescript
 * // Configure API once (in your app entry point)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 *
 * // Then use fetchers anywhere
 * const users = await getUsers({ page: 1 })
 *
 * // With SWR
 * const { data } = useSWR(['users', params], () => getUsers(params))
 *
 * // With React Query
 * const { data } = useQuery(['users', params], () => getUsers(params))
 *
 * // In Server Component or SSR (pass custom client)
 * import { API } from '../../index'
 * const api = new API('https://api.example.com')
 * const users = await getUsers({ page: 1 }, api)
 * ```
 */
import { CoinSchema, type Coin } from '../schemas/Coin.schema'
import { CoinStatsSchema, type CoinStats } from '../schemas/CoinStats.schema'
import { ExchangeSchema, type Exchange } from '../schemas/Exchange.schema'
import { PaginatedCoinListListSchema, type PaginatedCoinListList } from '../schemas/PaginatedCoinListList.schema'
import { PaginatedExchangeListSchema, type PaginatedExchangeList } from '../schemas/PaginatedExchangeList.schema'
import { PaginatedWalletListSchema, type PaginatedWalletList } from '../schemas/PaginatedWalletList.schema'
import { WalletSchema, type Wallet } from '../schemas/Wallet.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * List coins
 *
 * @method GET
 * @path /api/crypto/coins/
 */
export async function getCryptoCoinsList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedCoinListList> {
  const api = client || getAPIInstance()
  const response = await api.crypto_crypto.coinsList(params?.page, params?.page_size)
  return PaginatedCoinListListSchema.parse(response)
}


/**
 * Get coin details
 *
 * @method GET
 * @path /api/crypto/coins/{id}/
 */
export async function getCryptoCoinsRetrieve(  id: number,  client?: API
): Promise<Coin> {
  const api = client || getAPIInstance()
  const response = await api.crypto_crypto.coinsRetrieve(id)
  return CoinSchema.parse(response)
}


/**
 * Get coin statistics
 *
 * @method GET
 * @path /api/crypto/coins/stats/
 */
export async function getCryptoCoinsStatsRetrieve(  client?: API
): Promise<CoinStats> {
  const api = client || getAPIInstance()
  const response = await api.crypto_crypto.coinsStatsRetrieve()
  return CoinStatsSchema.parse(response)
}


/**
 * List exchanges
 *
 * @method GET
 * @path /api/crypto/exchanges/
 */
export async function getCryptoExchangesList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedExchangeList> {
  const api = client || getAPIInstance()
  const response = await api.crypto_crypto.exchangesList(params?.page, params?.page_size)
  return PaginatedExchangeListSchema.parse(response)
}


/**
 * Get exchange details
 *
 * @method GET
 * @path /api/crypto/exchanges/{slug}/
 */
export async function getCryptoExchangesRetrieve(  slug: string,  client?: API
): Promise<Exchange> {
  const api = client || getAPIInstance()
  const response = await api.crypto_crypto.exchangesRetrieve(slug)
  return ExchangeSchema.parse(response)
}


/**
 * List wallets
 *
 * @method GET
 * @path /api/crypto/wallets/
 */
export async function getCryptoWalletsList(  params?: { page?: number; page_size?: number },  client?: API
): Promise<PaginatedWalletList> {
  const api = client || getAPIInstance()
  const response = await api.crypto_crypto.walletsList(params?.page, params?.page_size)
  return PaginatedWalletListSchema.parse(response)
}


/**
 * Get wallet details
 *
 * @method GET
 * @path /api/crypto/wallets/{id}/
 */
export async function getCryptoWalletsRetrieve(  id: string,  client?: API
): Promise<Wallet> {
  const api = client || getAPIInstance()
  const response = await api.crypto_crypto.walletsRetrieve(id)
  return WalletSchema.parse(response)
}


