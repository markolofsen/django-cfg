/**
 * Zod schema for RecentUser
 *
 * This schema provides runtime validation and type inference.
 *  * Recent user serializer.
 *  */
import { z } from 'zod'

/**
 * Recent user serializer.
 */
export const RecentUserSchema = z.object({
  id: z.int(),
  username: z.string(),
  email: z.email(),
  date_joined: z.string(),
  is_active: z.boolean(),
  is_staff: z.boolean(),
  is_superuser: z.boolean(),
  last_login: z.string().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RecentUser = z.infer<typeof RecentUserSchema>