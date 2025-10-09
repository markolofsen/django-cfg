/**
 * Zod schema for PaginatedTariffList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { TariffSchema } from './Tariff.schema'

export const PaginatedTariffListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional(),
  previous_page: z.number().int().optional(),
  results: z.array(TariffSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedTariffList = z.infer<typeof PaginatedTariffListSchema>