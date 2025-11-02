/**
 * Zod schema for User
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for user details.
 *  */
import { z } from 'zod'

/**
 * Serializer for user details.
 */
export const UserSchema = z.object({
  id: z.int(),
  email: z.email(),
  first_name: z.string().max(50).optional(),
  last_name: z.string().max(50).optional(),
  full_name: z.string(),
  initials: z.string(),
  display_username: z.string(),
  company: z.string().max(100).optional(),
  phone: z.string().max(20).optional(),
  position: z.string().max(100).optional(),
  avatar: z.url().nullable(),
  is_staff: z.boolean(),
  is_superuser: z.boolean(),
  date_joined: z.iso.datetime(),
  last_login: z.iso.datetime().nullable(),
  unanswered_messages_count: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type User = z.infer<typeof UserSchema>