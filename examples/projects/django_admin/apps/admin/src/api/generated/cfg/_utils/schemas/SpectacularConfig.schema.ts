/**
 * Zod schema for SpectacularConfig
 *
 * This schema provides runtime validation and type inference.
 *  * DRF Spectacular configuration.
 *  */
import { z } from 'zod'

/**
 * DRF Spectacular configuration.
 */
export const SpectacularConfigSchema = z.object({
  title: z.string().nullable().optional(),
  description: z.string().nullable().optional(),
  version: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SpectacularConfig = z.infer<typeof SpectacularConfigSchema>