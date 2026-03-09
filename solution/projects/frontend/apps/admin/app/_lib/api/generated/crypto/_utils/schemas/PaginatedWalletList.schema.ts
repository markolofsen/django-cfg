/**
 * Zod schema for PaginatedWalletList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { WalletSchema } from './Wallet.schema'

export const PaginatedWalletListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().nullable().optional(),
  previous_page: z.number().int().nullable().optional(),
  results: z.array(WalletSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedWalletList = z.infer<typeof PaginatedWalletListSchema>