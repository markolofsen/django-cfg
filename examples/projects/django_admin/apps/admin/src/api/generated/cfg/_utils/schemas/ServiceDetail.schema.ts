/**
 * Zod schema for ServiceDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Detailed information about a service.
 *  */
import { z } from 'zod'
import { MethodInfoSchema } from './MethodInfo.schema'
import { RecentErrorSchema } from './RecentError.schema'
import { ServiceStatsSchema } from './ServiceStats.schema'

/**
 * Detailed information about a service.
 */
export const ServiceDetailSchema = z.object({
  name: z.string(),
  full_name: z.string(),
  package: z.string(),
  description: z.string().optional(),
  file_path: z.string().optional(),
  class_name: z.string(),
  base_class: z.string().optional(),
  methods: z.array(MethodInfoSchema).optional(),
  stats: ServiceStatsSchema,
  recent_errors: z.array(RecentErrorSchema).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServiceDetail = z.infer<typeof ServiceDetailSchema>