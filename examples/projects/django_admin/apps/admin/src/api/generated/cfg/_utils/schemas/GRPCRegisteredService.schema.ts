/**
 * Zod schema for GRPCRegisteredService
 *
 * This schema provides runtime validation and type inference.
 *  * Information about a registered gRPC service.
 *  */
import { z } from 'zod'

/**
 * Information about a registered gRPC service.
 */
export const GRPCRegisteredServiceSchema = z.object({
  name: z.string(),
  full_name: z.string(),
  methods_count: z.int(),
  request_count: z.int(),
  error_count: z.int(),
  success_rate: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCRegisteredService = z.infer<typeof GRPCRegisteredServiceSchema>