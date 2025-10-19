/**
 * Zod schema for PaginatedNewsletterCampaignList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { NewsletterCampaignSchema } from './NewsletterCampaign.schema'

export const PaginatedNewsletterCampaignListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(NewsletterCampaignSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedNewsletterCampaignList = z.infer<typeof PaginatedNewsletterCampaignListSchema>