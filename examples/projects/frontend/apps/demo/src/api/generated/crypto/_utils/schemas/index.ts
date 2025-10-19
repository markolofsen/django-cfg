/**
 * Zod Schemas - Runtime validation and type inference
 *
 * Auto-generated from OpenAPI specification.
 * Provides runtime validation for API requests and responses.
 *
 * Usage:
 * ```typescript
 * import { UserSchema } from './schemas'
 *
 * // Validate data
 * const user = UserSchema.parse(data)
 *
 * // Type inference
 * type User = z.infer<typeof UserSchema>
 * ```
 */

export * from './Coin.schema'
export * from './CoinList.schema'
export * from './CoinStats.schema'
export * from './Exchange.schema'
export * from './PaginatedCoinListList.schema'
export * from './PaginatedExchangeList.schema'
export * from './PaginatedWalletList.schema'
export * from './Wallet.schema'
