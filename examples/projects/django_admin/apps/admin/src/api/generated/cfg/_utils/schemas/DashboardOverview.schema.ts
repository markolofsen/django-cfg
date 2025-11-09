/**
 * Zod schema for DashboardOverview
 *
 * This schema provides runtime validation and type inference.
 *  * Main serializer for dashboard overview endpoint.
Uses typed serializers for proper OpenAPI schema generation.
 *  */
import { z } from 'zod'
import { ActivityEntrySchema } from './ActivityEntry.schema'
import { AppStatisticsSchema } from './AppStatistics.schema'
import { QuickActionSchema } from './QuickAction.schema'
import { StatCardSchema } from './StatCard.schema'
import { SystemHealthSchema } from './SystemHealth.schema'
import { SystemMetricsSchema } from './SystemMetrics.schema'
import { UserStatisticsSchema } from './UserStatistics.schema'

/**
 * Main serializer for dashboard overview endpoint.
Uses typed serializers for proper OpenAPI schema generation.
 */
export const DashboardOverviewSchema = z.object({
  stat_cards: z.array(StatCardSchema),
  system_health: SystemHealthSchema,
  quick_actions: z.array(QuickActionSchema),
  recent_activity: z.array(ActivityEntrySchema),
  system_metrics: SystemMetricsSchema,
  user_statistics: UserStatisticsSchema,
  app_statistics: z.array(AppStatisticsSchema).optional(),
  timestamp: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DashboardOverview = z.infer<typeof DashboardOverviewSchema>