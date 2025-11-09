/**
 * Zod schema for RunDemoRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for running demo tasks.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for running demo tasks.
 */
export const RunDemoRequestRequestSchema = z.object({
  scenario: z.nativeEnum(Enums.RunDemoRequestRequestScenario),
  queue: z.string().min(1).optional(),
  args: z.array(z.string()).optional(),
  kwargs: z.record(z.string(), z.any()).optional(),
  timeout: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RunDemoRequestRequest = z.infer<typeof RunDemoRequestRequestSchema>