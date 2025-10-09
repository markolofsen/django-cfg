/**
 * Zod schema for PaginatedAdminUserList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { AdminUserSchema } from './AdminUser.schema'

export const PaginatedAdminUserListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional(),
  previous_page: z.number().int().optional(),
  results: z.array(AdminUserSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedAdminUserList = z.infer<typeof PaginatedAdminUserListSchema>