/**
 * Zod schema for JobListRequest
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
export const JobListRequestSchema = z.object({
  id: z.string().min(1),
  func_name: z.string().min(1),
  created_at: z.iso.datetime(),
  status: z.string().min(1),
  queue: z.string().min(1),
  timeout: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type JobListRequest = z.infer<typeof JobListRequestSchema>