/**
 * Zod schema for TerminalResizeRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for resize command.
 *  */
import { z } from 'zod'

/**
 * Serializer for resize command.
 */
export const TerminalResizeRequestSchema = z.object({
  cols: z.int().min(1.0).max(500.0),
  rows: z.int().min(1.0).max(200.0),
  width: z.int().min(1.0).optional(),
  height: z.int().min(1.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TerminalResizeRequest = z.infer<typeof TerminalResizeRequestSchema>