/**
 * Zod schema for URLPattern
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for single URL pattern.
 *  */
import { z } from 'zod'

/**
 * Serializer for single URL pattern.
 */
export const URLPatternSchema = z.object({
  pattern: z.string(),
  name: z.string().nullable().optional(),
  full_name: z.string().nullable().optional(),
  namespace: z.string().nullable().optional(),
  view: z.string().nullable().optional(),
  view_class: z.string().nullable().optional(),
  methods: z.array(z.string()).optional(),
  module: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type URLPattern = z.infer<typeof URLPatternSchema>