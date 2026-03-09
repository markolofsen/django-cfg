/**
 * Zod schema for Wallet
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for wallets.
 *  */
import { z } from 'zod'
import { CoinListSchema } from './CoinList.schema'

/**
 * Serializer for wallets.
 */
export const WalletSchema = z.object({
  id: z.number().int(),
  user: z.number().int(),
  coin: z.number().int(),
  coin_info: CoinListSchema,
  balance: z.string().optional(),
  locked_balance: z.string(),
  total_balance: z.string(),
  value_usd: z.string(),
  address: z.string().max(200).optional(),
  created_at: z.string().datetime({ offset: true }),
  updated_at: z.string().datetime({ offset: true }),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Wallet = z.infer<typeof WalletSchema>