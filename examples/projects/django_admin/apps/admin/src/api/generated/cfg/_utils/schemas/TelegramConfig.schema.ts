/**
 * Zod schema for TelegramConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Telegram service configuration.
 *  */
import { z } from 'zod'

/**
 * Telegram service configuration.
 */
export const TelegramConfigSchema = z.object({
  bot_token: z.string().nullable().optional(),
  chat_id: z.int().nullable().optional(),
  parse_mode: z.string().nullable().optional(),
  disable_notification: z.boolean().nullable().optional(),
  disable_web_page_preview: z.boolean().nullable().optional(),
  timeout: z.int().nullable().optional(),
  webhook_url: z.string().nullable().optional(),
  webhook_secret: z.string().nullable().optional(),
  max_retries: z.int().nullable().optional(),
  retry_delay: z.number().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TelegramConfig = z.infer<typeof TelegramConfigSchema>