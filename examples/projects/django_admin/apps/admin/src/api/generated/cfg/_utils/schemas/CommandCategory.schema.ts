/**
 * Zod schema for CommandCategory
 *
 * This schema provides runtime validation and type inference.
 *  * Category with commands.
 *  */
import { z } from 'zod'
import { CommandSchema } from './Command.schema'

/**
 * Category with commands.
 */
export const CommandCategorySchema = z.object({
  category: z.string(),
  commands: z.array(CommandSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CommandCategory = z.infer<typeof CommandCategorySchema>