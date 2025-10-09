/**
 * Zod schema for AdminUser
 *
 * This schema provides runtime validation and type inference.
 *  * Simplified user serializer for admin interface.
 *  */
import { z } from 'zod'

/**
 * Simplified user serializer for admin interface.
 */
export const AdminUserSchema = z.object({
  id: z.number().int(),
  username: z.string(),
  email: z.string().email(),
  first_name: z.string(),
  last_name: z.string(),
  is_active: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type AdminUser = z.infer<typeof AdminUserSchema>