/**
 * Zod schema for SupportedProviders
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for supported providers response.
 *  */
import { z } from 'zod'

/**
 * Serializer for supported providers response.
 */
export const SupportedProvidersSchema = z.object({
  success: z.boolean(),
  providers: z.string(),
  total_count: z.number().int(),
  timestamp: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SupportedProviders = z.infer<typeof SupportedProvidersSchema>