/**
 * Zod schema for APIKeyValidationRequest
 *
 * This schema provides runtime validation and type inference.
 *  * API key validation serializer.

Validates API key and returns key information.
 *  */
import { z } from 'zod'

/**
 * API key validation serializer.

Validates API key and returns key information.
 */
export const APIKeyValidationRequestSchema = z.object({
  key: z.string().min(32).max(64),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIKeyValidationRequest = z.infer<typeof APIKeyValidationRequestSchema>