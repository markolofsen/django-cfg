/**
 * Zod schema for URLsList
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for URLs list response.
 *  */
import { z } from 'zod'
import { URLPatternSchema } from './URLPattern.schema'

/**
 * Serializer for URLs list response.
 */
export const URLsListSchema = z.object({
  status: z.string(),
  service: z.string(),
  version: z.string(),
  base_url: z.string(),
  total_urls: z.int(),
  urls: z.array(URLPatternSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type URLsList = z.infer<typeof URLsListSchema>