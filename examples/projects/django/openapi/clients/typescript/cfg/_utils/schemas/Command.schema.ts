/**
 * Zod schema for Command
 *
 * This schema provides runtime validation and type inference.
 *  * Django management command serializer.
 *  */
import { z } from 'zod'

/**
 * Django management command serializer.
 */
export const CommandSchema = z.object({
  name: z.string(),
  app: z.string(),
  help: z.string(),
  is_core: z.boolean(),
  is_custom: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Command = z.infer<typeof CommandSchema>