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
  timestamp: z.iso.datetime(),
  total_endpoints: z.int(),
  healthy: z.int(),
  unhealthy: z.int(),
  warnings: z.int(),
  errors: z.int(),
  skipped: z.int(),
  endpoints: z.array(EndpointSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type EndpointsStatus = z.infer<typeof EndpointsStatusSchema>