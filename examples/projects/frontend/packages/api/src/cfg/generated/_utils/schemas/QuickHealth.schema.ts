/**
 * Zod schema for QuickHealth
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for quick health check response.
 *  */
import { z } from 'zod'

/**
 * Serializer for quick health check response.
 */
export const QuickHealthSchema = z.object({
  status: z.string(),
  timestamp: z.iso.datetime(),
  error: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type QuickHealth = z.infer<typeof QuickHealthSchema>