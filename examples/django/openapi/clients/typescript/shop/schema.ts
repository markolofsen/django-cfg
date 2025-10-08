/**
 * OpenAPI Schema Export
 *
 * Contains the complete OpenAPI specification for runtime access.
 */

export const OPENAPI_SCHEMA = {
  "components": {
    "schemas": {
      "Author": {
        "description": "Serializer for post authors.",
        "properties": {
          "avatar": {
            "format": "uri",
            "nullable": true,
            "type": "string"
          },
          "first_name": {
            "maxLength": 50,
            "type": "string"
          },
          "full_name": {
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "last_name": {
            "maxLength": 50,
            "type": "string"
          },
          "username": {
            "description": "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
            "maxLength": 150,
            "pattern": "^[\\w.@+-]+$",
            "type": "string"
          }
        },
        "required": [
          "full_name",
          "id",
          "username"
        ],
        "type": "object"
      },
      "AuthorRequest": {
        "description": "Serializer for post authors.",
        "properties": {
          "avatar": {
            "format": "binary",
            "nullable": true,
            "type": "string"
          },
          "first_name": {
            "maxLength": 50,
            "type": "string"
          },
          "last_name": {
            "maxLength": 50,
            "type": "string"
          },
          "username": {
            "description": "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
            "maxLength": 150,
            "minLength": 1,
            "pattern": "^[\\w.@+-]+$",
            "type": "string"
          }
        },
        "required": [
          "username"
        ],
        "type": "object"
      },
      "BlogCategory": {
        "description": "Serializer for blog categories.",
        "properties": {
          "children": {
            "items": {
              "additionalProperties": {},
              "type": "object"
            },
            "readOnly": true,
            "type": "array"
          },
          "color": {
            "description": "Hex color code",
            "maxLength": 7,
            "type": "string"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "name": {
            "maxLength": 100,
            "type": "string"
          },
          "parent": {
            "nullable": true,
            "type": "integer"
          },
          "posts_count": {
            "readOnly": true,
            "type": "integer"
          },
          "slug": {
            "pattern": "^[-a-zA-Z0-9_]+$",
            "readOnly": true,
            "type": "string"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "children",
          "created_at",
          "id",
          "name",
          "posts_count",
          "slug",
          "updated_at"
        ],
        "type": "object"
      },
      "BlogCategoryRequest": {
        "description": "Serializer for blog categories.",
        "properties": {
          "color": {
            "description": "Hex color code",
            "maxLength": 7,
            "minLength": 1,
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "name": {
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          },
          "parent": {
            "nullable": true,
            "type": "integer"
          }
        },
        "required": [
          "name"
        ],
        "type": "object"
      },
      "BlogStats": {
        "description": "Serializer for blog statistics.",
        "properties": {
          "draft_posts": {
            "type": "integer"
          },
          "popular_posts": {
            "items": {
              "$ref": "#/components/schemas/PostList"
            },
            "type": "array"
          },
          "published_posts": {
            "type": "integer"
          },
          "recent_posts": {
            "items": {
              "$ref": "#/components/schemas/PostList"
            },
            "type": "array"
          },
          "top_categories": {
            "items": {
              "$ref": "#/components/schemas/BlogCategory"
            },
            "type": "array"
          },
          "top_tags": {
            "items": {
              "$ref": "#/components/schemas/Tag"
            },
            "type": "array"
          },
          "total_comments": {
            "type": "integer"
          },
          "total_likes": {
            "type": "integer"
          },
          "total_posts": {
            "type": "integer"
          },
          "total_views": {
            "type": "integer"
          }
        },
        "required": [
          "draft_posts",
          "popular_posts",
          "published_posts",
          "recent_posts",
          "top_categories",
          "top_tags",
          "total_comments",
          "total_likes",
          "total_posts",
          "total_views"
        ],
        "type": "object"
      },
      "Comment": {
        "description": "Serializer for blog comments.",
        "properties": {
          "author": {
            "allOf": [
              {
                "$ref": "#/components/schemas/Author"
              }
            ],
            "readOnly": true
          },
          "can_edit": {
            "readOnly": true,
            "type": "boolean"
          },
          "content": {
            "type": "string"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_approved": {
            "readOnly": true,
            "type": "boolean"
          },
          "likes_count": {
            "readOnly": true,
            "type": "integer"
          },
          "parent": {
            "nullable": true,
            "type": "integer"
          },
          "replies": {
            "items": {
              "additionalProperties": {},
              "type": "object"
            },
            "readOnly": true,
            "type": "array"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "author",
          "can_edit",
          "content",
          "created_at",
          "id",
          "is_approved",
          "likes_count",
          "replies",
          "updated_at"
        ],
        "type": "object"
      },
      "CommentRequest": {
        "description": "Serializer for blog comments.",
        "properties": {
          "content": {
            "minLength": 1,
            "type": "string"
          },
          "parent": {
            "nullable": true,
            "type": "integer"
          }
        },
        "required": [
          "content"
        ],
        "type": "object"
      },
      "OrderDetail": {
        "description": "Serializer for order detail view.",
        "properties": {
          "admin_notes": {
            "type": "string"
          },
          "billing_address": {
            "type": "string"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "customer": {
            "readOnly": true,
            "type": "string"
          },
          "customer_notes": {
            "type": "string"
          },
          "delivered_at": {
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "discount_amount": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "items": {
            "items": {
              "$ref": "#/components/schemas/OrderItem"
            },
            "readOnly": true,
            "type": "array"
          },
          "order_number": {
            "maxLength": 50,
            "type": "string"
          },
          "shipped_at": {
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "shipping_address": {
            "type": "string"
          },
          "shipping_amount": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "status": {
            "description": "* `pending` - Pending\n* `processing` - Processing\n* `shipped` - Shipped\n* `delivered` - Delivered\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
            "enum": [
              "pending",
              "processing",
              "shipped",
              "delivered",
              "cancelled",
              "refunded"
            ],
            "type": "string",
            "x-spec-enum-id": "a98f61c8de1ef65b"
          },
          "subtotal": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "tax_amount": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "total_amount": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "billing_address",
          "created_at",
          "customer",
          "id",
          "items",
          "order_number",
          "shipping_address",
          "updated_at"
        ],
        "type": "object"
      },
      "OrderItem": {
        "description": "Serializer for order items.",
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "product": {
            "allOf": [
              {
                "$ref": "#/components/schemas/ProductList"
              }
            ],
            "readOnly": true
          },
          "product_name": {
            "readOnly": true,
            "type": "string"
          },
          "product_sku": {
            "readOnly": true,
            "type": "string"
          },
          "quantity": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "total_price": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "unit_price": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          }
        },
        "required": [
          "created_at",
          "id",
          "product",
          "product_name",
          "product_sku",
          "total_price",
          "unit_price"
        ],
        "type": "object"
      },
      "OrderList": {
        "description": "Serializer for order list view.",
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "customer": {
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "items_count": {
            "readOnly": true,
            "type": "integer"
          },
          "order_number": {
            "maxLength": 50,
            "type": "string"
          },
          "status": {
            "description": "* `pending` - Pending\n* `processing` - Processing\n* `shipped` - Shipped\n* `delivered` - Delivered\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
            "enum": [
              "pending",
              "processing",
              "shipped",
              "delivered",
              "cancelled",
              "refunded"
            ],
            "type": "string",
            "x-spec-enum-id": "a98f61c8de1ef65b"
          },
          "subtotal": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "total_amount": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "created_at",
          "customer",
          "id",
          "items_count",
          "order_number",
          "updated_at"
        ],
        "type": "object"
      },
      "PaginatedBlogCategoryList": {
        "properties": {
          "count": {
            "description": "Total number of items across all pages",
            "example": 150,
            "type": "integer"
          },
          "has_next": {
            "description": "Whether there is a next page",
            "example": true,
            "type": "boolean"
          },
          "has_previous": {
            "description": "Whether there is a previous page",
            "example": true,
            "type": "boolean"
          },
          "next_page": {
            "description": "Next page number (null if no next page)",
            "example": 3,
            "nullable": true,
            "type": "integer"
          },
          "page": {
            "description": "Current page number (1-based)",
            "example": 2,
            "type": "integer"
          },
          "page_size": {
            "description": "Number of items per page",
            "example": 10,
            "type": "integer"
          },
          "pages": {
            "description": "Total number of pages",
            "example": 15,
            "type": "integer"
          },
          "previous_page": {
            "description": "Previous page number (null if no previous page)",
            "example": 1,
            "nullable": true,
            "type": "integer"
          },
          "results": {
            "description": "Array of items for current page",
            "items": {
              "$ref": "#/components/schemas/BlogCategory"
            },
            "type": "array"
          }
        },
        "required": [
          "count",
          "page",
          "pages",
          "page_size",
          "has_next",
          "has_previous",
          "results"
        ],
        "type": "object"
      },
      "PaginatedCommentList": {
        "properties": {
          "count": {
            "description": "Total number of items across all pages",
            "example": 150,
            "type": "integer"
          },
          "has_next": {
            "description": "Whether there is a next page",
            "example": true,
            "type": "boolean"
          },
          "has_previous": {
            "description": "Whether there is a previous page",
            "example": true,
            "type": "boolean"
          },
          "next_page": {
            "description": "Next page number (null if no next page)",
            "example": 3,
            "nullable": true,
            "type": "integer"
          },
          "page": {
            "description": "Current page number (1-based)",
            "example": 2,
            "type": "integer"
          },
          "page_size": {
            "description": "Number of items per page",
            "example": 10,
            "type": "integer"
          },
          "pages": {
            "description": "Total number of pages",
            "example": 15,
            "type": "integer"
          },
          "previous_page": {
            "description": "Previous page number (null if no previous page)",
            "example": 1,
            "nullable": true,
            "type": "integer"
          },
          "results": {
            "description": "Array of items for current page",
            "items": {
              "$ref": "#/components/schemas/Comment"
            },
            "type": "array"
          }
        },
        "required": [
          "count",
          "page",
          "pages",
          "page_size",
          "has_next",
          "has_previous",
          "results"
        ],
        "type": "object"
      },
      "PaginatedOrderListList": {
        "properties": {
          "count": {
            "description": "Total number of items across all pages",
            "example": 150,
            "type": "integer"
          },
          "has_next": {
            "description": "Whether there is a next page",
            "example": true,
            "type": "boolean"
          },
          "has_previous": {
            "description": "Whether there is a previous page",
            "example": true,
            "type": "boolean"
          },
          "next_page": {
            "description": "Next page number (null if no next page)",
            "example": 3,
            "nullable": true,
            "type": "integer"
          },
          "page": {
            "description": "Current page number (1-based)",
            "example": 2,
            "type": "integer"
          },
          "page_size": {
            "description": "Number of items per page",
            "example": 10,
            "type": "integer"
          },
          "pages": {
            "description": "Total number of pages",
            "example": 15,
            "type": "integer"
          },
          "previous_page": {
            "description": "Previous page number (null if no previous page)",
            "example": 1,
            "nullable": true,
            "type": "integer"
          },
          "results": {
            "description": "Array of items for current page",
            "items": {
              "$ref": "#/components/schemas/OrderList"
            },
            "type": "array"
          }
        },
        "required": [
          "count",
          "page",
          "pages",
          "page_size",
          "has_next",
          "has_previous",
          "results"
        ],
        "type": "object"
      },
      "PaginatedPostLikeList": {
        "properties": {
          "count": {
            "description": "Total number of items across all pages",
            "example": 150,
            "type": "integer"
          },
          "has_next": {
            "description": "Whether there is a next page",
            "example": true,
            "type": "boolean"
          },
          "has_previous": {
            "description": "Whether there is a previous page",
            "example": true,
            "type": "boolean"
          },
          "next_page": {
            "description": "Next page number (null if no next page)",
            "example": 3,
            "nullable": true,
            "type": "integer"
          },
          "page": {
            "description": "Current page number (1-based)",
            "example": 2,
            "type": "integer"
          },
          "page_size": {
            "description": "Number of items per page",
            "example": 10,
            "type": "integer"
          },
          "pages": {
            "description": "Total number of pages",
            "example": 15,
            "type": "integer"
          },
          "previous_page": {
            "description": "Previous page number (null if no previous page)",
            "example": 1,
            "nullable": true,
            "type": "integer"
          },
          "results": {
            "description": "Array of items for current page",
            "items": {
              "$ref": "#/components/schemas/PostLike"
            },
            "type": "array"
          }
        },
        "required": [
          "count",
          "page",
          "pages",
          "page_size",
          "has_next",
          "has_previous",
          "results"
        ],
        "type": "object"
      },
      "PaginatedPostListList": {
        "properties": {
          "count": {
            "description": "Total number of items across all pages",
            "example": 150,
            "type": "integer"
          },
          "has_next": {
            "description": "Whether there is a next page",
            "example": true,
            "type": "boolean"
          },
          "has_previous": {
            "description": "Whether there is a previous page",
            "example": true,
            "type": "boolean"
          },
          "next_page": {
            "description": "Next page number (null if no next page)",
            "example": 3,
            "nullable": true,
            "type": "integer"
          },
          "page": {
            "description": "Current page number (1-based)",
            "example": 2,
            "type": "integer"
          },
          "page_size": {
            "description": "Number of items per page",
            "example": 10,
            "type": "integer"
          },
          "pages": {
            "description": "Total number of pages",
            "example": 15,
            "type": "integer"
          },
          "previous_page": {
            "description": "Previous page number (null if no previous page)",
            "example": 1,
            "nullable": true,
            "type": "integer"
          },
          "results": {
            "description": "Array of items for current page",
            "items": {
              "$ref": "#/components/schemas/PostList"
            },
            "type": "array"
          }
        },
        "required": [
          "count",
          "page",
          "pages",
          "page_size",
          "has_next",
          "has_previous",
          "results"
        ],
        "type": "object"
      },
      "PaginatedProductListList": {
        "properties": {
          "count": {
            "description": "Total number of items across all pages",
            "example": 150,
            "type": "integer"
          },
          "has_next": {
            "description": "Whether there is a next page",
            "example": true,
            "type": "boolean"
          },
          "has_previous": {
            "description": "Whether there is a previous page",
            "example": true,
            "type": "boolean"
          },
          "next_page": {
            "description": "Next page number (null if no next page)",
            "example": 3,
            "nullable": true,
            "type": "integer"
          },
          "page": {
            "description": "Current page number (1-based)",
            "example": 2,
            "type": "integer"
          },
          "page_size": {
            "description": "Number of items per page",
            "example": 10,
            "type": "integer"
          },
          "pages": {
            "description": "Total number of pages",
            "example": 15,
            "type": "integer"
          },
          "previous_page": {
            "description": "Previous page number (null if no previous page)",
            "example": 1,
            "nullable": true,
            "type": "integer"
          },
          "results": {
            "description": "Array of items for current page",
            "items": {
              "$ref": "#/components/schemas/ProductList"
            },
            "type": "array"
          }
        },
        "required": [
          "count",
          "page",
          "pages",
          "page_size",
          "has_next",
          "has_previous",
          "results"
        ],
        "type": "object"
      },
      "PaginatedShopCategoryList": {
        "properties": {
          "count": {
            "description": "Total number of items across all pages",
            "example": 150,
            "type": "integer"
          },
          "has_next": {
            "description": "Whether there is a next page",
            "example": true,
            "type": "boolean"
          },
          "has_previous": {
            "description": "Whether there is a previous page",
            "example": true,
            "type": "boolean"
          },
          "next_page": {
            "description": "Next page number (null if no next page)",
            "example": 3,
            "nullable": true,
            "type": "integer"
          },
          "page": {
            "description": "Current page number (1-based)",
            "example": 2,
            "type": "integer"
          },
          "page_size": {
            "description": "Number of items per page",
            "example": 10,
            "type": "integer"
          },
          "pages": {
            "description": "Total number of pages",
            "example": 15,
            "type": "integer"
          },
          "previous_page": {
            "description": "Previous page number (null if no previous page)",
            "example": 1,
            "nullable": true,
            "type": "integer"
          },
          "results": {
            "description": "Array of items for current page",
            "items": {
              "$ref": "#/components/schemas/ShopCategory"
            },
            "type": "array"
          }
        },
        "required": [
          "count",
          "page",
          "pages",
          "page_size",
          "has_next",
          "has_previous",
          "results"
        ],
        "type": "object"
      },
      "PaginatedTagList": {
        "properties": {
          "count": {
            "description": "Total number of items across all pages",
            "example": 150,
            "type": "integer"
          },
          "has_next": {
            "description": "Whether there is a next page",
            "example": true,
            "type": "boolean"
          },
          "has_previous": {
            "description": "Whether there is a previous page",
            "example": true,
            "type": "boolean"
          },
          "next_page": {
            "description": "Next page number (null if no next page)",
            "example": 3,
            "nullable": true,
            "type": "integer"
          },
          "page": {
            "description": "Current page number (1-based)",
            "example": 2,
            "type": "integer"
          },
          "page_size": {
            "description": "Number of items per page",
            "example": 10,
            "type": "integer"
          },
          "pages": {
            "description": "Total number of pages",
            "example": 15,
            "type": "integer"
          },
          "previous_page": {
            "description": "Previous page number (null if no previous page)",
            "example": 1,
            "nullable": true,
            "type": "integer"
          },
          "results": {
            "description": "Array of items for current page",
            "items": {
              "$ref": "#/components/schemas/Tag"
            },
            "type": "array"
          }
        },
        "required": [
          "count",
          "page",
          "pages",
          "page_size",
          "has_next",
          "has_previous",
          "results"
        ],
        "type": "object"
      },
      "PatchedBlogCategoryRequest": {
        "description": "Serializer for blog categories.",
        "properties": {
          "color": {
            "description": "Hex color code",
            "maxLength": 7,
            "minLength": 1,
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "name": {
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          },
          "parent": {
            "nullable": true,
            "type": "integer"
          }
        },
        "type": "object"
      },
      "PatchedCommentRequest": {
        "description": "Serializer for blog comments.",
        "properties": {
          "content": {
            "minLength": 1,
            "type": "string"
          },
          "parent": {
            "nullable": true,
            "type": "integer"
          }
        },
        "type": "object"
      },
      "PatchedPostUpdateRequest": {
        "description": "Serializer for post updates.",
        "properties": {
          "allow_comments": {
            "type": "boolean"
          },
          "category": {
            "nullable": true,
            "type": "integer"
          },
          "content": {
            "minLength": 1,
            "type": "string"
          },
          "excerpt": {
            "description": "Brief description",
            "maxLength": 500,
            "type": "string"
          },
          "featured_image": {
            "format": "binary",
            "nullable": true,
            "type": "string"
          },
          "featured_image_alt": {
            "maxLength": 255,
            "type": "string"
          },
          "is_featured": {
            "type": "boolean"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_keywords": {
            "maxLength": 255,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "status": {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "enum": [
              "draft",
              "published",
              "archived"
            ],
            "type": "string",
            "x-spec-enum-id": "3999cf41a064d13a"
          },
          "tags": {
            "items": {
              "type": "integer"
            },
            "type": "array"
          },
          "title": {
            "maxLength": 200,
            "minLength": 1,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PatchedTagRequest": {
        "description": "Serializer for blog tags.",
        "properties": {
          "description": {
            "type": "string"
          },
          "name": {
            "maxLength": 50,
            "minLength": 1,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PostCreate": {
        "description": "Serializer for post creation.",
        "properties": {
          "allow_comments": {
            "type": "boolean"
          },
          "category": {
            "nullable": true,
            "type": "integer"
          },
          "content": {
            "type": "string"
          },
          "excerpt": {
            "description": "Brief description",
            "maxLength": 500,
            "type": "string"
          },
          "featured_image": {
            "format": "uri",
            "nullable": true,
            "type": "string"
          },
          "featured_image_alt": {
            "maxLength": 255,
            "type": "string"
          },
          "is_featured": {
            "type": "boolean"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_keywords": {
            "maxLength": 255,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "status": {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "enum": [
              "draft",
              "published",
              "archived"
            ],
            "type": "string",
            "x-spec-enum-id": "3999cf41a064d13a"
          },
          "tags": {
            "items": {
              "type": "integer"
            },
            "type": "array"
          },
          "title": {
            "maxLength": 200,
            "type": "string"
          }
        },
        "required": [
          "content",
          "title"
        ],
        "type": "object"
      },
      "PostCreateRequest": {
        "description": "Serializer for post creation.",
        "properties": {
          "allow_comments": {
            "type": "boolean"
          },
          "category": {
            "nullable": true,
            "type": "integer"
          },
          "content": {
            "minLength": 1,
            "type": "string"
          },
          "excerpt": {
            "description": "Brief description",
            "maxLength": 500,
            "type": "string"
          },
          "featured_image": {
            "format": "binary",
            "nullable": true,
            "type": "string"
          },
          "featured_image_alt": {
            "maxLength": 255,
            "type": "string"
          },
          "is_featured": {
            "type": "boolean"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_keywords": {
            "maxLength": 255,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "status": {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "enum": [
              "draft",
              "published",
              "archived"
            ],
            "type": "string",
            "x-spec-enum-id": "3999cf41a064d13a"
          },
          "tags": {
            "items": {
              "type": "integer"
            },
            "type": "array"
          },
          "title": {
            "maxLength": 200,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "content",
          "title"
        ],
        "type": "object"
      },
      "PostDetail": {
        "description": "Serializer for post detail view.",
        "properties": {
          "allow_comments": {
            "type": "boolean"
          },
          "author": {
            "allOf": [
              {
                "$ref": "#/components/schemas/Author"
              }
            ],
            "readOnly": true
          },
          "can_edit": {
            "readOnly": true,
            "type": "boolean"
          },
          "category": {
            "allOf": [
              {
                "$ref": "#/components/schemas/BlogCategory"
              }
            ],
            "readOnly": true
          },
          "comments": {
            "items": {},
            "readOnly": true,
            "type": "array"
          },
          "comments_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "content": {
            "type": "string"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "excerpt": {
            "description": "Brief description",
            "maxLength": 500,
            "type": "string"
          },
          "featured_image": {
            "format": "uri",
            "nullable": true,
            "type": "string"
          },
          "featured_image_alt": {
            "maxLength": 255,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_featured": {
            "type": "boolean"
          },
          "likes_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_keywords": {
            "maxLength": 255,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "published_at": {
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "shares_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "slug": {
            "maxLength": 200,
            "pattern": "^[-a-zA-Z0-9_]+$",
            "type": "string"
          },
          "status": {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "enum": [
              "draft",
              "published",
              "archived"
            ],
            "type": "string",
            "x-spec-enum-id": "3999cf41a064d13a"
          },
          "tags": {
            "items": {
              "$ref": "#/components/schemas/Tag"
            },
            "readOnly": true,
            "type": "array"
          },
          "title": {
            "maxLength": 200,
            "type": "string"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "user_reaction": {
            "nullable": true,
            "readOnly": true
          },
          "views_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          }
        },
        "required": [
          "author",
          "can_edit",
          "category",
          "comments",
          "content",
          "created_at",
          "id",
          "tags",
          "title",
          "updated_at",
          "user_reaction"
        ],
        "type": "object"
      },
      "PostDetailRequest": {
        "description": "Serializer for post detail view.",
        "properties": {
          "allow_comments": {
            "type": "boolean"
          },
          "comments_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "content": {
            "minLength": 1,
            "type": "string"
          },
          "excerpt": {
            "description": "Brief description",
            "maxLength": 500,
            "type": "string"
          },
          "featured_image": {
            "format": "binary",
            "nullable": true,
            "type": "string"
          },
          "featured_image_alt": {
            "maxLength": 255,
            "type": "string"
          },
          "is_featured": {
            "type": "boolean"
          },
          "likes_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_keywords": {
            "maxLength": 255,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "published_at": {
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "shares_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "slug": {
            "maxLength": 200,
            "pattern": "^[-a-zA-Z0-9_]+$",
            "type": "string"
          },
          "status": {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "enum": [
              "draft",
              "published",
              "archived"
            ],
            "type": "string",
            "x-spec-enum-id": "3999cf41a064d13a"
          },
          "title": {
            "maxLength": 200,
            "minLength": 1,
            "type": "string"
          },
          "views_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          }
        },
        "required": [
          "content",
          "title"
        ],
        "type": "object"
      },
      "PostLike": {
        "description": "Serializer for post likes.",
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "reaction": {
            "description": "* `like` - \ud83d\udc4d\n* `love` - \u2764\ufe0f\n* `laugh` - \ud83d\ude02\n* `wow` - \ud83d\ude2e\n* `sad` - \ud83d\ude22\n* `angry` - \ud83d\ude20",
            "enum": [
              "like",
              "love",
              "laugh",
              "wow",
              "sad",
              "angry"
            ],
            "type": "string",
            "x-spec-enum-id": "aecaede12861eb54"
          },
          "user": {
            "allOf": [
              {
                "$ref": "#/components/schemas/Author"
              }
            ],
            "readOnly": true
          }
        },
        "required": [
          "created_at",
          "id",
          "user"
        ],
        "type": "object"
      },
      "PostList": {
        "description": "Serializer for post list view.",
        "properties": {
          "author": {
            "allOf": [
              {
                "$ref": "#/components/schemas/Author"
              }
            ],
            "readOnly": true
          },
          "category": {
            "allOf": [
              {
                "$ref": "#/components/schemas/BlogCategory"
              }
            ],
            "readOnly": true
          },
          "comments_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "excerpt": {
            "description": "Brief description",
            "maxLength": 500,
            "type": "string"
          },
          "featured_image": {
            "format": "uri",
            "nullable": true,
            "type": "string"
          },
          "featured_image_alt": {
            "maxLength": 255,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_featured": {
            "type": "boolean"
          },
          "likes_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "published_at": {
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "shares_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "slug": {
            "maxLength": 200,
            "pattern": "^[-a-zA-Z0-9_]+$",
            "type": "string"
          },
          "status": {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "enum": [
              "draft",
              "published",
              "archived"
            ],
            "type": "string",
            "x-spec-enum-id": "3999cf41a064d13a"
          },
          "tags": {
            "items": {
              "$ref": "#/components/schemas/Tag"
            },
            "readOnly": true,
            "type": "array"
          },
          "title": {
            "maxLength": 200,
            "type": "string"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "views_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          }
        },
        "required": [
          "author",
          "category",
          "created_at",
          "id",
          "tags",
          "title",
          "updated_at"
        ],
        "type": "object"
      },
      "PostUpdate": {
        "description": "Serializer for post updates.",
        "properties": {
          "allow_comments": {
            "type": "boolean"
          },
          "category": {
            "nullable": true,
            "type": "integer"
          },
          "content": {
            "type": "string"
          },
          "excerpt": {
            "description": "Brief description",
            "maxLength": 500,
            "type": "string"
          },
          "featured_image": {
            "format": "uri",
            "nullable": true,
            "type": "string"
          },
          "featured_image_alt": {
            "maxLength": 255,
            "type": "string"
          },
          "is_featured": {
            "type": "boolean"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_keywords": {
            "maxLength": 255,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "status": {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "enum": [
              "draft",
              "published",
              "archived"
            ],
            "type": "string",
            "x-spec-enum-id": "3999cf41a064d13a"
          },
          "tags": {
            "items": {
              "type": "integer"
            },
            "type": "array"
          },
          "title": {
            "maxLength": 200,
            "type": "string"
          }
        },
        "required": [
          "content",
          "title"
        ],
        "type": "object"
      },
      "PostUpdateRequest": {
        "description": "Serializer for post updates.",
        "properties": {
          "allow_comments": {
            "type": "boolean"
          },
          "category": {
            "nullable": true,
            "type": "integer"
          },
          "content": {
            "minLength": 1,
            "type": "string"
          },
          "excerpt": {
            "description": "Brief description",
            "maxLength": 500,
            "type": "string"
          },
          "featured_image": {
            "format": "binary",
            "nullable": true,
            "type": "string"
          },
          "featured_image_alt": {
            "maxLength": 255,
            "type": "string"
          },
          "is_featured": {
            "type": "boolean"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_keywords": {
            "maxLength": 255,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "status": {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "enum": [
              "draft",
              "published",
              "archived"
            ],
            "type": "string",
            "x-spec-enum-id": "3999cf41a064d13a"
          },
          "tags": {
            "items": {
              "type": "integer"
            },
            "type": "array"
          },
          "title": {
            "maxLength": 200,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "content",
          "title"
        ],
        "type": "object"
      },
      "ProductDetail": {
        "description": "Serializer for product detail view.",
        "properties": {
          "category": {
            "allOf": [
              {
                "$ref": "#/components/schemas/ShopCategory"
              }
            ],
            "readOnly": true
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "current_price": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "discount_percentage": {
            "readOnly": true,
            "type": "integer"
          },
          "height": {
            "description": "Height in cm",
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,6}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "image": {
            "format": "uri",
            "nullable": true,
            "type": "string"
          },
          "is_digital": {
            "type": "boolean"
          },
          "is_featured": {
            "type": "boolean"
          },
          "is_in_stock": {
            "readOnly": true,
            "type": "boolean"
          },
          "is_on_sale": {
            "readOnly": true,
            "type": "boolean"
          },
          "length": {
            "description": "Length in cm",
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,6}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "manage_stock": {
            "type": "boolean"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "name": {
            "maxLength": 200,
            "type": "string"
          },
          "price": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "sale_price": {
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "sales_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "short_description": {
            "maxLength": 500,
            "type": "string"
          },
          "sku": {
            "maxLength": 100,
            "type": "string"
          },
          "slug": {
            "maxLength": 200,
            "pattern": "^[-a-zA-Z0-9_]+$",
            "type": "string"
          },
          "status": {
            "description": "* `active` - Active\n* `inactive` - Inactive\n* `out_of_stock` - Out of Stock",
            "enum": [
              "active",
              "inactive",
              "out_of_stock"
            ],
            "type": "string",
            "x-spec-enum-id": "50e9f6640da1d7f3"
          },
          "stock_quantity": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "views_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "weight": {
            "description": "Weight in kg",
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,6}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "width": {
            "description": "Width in cm",
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,6}(?:\\.\\d{0,2})?$",
            "type": "string"
          }
        },
        "required": [
          "category",
          "created_at",
          "current_price",
          "description",
          "discount_percentage",
          "id",
          "is_in_stock",
          "is_on_sale",
          "name",
          "price",
          "sku",
          "updated_at"
        ],
        "type": "object"
      },
      "ProductList": {
        "description": "Serializer for product list view.",
        "properties": {
          "category": {
            "allOf": [
              {
                "$ref": "#/components/schemas/ShopCategory"
              }
            ],
            "readOnly": true
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "current_price": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "discount_percentage": {
            "readOnly": true,
            "type": "integer"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "image": {
            "format": "uri",
            "nullable": true,
            "type": "string"
          },
          "is_digital": {
            "type": "boolean"
          },
          "is_featured": {
            "type": "boolean"
          },
          "is_in_stock": {
            "readOnly": true,
            "type": "boolean"
          },
          "is_on_sale": {
            "readOnly": true,
            "type": "boolean"
          },
          "name": {
            "maxLength": 200,
            "type": "string"
          },
          "price": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "sale_price": {
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "sales_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "short_description": {
            "maxLength": 500,
            "type": "string"
          },
          "slug": {
            "maxLength": 200,
            "pattern": "^[-a-zA-Z0-9_]+$",
            "type": "string"
          },
          "status": {
            "description": "* `active` - Active\n* `inactive` - Inactive\n* `out_of_stock` - Out of Stock",
            "enum": [
              "active",
              "inactive",
              "out_of_stock"
            ],
            "type": "string",
            "x-spec-enum-id": "50e9f6640da1d7f3"
          },
          "stock_quantity": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "views_count": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          }
        },
        "required": [
          "category",
          "created_at",
          "current_price",
          "discount_percentage",
          "id",
          "is_in_stock",
          "is_on_sale",
          "name",
          "price"
        ],
        "type": "object"
      },
      "ShopCategory": {
        "description": "Serializer for shop categories.",
        "properties": {
          "children": {
            "items": {
              "additionalProperties": {},
              "type": "object"
            },
            "readOnly": true,
            "type": "array"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "image": {
            "format": "uri",
            "nullable": true,
            "type": "string"
          },
          "is_active": {
            "type": "boolean"
          },
          "meta_description": {
            "maxLength": 160,
            "type": "string"
          },
          "meta_title": {
            "maxLength": 60,
            "type": "string"
          },
          "name": {
            "maxLength": 100,
            "type": "string"
          },
          "parent": {
            "nullable": true,
            "type": "integer"
          },
          "products_count": {
            "readOnly": true,
            "type": "integer"
          },
          "slug": {
            "pattern": "^[-a-zA-Z0-9_]+$",
            "readOnly": true,
            "type": "string"
          },
          "sort_order": {
            "format": "int64",
            "maximum": 9223372036854775807,
            "minimum": 0,
            "type": "integer"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "children",
          "created_at",
          "id",
          "name",
          "products_count",
          "slug",
          "updated_at"
        ],
        "type": "object"
      },
      "ShopStats": {
        "description": "Serializer for shop statistics.",
        "properties": {
          "active_products": {
            "type": "integer"
          },
          "out_of_stock_products": {
            "type": "integer"
          },
          "pending_orders": {
            "type": "integer"
          },
          "popular_products": {
            "items": {
              "$ref": "#/components/schemas/ProductList"
            },
            "type": "array"
          },
          "recent_orders": {
            "items": {
              "$ref": "#/components/schemas/OrderList"
            },
            "type": "array"
          },
          "total_orders": {
            "type": "integer"
          },
          "total_products": {
            "type": "integer"
          },
          "total_revenue": {
            "format": "decimal",
            "pattern": "^-?\\d{0,10}(?:\\.\\d{0,2})?$",
            "type": "string"
          }
        },
        "required": [
          "active_products",
          "out_of_stock_products",
          "pending_orders",
          "popular_products",
          "recent_orders",
          "total_orders",
          "total_products",
          "total_revenue"
        ],
        "type": "object"
      },
      "Tag": {
        "description": "Serializer for blog tags.",
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "name": {
            "maxLength": 50,
            "type": "string"
          },
          "posts_count": {
            "readOnly": true,
            "type": "integer"
          },
          "slug": {
            "pattern": "^[-a-zA-Z0-9_]+$",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "created_at",
          "id",
          "name",
          "posts_count",
          "slug"
        ],
        "type": "object"
      },
      "TagRequest": {
        "description": "Serializer for blog tags.",
        "properties": {
          "description": {
            "type": "string"
          },
          "name": {
            "maxLength": 50,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "name"
        ],
        "type": "object"
      }
    },
    "securitySchemes": {
      "basicAuth": {
        "scheme": "basic",
        "type": "http"
      },
      "cookieAuth": {
        "in": "cookie",
        "name": "sessionid",
        "type": "apiKey"
      }
    }
  },
  "info": {
    "description": "Complete API documentation for Django CFG sample project",
    "title": "Django CFG Sample API",
    "version": "1.0.0",
    "x-django-metadata": {
      "apps": [
        "blog",
        "shop"
      ],
      "generator": "django-client",
      "generator_version": "1.0.0",
      "group": "shop"
    }
  },
  "openapi": "3.0.3",
  "paths": {
    "/blog/categories/": {
      "get": {
        "description": "Get a list of all blog categories",
        "operationId": "blog_categories_list",
        "parameters": [
          {
            "description": "Which field to use when ordering the results.",
            "in": "query",
            "name": "ordering",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "A page number within the paginated result set.",
            "in": "query",
            "name": "page",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Number of results to return per page.",
            "in": "query",
            "name": "page_size",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "A search term.",
            "in": "query",
            "name": "search",
            "required": false,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedBlogCategoryList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "List categories",
        "tags": [
          "Blog - Categories"
        ]
      },
      "post": {
        "description": "Create a new blog category",
        "operationId": "blog_categories_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/BlogCategoryRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/BlogCategoryRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/BlogCategoryRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/BlogCategory"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Create category",
        "tags": [
          "Blog - Categories"
        ]
      }
    },
    "/blog/categories/{slug}/": {
      "delete": {
        "description": "Delete a category",
        "operationId": "blog_categories_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Delete category",
        "tags": [
          "Blog - Categories"
        ]
      },
      "get": {
        "description": "Get details of a specific category",
        "operationId": "blog_categories_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/BlogCategory"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get category",
        "tags": [
          "Blog - Categories"
        ]
      },
      "patch": {
        "description": "ViewSet for blog categories.",
        "operationId": "blog_categories_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PatchedBlogCategoryRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PatchedBlogCategoryRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PatchedBlogCategoryRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/BlogCategory"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "blog"
        ]
      },
      "put": {
        "description": "Update category information",
        "operationId": "blog_categories_update",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/BlogCategoryRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/BlogCategoryRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/BlogCategoryRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/BlogCategory"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Update category",
        "tags": [
          "Blog - Categories"
        ]
      }
    },
    "/blog/comments/": {
      "get": {
        "description": "Get a list of comments",
        "operationId": "blog_comments_list",
        "parameters": [
          {
            "in": "query",
            "name": "author",
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "is_approved",
            "schema": {
              "type": "boolean"
            }
          },
          {
            "description": "Which field to use when ordering the results.",
            "in": "query",
            "name": "ordering",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "A page number within the paginated result set.",
            "in": "query",
            "name": "page",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Number of results to return per page.",
            "in": "query",
            "name": "page_size",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "parent",
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "post",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Post slug for nested comments endpoint",
            "in": "path",
            "name": "post_slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedCommentList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "List comments",
        "tags": [
          "Blog - Comments"
        ]
      },
      "post": {
        "description": "Create a new comment",
        "operationId": "blog_comments_create",
        "parameters": [
          {
            "description": "Post slug for nested comments endpoint",
            "in": "path",
            "name": "post_slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Comment"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Create comment",
        "tags": [
          "Blog - Comments"
        ]
      }
    },
    "/blog/comments/{id}/": {
      "delete": {
        "description": "Delete a comment",
        "operationId": "blog_comments_destroy",
        "parameters": [
          {
            "description": "A unique integer value identifying this Comment.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "type": "integer"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Delete comment",
        "tags": [
          "Blog - Comments"
        ]
      },
      "get": {
        "description": "Get details of a specific comment",
        "operationId": "blog_comments_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Comment.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "type": "integer"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Comment"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get comment",
        "tags": [
          "Blog - Comments"
        ]
      },
      "patch": {
        "description": "Partially update comment content",
        "operationId": "blog_comments_partial_update",
        "parameters": [
          {
            "description": "A unique integer value identifying this Comment.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "type": "integer"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PatchedCommentRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PatchedCommentRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PatchedCommentRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Comment"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Partially update comment",
        "tags": [
          "Blog - Comments"
        ]
      },
      "put": {
        "description": "Update comment content",
        "operationId": "blog_comments_update",
        "parameters": [
          {
            "description": "A unique integer value identifying this Comment.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "type": "integer"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Comment"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Update comment",
        "tags": [
          "Blog - Comments"
        ]
      }
    },
    "/blog/posts/": {
      "get": {
        "description": "Get a paginated list of blog posts",
        "operationId": "blog_posts_list",
        "parameters": [
          {
            "in": "query",
            "name": "author",
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "category",
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "is_featured",
            "schema": {
              "type": "boolean"
            }
          },
          {
            "description": "Which field to use when ordering the results.",
            "in": "query",
            "name": "ordering",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "A page number within the paginated result set.",
            "in": "query",
            "name": "page",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Number of results to return per page.",
            "in": "query",
            "name": "page_size",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "A search term.",
            "in": "query",
            "name": "search",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "in": "query",
            "name": "status",
            "schema": {
              "enum": [
                "archived",
                "draft",
                "published"
              ],
              "type": "string",
              "x-spec-enum-id": "3999cf41a064d13a"
            }
          },
          {
            "explode": true,
            "in": "query",
            "name": "tags",
            "schema": {
              "items": {
                "type": "integer"
              },
              "type": "array"
            },
            "style": "form"
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedPostListList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "List posts",
        "tags": [
          "Blog - Posts"
        ]
      },
      "post": {
        "description": "Create a new blog post",
        "operationId": "blog_posts_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PostCreateRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PostCreateRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PostCreateRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PostCreate"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Create post",
        "tags": [
          "Blog - Posts"
        ]
      }
    },
    "/blog/posts/featured/": {
      "get": {
        "description": "Get featured blog posts",
        "operationId": "blog_posts_featured_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PostDetail"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get featured posts",
        "tags": [
          "Blog - Posts"
        ]
      }
    },
    "/blog/posts/stats/": {
      "get": {
        "description": "Get comprehensive blog statistics",
        "operationId": "blog_posts_stats_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/BlogStats"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get blog statistics",
        "tags": [
          "Blog - Posts"
        ]
      }
    },
    "/blog/posts/{post_slug}/comments/": {
      "get": {
        "description": "Get a list of comments",
        "operationId": "blog_posts_comments_list",
        "parameters": [
          {
            "in": "query",
            "name": "author",
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "is_approved",
            "schema": {
              "type": "boolean"
            }
          },
          {
            "description": "Which field to use when ordering the results.",
            "in": "query",
            "name": "ordering",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "A page number within the paginated result set.",
            "in": "query",
            "name": "page",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Number of results to return per page.",
            "in": "query",
            "name": "page_size",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "parent",
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "post",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Post slug for nested comments endpoint",
            "in": "path",
            "name": "post_slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedCommentList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "List comments",
        "tags": [
          "Blog - Comments"
        ]
      },
      "post": {
        "description": "Create a new comment",
        "operationId": "blog_posts_comments_create",
        "parameters": [
          {
            "description": "Post slug for nested comments endpoint",
            "in": "path",
            "name": "post_slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Comment"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Create comment",
        "tags": [
          "Blog - Comments"
        ]
      }
    },
    "/blog/posts/{post_slug}/comments/{id}/": {
      "delete": {
        "description": "Delete a comment",
        "operationId": "blog_posts_comments_destroy",
        "parameters": [
          {
            "description": "A unique integer value identifying this Comment.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "path",
            "name": "post_slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Delete comment",
        "tags": [
          "Blog - Comments"
        ]
      },
      "get": {
        "description": "Get details of a specific comment",
        "operationId": "blog_posts_comments_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Comment.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "path",
            "name": "post_slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Comment"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get comment",
        "tags": [
          "Blog - Comments"
        ]
      },
      "patch": {
        "description": "Partially update comment content",
        "operationId": "blog_posts_comments_partial_update",
        "parameters": [
          {
            "description": "A unique integer value identifying this Comment.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "path",
            "name": "post_slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PatchedCommentRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PatchedCommentRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PatchedCommentRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Comment"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Partially update comment",
        "tags": [
          "Blog - Comments"
        ]
      },
      "put": {
        "description": "Update comment content",
        "operationId": "blog_posts_comments_update",
        "parameters": [
          {
            "description": "A unique integer value identifying this Comment.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "path",
            "name": "post_slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CommentRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Comment"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Update comment",
        "tags": [
          "Blog - Comments"
        ]
      }
    },
    "/blog/posts/{slug}/": {
      "delete": {
        "description": "Delete a blog post",
        "operationId": "blog_posts_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Delete post",
        "tags": [
          "Blog - Posts"
        ]
      },
      "get": {
        "description": "Get detailed information about a specific post",
        "operationId": "blog_posts_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PostDetail"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get post",
        "tags": [
          "Blog - Posts"
        ]
      },
      "patch": {
        "description": "ViewSet for blog posts.",
        "operationId": "blog_posts_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PatchedPostUpdateRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PatchedPostUpdateRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PatchedPostUpdateRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PostUpdate"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "blog"
        ]
      },
      "put": {
        "description": "Update post information",
        "operationId": "blog_posts_update",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PostUpdateRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PostUpdateRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PostUpdateRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PostUpdate"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Update post",
        "tags": [
          "Blog - Posts"
        ]
      }
    },
    "/blog/posts/{slug}/like/": {
      "post": {
        "description": "Toggle like status for a post",
        "operationId": "blog_posts_like_create",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PostDetailRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PostDetailRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PostDetailRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PostDetail"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Like/unlike post",
        "tags": [
          "Blog - Posts"
        ]
      }
    },
    "/blog/posts/{slug}/likes/": {
      "get": {
        "description": "Get all likes for a post",
        "operationId": "blog_posts_likes_list",
        "parameters": [
          {
            "in": "query",
            "name": "author",
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "category",
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "is_featured",
            "schema": {
              "type": "boolean"
            }
          },
          {
            "description": "Which field to use when ordering the results.",
            "in": "query",
            "name": "ordering",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "A page number within the paginated result set.",
            "in": "query",
            "name": "page",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Number of results to return per page.",
            "in": "query",
            "name": "page_size",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "A search term.",
            "in": "query",
            "name": "search",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "* `draft` - Draft\n* `published` - Published\n* `archived` - Archived",
            "in": "query",
            "name": "status",
            "schema": {
              "enum": [
                "archived",
                "draft",
                "published"
              ],
              "type": "string",
              "x-spec-enum-id": "3999cf41a064d13a"
            }
          },
          {
            "explode": true,
            "in": "query",
            "name": "tags",
            "schema": {
              "items": {
                "type": "integer"
              },
              "type": "array"
            },
            "style": "form"
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedPostLikeList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get post likes",
        "tags": [
          "Blog - Posts"
        ]
      }
    },
    "/blog/tags/": {
      "get": {
        "description": "Get a list of all blog tags",
        "operationId": "blog_tags_list",
        "parameters": [
          {
            "description": "Which field to use when ordering the results.",
            "in": "query",
            "name": "ordering",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "A page number within the paginated result set.",
            "in": "query",
            "name": "page",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Number of results to return per page.",
            "in": "query",
            "name": "page_size",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "A search term.",
            "in": "query",
            "name": "search",
            "required": false,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedTagList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "List tags",
        "tags": [
          "Blog - Tags"
        ]
      },
      "post": {
        "description": "Create a new blog tag",
        "operationId": "blog_tags_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/TagRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/TagRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/TagRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Tag"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Create tag",
        "tags": [
          "Blog - Tags"
        ]
      }
    },
    "/blog/tags/{slug}/": {
      "delete": {
        "description": "ViewSet for blog tags.",
        "operationId": "blog_tags_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "blog"
        ]
      },
      "get": {
        "description": "ViewSet for blog tags.",
        "operationId": "blog_tags_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Tag"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "tags": [
          "blog"
        ]
      },
      "patch": {
        "description": "ViewSet for blog tags.",
        "operationId": "blog_tags_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PatchedTagRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PatchedTagRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PatchedTagRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Tag"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "blog"
        ]
      },
      "put": {
        "description": "ViewSet for blog tags.",
        "operationId": "blog_tags_update",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/TagRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/TagRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/TagRequest"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Tag"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "blog"
        ]
      }
    },
    "/shop/categories/": {
      "get": {
        "description": "Get a list of all shop categories",
        "operationId": "shop_categories_list",
        "parameters": [
          {
            "description": "Which field to use when ordering the results.",
            "in": "query",
            "name": "ordering",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "A page number within the paginated result set.",
            "in": "query",
            "name": "page",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Number of results to return per page.",
            "in": "query",
            "name": "page_size",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "A search term.",
            "in": "query",
            "name": "search",
            "required": false,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedShopCategoryList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "List categories",
        "tags": [
          "Shop - Categories"
        ]
      }
    },
    "/shop/categories/{slug}/": {
      "get": {
        "description": "Get details of a specific category",
        "operationId": "shop_categories_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ShopCategory"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get category",
        "tags": [
          "Shop - Categories"
        ]
      }
    },
    "/shop/orders/": {
      "get": {
        "description": "Get a list of orders (admin only)",
        "operationId": "shop_orders_list",
        "parameters": [
          {
            "in": "query",
            "name": "customer",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Which field to use when ordering the results.",
            "in": "query",
            "name": "ordering",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "A page number within the paginated result set.",
            "in": "query",
            "name": "page",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Number of results to return per page.",
            "in": "query",
            "name": "page_size",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "A search term.",
            "in": "query",
            "name": "search",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "* `pending` - Pending\n* `processing` - Processing\n* `shipped` - Shipped\n* `delivered` - Delivered\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
            "in": "query",
            "name": "status",
            "schema": {
              "enum": [
                "cancelled",
                "delivered",
                "pending",
                "processing",
                "refunded",
                "shipped"
              ],
              "type": "string",
              "x-spec-enum-id": "a98f61c8de1ef65b"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedOrderListList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "List orders",
        "tags": [
          "Shop - Orders"
        ]
      }
    },
    "/shop/orders/{id}/": {
      "get": {
        "description": "Get details of a specific order",
        "operationId": "shop_orders_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Order.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "type": "integer"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/OrderDetail"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Get order",
        "tags": [
          "Shop - Orders"
        ]
      }
    },
    "/shop/products/": {
      "get": {
        "description": "Get a paginated list of products",
        "operationId": "shop_products_list",
        "parameters": [
          {
            "in": "query",
            "name": "category",
            "schema": {
              "type": "integer"
            }
          },
          {
            "in": "query",
            "name": "is_digital",
            "schema": {
              "type": "boolean"
            }
          },
          {
            "in": "query",
            "name": "is_featured",
            "schema": {
              "type": "boolean"
            }
          },
          {
            "description": "Which field to use when ordering the results.",
            "in": "query",
            "name": "ordering",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "A page number within the paginated result set.",
            "in": "query",
            "name": "page",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Number of results to return per page.",
            "in": "query",
            "name": "page_size",
            "required": false,
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "A search term.",
            "in": "query",
            "name": "search",
            "required": false,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "* `active` - Active\n* `inactive` - Inactive\n* `out_of_stock` - Out of Stock",
            "in": "query",
            "name": "status",
            "schema": {
              "enum": [
                "active",
                "inactive",
                "out_of_stock"
              ],
              "type": "string",
              "x-spec-enum-id": "50e9f6640da1d7f3"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedProductListList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "List products",
        "tags": [
          "Shop - Products"
        ]
      }
    },
    "/shop/products/featured/": {
      "get": {
        "description": "Get featured products",
        "operationId": "shop_products_featured_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ProductDetail"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get featured products",
        "tags": [
          "Shop - Products"
        ]
      }
    },
    "/shop/products/stats/": {
      "get": {
        "description": "Get comprehensive shop statistics",
        "operationId": "shop_products_stats_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ShopStats"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get shop statistics",
        "tags": [
          "Shop - Products"
        ]
      }
    },
    "/shop/products/{slug}/": {
      "get": {
        "description": "Get detailed information about a specific product",
        "operationId": "shop_products_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "slug",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ProductDetail"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Get product",
        "tags": [
          "Shop - Products"
        ]
      }
    }
  }
};