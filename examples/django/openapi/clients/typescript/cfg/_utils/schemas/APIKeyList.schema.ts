/**
 * Zod schema for APIKeyList
 *
 * This schema provides runtime validation and type inference.
 *  * Lightweight API key serializer for lists.

Optimized for API key lists with minimal data (no key value).
 *  */
import { z } from 'zod'

/**
 * Lightweight API key serializer for lists.

Optimized for API key lists with minimal data (no key value).
 */
export const APIKeyListSchema = z.object({
  id: z.string().uuid(),
  user: z.string(),
  name: z.string(),
  is_active: z.boolean(),
  is_expired: z.boolean(),
  is_valid: z.boolean(),
  total_requests: z.number().int(),
  last_used_at: z.string().datetime().nullable(),
  expires_at: z.string().datetime().nullable(),
  created_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIKeyList = z.infer<typeof APIKeyListSchema>