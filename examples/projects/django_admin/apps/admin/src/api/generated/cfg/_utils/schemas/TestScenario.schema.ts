/**
 * Zod schema for TestScenario
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for available test scenarios.
 *  */
import { z } from 'zod'

/**
 * Serializer for available test scenarios.
 */
export const TestScenarioSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  task_func: z.string(),
  default_args: z.array(z.string()).optional(),
  default_kwargs: z.record(z.string(), z.any()).optional(),
  estimated_duration: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TestScenario = z.infer<typeof TestScenarioSchema>