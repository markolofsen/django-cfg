/**
 * Zod schema for StressTestRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for stress testing.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for stress testing.
 */
export const StressTestRequestRequestSchema = z.object({
  num_jobs: z.int().min(1.0).max(1000.0).optional(),
  queue: z.string().min(1).optional(),
  scenario: z.nativeEnum(Enums.StressTestRequestRequestScenario).optional(),
  duration: z.int().min(1.0).max(60.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type StressTestRequestRequest = z.infer<typeof StressTestRequestRequestSchema>