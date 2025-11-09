/**
 * Zod schema for GRPCInterceptorInfo
 *
 * This schema provides runtime validation and type inference.
 *  * Information about an interceptor.
 *  */
import { z } from 'zod'

/**
 * Information about an interceptor.
 */
export const GRPCInterceptorInfoSchema = z.object({
  name: z.string(),
  enabled: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCInterceptorInfo = z.infer<typeof GRPCInterceptorInfoSchema>