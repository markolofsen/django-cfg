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
  email: z.email().optional(),
  company: z.string().max(200).nullable().optional(),
  company_site: z.string().max(200).nullable().optional(),
  contact_type: z.nativeEnum(Enums.PatchedLeadSubmissionRequestContactType).optional(),
  contact_value: z.string().max(200).nullable().optional(),
  subject: z.string().max(200).nullable().optional(),
  message: z.string().min(1).optional(),
  extra: z.string().nullable().optional(),
  site_url: z.url().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedLeadSubmissionRequest = z.infer<typeof PatchedLeadSubmissionRequestSchema>