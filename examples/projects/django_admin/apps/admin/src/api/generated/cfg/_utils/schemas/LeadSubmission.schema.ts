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
  email: z.email(),
  company: z.string().max(200).nullable().optional(),
  company_site: z.string().max(200).nullable().optional(),
  contact_type: z.nativeEnum(Enums.LeadSubmissionContactType).optional(),
  contact_value: z.string().max(200).nullable().optional(),
  subject: z.string().max(200).nullable().optional(),
  message: z.string(),
  extra: z.string().nullable().optional(),
  site_url: z.url(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type LeadSubmission = z.infer<typeof LeadSubmissionSchema>