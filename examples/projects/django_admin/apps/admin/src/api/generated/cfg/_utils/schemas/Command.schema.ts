/**
 * Zod schema for Command
 *
 * This schema provides runtime validation and type inference.
 *  * Django management command serializer.

Includes security metadata from base classes (SafeCommand, InteractiveCommand, etc.):
- web_executable: Can be executed via web interface
- requires_input: Requires interactive user input
- is_destructive: Modifies or deletes data
 *  */
import { z } from 'zod'

/**
 * Django management command serializer.

Includes security metadata from base classes (SafeCommand, InteractiveCommand, etc.):
- web_executable: Can be executed via web interface
- requires_input: Requires interactive user input
- is_destructive: Modifies or deletes data
 */
export const CommandSchema = z.object({
  name: z.string(),
  app: z.string(),
  help: z.string(),
  is_core: z.boolean(),
  is_custom: z.boolean(),
  is_allowed: z.boolean().optional(),
  risk_level: z.string().optional(),
  web_executable: z.boolean().nullable().optional(),
  requires_input: z.boolean().nullable().optional(),
  is_destructive: z.boolean().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Command = z.infer<typeof CommandSchema>