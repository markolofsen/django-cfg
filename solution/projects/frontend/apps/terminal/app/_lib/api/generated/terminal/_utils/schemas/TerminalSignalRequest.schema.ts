/**
 * Zod schema for TerminalSignalRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for signal command.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for signal command.
 */
export const TerminalSignalRequestSchema = z.object({
  signal: z.nativeEnum(Enums.TerminalSignalRequestSignal),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TerminalSignalRequest = z.infer<typeof TerminalSignalRequestSchema>