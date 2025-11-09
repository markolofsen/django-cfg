/**
 * Zod schema for NgrokConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Ngrok tunneling configuration.
 *  */
import { z } from 'zod'

/**
 * Ngrok tunneling configuration.
 */
export const NgrokConfigSchema = z.object({
  enabled: z.boolean().nullable().optional(),
  authtoken: z.string().nullable().optional(),
  basic_auth: z.array(z.string()).nullable().optional(),
  compression: z.boolean().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type NgrokConfig = z.infer<typeof NgrokConfigSchema>