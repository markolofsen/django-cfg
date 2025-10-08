/**
 * Zod schema for Newsletter
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for Newsletter model.
 *  */
import { z } from 'zod'

/**
 * Serializer for Newsletter model.
 */
export const NewsletterSchema = z.object({
  id: z.number().int(),
  title: z.string().max(255),
  description: z.string().optional(),
  is_active: z.boolean().optional(),
  auto_subscribe: z.boolean().optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  subscribers_count: z.number().int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Newsletter = z.infer<typeof NewsletterSchema>