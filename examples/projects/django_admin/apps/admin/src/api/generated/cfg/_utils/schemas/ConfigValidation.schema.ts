/**
 * Zod schema for ConfigValidation
 *
 * This schema provides runtime validation and type inference.
 *  * Validation result for config serializer.
 *  */
import { z } from 'zod'

/**
 * Validation result for config serializer.
 */
export const ConfigValidationSchema = z.object({
  status: z.string(),
  missing_in_serializer: z.array(z.string()),
  extra_in_serializer: z.array(z.string()),
  type_mismatches: z.array(z.record(z.string(), z.any())),
  total_config_fields: z.int(),
  total_serializer_fields: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ConfigValidation = z.infer<typeof ConfigValidationSchema>