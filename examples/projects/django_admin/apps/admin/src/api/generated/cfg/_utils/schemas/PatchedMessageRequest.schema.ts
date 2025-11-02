/**
 * Zod schema for PatchedMessageRequest
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'

export const PatchedMessageRequestSchema = z.object({
  text: z.string().min(1).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedMessageRequest = z.infer<typeof PatchedMessageRequestSchema>