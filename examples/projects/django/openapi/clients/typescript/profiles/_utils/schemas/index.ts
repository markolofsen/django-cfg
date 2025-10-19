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

export * from './PaginatedUserProfileList.schema'
export * from './PatchedUserProfileRequest.schema'
export * from './PatchedUserProfileUpdateRequest.schema'
export * from './UserProfile.schema'
export * from './UserProfileRequest.schema'
export * from './UserProfileStats.schema'
export * from './UserProfileUpdate.schema'
export * from './UserProfileUpdateRequest.schema'
