/**
 * Zod schema for JobList
 *
 * This schema provides runtime validation and type inference.
 *  * Job list item serializer.

Provides basic job information for list views.
 *  */
import { z } from 'zod'

/**
 * Job list item serializer.

Provides basic job information for list views.
 */
export const JobListSchema = z.object({
  id: z.string(),
  func_name: z.string(),
  created_at: z.iso.datetime(),
  status: z.string(),
  queue: z.string(),
  timeout: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type JobList = z.infer<typeof JobListSchema>