/**
 * Zod schema for GRPCExample
 *
 * This schema provides runtime validation and type inference.
 *  * Example payload for a gRPC method.
 *  */
import { z } from 'zod'

/**
 * Example payload for a gRPC method.
 */
export const GRPCExampleSchema = z.object({
  service: z.string(),
  method: z.string(),
  description: z.string(),
  payload_example: z.record(z.string(), z.record(z.string(), z.any())),
  expected_response: z.record(z.string(), z.record(z.string(), z.any())),
  metadata_example: z.record(z.string(), z.record(z.string(), z.any())).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCExample = z.infer<typeof GRPCExampleSchema>