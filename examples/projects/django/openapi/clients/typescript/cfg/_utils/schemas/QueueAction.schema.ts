/**
 * Zod schema for QueueAction
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for queue management actions.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for queue management actions.
 */
export const QueueActionSchema = z.object({
  action: z.nativeEnum(Enums.QueueActionAction),
  queue_names: z.array(z.string()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type QueueAction = z.infer<typeof QueueActionSchema>