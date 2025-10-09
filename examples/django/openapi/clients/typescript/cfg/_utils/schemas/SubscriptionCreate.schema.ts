/**
 * Zod schema for SubscriptionCreate
 *
 * This schema provides runtime validation and type inference.
 *  * Subscription creation serializer with service integration.

Validates input and delegates to SubscriptionService.
 *  */
import { z } from 'zod'

/**
 * Subscription creation serializer with service integration.

Validates input and delegates to SubscriptionService.
 */
export const SubscriptionCreateSchema = z.object({
  tariff_id: z.number().int().min(1.0),
  endpoint_group_id: z.number().int().min(1.0).optional(),
  duration_days: z.number().int().min(1.0).max(365.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type SubscriptionCreate = z.infer<typeof SubscriptionCreateSchema>