/**
 * Zod schema for SuccessResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Generic success response.
 *  */
import { z } from 'zod'

/**
 * Generic success response.
 */
export const SuccessResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SuccessResponse = z.infer<typeof SuccessResponseSchema>