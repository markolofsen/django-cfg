/**
 * Zod schema for SubscriptionList
 *
 * This schema provides runtime validation and type inference.
 *  * Lightweight subscription serializer for lists.

Optimized for subscription lists with minimal data.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Lightweight subscription serializer for lists.

Optimized for subscription lists with minimal data.
 */
export const SubscriptionListSchema = z.object({
  id: z.string().uuid(),
  user: z.string(),
  tariff_name: z.string(),
  status: z.nativeEnum(Enums.SubscriptionListStatus),
  status_display: z.string(),
  is_active: z.boolean(),
  is_expired: z.boolean(),
  expires_at: z.string().datetime(),
  created_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SubscriptionList = z.infer<typeof SubscriptionListSchema>