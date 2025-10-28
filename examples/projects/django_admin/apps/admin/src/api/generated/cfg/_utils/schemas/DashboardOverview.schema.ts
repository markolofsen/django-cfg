/**
 * Zod schema for DashboardOverview
 *
 * This schema provides runtime validation and type inference.
 *  * Main serializer for dashboard overview endpoint.
Uses DictField to avoid allOf generation in OpenAPI.
 *  */
import { z } from 'zod'

/**
 * Main serializer for dashboard overview endpoint.
Uses DictField to avoid allOf generation in OpenAPI.
 */
export const DashboardOverviewSchema = z.object({
  stat_cards: z.array(z.record(z.string(), z.any())),
  system_health: z.array(z.record(z.string(), z.any())),
  quick_actions: z.array(z.record(z.string(), z.any())),
  recent_activity: z.array(z.record(z.string(), z.any())),
  system_metrics: z.record(z.string(), z.any()),
  user_statistics: z.record(z.string(), z.any()),
  timestamp: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DashboardOverview = z.infer<typeof DashboardOverviewSchema>