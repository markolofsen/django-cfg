/**
 * Zod schema for RecentRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Recent request information.
 *  */
import { z } from 'zod'

/**
 * Recent request information.
 */
export const RecentRequestSchema = z.object({
  id: z.int(),
  request_id: z.string(),
  service_name: z.string(),
  method_name: z.string(),
  status: z.string(),
  duration_ms: z.int().optional(),
  grpc_status_code: z.string().optional(),
  error_message: z.string().optional(),
  created_at: z.string(),
  client_ip: z.string().optional(),
  user_id: z.int().nullable().optional(),
  username: z.string().nullable().optional(),
  is_authenticated: z.boolean().optional(),
  api_key_id: z.int().nullable().optional(),
  api_key_name: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RecentRequest = z.infer<typeof RecentRequestSchema>