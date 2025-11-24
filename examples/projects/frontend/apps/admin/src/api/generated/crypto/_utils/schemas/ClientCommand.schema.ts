/**
 * Zod schema for ClientCommand
 *
 * This schema provides runtime validation and type inference.
 *  * Virtual serializer for Crypto Client Command interface.

Clients are not stored in database - they exist as gRPC connections.
This serializer represents a connected crypto client with its metadata.
 *  */
import { z } from 'zod'

/**
 * Virtual serializer for Crypto Client Command interface.

Clients are not stored in database - they exist as gRPC connections.
This serializer represents a connected crypto client with its metadata.
 */
export const ClientCommandSchema = z.object({
  client_id: z.string(),
  client_name: z.string(),
  connected: z.boolean(),
  last_heartbeat: z.iso.datetime().nullable(),
  metadata: z.record(z.string(), z.any()),
  wallets_synced: z.int(),
  sync_requests: z.int(),
  last_sync: z.iso.datetime().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ClientCommand = z.infer<typeof ClientCommandSchema>