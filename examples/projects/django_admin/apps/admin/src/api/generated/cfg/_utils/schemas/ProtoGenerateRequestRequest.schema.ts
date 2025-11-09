/**
 * Zod schema for ProtoGenerateRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request to generate proto files.
 *  */
import { z } from 'zod'

/**
 * Request to generate proto files.
 */
export const ProtoGenerateRequestRequestSchema = z.object({
  apps: z.array(z.string().min(1)).optional(),
  force: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ProtoGenerateRequestRequest = z.infer<typeof ProtoGenerateRequestRequestSchema>