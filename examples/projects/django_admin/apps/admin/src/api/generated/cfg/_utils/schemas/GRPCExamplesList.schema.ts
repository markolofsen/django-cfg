/**
 * Zod schema for GRPCExamplesList
 *
 * This schema provides runtime validation and type inference.
 *  * List of examples response.
 *  */
import { z } from 'zod'
import { GRPCExampleSchema } from './GRPCExample.schema'

/**
 * List of examples response.
 */
export const GRPCExamplesListSchema = z.object({
  examples: z.array(GRPCExampleSchema).optional(),
  total_examples: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCExamplesList = z.infer<typeof GRPCExamplesListSchema>