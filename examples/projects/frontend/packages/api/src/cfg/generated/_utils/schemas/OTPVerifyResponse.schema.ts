/**
 * Zod schema for OTPVerifyResponse
 *
 * This schema provides runtime validation and type inference.
 *  * OTP verification response.
 *  */
import { z } from 'zod'
import { UserSchema } from './User.schema'

/**
 * OTP verification response.
 */
export const OTPVerifyResponseSchema = z.object({
  refresh: z.string(),
  access: z.string(),
  user: UserSchema,
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OTPVerifyResponse = z.infer<typeof OTPVerifyResponseSchema>