/**
 * Zod schema for ConfigData
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for complete config data endpoint.

Returns both DjangoConfig and Django settings with validation info.
 *  */
import { z } from 'zod'
import { ConfigValidationSchema } from './ConfigValidation.schema'
import { DjangoConfigSchema } from './DjangoConfig.schema'

/**
 * Serializer for complete config data endpoint.

Returns both DjangoConfig and Django settings with validation info.
 */
export const ConfigDataSchema = z.object({
  django_config: DjangoConfigSchema,
  django_settings: z.record(z.string(), z.any()),
  _validation: ConfigValidationSchema,
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ConfigData = z.infer<typeof ConfigDataSchema>