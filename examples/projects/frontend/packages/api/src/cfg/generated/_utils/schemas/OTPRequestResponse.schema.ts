/**
 * Zod schema for OTPRequestResponse
 *
 * This schema provides runtime validation and type inference.
 *  * OTP request response.
 *  */
import { z } from 'zod'

/**
 * OTP request response.
 */
export const OTPRequestResponseSchema = z.object({
  message: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OTPRequestResponse = z.infer<typeof OTPRequestResponseSchema>