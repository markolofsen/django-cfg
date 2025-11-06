/**
 * Zod schema for GRPCConfigDashboard
 *
 * This schema provides runtime validation and type inference.
 *  * gRPC configuration for dashboard.
 *  */
import { z } from 'zod'

/**
 * gRPC configuration for dashboard.
 */
export const GRPCConfigDashboardSchema = z.object({
  enabled: z.boolean().nullable().optional(),
  host: z.string().nullable().optional(),
  port: z.int().nullable().optional(),
  max_workers: z.int().nullable().optional(),
  reflection: z.boolean().nullable().optional(),
  health_check: z.boolean().nullable().optional(),
  interceptors: z.array(z.string()).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCConfigDashboard = z.infer<typeof GRPCConfigDashboardSchema>