/**
 * Zod schema for ServiceList
 *
 * This schema provides runtime validation and type inference.
 *  * List of gRPC services with statistics.
 *  */
import { z } from 'zod'
import { ServiceStatsSerializerSchema } from './ServiceStatsSerializer.schema'

/**
 * List of gRPC services with statistics.
 */
export const ServiceListSchema = z.object({
  services: z.array(ServiceStatsSerializerSchema),
  total_services: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServiceList = z.infer<typeof ServiceListSchema>