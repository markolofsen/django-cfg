/**
 * Zod schema for APIKeyCreate
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
export const APIKeyCreateSchema = z.object({
  name: z.string().max(100),
  expires_in_days: z.number().int().min(1.0).max(365.0).optional().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIKeyCreate = z.infer<typeof APIKeyCreateSchema>