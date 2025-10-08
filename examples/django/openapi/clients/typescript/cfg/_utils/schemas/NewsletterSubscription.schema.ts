/**
 * Zod schema for NewsletterSubscription
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for NewsletterSubscription model.
 *  */
import { z } from 'zod'

/**
 * Serializer for NewsletterSubscription model.
 */
export const NewsletterSubscriptionSchema = z.object({
  id: z.number().int(),
  newsletter: z.number().int(),
  newsletter_title: z.string(),
  user: z.number().int().optional().nullable(),
  user_email: z.string(),
  email: z.string().email().max(254),
  is_active: z.boolean().optional(),
  subscribed_at: z.string().datetime(),
  unsubscribed_at: z.string().datetime().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type NewsletterSubscription = z.infer<typeof NewsletterSubscriptionSchema>