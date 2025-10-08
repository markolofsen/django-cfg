/**
 * Zod schema for APIKeyValidationResponse
 *
 * This schema provides runtime validation and type inference.
 *  * API key validation response serializer.

Defines the structure of API key validation response for OpenAPI schema.
 *  */
import { z } from 'zod'
import { APIKeyDetailSchema } from './APIKeyDetail.schema'

/**
 * API key validation response serializer.

Defines the structure of API key validation response for OpenAPI schema.
 */
export const APIKeyValidationResponseSchema = z.object({
  success: z.boolean(),
  valid: z.boolean(),
  api_key: APIKeyDetailSchema,
  message: z.string(),
  error: z.string().optional(),
  error_code: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIKeyValidationResponse = z.infer<typeof APIKeyValidationResponseSchema>