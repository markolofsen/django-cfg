/**
 * Zod schema for SystemHealthItem
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for system health status items.

Maps to SystemHealthItem Pydantic model.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for system health status items.

Maps to SystemHealthItem Pydantic model.
 */
export const SystemHealthItemSchema = z.object({
  component: z.string(),
  status: z.nativeEnum(Enums.SystemHealthItemStatus),
  description: z.string(),
  last_check: z.string(),
  health_percentage: z.int().min(0.0).max(100.0).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SystemHealthItem = z.infer<typeof SystemHealthItemSchema>