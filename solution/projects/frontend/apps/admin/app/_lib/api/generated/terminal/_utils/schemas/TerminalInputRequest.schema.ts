/**
 * Zod schema for TerminalInputRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for sending input.
 *  */
import { z } from 'zod'

/**
 * Serializer for sending input.
 */
export const TerminalInputRequestSchema = z.object({
  data: z.string().min(1).optional(),
  data_base64: z.string().min(1).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TerminalInputRequest = z.infer<typeof TerminalInputRequestSchema>