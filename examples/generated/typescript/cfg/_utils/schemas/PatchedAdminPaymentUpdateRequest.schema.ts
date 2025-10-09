/**
 * Zod schema for PatchedAdminPaymentUpdateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for updating payments in admin interface.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for updating payments in admin interface.
 */
export const PatchedAdminPaymentUpdateRequestSchema = z.object({
  status: z.nativeEnum(Enums.PatchedAdminPaymentUpdateRequestStatus).optional(),
  description: z.string().optional(),
  callback_url: z.string().url().max(200).optional(),
  cancel_url: z.string().url().max(200).optional(),
  provider_data: z.string().optional(),
  webhook_data: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedAdminPaymentUpdateRequest = z.infer<typeof PatchedAdminPaymentUpdateRequestSchema>