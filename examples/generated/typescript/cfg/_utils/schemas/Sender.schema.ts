/**
 * Zod schema for Sender
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'

export const SenderSchema = z.object({
  id: z.number().int(),
  display_username: z.string(),
  email: z.string().email(),
  avatar: z.string().nullable(),
  initials: z.string(),
  is_staff: z.boolean(),
  is_superuser: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Sender = z.infer<typeof SenderSchema>