/**
 * Zod schema for NewsletterCampaign
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for NewsletterCampaign model.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for NewsletterCampaign model.
 */
export const NewsletterCampaignSchema = z.object({
  id: z.int(),
  newsletter: z.int(),
  newsletter_title: z.string(),
  subject: z.string().max(255),
  email_title: z.string().max(255),
  main_text: z.string(),
  main_html_content: z.string().optional(),
  button_text: z.string().max(100).optional(),
  button_url: z.url().optional(),
  secondary_text: z.string().optional(),
  status: z.nativeEnum(Enums.NewsletterCampaignStatus),
  created_at: z.iso.datetime(),
  sent_at: z.iso.datetime().nullable(),
  recipient_count: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type NewsletterCampaign = z.infer<typeof NewsletterCampaignSchema>