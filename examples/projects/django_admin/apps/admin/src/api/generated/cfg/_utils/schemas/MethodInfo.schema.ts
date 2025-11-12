/**
 * Zod schema for MethodInfo
 *
 * This schema provides runtime validation and type inference.
 *  * Information about a service method.
 *  */
import { z } from 'zod'

/**
 * Information about a service method.
 */
export const MethodInfoSchema = z.object({
  name: z.string(),
  full_name: z.string(),
  request_type: z.string().optional(),
  response_type: z.string().optional(),
  streaming: z.boolean().optional(),
  auth_required: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type MethodInfo = z.infer<typeof MethodInfoSchema>