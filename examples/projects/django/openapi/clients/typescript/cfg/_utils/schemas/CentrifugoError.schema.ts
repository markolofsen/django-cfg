/**
 * Zod schema for CentrifugoError
 *
 * This schema provides runtime validation and type inference.
 *  * Centrifugo API error structure.
 *  */
import { z } from 'zod'

/**
 * Centrifugo API error structure.
 */
export const CentrifugoErrorSchema = z.object({
  code: z.int().optional(),
  message: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoError = z.infer<typeof CentrifugoErrorSchema>