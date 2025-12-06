/**
 * Zod schema for TerminalSessionCreateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for creating new session.
 *  */
import { z } from 'zod'

/**
 * Serializer for creating new session.
 */
export const TerminalSessionCreateRequestSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  shell: z.string().min(1).max(50).optional(),
  working_directory: z.string().min(1).max(500).optional(),
  environment: z.record(z.string(), z.any()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TerminalSessionCreateRequest = z.infer<typeof TerminalSessionCreateRequestSchema>