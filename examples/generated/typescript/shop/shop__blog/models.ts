import * as Enums from "../enums";

/**
 * Serializer for blog categories.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedBlogCategoryRequest {
  name?: string;
  description?: string;
  /** Hex color code */
  color?: string;
  meta_title?: string;
  meta_description?: string;
  parent?: number;
}

/**
 * Serializer for blog categories.
 * 
 * Response model (includes read-only fields).
 */
export interface BlogCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
  /** Hex color code */
  color?: string;
  meta_title?: string;
  meta_description?: string;
  parent?: number;
  posts_count: number;
  children: Array<Record<string, any>>;
  created_at: string;
  updated_at: string;
}

/**
 * Serializer for post updates.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedPostUpdateRequest {
  title?: string;
  content?: string;
  /** Brief description */
  excerpt?: string;
  category?: number;
  tags?: Array<number>;
  /** * `draft` - Draft
  * `published` - Published
  * `archived` - Archived */
  status?: Enums.PatchedPostUpdateRequestStatus;
  is_featured?: boolean;
  allow_comments?: boolean;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  featured_image?: string;
  featured_image_alt?: string;
}

/**
 * Serializer for post updates.
 * 
 * Response model (includes read-only fields).
 */
export interface PostUpdate {
  title: string;
  content: string;
  /** Brief description */
  excerpt?: string;
  category?: number;
  tags?: Array<number>;
  /** * `draft` - Draft
  * `published` - Published
  * `archived` - Archived */
  status?: Enums.PostUpdateStatus;
  is_featured?: boolean;
  allow_comments?: boolean;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  featured_image?: string;
  featured_image_alt?: string;
}

/**
 * Serializer for blog tags.
 * 
 * Response model (includes read-only fields).
 */
export interface Tag {
  id: number;
  name: string;
  slug: string;
  description?: string;
  posts_count: number;
  created_at: string;
}

/**
 * Serializer for blog tags.
 * 
 * Request model (no read-only fields).
 */
export interface TagRequest {
  name: string;
  description?: string;
}

/**
 * Serializer for blog tags.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedTagRequest {
  name?: string;
  description?: string;
}

