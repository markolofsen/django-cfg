/**
 * Zod schema for APIResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Standard API response serializer.
 *  */
import { z } from 'zod'

/**
 * Standard API response serializer.
 */
export const APIResponseSchema = z.object({
  success: z.boolean(),
  message: z.string().optional(),
  error: z.string().optional(),
  data: z.record(z.string(), z.any()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIResponse = z.infer<typeof APIResponseSchema>