import { ShopBlogCategoriesAPI } from "./shop__blog__blog_categories";
import { ShopBlogCommentsAPI } from "./shop__blog__blog_comments";
import { ShopBlogPostsAPI } from "./shop__blog__blog_posts";
import { ShopBlogTagsAPI } from "./shop__blog__blog_tags";
import { ShopCategoriesAPI } from "./shop__shop__shop_categories";
import { ShopOrdersAPI } from "./shop__shop__shop_orders";
import { ShopProductsAPI } from "./shop__shop__shop_products";
import { ShopBlogAPI } from "./shop__blog";
import { HttpClientAdapter, FetchAdapter } from "./http";
import { APIError, NetworkError } from "./errors";
import { APILogger, type LoggerConfig } from "./logger";


/**
 * Async API client for Django CFG Sample API.
 *
 * Usage:
 * ```typescript
 * const client = new APIClient('https://api.example.com');
 * const users = await client.users.list();
 * const post = await client.posts.create(newPost);
 *
 * // Custom HTTP adapter (e.g., Axios)
 * const client = new APIClient('https://api.example.com', {
 *   httpClient: new AxiosAdapter()
 * });
 * ```
 */
export class APIClient {
  private baseUrl: string;
  private httpClient: HttpClientAdapter;
  private logger: APILogger | null = null;

  // Sub-clients
  public shop_blog_categories: ShopBlogCategoriesAPI;
  public shop_blog_comments: ShopBlogCommentsAPI;
  public shop_blog_posts: ShopBlogPostsAPI;
  public shop_blog_tags: ShopBlogTagsAPI;
  public shop_categories: ShopCategoriesAPI;
  public shop_orders: ShopOrdersAPI;
  public shop_products: ShopProductsAPI;
  public shop_blog: ShopBlogAPI;

  constructor(
    baseUrl: string,
    options?: {
      httpClient?: HttpClientAdapter;
      loggerConfig?: Partial<LoggerConfig>;
    }
  ) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.httpClient = options?.httpClient || new FetchAdapter();

    // Initialize logger if config provided
    if (options?.loggerConfig !== undefined) {
      this.logger = new APILogger(options.loggerConfig);
    }

    // Initialize sub-clients
    this.shop_blog_categories = new ShopBlogCategoriesAPI(this);
    this.shop_blog_comments = new ShopBlogCommentsAPI(this);
    this.shop_blog_posts = new ShopBlogPostsAPI(this);
    this.shop_blog_tags = new ShopBlogTagsAPI(this);
    this.shop_categories = new ShopCategoriesAPI(this);
    this.shop_orders = new ShopOrdersAPI(this);
    this.shop_products = new ShopProductsAPI(this);
    this.shop_blog = new ShopBlogAPI(this);
  }

  /**
   * Get CSRF token from cookies.
   */
  getCsrfToken(): string | null {
    const name = 'csrftoken';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop()?.split(';').shift() || null;
    }
    return null;
  }

  /**
   * Make HTTP request with Django CSRF and session handling.
   */
  async request<T>(
    method: string,
    path: string,
    options?: {
      params?: Record<string, any>;
      body?: any;
      formData?: FormData;
    }
  ): Promise<T> {
    const url = new URL(path, this.baseUrl);
    const startTime = Date.now();

    // Build headers
    const headers: Record<string, string> = {};

    // Don't set Content-Type for FormData (browser will set it with boundary)
    if (!options?.formData) {
      headers['Content-Type'] = 'application/json';
    }

    // Add CSRF token for non-GET requests
    if (method !== 'GET') {
      const csrfToken = this.getCsrfToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
    }

    // Log request
    if (this.logger) {
      this.logger.logRequest({
        method,
        url: url.toString(),
        headers,
        body: options?.formData || options?.body,
        timestamp: startTime,
      });
    }

    try {
      // Make request via HTTP adapter
      const response = await this.httpClient.request<T>({
        method,
        url: url.toString(),
        headers,
        params: options?.params,
        body: options?.body,
        formData: options?.formData,
      });

      const duration = Date.now() - startTime;

      // Check for HTTP errors
      if (response.status >= 400) {
        const error = new APIError(
          response.status,
          response.statusText,
          response.data,
          url.toString()
        );

        // Log error
        if (this.logger) {
          this.logger.logError(
            {
              method,
              url: url.toString(),
              headers,
              body: options?.formData || options?.body,
              timestamp: startTime,
            },
            {
              message: error.message,
              statusCode: response.status,
              duration,
              timestamp: Date.now(),
            }
          );
        }

        throw error;
      }

      // Log successful response
      if (this.logger) {
        this.logger.logResponse(
          {
            method,
            url: url.toString(),
            headers,
            body: options?.formData || options?.body,
            timestamp: startTime,
          },
          {
            status: response.status,
            statusText: response.statusText,
            data: response.data,
            duration,
            timestamp: Date.now(),
          }
        );
      }

      return response.data as T;
    } catch (error) {
      const duration = Date.now() - startTime;

      // Re-throw APIError as-is
      if (error instanceof APIError) {
        throw error;
      }

      // Wrap other errors as NetworkError
      const networkError = error instanceof Error
        ? new NetworkError(error.message, url.toString(), error)
        : new NetworkError('Unknown error', url.toString());

      // Log network error
      if (this.logger) {
        this.logger.logError(
          {
            method,
            url: url.toString(),
            headers,
            body: options?.formData || options?.body,
            timestamp: startTime,
          },
          {
            message: networkError.message,
            duration,
            timestamp: Date.now(),
          }
        );
      }

      throw networkError;
    }
  }
}
