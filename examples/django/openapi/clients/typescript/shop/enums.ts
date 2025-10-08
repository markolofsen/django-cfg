/**
 * * `pending` - Pending * `processing` - Processing * `shipped` - Shipped *
 * `delivered` - Delivered * `cancelled` - Cancelled * `refunded` - Refunded
 */
export enum OrderDetail.status {
  PENDING = "pending",
  PROCESSING = "processing",
  SHIPPED = "shipped",
  DELIVERED = "delivered",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * * `pending` - Pending * `processing` - Processing * `shipped` - Shipped *
 * `delivered` - Delivered * `cancelled` - Cancelled * `refunded` - Refunded
 */
export enum OrderList.status {
  PENDING = "pending",
  PROCESSING = "processing",
  SHIPPED = "shipped",
  DELIVERED = "delivered",
  CANCELLED = "cancelled",
  REFUNDED = "refunded",
}

/**
 * * `draft` - Draft * `published` - Published * `archived` - Archived
 */
export enum PatchedPostUpdateRequest.status {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft * `published` - Published * `archived` - Archived
 */
export enum PostCreate.status {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft * `published` - Published * `archived` - Archived
 */
export enum PostCreateRequest.status {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft * `published` - Published * `archived` - Archived
 */
export enum PostDetail.status {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft * `published` - Published * `archived` - Archived
 */
export enum PostDetailRequest.status {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `like` - 👍 * `love` - ❤️ * `laugh` - 😂 * `wow` - 😮 * `sad` - 😢 * `angry` -
 * 😠
 */
export enum PostLike.reaction {
  LIKE = "like",
  LOVE = "love",
  LAUGH = "laugh",
  WOW = "wow",
  SAD = "sad",
  ANGRY = "angry",
}

/**
 * * `draft` - Draft * `published` - Published * `archived` - Archived
 */
export enum PostList.status {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft * `published` - Published * `archived` - Archived
 */
export enum PostUpdate.status {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `draft` - Draft * `published` - Published * `archived` - Archived
 */
export enum PostUpdateRequest.status {
  DRAFT = "draft",
  PUBLISHED = "published",
  ARCHIVED = "archived",
}

/**
 * * `active` - Active * `inactive` - Inactive * `out_of_stock` - Out of Stock
 */
export enum ProductDetail.status {
  ACTIVE = "active",
  INACTIVE = "inactive",
  OUT_OF_STOCK = "out_of_stock",
}

/**
 * * `active` - Active * `inactive` - Inactive * `out_of_stock` - Out of Stock
 */
export enum ProductList.status {
  ACTIVE = "active",
  INACTIVE = "inactive",
  OUT_OF_STOCK = "out_of_stock",
}

