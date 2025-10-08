/**
 * Zod schema for PaginatedNewsletterCampaignList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { NewsletterCampaignSchema } from './NewsletterCampaign.schema'

export const PaginatedNewsletterCampaignListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional().nullable(),
  previous_page: z.number().int().optional().nullable(),
  results: z.array(NewsletterCampaignSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedNewsletterCampaignList = z.infer<typeof PaginatedNewsletterCampaignListSchema>