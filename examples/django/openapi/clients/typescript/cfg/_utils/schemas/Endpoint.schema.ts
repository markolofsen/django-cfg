/**
 * Zod schema for Endpoint
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for single endpoint status.
 *  */
import { z } from 'zod'

/**
 * Serializer for single endpoint status.
 */
export const EndpointSchema = z.object({
  url: z.string(),
  url_pattern: z.string().optional(),
  url_name: z.string().optional(),
  namespace: z.string().optional(),
  group: z.string(),
  view: z.string().optional(),
  status: z.string(),
  status_code: z.number().int().optional(),
  response_time_ms: z.number().optional(),
  is_healthy: z.boolean().optional(),
  error: z.string().optional(),
  error_type: z.string().optional(),
  reason: z.string().optional(),
  last_checked: z.string().datetime().optional(),
  has_parameters: z.boolean().optional(),
  required_auth: z.boolean().optional(),
  rate_limited: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Endpoint = z.infer<typeof EndpointSchema>