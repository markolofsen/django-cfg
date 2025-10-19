/**
 * Zod schema for WorkerActionRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for worker management actions.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for worker management actions.
 */
export const WorkerActionRequestSchema = z.object({
  action: z.nativeEnum(Enums.WorkerActionRequestAction),
  processes: z.int().min(1.0).max(10.0).optional(),
  threads: z.int().min(1.0).max(20.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WorkerActionRequest = z.infer<typeof WorkerActionRequestSchema>