/**
 * * `pending` - Pending
 * * `processing` - Processing
 * * `shipped` - Shipped
 * * `delivered` - Delivered
 * * `cancelled` - Cancelled
 * * `refunded` - Refunded
 */
export enum OrderDetailStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  SHIPPED = "shipped",
  DELIVERED = "delivered",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * * `pending` - Pending
 * * `processing` - Processing
 * * `shipped` - Shipped
 * * `delivered` - Delivered
 * * `cancelled` - Cancelled
 * * `refunded` - Refunded
 */
export enum OrderListStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  SHIPPED = "shipped",
  DELIVERED = "delivered",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * * `draft` - Draft
 * * `published` - Published
 * * `archived` - Archived
 */
export enum PatchedPostUpdateRequestStatus {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft
 * * `published` - Published
 * * `archived` - Archived
 */
export enum PostCreateStatus {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft
 * * `published` - Published
 * * `archived` - Archived
 */
export enum PostCreateRequestStatus {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft
 * * `published` - Published
 * * `archived` - Archived
 */
export enum PostDetailStatus {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft
 * * `published` - Published
 * * `archived` - Archived
 */
export enum PostDetailRequestStatus {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `like` - 👍
 * * `love` - ❤️
 * * `laugh` - 😂
 * * `wow` - 😮
 * * `sad` - 😢
 * * `angry` - 😠
 */
export enum PostLikeReaction {
  LIKE = "like",
  LOVE = "love",
  LAUGH = "laugh",
  WOW = "wow",
  SAD = "sad",
  ANGRY = "angry",
}

/**
 * * `draft` - Draft
 * * `published` - Published
 * * `archived` - Archived
 */
export enum PostListStatus {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft
 * * `published` - Published
 * * `archived` - Archived
 */
export enum PostUpdateStatus {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft
 * * `published` - Published
 * * `archived` - Archived
 */
export enum PostUpdateRequestStatus {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `active` - Active
 * * `inactive` - Inactive
 * * `out_of_stock` - Out of Stock
 */
export enum ProductDetailStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  OUT_OF_STOCK = "out_of_stock",
}

/**
 * * `active` - Active
 * * `inactive` - Inactive
 * * `out_of_stock` - Out of Stock
 */
export enum ProductListStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  OUT_OF_STOCK = "out_of_stock",
}

