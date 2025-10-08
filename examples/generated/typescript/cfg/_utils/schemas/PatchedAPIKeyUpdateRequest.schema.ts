/**
 * Zod schema for PatchedAPIKeyUpdateRequest
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
export const PatchedAPIKeyUpdateRequestSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  is_active: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedAPIKeyUpdateRequest = z.infer<typeof PatchedAPIKeyUpdateRequestSchema>