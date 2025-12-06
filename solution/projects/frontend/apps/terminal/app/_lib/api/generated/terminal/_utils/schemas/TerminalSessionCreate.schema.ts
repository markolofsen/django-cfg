/**
 * Zod schema for TerminalSessionCreate
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for creating new session.
 *  */
import { z } from 'zod'

/**
 * Serializer for creating new session.
 */
export const TerminalSessionCreateSchema = z.object({
  name: z.string().max(100).optional(),
  shell: z.string().max(50).optional(),
  working_directory: z.string().max(500).optional(),
  environment: z.record(z.string(), z.any()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TerminalSessionCreate = z.infer<typeof TerminalSessionCreateSchema>