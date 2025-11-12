/**
 * Zod schema for ProtoGenerateError
 *
 * This schema provides runtime validation and type inference.
 *  * Proto generation error.
 *  */
import { z } from 'zod'

/**
 * Proto generation error.
 */
export const ProtoGenerateErrorSchema = z.object({
  app: z.string(),
  error: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ProtoGenerateError = z.infer<typeof ProtoGenerateErrorSchema>