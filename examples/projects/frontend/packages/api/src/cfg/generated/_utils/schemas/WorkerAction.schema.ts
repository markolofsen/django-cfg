/**
 * Zod schema for WorkerAction
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for worker management actions.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for worker management actions.
 */
export const WorkerActionSchema = z.object({
  action: z.nativeEnum(Enums.WorkerActionAction),
  processes: z.int().min(1.0).max(10.0).optional(),
  threads: z.int().min(1.0).max(20.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WorkerAction = z.infer<typeof WorkerActionSchema>