/**
 * Zod schema for GRPCCallRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request to call a gRPC method (for future implementation).
 *  */
import { z } from 'zod'

/**
 * Request to call a gRPC method (for future implementation).
 */
export const GRPCCallRequestRequestSchema = z.object({
  service: z.string().min(1),
  method: z.string().min(1),
  payload: z.record(z.string(), z.any()),
  metadata: z.record(z.string(), z.any()).optional(),
  timeout_ms: z.int().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCCallRequestRequest = z.infer<typeof GRPCCallRequestRequestSchema>