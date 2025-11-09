/**
 * Zod schema for MethodList
 *
 * This schema provides runtime validation and type inference.
 *  * List of gRPC methods with statistics.
 *  */
import { z } from 'zod'
import { MethodStatsSchema } from './MethodStats.schema'

/**
 * List of gRPC methods with statistics.
 */
export const MethodListSchema = z.object({
  methods: z.array(MethodStatsSchema),
  total_methods: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type MethodList = z.infer<typeof MethodListSchema>