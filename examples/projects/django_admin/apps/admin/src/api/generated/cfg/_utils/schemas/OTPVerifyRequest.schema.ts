/**
 * Zod schema for OTPVerifyRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for OTP verification.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for OTP verification.
 */
export const OTPVerifyRequestSchema = z.object({
  identifier: z.string().min(1),
  otp: z.string().min(6).max(6),
  channel: z.nativeEnum(Enums.OTPVerifyRequestChannel).optional(),
  source_url: z.url().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OTPVerifyRequest = z.infer<typeof OTPVerifyRequestSchema>