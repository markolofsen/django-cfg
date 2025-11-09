/**
 * Zod schema for PaginatedChatResponseList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ChatResponseSchema } from './ChatResponse.schema'

export const PaginatedChatResponseListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(ChatResponseSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedChatResponseList = z.infer<typeof PaginatedChatResponseListSchema>