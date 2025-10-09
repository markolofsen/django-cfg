import * as Enums from "../enums";

/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedOrderListList {
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
  results: Array<OrderList>;
}

/**
 * Serializer for order detail view.
 * 
 * Response model (includes read-only fields).
 */
export interface OrderDetail {
  id: number;
  order_number: string;
  customer: string;
  /** * `pending` - Pending
  * `processing` - Processing
  * `shipped` - Shipped
  * `delivered` - Delivered
  * `cancelled` - Cancelled
  * `refunded` - Refunded */
  status?: Enums.OrderDetailStatus;
  subtotal?: string;
  tax_amount?: string;
  shipping_amount?: string;
  discount_amount?: string;
  total_amount?: string;
  billing_address: string;
  shipping_address: string;
  customer_notes?: string;
  admin_notes?: string;
  items: Array<OrderItem>;
  created_at: string;
  updated_at: string;
  shipped_at?: string;
  delivered_at?: string;
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

/**
 * Serializer for order items.
 * 
 * Response model (includes read-only fields).
 */
export interface OrderItem {
  id: number;
  product: Record<string, any>;
  quantity?: number;
  unit_price: string;
  total_price: string;
  product_name: string;
  product_sku: string;
  created_at: string;
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

