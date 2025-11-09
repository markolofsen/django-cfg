/**
 * Zod schema for OTPErrorResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Error response for OTP operations.
 *  */
import { z } from 'zod'

/**
 * Error response for OTP operations.
 */
export const OTPErrorResponseSchema = z.object({
  error: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OTPErrorResponse = z.infer<typeof OTPErrorResponseSchema>