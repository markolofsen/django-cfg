/**
 * Zod schema for APIKeyCreateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * API key creation serializer with service integration.

Creates new API keys and returns the full key value (only once).
 *  */
import { z } from 'zod'

/**
 * API key creation serializer with service integration.

Creates new API keys and returns the full key value (only once).
 */
export const APIKeyCreateRequestSchema = z.object({
  name: z.string().min(1).max(100),
  expires_in_days: z.number().int().min(1.0).max(365.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIKeyCreateRequest = z.infer<typeof APIKeyCreateRequestSchema>