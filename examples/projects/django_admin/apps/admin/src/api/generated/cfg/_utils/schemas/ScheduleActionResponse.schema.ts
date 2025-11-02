/**
 * Zod schema for ScheduleActionResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response serializer for schedule actions (create/delete).
 *  */
import { z } from 'zod'

/**
 * Response serializer for schedule actions (create/delete).
 */
export const ScheduleActionResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  job_id: z.string().nullable().optional(),
  action: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ScheduleActionResponse = z.infer<typeof ScheduleActionResponseSchema>