/**
 * Zod schema for QuickAction
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for quick action buttons.

Maps to QuickAction Pydantic model.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for quick action buttons.

Maps to QuickAction Pydantic model.
 */
export const QuickActionSchema = z.object({
  title: z.string(),
  description: z.string(),
  icon: z.string(),
  link: z.string(),
  color: z.nativeEnum(Enums.QuickActionColor).optional(),
  category: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type QuickAction = z.infer<typeof QuickActionSchema>