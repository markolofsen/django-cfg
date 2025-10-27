/**
 * Zod schema for APIZonesSummary
 *
 * This schema provides runtime validation and type inference.
 *  * API zones summary serializer.
 *  */
import { z } from 'zod'
import { APIZoneSchema } from './APIZone.schema'

/**
 * API zones summary serializer.
 */
export const APIZonesSummarySchema = z.object({
  zones: z.array(APIZoneSchema),
  summary: z.record(z.string(), z.any()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type APIZonesSummary = z.infer<typeof APIZonesSummarySchema>