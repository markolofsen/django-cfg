/**
 * Zod schema for CentrifugoStreamPosition
 *
 * This schema provides runtime validation and type inference.
 *  * Stream position for pagination.
 *  */
import { z } from 'zod'

/**
 * Stream position for pagination.
 */
export const CentrifugoStreamPositionSchema = z.object({
  offset: z.int(),
  epoch: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoStreamPosition = z.infer<typeof CentrifugoStreamPositionSchema>