/**
 * Zod schema for APIKeyDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Complete API key serializer with full details.

Used for API key detail views (no key value for security).
 *  */
import { z } from 'zod'

/**
 * Complete API key serializer with full details.

Used for API key detail views (no key value for security).
 */
export const APIKeyDetailSchema = z.object({
  id: z.string().uuid(),
  user: z.string(),
  name: z.string(),
  key_preview: z.string(),
  is_active: z.boolean(),
  is_expired: z.boolean(),
  is_valid: z.boolean(),
  days_until_expiry: z.number().int(),
  total_requests: z.number().int(),
  last_used_at: z.string().datetime().optional(),
  expires_at: z.string().datetime().optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIKeyDetail = z.infer<typeof APIKeyDetailSchema>