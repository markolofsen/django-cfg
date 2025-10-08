/**
 * Zod schema for PatchedNewsletterCampaignRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for NewsletterCampaign model.
 *  */
import { z } from 'zod'

/**
 * Serializer for NewsletterCampaign model.
 */
export const PatchedNewsletterCampaignRequestSchema = z.object({
  newsletter: z.number().int().optional(),
  subject: z.string().min(1).max(255).optional(),
  email_title: z.string().min(1).max(255).optional(),
  main_text: z.string().min(1).optional(),
  main_html_content: z.string().optional(),
  button_text: z.string().max(100).optional(),
  button_url: z.string().url().max(200).optional(),
  secondary_text: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedNewsletterCampaignRequest = z.infer<typeof PatchedNewsletterCampaignRequestSchema>