/**
 * Zod schema for EndpointGroup
 *
 * This schema provides runtime validation and type inference.
 *  * Endpoint group serializer for API access management.

Used for subscription endpoint group configuration.
 *  */
import { z } from 'zod'

/**
 * Endpoint group serializer for API access management.

Used for subscription endpoint group configuration.
 */
export const EndpointGroupSchema = z.object({
  id: z.number().int(),
  name: z.string(),
  description: z.string(),
  is_enabled: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type EndpointGroup = z.infer<typeof EndpointGroupSchema>