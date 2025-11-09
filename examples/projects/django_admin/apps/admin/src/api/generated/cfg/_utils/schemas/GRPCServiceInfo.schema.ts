/**
 * Zod schema for GRPCServiceInfo
 *
 * This schema provides runtime validation and type inference.
 *  * Information about a single gRPC service.
 *  */
import { z } from 'zod'

/**
 * Information about a single gRPC service.
 */
export const GRPCServiceInfoSchema = z.object({
  name: z.string(),
  methods: z.array(z.string()).optional(),
  full_name: z.string(),
  description: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCServiceInfo = z.infer<typeof GRPCServiceInfoSchema>