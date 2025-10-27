/**
 * Zod schema for SystemHealth
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for overall system health status.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { SystemHealthItemSchema } from './SystemHealthItem.schema'

/**
 * Serializer for overall system health status.
 */
export const SystemHealthSchema = z.object({
  overall_status: z.nativeEnum(Enums.SystemHealthOverallStatus),
  overall_health_percentage: z.int().min(0.0).max(100.0),
  components: z.array(SystemHealthItemSchema),
  timestamp: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SystemHealth = z.infer<typeof SystemHealthSchema>