/**
 * Zod schema for SubscriptionOverview
 *
 * This schema provides runtime validation and type inference.
 *  * Current subscription overview
 *  */
import { z } from 'zod'

/**
 * Current subscription overview
 */
export const SubscriptionOverviewSchema = z.object({
  tier: z.string(),
  tier_display: z.string(),
  status: z.string(),
  status_display: z.string(),
  status_color: z.string(),
  is_active: z.boolean(),
  is_expired: z.boolean(),
  days_remaining: z.number().int(),
  requests_per_hour: z.number().int(),
  requests_per_day: z.number().int(),
  total_requests: z.number().int(),
  usage_percentage: z.number(),
  monthly_cost_usd: z.number(),
  cost_display: z.string(),
  starts_at: z.string().datetime(),
  expires_at: z.string().datetime(),
  last_request_at: z.string().datetime().nullable(),
  endpoint_groups_count: z.number().int(),
  endpoint_groups: z.array(z.string()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SubscriptionOverview = z.infer<typeof SubscriptionOverviewSchema>