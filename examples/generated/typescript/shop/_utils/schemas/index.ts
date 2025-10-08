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

export * from './Author.schema'
export * from './AuthorRequest.schema'
export * from './BlogCategory.schema'
export * from './BlogCategoryRequest.schema'
export * from './BlogStats.schema'
export * from './Comment.schema'
export * from './CommentRequest.schema'
export * from './OrderDetail.schema'
export * from './OrderItem.schema'
export * from './OrderList.schema'
export * from './PaginatedBlogCategoryList.schema'
export * from './PaginatedCommentList.schema'
export * from './PaginatedOrderListList.schema'
export * from './PaginatedPostLikeList.schema'
export * from './PaginatedPostListList.schema'
export * from './PaginatedProductListList.schema'
export * from './PaginatedShopCategoryList.schema'
export * from './PaginatedTagList.schema'
export * from './PatchedBlogCategoryRequest.schema'
export * from './PatchedCommentRequest.schema'
export * from './PatchedPostUpdateRequest.schema'
export * from './PatchedTagRequest.schema'
export * from './PostCreate.schema'
export * from './PostCreateRequest.schema'
export * from './PostDetail.schema'
export * from './PostDetailRequest.schema'
export * from './PostLike.schema'
export * from './PostList.schema'
export * from './PostUpdate.schema'
export * from './PostUpdateRequest.schema'
export * from './ProductDetail.schema'
export * from './ProductList.schema'
export * from './ShopCategory.schema'
export * from './ShopStats.schema'
export * from './Tag.schema'
export * from './TagRequest.schema'
