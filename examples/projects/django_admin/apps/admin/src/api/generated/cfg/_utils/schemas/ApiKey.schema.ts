/**
 * Zod schema for ApiKey
 *
 * This schema provides runtime validation and type inference.
 *  * API Key information (read-only).
 *  */
import { z } from 'zod'

/**
 * API Key information (read-only).
 */
export const ApiKeySchema = z.object({
  id: z.int(),
  name: z.string(),
  key_type: z.string(),
  masked_key: z.string(),
  is_active: z.boolean(),
  is_valid: z.boolean(),
  user_id: z.int(),
  username: z.string(),
  user_email: z.string(),
  request_count: z.int(),
  last_used_at: z.iso.datetime().nullable(),
  expires_at: z.iso.datetime().nullable(),
  created_at: z.iso.datetime(),
  created_by: z.string().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ApiKey = z.infer<typeof ApiKeySchema>