/**
 * Zod schema for LeadSubmission
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for lead form submission from frontend.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for lead form submission from frontend.
 */
export const LeadSubmissionSchema = z.object({
  name: z.string().max(200),
  email: z.string().email().max(254),
  company: z.string().max(200).optional().nullable(),
  company_site: z.string().max(200).optional().nullable(),
  contact_type: z.nativeEnum(Enums.LeadSubmissionContactType).optional(),
  contact_value: z.string().max(200).optional().nullable(),
  subject: z.string().max(200).optional().nullable(),
  message: z.string(),
  extra: z.string().optional().nullable(),
  site_url: z.string().url().max(200),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type LeadSubmission = z.infer<typeof LeadSubmissionSchema>