/**
 * Zod schema for APIKeyUpdate
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
export const APIKeyUpdateSchema = z.object({
  name: z.string().max(100),
  is_active: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIKeyUpdate = z.infer<typeof APIKeyUpdateSchema>