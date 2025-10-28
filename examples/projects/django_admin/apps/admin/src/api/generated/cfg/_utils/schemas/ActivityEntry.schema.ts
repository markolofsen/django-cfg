/**
 * Zod schema for ActivityEntry
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for recent activity entries.
 *  */
import { z } from 'zod'

/**
 * Serializer for recent activity entries.
 */
export const ActivityEntrySchema = z.object({
  id: z.int(),
  user: z.string(),
  action: z.string(),
  resource: z.string(),
  timestamp: z.string(),
  icon: z.string(),
  color: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ActivityEntry = z.infer<typeof ActivityEntrySchema>