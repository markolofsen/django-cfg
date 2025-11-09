/**
 * Zod schema for JobActionResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Job action response serializer.

Used for job management actions (requeue, delete, etc.).
 *  */
import { z } from 'zod'

/**
 * Job action response serializer.

Used for job management actions (requeue, delete, etc.).
 */
export const JobActionResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  job_id: z.string(),
  action: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type JobActionResponse = z.infer<typeof JobActionResponseSchema>