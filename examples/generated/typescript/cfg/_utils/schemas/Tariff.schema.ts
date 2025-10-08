/**
 * Zod schema for Tariff
 *
 * This schema provides runtime validation and type inference.
 *  * Tariff serializer for subscription pricing.

Used for tariff information and selection.
 *  */
import { z } from 'zod'
import { EndpointGroupSchema } from './EndpointGroup.schema'

/**
 * Tariff serializer for subscription pricing.

Used for tariff information and selection.
 */
export const TariffSchema = z.object({
  id: z.number().int(),
  name: z.string(),
  description: z.string(),
  monthly_price_usd: z.number(),
  requests_per_month: z.number().int(),
  requests_per_hour: z.number().int(),
  is_active: z.boolean(),
  endpoint_groups: z.array(EndpointGroupSchema),
  endpoint_groups_count: z.number().int(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Tariff = z.infer<typeof TariffSchema>