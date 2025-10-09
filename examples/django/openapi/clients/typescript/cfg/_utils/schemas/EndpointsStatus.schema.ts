/**
 * Zod schema for EndpointsStatus
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for overall endpoints status response.
 *  */
import { z } from 'zod'
import { EndpointSchema } from './Endpoint.schema'

/**
 * Serializer for overall endpoints status response.
 */
export const EndpointsStatusSchema = z.object({
  status: z.string(),
  timestamp: z.string().datetime(),
  total_endpoints: z.number().int(),
  healthy: z.number().int(),
  unhealthy: z.number().int(),
  warnings: z.number().int(),
  errors: z.number().int(),
  skipped: z.number().int(),
  endpoints: z.array(EndpointSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type EndpointsStatus = z.infer<typeof EndpointsStatusSchema>