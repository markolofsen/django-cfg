/**
 * Zod schema for PaginatedNetworkList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { NetworkSchema } from './Network.schema'

export const PaginatedNetworkListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional(),
  previous_page: z.number().int().optional(),
  results: z.array(NetworkSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedNetworkList = z.infer<typeof PaginatedNetworkListSchema>