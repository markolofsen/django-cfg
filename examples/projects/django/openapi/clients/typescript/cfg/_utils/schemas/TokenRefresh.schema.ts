/**
 * Zod schema for TokenRefresh
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'

export const TokenRefreshSchema = z.object({
  access: z.string(),
  refresh: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TokenRefresh = z.infer<typeof TokenRefreshSchema>