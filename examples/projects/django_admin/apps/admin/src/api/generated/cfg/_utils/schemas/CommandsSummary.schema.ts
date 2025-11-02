/**
 * Zod schema for CommandsSummary
 *
 * This schema provides runtime validation and type inference.
 *  * Commands summary serializer.
 *  */
import { z } from 'zod'
import { CommandSchema } from './Command.schema'

/**
 * Commands summary serializer.
 */
export const CommandsSummarySchema = z.object({
  total_commands: z.int(),
  core_commands: z.int(),
  custom_commands: z.int(),
  categories: z.array(z.string()),
  commands: z.array(CommandSchema),
  categorized: z.record(z.string(), z.any()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CommandsSummary = z.infer<typeof CommandsSummarySchema>