/**
 * Zod schema for ProtoGenerateResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response from proto generation.
 *  */
import { z } from 'zod'
import { ProtoGenerateErrorSchema } from './ProtoGenerateError.schema'

/**
 * Response from proto generation.
 */
export const ProtoGenerateResponseSchema = z.object({
  status: z.string(),
  generated: z.array(z.string()),
  generated_count: z.int(),
  errors: z.array(ProtoGenerateErrorSchema),
  proto_dir: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ProtoGenerateResponse = z.infer<typeof ProtoGenerateResponseSchema>