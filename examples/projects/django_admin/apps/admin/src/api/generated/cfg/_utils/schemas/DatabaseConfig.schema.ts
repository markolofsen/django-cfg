/**
 * Zod schema for DatabaseConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Database configuration.
 *  */
import { z } from 'zod'

/**
 * Database configuration.
 */
export const DatabaseConfigSchema = z.object({
  engine: z.string(),
  name: z.string(),
  user: z.string().nullable().optional(),
  password: z.string().nullable().optional(),
  host: z.string().nullable().optional(),
  port: z.int().nullable().optional(),
  connect_timeout: z.int().nullable().optional(),
  sslmode: z.string().nullable().optional(),
  options: z.record(z.string(), z.any()).nullable().optional(),
  apps: z.array(z.string()).nullable().optional(),
  operations: z.array(z.string()).nullable().optional(),
  migrate_to: z.string().nullable().optional(),
  routing_description: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DatabaseConfig = z.infer<typeof DatabaseConfigSchema>