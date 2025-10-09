/**
 * Zod schema for Subscription
 *
 * This schema provides runtime validation and type inference.
 *  * Complete subscription serializer with full details.

Used for subscription detail views and updates.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { EndpointGroupSchema } from './EndpointGroup.schema'
import { TariffSchema } from './Tariff.schema'

/**
 * Complete subscription serializer with full details.

Used for subscription detail views and updates.
 */
export const SubscriptionSchema = z.object({
  id: z.string().uuid(),
  user: z.string(),
  tariff: TariffSchema,
  endpoint_group: EndpointGroupSchema,
  status: z.nativeEnum(Enums.SubscriptionStatus).optional(),
  status_display: z.string(),
  status_color: z.string(),
  tier: z.nativeEnum(Enums.SubscriptionTier).optional(),
  total_requests: z.number().int(),
  usage_percentage: z.number(),
  last_request_at: z.string().datetime().optional(),
  expires_at: z.string().datetime(),
  is_active: z.boolean(),
  is_expired: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Subscription = z.infer<typeof SubscriptionSchema>