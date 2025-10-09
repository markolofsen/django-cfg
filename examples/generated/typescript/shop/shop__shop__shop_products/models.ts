import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedProductListList {
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
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<ProductList>;
}

/**
 * Serializer for product detail view.
 * 
 * Response model (includes read-only fields).
 */
export interface ProductDetail {
  id: number;
  name: string;
  slug?: string;
  description: string;
  short_description?: string;
  price: string;
  sale_price?: string;
  current_price: string;
  is_on_sale: boolean;
  discount_percentage: number;
  sku: string;
  stock_quantity?: number;
  manage_stock?: boolean;
  is_in_stock: boolean;
  category: Record<string, any>;
  image?: string;
  /** * `active` - Active
  * `inactive` - Inactive
  * `out_of_stock` - Out of Stock */
  status?: Enums.ProductDetailStatus;
  is_featured?: boolean;
  is_digital?: boolean;
  meta_title?: string;
  meta_description?: string;
  views_count?: number;
  sales_count?: number;
  /** Weight in kg */
  weight?: string;
  /** Length in cm */
  length?: string;
  /** Width in cm */
  width?: string;
  /** Height in cm */
  height?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Serializer for shop statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface ShopStats {
  total_products: number;
  active_products: number;
  out_of_stock_products: number;
  total_orders: number;
  pending_orders: number;
  total_revenue: string;
  popular_products: Array<ProductList>;
  recent_orders: Array<OrderList>;
}

/**
 * Serializer for product list view.
 * 
 * Response model (includes read-only fields).
 */
export interface ProductList {
  id: number;
  name: string;
  slug?: string;
  short_description?: string;
  price: string;
  sale_price?: string;
  current_price: string;
  is_on_sale: boolean;
  discount_percentage: number;
  category: Record<string, any>;
  image?: string;
  /** * `active` - Active
  * `inactive` - Inactive
  * `out_of_stock` - Out of Stock */
  status?: Enums.ProductListStatus;
  is_featured?: boolean;
  is_digital?: boolean;
  stock_quantity?: number;
  is_in_stock: boolean;
  views_count?: number;
  sales_count?: number;
  created_at: string;
}

/**
 * Serializer for shop categories.
 * 
 * Response model (includes read-only fields).
 */
export interface ShopCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image?: string;
  parent?: number;
  meta_title?: string;
  meta_description?: string;
  products_count: number;
  children: Array<Record<string, any>>;
  is_active?: boolean;
  sort_order?: number;
  created_at: string;
  updated_at: string;
}

/**
 * Serializer for order list view.
 * 
 * Response model (includes read-only fields).
 */
export interface OrderList {
  id: number;
  order_number: string;
  customer: string;
  /** * `pending` - Pending
  * `processing` - Processing
  * `shipped` - Shipped
  * `delivered` - Delivered
  * `cancelled` - Cancelled
  * `refunded` - Refunded */
  status?: Enums.OrderListStatus;
  subtotal?: string;
  total_amount?: string;
  items_count: number;
  created_at: string;
  updated_at: string;
}

