/**
 * Zod schema for APIKeyUpdateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * API key update serializer for modifying API key properties.

Allows updating name and active status only.
 *  */
import { z } from 'zod'

/**
 * API key update serializer for modifying API key properties.

Allows updating name and active status only.
 */
export const APIKeyUpdateRequestSchema = z.object({
  name: z.string().min(1).max(100),
  is_active: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIKeyUpdateRequest = z.infer<typeof APIKeyUpdateRequestSchema>