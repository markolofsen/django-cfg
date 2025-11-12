/**
 * Zod schema for Publish
 *
 * This schema provides runtime validation and type inference.
 *  * Single publish item for DRF pagination.
 *  */
import { z } from 'zod'

/**
 * Single publish item for DRF pagination.
 */
export const PublishSchema = z.object({
  message_id: z.string(),
  channel: z.string(),
  status: z.string(),
  wait_for_ack: z.boolean(),
  acks_received: z.int(),
  acks_expected: z.int().nullable(),
  duration_ms: z.number().nullable(),
  created_at: z.iso.datetime(),
  completed_at: z.iso.datetime().nullable(),
  error_code: z.string().nullable(),
  error_message: z.string().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Publish = z.infer<typeof PublishSchema>