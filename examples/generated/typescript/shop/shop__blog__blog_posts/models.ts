import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedPostListList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<PostList>;
}

/**
 * Serializer for post creation.
 * 
 * Request model (no read-only fields).
 */
export interface PostCreateRequest {
  title: string;
  content: string;
  /** Brief description */
  excerpt?: string;
  category?: number | null;
  tags?: Array<number>;
  /** * `draft` - Draft
  * `published` - Published
  * `archived` - Archived */
  status?: Enums.PostCreateRequestStatus;
  is_featured?: boolean;
  allow_comments?: boolean;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  featured_image?: string | null;
  featured_image_alt?: string;
}

/**
 * Serializer for post creation.
 * 
 * Response model (includes read-only fields).
 */
export interface PostCreate {
  title: string;
  content: string;
  /** Brief description */
  excerpt?: string;
  category?: number | null;
  tags?: Array<number>;
  /** * `draft` - Draft
  * `published` - Published
  * `archived` - Archived */
  status?: Enums.PostCreateStatus;
  is_featured?: boolean;
  allow_comments?: boolean;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  featured_image?: string | null;
  featured_image_alt?: string;
}

/**
 * Serializer for post detail view.
 * 
 * Response model (includes read-only fields).
 */
export interface PostDetail {
  id: number;
  title: string;
  slug?: string;
  content: string;
  /** Brief description */
  excerpt?: string;
  author: Record<string, any>;
  category: Record<string, any>;
  tags: Array<Tag>;
  /** * `draft` - Draft
  * `published` - Published
  * `archived` - Archived */
  status?: Enums.PostDetailStatus;
  is_featured?: boolean;
  allow_comments?: boolean;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  featured_image?: string | null;
  featured_image_alt?: string;
  views_count?: number;
  likes_count?: number;
  comments_count?: number;
  shares_count?: number;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
  comments: Array<string>;
  user_reaction: string | null;
  can_edit: boolean;
}

/**
 * Serializer for post updates.
 * 
 * Request model (no read-only fields).
 */
export interface PostUpdateRequest {
  title: string;
  content: string;
  /** Brief description */
  excerpt?: string;
  category?: number | null;
  tags?: Array<number>;
  /** * `draft` - Draft
  * `published` - Published
  * `archived` - Archived */
  status?: Enums.PostUpdateRequestStatus;
  is_featured?: boolean;
  allow_comments?: boolean;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  featured_image?: string | null;
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
  category?: number | null;
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
  featured_image?: string | null;
  featured_image_alt?: string;
}

/**
 * Serializer for post detail view.
 * 
 * Request model (no read-only fields).
 */
export interface PostDetailRequest {
  title: string;
  slug?: string;
  content: string;
  /** Brief description */
  excerpt?: string;
  /** * `draft` - Draft
  * `published` - Published
  * `archived` - Archived */
  status?: Enums.PostDetailRequestStatus;
  is_featured?: boolean;
  allow_comments?: boolean;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  featured_image?: string | null;
  featured_image_alt?: string;
  views_count?: number;
  likes_count?: number;
  comments_count?: number;
  shares_count?: number;
  published_at?: string | null;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedPostLikeList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<PostLike>;
}

/**
 * Serializer for blog statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface BlogStats {
  total_posts: number;
  published_posts: number;
  draft_posts: number;
  total_comments: number;
  total_views: number;
  total_likes: number;
  popular_posts: Array<PostList>;
  recent_posts: Array<PostList>;
  top_categories: Array<BlogCategory>;
  top_tags: Array<Tag>;
}

/**
 * Serializer for post list view.
 * 
 * Response model (includes read-only fields).
 */
export interface PostList {
  id: number;
  title: string;
  slug?: string;
  /** Brief description */
  excerpt?: string;
  author: Record<string, any>;
  category: Record<string, any>;
  tags: Array<Tag>;
  /** * `draft` - Draft
  * `published` - Published
  * `archived` - Archived */
  status?: Enums.PostListStatus;
  is_featured?: boolean;
  featured_image?: string | null;
  featured_image_alt?: string;
  views_count?: number;
  likes_count?: number;
  comments_count?: number;
  shares_count?: number;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Serializer for post authors.
 * 
 * Response model (includes read-only fields).
 */
export interface Author {
  id: number;
  /** Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. */
  username: string;
  first_name?: string;
  last_name?: string;
  full_name: string;
  avatar?: string | null;
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
  parent?: number | null;
  posts_count: number;
  children: Array<Record<string, any>>;
  created_at: string;
  updated_at: string;
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
 * Serializer for post likes.
 * 
 * Response model (includes read-only fields).
 */
export interface PostLike {
  id: number;
  user: Record<string, any>;
  /** * `like` - 👍
  * `love` - ❤️
  * `laugh` - 😂
  * `wow` - 😮
  * `sad` - 😢
  * `angry` - 😠 */
  reaction?: Enums.PostLikeReaction;
  created_at: string;
}

