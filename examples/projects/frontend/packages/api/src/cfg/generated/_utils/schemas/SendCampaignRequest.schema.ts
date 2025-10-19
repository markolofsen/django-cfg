/**
 * Zod schema for SendCampaignRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Simple serializer for sending campaign.
 *  */
import { z } from 'zod'

/**
 * Simple serializer for sending campaign.
 */
export const SendCampaignRequestSchema = z.object({
  campaign_id: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SendCampaignRequest = z.infer<typeof SendCampaignRequestSchema>