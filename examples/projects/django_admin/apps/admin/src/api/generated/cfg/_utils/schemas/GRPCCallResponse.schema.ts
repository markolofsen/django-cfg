/**
 * Zod schema for GRPCCallResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response from calling a gRPC method.
 *  */
import { z } from 'zod'

/**
 * Response from calling a gRPC method.
 */
export const GRPCCallResponseSchema = z.object({
  success: z.boolean(),
  request_id: z.string(),
  service: z.string(),
  method: z.string(),
  status: z.string(),
  grpc_status_code: z.string(),
  duration_ms: z.int(),
  response: z.string().nullable().optional(),
  error: z.string().nullable().optional(),
  metadata: z.record(z.string(), z.record(z.string(), z.any())).optional(),
  timestamp: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCCallResponse = z.infer<typeof GRPCCallResponseSchema>