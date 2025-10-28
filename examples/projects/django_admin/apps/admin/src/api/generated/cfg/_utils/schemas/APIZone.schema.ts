/**
 * Zod schema for APIZone
 *
 * This schema provides runtime validation and type inference.
 *  * OpenAPI zone/group serializer.
 *  */
import { z } from 'zod'

/**
 * OpenAPI zone/group serializer.
 */
export const APIZoneSchema = z.object({
  name: z.string(),
  title: z.string(),
  description: z.string(),
  app_count: z.int(),
  endpoint_count: z.int(),
  status: z.string(),
  schema_url: z.string(),
  api_url: z.string(),
  apps: z.array(z.string()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIZone = z.infer<typeof APIZoneSchema>