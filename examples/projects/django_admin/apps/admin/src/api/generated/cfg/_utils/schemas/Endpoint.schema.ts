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
  url_pattern: z.string().nullable().optional(),
  url_name: z.string().nullable().optional(),
  namespace: z.string().optional(),
  group: z.string(),
  view: z.string().optional(),
  status: z.string(),
  status_code: z.int().nullable().optional(),
  response_time_ms: z.number().nullable().optional(),
  is_healthy: z.boolean().nullable().optional(),
  error: z.string().optional(),
  error_type: z.string().optional(),
  reason: z.string().optional(),
  last_checked: z.iso.datetime().nullable().optional(),
  has_parameters: z.boolean().optional(),
  required_auth: z.boolean().optional(),
  rate_limited: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Endpoint = z.infer<typeof EndpointSchema>