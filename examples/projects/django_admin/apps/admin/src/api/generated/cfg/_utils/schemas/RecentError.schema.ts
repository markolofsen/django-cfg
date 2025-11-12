/**
 * Zod schema for RecentError
 *
 * This schema provides runtime validation and type inference.
 *  * Recent error information.
 *  */
import { z } from 'zod'

/**
 * Recent error information.
 */
export const RecentErrorSchema = z.object({
  method: z.string(),
  error_message: z.string(),
  grpc_status_code: z.string(),
  occurred_at: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RecentError = z.infer<typeof RecentErrorSchema>