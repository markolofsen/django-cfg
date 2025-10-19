/**
 * Zod schema for SendCampaignResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response for sending campaign.
 *  */
import { z } from 'zod'

/**
 * Response for sending campaign.
 */
export const SendCampaignResponseSchema = z.object({
  success: z.boolean(),
  message: z.string().optional(),
  sent_count: z.int().optional(),
  error: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SendCampaignResponse = z.infer<typeof SendCampaignResponseSchema>