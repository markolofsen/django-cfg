/**
 * Zod schema for APIResponseRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Standard API response serializer.
 *  */
import { z } from 'zod'

/**
 * Standard API response serializer.
 */
export const APIResponseRequestSchema = z.object({
  success: z.boolean(),
  message: z.string().min(1).optional(),
  error: z.string().min(1).optional(),
  data: z.record(z.string(), z.any()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIResponseRequest = z.infer<typeof APIResponseRequestSchema>