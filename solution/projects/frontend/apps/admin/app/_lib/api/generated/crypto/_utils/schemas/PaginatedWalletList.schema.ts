/**
 * Zod schema for PaginatedWalletList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod';

import { WalletSchema } from './Wallet.schema';

export const PaginatedWalletListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(WalletSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedWalletList = z.infer<typeof PaginatedWalletListSchema>