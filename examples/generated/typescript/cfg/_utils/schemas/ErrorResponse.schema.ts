/**
 * Zod schema for ErrorResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Generic error response.
 *  */
import { z } from 'zod'

/**
 * Generic error response.
 */
export const ErrorResponseSchema = z.object({
  success: z.boolean().optional(),
  message: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>