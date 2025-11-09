/**
 * Zod schema for TestingActionResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for testing action responses.
 *  */
import { z } from 'zod'

/**
 * Serializer for testing action responses.
 */
export const TestingActionResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  job_ids: z.array(z.string()).optional(),
  count: z.int().nullable().optional(),
  metadata: z.record(z.string(), z.any()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TestingActionResponse = z.infer<typeof TestingActionResponseSchema>