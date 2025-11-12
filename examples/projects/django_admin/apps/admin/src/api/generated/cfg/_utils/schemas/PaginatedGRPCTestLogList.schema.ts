/**
 * Zod schema for PaginatedGRPCTestLogList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { GRPCTestLogSchema } from './GRPCTestLog.schema'

export const PaginatedGRPCTestLogListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(GRPCTestLogSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedGRPCTestLogList = z.infer<typeof PaginatedGRPCTestLogListSchema>