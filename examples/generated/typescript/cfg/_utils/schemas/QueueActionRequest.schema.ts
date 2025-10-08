/**
 * Zod schema for QueueActionRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for queue management actions.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for queue management actions.
 */
export const QueueActionRequestSchema = z.object({
  action: z.nativeEnum(Enums.QueueActionRequestAction),
  queue_names: z.array(z.string().min(1)).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type QueueActionRequest = z.infer<typeof QueueActionRequestSchema>