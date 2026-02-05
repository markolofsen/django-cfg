/**
 * Zod schema for PaginatedPortfolioList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod';

import { PortfolioSchema } from './Portfolio.schema';

export const PaginatedPortfolioListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(PortfolioSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedPortfolioList = z.infer<typeof PaginatedPortfolioListSchema>