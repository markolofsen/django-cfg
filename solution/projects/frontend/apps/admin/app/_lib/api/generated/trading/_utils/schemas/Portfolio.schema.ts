/**
 * Zod schema for Portfolio
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for trading portfolios.
 *  */
import { z } from 'zod';

/**
 * Serializer for trading portfolios.
 */
export const PortfolioSchema = z.object({
  id: z.int(),
  user: z.int(),
  user_info: z.record(z.string(), z.record(z.string(), z.any())),
  total_balance_usd: z.string(),
  available_balance_usd: z.string().optional(),
  total_profit_loss: z.string(),
  total_trades: z.int(),
  winning_trades: z.int(),
  losing_trades: z.int(),
  win_rate: z.number(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Portfolio = z.infer<typeof PortfolioSchema>