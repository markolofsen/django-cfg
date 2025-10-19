/**
 * OpenAPI Schema Export
 *
 * Contains the complete OpenAPI specification for runtime access.
 */

export const OPENAPI_SCHEMA = {
  "components": {
    "schemas": {
      "Order": {
        "description": "Serializer for orders.",
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "filled_quantity": {
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "order_type": {
            "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
            "enum": [
              "market",
              "limit",
              "stop_loss"
            ],
            "type": "string",
            "x-spec-enum-id": "7ae341549edd1dc5"
          },
          "portfolio": {
            "type": "integer"
          },
          "price": {
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "quantity": {
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "side": {
            "description": "* `buy` - Buy\n* `sell` - Sell",
            "enum": [
              "buy",
              "sell"
            ],
            "type": "string",
            "x-spec-enum-id": "920814eb0ee9f573"
          },
          "status": {
            "description": "* `pending` - Pending\n* `filled` - Filled\n* `cancelled` - Cancelled",
            "enum": [
              "pending",
              "filled",
              "cancelled"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "7146ae5d4fbefc4c"
          },
          "symbol": {
            "description": "Trading pair (e.g., BTC/USDT)",
            "maxLength": 20,
            "type": "string"
          },
          "total_usd": {
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
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
          "created_at",
          "filled_quantity",
          "id",
          "portfolio",
          "quantity",
          "side",
          "status",
          "symbol",
          "total_usd",
          "updated_at"
        ],
        "type": "object"
      },
      "OrderCreate": {
        "description": "Serializer for creating orders.",
        "properties": {
          "order_type": {
            "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
            "enum": [
              "market",
              "limit",
              "stop_loss"
            ],
            "type": "string",
            "x-spec-enum-id": "7ae341549edd1dc5"
          },
          "price": {
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "quantity": {
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "side": {
            "description": "* `buy` - Buy\n* `sell` - Sell",
            "enum": [
              "buy",
              "sell"
            ],
            "type": "string",
            "x-spec-enum-id": "920814eb0ee9f573"
          },
          "symbol": {
            "description": "Trading pair (e.g., BTC/USDT)",
            "maxLength": 20,
            "type": "string"
          }
        },
        "required": [
          "quantity",
          "side",
          "symbol"
        ],
        "type": "object"
      },
      "OrderCreateRequest": {
        "description": "Serializer for creating orders.",
        "properties": {
          "order_type": {
            "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
            "enum": [
              "market",
              "limit",
              "stop_loss"
            ],
            "type": "string",
            "x-spec-enum-id": "7ae341549edd1dc5"
          },
          "price": {
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "quantity": {
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "side": {
            "description": "* `buy` - Buy\n* `sell` - Sell",
            "enum": [
              "buy",
              "sell"
            ],
            "type": "string",
            "x-spec-enum-id": "920814eb0ee9f573"
          },
          "symbol": {
            "description": "Trading pair (e.g., BTC/USDT)",
            "maxLength": 20,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "quantity",
          "side",
          "symbol"
        ],
        "type": "object"
      },
      "OrderRequest": {
        "description": "Serializer for orders.",
        "properties": {
          "order_type": {
            "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
            "enum": [
              "market",
              "limit",
              "stop_loss"
            ],
            "type": "string",
            "x-spec-enum-id": "7ae341549edd1dc5"
          },
          "portfolio": {
            "type": "integer"
          },
          "price": {
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "quantity": {
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "side": {
            "description": "* `buy` - Buy\n* `sell` - Sell",
            "enum": [
              "buy",
              "sell"
            ],
            "type": "string",
            "x-spec-enum-id": "920814eb0ee9f573"
          },
          "symbol": {
            "description": "Trading pair (e.g., BTC/USDT)",
            "maxLength": 20,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "portfolio",
          "quantity",
          "side",
          "symbol"
        ],
        "type": "object"
      },
      "PaginatedOrderList": {
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
              "$ref": "#/components/schemas/Order"
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
      "PaginatedPortfolioList": {
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
              "$ref": "#/components/schemas/Portfolio"
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
      "PatchedOrderRequest": {
        "description": "Serializer for orders.",
        "properties": {
          "order_type": {
            "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
            "enum": [
              "market",
              "limit",
              "stop_loss"
            ],
            "type": "string",
            "x-spec-enum-id": "7ae341549edd1dc5"
          },
          "portfolio": {
            "type": "integer"
          },
          "price": {
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "quantity": {
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "side": {
            "description": "* `buy` - Buy\n* `sell` - Sell",
            "enum": [
              "buy",
              "sell"
            ],
            "type": "string",
            "x-spec-enum-id": "920814eb0ee9f573"
          },
          "symbol": {
            "description": "Trading pair (e.g., BTC/USDT)",
            "maxLength": 20,
            "minLength": 1,
            "type": "string"
          }
        },
        "type": "object"
      },
      "Portfolio": {
        "description": "Serializer for trading portfolios.",
        "properties": {
          "available_balance_usd": {
            "description": "Available balance for trading",
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
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
          "losing_trades": {
            "readOnly": true,
            "type": "integer"
          },
          "total_balance_usd": {
            "description": "Total portfolio value in USD",
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "total_profit_loss": {
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "total_trades": {
            "readOnly": true,
            "type": "integer"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "user": {
            "readOnly": true,
            "type": "integer"
          },
          "user_info": {
            "additionalProperties": {},
            "readOnly": true,
            "type": "object"
          },
          "win_rate": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "winning_trades": {
            "readOnly": true,
            "type": "integer"
          }
        },
        "required": [
          "created_at",
          "id",
          "losing_trades",
          "total_balance_usd",
          "total_profit_loss",
          "total_trades",
          "updated_at",
          "user",
          "user_info",
          "win_rate",
          "winning_trades"
        ],
        "type": "object"
      },
      "PortfolioStats": {
        "description": "Serializer for portfolio statistics.",
        "properties": {
          "total_orders": {
            "type": "integer"
          },
          "total_portfolios": {
            "type": "integer"
          },
          "total_volume_usd": {
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
            "type": "string"
          }
        },
        "required": [
          "total_orders",
          "total_portfolios",
          "total_volume_usd"
        ],
        "type": "object"
      }
    },
    "securitySchemes": {
      "cookieAuth": {
        "in": "cookie",
        "name": "sessionid",
        "type": "apiKey"
      },
      "jwtAuth": {
        "bearerFormat": "JWT",
        "scheme": "bearer",
        "type": "http"
      }
    }
  },
  "info": {
    "description": "Complete API documentation for Django CFG Demo Project",
    "title": "Django CFG API",
    "version": "1.0.0",
    "x-django-metadata": {
      "apps": [
        "trading"
      ],
      "generator": "django-client",
      "generator_version": "1.0.0",
      "group": "trading"
    }
  },
  "openapi": "3.0.3",
  "paths": {
    "/api/trading/orders/": {
      "get": {
        "description": "ViewSet for trading orders.",
        "operationId": "trading_orders_list",
        "parameters": [
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
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedOrderList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "summary": "List orders",
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "ViewSet for trading orders.",
        "operationId": "trading_orders_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/OrderCreateRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/OrderCreateRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/OrderCreateRequest"
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
                  "$ref": "#/components/schemas/OrderCreate"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "summary": "Create order",
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      }
    },
    "/api/trading/orders/{id}/": {
      "delete": {
        "description": "ViewSet for trading orders.",
        "operationId": "trading_orders_destroy",
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
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "ViewSet for trading orders.",
        "operationId": "trading_orders_retrieve",
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
                  "$ref": "#/components/schemas/Order"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "summary": "Get order",
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "ViewSet for trading orders.",
        "operationId": "trading_orders_partial_update",
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
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PatchedOrderRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PatchedOrderRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PatchedOrderRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Order"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "ViewSet for trading orders.",
        "operationId": "trading_orders_update",
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
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/OrderRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/OrderRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/OrderRequest"
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
                  "$ref": "#/components/schemas/Order"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      }
    },
    "/api/trading/portfolios/": {
      "get": {
        "description": "ViewSet for trading portfolios.",
        "operationId": "trading_portfolios_list",
        "parameters": [
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
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PaginatedPortfolioList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "summary": "List portfolios",
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      }
    },
    "/api/trading/portfolios/me/": {
      "get": {
        "description": "Get current user\u0027s portfolio.",
        "operationId": "trading_portfolios_me_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Portfolio"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "summary": "Get my portfolio",
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      }
    },
    "/api/trading/portfolios/stats/": {
      "get": {
        "description": "Get portfolio statistics.",
        "operationId": "trading_portfolios_stats_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PortfolioStats"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "summary": "Get portfolio statistics",
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      }
    },
    "/api/trading/portfolios/{id}/": {
      "get": {
        "description": "ViewSet for trading portfolios.",
        "operationId": "trading_portfolios_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Portfolio.",
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
                  "$ref": "#/components/schemas/Portfolio"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {
            "cookieAuth": []
          }
        ],
        "summary": "Get portfolio",
        "tags": [
          "trading"
        ],
        "x-async-capable": false
      }
    }
  }
};