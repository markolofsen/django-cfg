/**
 * Zod schema for StatCard
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for dashboard statistics cards.

Maps to StatCard Pydantic model.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for dashboard statistics cards.

Maps to StatCard Pydantic model.
 */
export const StatCardSchema = z.object({
  title: z.string(),
  value: z.string(),
  icon: z.string(),
  change: z.string().nullable().optional(),
  change_type: z.nativeEnum(Enums.StatCardChangeType).optional(),
  description: z.string().nullable().optional(),
  color: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type StatCard = z.infer<typeof StatCardSchema>