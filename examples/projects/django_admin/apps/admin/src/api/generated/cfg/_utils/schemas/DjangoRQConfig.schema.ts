/**
 * Zod schema for DjangoRQConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Django-RQ configuration.
 *  */
import { z } from 'zod'
import { RedisQueueConfigSchema } from './RedisQueueConfig.schema'

/**
 * Django-RQ configuration.
 */
export const DjangoRQConfigSchema = z.object({
  enabled: z.boolean().nullable().optional(),
  queues: z.array(RedisQueueConfigSchema).nullable().optional(),
  show_admin_link: z.boolean().nullable().optional(),
  exception_handlers: z.array(z.string()).nullable().optional(),
  api_token: z.string().nullable().optional(),
  prometheus_enabled: z.boolean().nullable().optional(),
  schedules: z.array(z.record(z.string(), z.any())).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DjangoRQConfig = z.infer<typeof DjangoRQConfigSchema>