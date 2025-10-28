/**
 * Zod schema for NewsletterCampaignRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for NewsletterCampaign model.
 *  */
import { z } from 'zod'

/**
 * Serializer for NewsletterCampaign model.
 */
export const NewsletterCampaignRequestSchema = z.object({
  newsletter: z.int(),
  subject: z.string().min(1).max(255),
  email_title: z.string().min(1).max(255),
  main_text: z.string().min(1),
  main_html_content: z.string().optional(),
  button_text: z.string().max(100).optional(),
  button_url: z.url().optional(),
  secondary_text: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type NewsletterCampaignRequest = z.infer<typeof NewsletterCampaignRequestSchema>