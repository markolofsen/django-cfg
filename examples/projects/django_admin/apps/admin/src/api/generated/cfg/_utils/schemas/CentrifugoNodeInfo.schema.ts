/**
 * Zod schema for CentrifugoNodeInfo
 *
 * This schema provides runtime validation and type inference.
 *  * Information about a single Centrifugo node.
 *  */
import { z } from 'zod'
import { CentrifugoMetricsSchema } from './CentrifugoMetrics.schema'
import { CentrifugoProcessSchema } from './CentrifugoProcess.schema'

/**
 * Information about a single Centrifugo node.
 */
export const CentrifugoNodeInfoSchema = z.object({
  uid: z.string(),
  name: z.string(),
  version: z.string(),
  num_clients: z.int(),
  num_users: z.int(),
  num_channels: z.int(),
  uptime: z.int(),
  num_subs: z.int(),
  metrics: CentrifugoMetricsSchema.optional(),
  process: CentrifugoProcessSchema.optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoNodeInfo = z.infer<typeof CentrifugoNodeInfoSchema>