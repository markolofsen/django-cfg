/**
 * Zod schema for RedisQueueConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Redis Queue configuration.
 *  */
import { z } from 'zod'

/**
 * Redis Queue configuration.
 */
export const RedisQueueConfigSchema = z.object({
  url: z.string().nullable().optional(),
  host: z.string().nullable().optional(),
  port: z.int().nullable().optional(),
  db: z.int().nullable().optional(),
  username: z.string().nullable().optional(),
  password: z.string().nullable().optional(),
  default_timeout: z.int().nullable().optional(),
  default_result_ttl: z.int().nullable().optional(),
  sentinels: z.record(z.string(), z.any()).nullable().optional(),
  master_name: z.string().nullable().optional(),
  socket_timeout: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RedisQueueConfig = z.infer<typeof RedisQueueConfigSchema>