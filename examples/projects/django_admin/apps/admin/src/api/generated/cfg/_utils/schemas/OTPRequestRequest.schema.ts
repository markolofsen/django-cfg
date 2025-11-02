/**
 * Zod schema for OTPRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for OTP request.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for OTP request.
 */
export const OTPRequestRequestSchema = z.object({
  identifier: z.string().min(1),
  channel: z.nativeEnum(Enums.OTPRequestRequestChannel).optional(),
  source_url: z.url().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OTPRequestRequest = z.infer<typeof OTPRequestRequestSchema>