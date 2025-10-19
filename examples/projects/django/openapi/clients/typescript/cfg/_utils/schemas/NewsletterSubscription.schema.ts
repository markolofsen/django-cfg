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
  id: z.int(),
  newsletter: z.int(),
  newsletter_title: z.string(),
  user: z.int().nullable().optional(),
  user_email: z.string(),
  email: z.email(),
  is_active: z.boolean().optional(),
  subscribed_at: z.iso.datetime(),
  unsubscribed_at: z.iso.datetime().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type NewsletterSubscription = z.infer<typeof NewsletterSubscriptionSchema>