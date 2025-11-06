/**
 * Zod schema for GRPCTestLog
 *
 * This schema provides runtime validation and type inference.
 *  * Single test log entry.
 *  */
import { z } from 'zod'

/**
 * Single test log entry.
 */
export const GRPCTestLogSchema = z.object({
  request_id: z.string(),
  service: z.string(),
  method: z.string(),
  status: z.string(),
  grpc_status_code: z.string().nullable().optional(),
  error_message: z.string().nullable().optional(),
  duration_ms: z.int().nullable().optional(),
  created_at: z.string(),
  user: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCTestLog = z.infer<typeof GRPCTestLogSchema>