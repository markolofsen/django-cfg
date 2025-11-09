/**
 * Zod schema for DRFConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Django REST Framework configuration.
 *  */
import { z } from 'zod'

/**
 * Django REST Framework configuration.
 */
export const DRFConfigSchema = z.object({
  default_pagination_class: z.string().nullable().optional(),
  page_size: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DRFConfig = z.infer<typeof DRFConfigSchema>