/**
 * Zod schema for CommandExecuteRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request serializer for command execution.
 *  */
import { z } from 'zod'

/**
 * Request serializer for command execution.
 */
export const CommandExecuteRequestRequestSchema = z.object({
  command: z.string().min(1),
  args: z.array(z.string().min(1)).optional(),
  options: z.record(z.string(), z.any()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CommandExecuteRequestRequest = z.infer<typeof CommandExecuteRequestRequestSchema>