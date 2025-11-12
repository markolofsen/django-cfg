/**
 * Zod schema for RQConfig
 *
 * This schema provides runtime validation and type inference.
 *  * RQ configuration serializer.

Returns current RQ configuration from django-cfg.
 *  */
import { z } from 'zod'
import { ScheduleInfoSchema } from './ScheduleInfo.schema'

/**
 * RQ configuration serializer.

Returns current RQ configuration from django-cfg.
 */
export const RQConfigSchema = z.object({
  enabled: z.boolean(),
  queues: z.record(z.string(), z.any()),
  async_mode: z.boolean().optional(),
  show_admin_link: z.boolean().optional(),
  prometheus_enabled: z.boolean().optional(),
  api_token_configured: z.boolean().optional(),
  schedules: z.array(ScheduleInfoSchema).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RQConfig = z.infer<typeof RQConfigSchema>