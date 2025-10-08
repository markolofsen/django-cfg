/**
 * Zod schema for PatchedSubscriptionRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Complete subscription serializer with full details.

Used for subscription detail views and updates.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Complete subscription serializer with full details.

Used for subscription detail views and updates.
 */
export const PatchedSubscriptionRequestSchema = z.object({
  status: z.nativeEnum(Enums.PatchedSubscriptionRequestStatus).optional(),
  tier: z.nativeEnum(Enums.PatchedSubscriptionRequestTier).optional(),
  expires_at: z.string().datetime().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedSubscriptionRequest = z.infer<typeof PatchedSubscriptionRequestSchema>