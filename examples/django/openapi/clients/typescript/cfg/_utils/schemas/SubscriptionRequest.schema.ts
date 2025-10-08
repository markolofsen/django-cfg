/**
 * Zod schema for SubscriptionRequest
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
export const SubscriptionRequestSchema = z.object({
  status: z.nativeEnum(Enums.SubscriptionRequestStatus).optional(),
  tier: z.nativeEnum(Enums.SubscriptionRequestTier).optional(),
  expires_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SubscriptionRequest = z.infer<typeof SubscriptionRequestSchema>