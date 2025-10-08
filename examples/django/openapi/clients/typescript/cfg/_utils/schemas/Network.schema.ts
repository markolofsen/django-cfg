/**
 * Zod schema for Network
 *
 * This schema provides runtime validation and type inference.
 *  * Network serializer for blockchain networks.

Used for network information and selection.
 *  */
import { z } from 'zod'
import { CurrencyListSchema } from './CurrencyList.schema'

/**
 * Network serializer for blockchain networks.

Used for network information and selection.
 */
export const NetworkSchema = z.object({
  id: z.number().int(),
  currency: CurrencyListSchema,
  name: z.string(),
  code: z.string(),
  is_active: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Network = z.infer<typeof NetworkSchema>