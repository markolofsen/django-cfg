/**
 * Zod schema for PaginatedChatSessionList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ChatSessionSchema } from './ChatSession.schema'

export const PaginatedChatSessionListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(ChatSessionSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedChatSessionList = z.infer<typeof PaginatedChatSessionListSchema>