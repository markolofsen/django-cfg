/**
 * Zod schema for CommandHelpResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response serializer for command help.
 *  */
import { z } from 'zod'

/**
 * Response serializer for command help.
 */
export const CommandHelpResponseSchema = z.object({
  status: z.string(),
  command: z.string(),
  app: z.string().optional(),
  help_text: z.string().optional(),
  is_allowed: z.boolean().optional(),
  risk_level: z.string().optional(),
  error: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CommandHelpResponse = z.infer<typeof CommandHelpResponseSchema>