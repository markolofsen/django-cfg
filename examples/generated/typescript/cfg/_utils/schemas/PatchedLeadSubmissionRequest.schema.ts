/**
 * Zod schema for PatchedLeadSubmissionRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for lead form submission from frontend.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for lead form submission from frontend.
 */
export const PatchedLeadSubmissionRequestSchema = z.object({
  name: z.string().min(1).max(200).optional(),
  email: z.string().email().min(1).max(254).optional(),
  company: z.string().max(200).optional().nullable(),
  company_site: z.string().max(200).optional().nullable(),
  contact_type: z.nativeEnum(Enums.PatchedLeadSubmissionRequestContactType).optional(),
  contact_value: z.string().max(200).optional().nullable(),
  subject: z.string().max(200).optional().nullable(),
  message: z.string().min(1).optional(),
  extra: z.string().optional().nullable(),
  site_url: z.string().url().min(1).max(200).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedLeadSubmissionRequest = z.infer<typeof PatchedLeadSubmissionRequestSchema>