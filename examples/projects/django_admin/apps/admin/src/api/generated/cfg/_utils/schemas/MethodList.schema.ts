/**
 * Zod schema for MethodList
 *
 * This schema provides runtime validation and type inference.
 *  * List of gRPC methods with statistics.
 *  */
import { z } from 'zod'
import { MethodStatsSerializerSchema } from './MethodStatsSerializer.schema'

/**
 * List of gRPC methods with statistics.
 */
export const MethodListSchema = z.object({
  methods: z.array(MethodStatsSerializerSchema),
  total_methods: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type MethodList = z.infer<typeof MethodListSchema>