/**
 * Zod schema for TokenRefreshRequest
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'

export const TokenRefreshRequestSchema = z.object({
  refresh: z.string().min(1),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TokenRefreshRequest = z.infer<typeof TokenRefreshRequestSchema>