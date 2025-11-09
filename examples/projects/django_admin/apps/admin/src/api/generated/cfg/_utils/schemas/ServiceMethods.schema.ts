/**
 * Zod schema for ServiceMethods
 *
 * This schema provides runtime validation and type inference.
 *  * List of methods for a service.
 *  */
import { z } from 'zod'
import { MethodSummarySchema } from './MethodSummary.schema'

/**
 * List of methods for a service.
 */
export const ServiceMethodsSchema = z.object({
  service_name: z.string(),
  methods: z.array(MethodSummarySchema).optional(),
  total_methods: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServiceMethods = z.infer<typeof ServiceMethodsSchema>