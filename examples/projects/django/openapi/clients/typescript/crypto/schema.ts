/**
 * OpenAPI Schema Export
 *
 * Contains the complete OpenAPI specification for runtime access.
 */

export const OPENAPI_SCHEMA = {
  "components": {
    "schemas": {
      "Coin": {
        "description": "Serializer for coins.",
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "current_price_usd": {
            "description": "Current price in USD",
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_active": {
            "type": "boolean"
          },
          "is_price_up_24h": {
            "readOnly": true,
            "type": "boolean"
          },
          "is_tradeable": {
            "type": "boolean"
          },
          "logo_url": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          },
          "market_cap_usd": {
            "description": "Market capitalization",
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "name": {
            "description": "Full name (e.g., Bitcoin, Ethereum)",
            "maxLength": 100,
            "type": "string"
          },
          "price_change_24h_percent": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "price_change_30d_percent": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "price_change_7d_percent": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "rank": {
            "description": "Market cap rank",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "slug": {
            "maxLength": 100,
            "pattern": "^[-a-zA-Z0-9_]+$",
            "type": "string"
          },
          "symbol": {
            "description": "Coin symbol (e.g., BTC, ETH)",
            "maxLength": 10,
            "type": "string"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "volume_24h_usd": {
            "description": "24h trading volume",
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "website": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          },
          "whitepaper_url": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          }
        },
        "required": [
          "created_at",
          "id",
          "is_price_up_24h",
          "name",
          "slug",
          "symbol",
          "updated_at"
        ],
        "type": "object"
      },
      "CoinList": {
        "description": "Lightweight serializer for coin lists.",
        "properties": {
          "current_price_usd": {
            "description": "Current price in USD",
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_price_up_24h": {
            "readOnly": true,
            "type": "boolean"
          },
          "logo_url": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          },
          "market_cap_usd": {
            "description": "Market capitalization",
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "name": {
            "description": "Full name (e.g., Bitcoin, Ethereum)",
            "maxLength": 100,
            "type": "string"
          },
          "price_change_24h_percent": {
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "rank": {
            "description": "Market cap rank",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "slug": {
            "maxLength": 100,
            "pattern": "^[-a-zA-Z0-9_]+$",
            "type": "string"
          },
          "symbol": {
            "description": "Coin symbol (e.g., BTC, ETH)",
            "maxLength": 10,
            "type": "string"
          }
        },
        "required": [
          "id",
          "is_price_up_24h",
          "name",
          "slug",
          "symbol"
        ],
        "type": "object"
      },
      "CoinStats": {
        "description": "Serializer for coin statistics.",
        "properties": {
          "total_coins": {
            "type": "integer"
          },
          "total_market_cap_usd": {
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "total_volume_24h_usd": {
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "trending_coins": {
            "items": {
              "$ref": "#/components/schemas/CoinList"
            },
            "type": "array"
          }
        },
        "required": [
          "total_coins",
          "total_market_cap_usd",
          "total_volume_24h_usd",
          "trending_coins"
        ],
        "type": "object"
      },
      "Exchange": {
        "description": "Serializer for exchanges.",
        "properties": {
          "code": {
            "description": "Exchange code (e.g., BINANCE, COINBASE)",
            "maxLength": 20,
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
          "is_active": {
            "type": "boolean"
          },
          "is_verified": {
            "type": "boolean"
          },
          "logo_url": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          },
          "maker_fee_percent": {
            "format": "decimal",
            "pattern": "^-?\\d{0,1}(?:\\.\\d{0,4})?$",
            "type": "string"
          },
          "name": {
            "description": "Exchange name",
            "maxLength": 100,
            "type": "string"
          },
          "num_coins": {
            "description": "Number of supported coins",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "num_markets": {
            "description": "Number of trading pairs",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "rank": {
            "description": "Exchange rank by volume",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "slug": {
            "maxLength": 100,
            "pattern": "^[-a-zA-Z0-9_]+$",
            "type": "string"
          },
          "supports_api": {
            "type": "boolean"
          },
          "taker_fee_percent": {
            "format": "decimal",
            "pattern": "^-?\\d{0,1}(?:\\.\\d{0,4})?$",
            "type": "string"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "volume_24h_usd": {
            "description": "24h trading volume",
            "format": "decimal",
            "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
            "type": "string"
          },
          "website": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          }
        },
        "required": [
          "code",
          "created_at",
          "id",
          "name",
          "slug",
          "updated_at"
        ],
        "type": "object"
      },
      "PaginatedCoinListList": {
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
              "$ref": "#/components/schemas/CoinList"
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
      "PaginatedExchangeList": {
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
              "$ref": "#/components/schemas/Exchange"
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
      "PaginatedWalletList": {
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
              "$ref": "#/components/schemas/Wallet"
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
      "Wallet": {
        "description": "Serializer for wallets.",
        "properties": {
          "address": {
            "description": "Deposit address",
            "maxLength": 200,
            "type": "string"
          },
          "balance": {
            "description": "Available balance",
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "type": "string"
          },
          "coin": {
            "type": "integer"
          },
          "coin_info": {
            "allOf": [
              {
                "$ref": "#/components/schemas/CoinList"
              }
            ],
            "readOnly": true
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
          "locked_balance": {
            "description": "Locked balance (in orders)",
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "readOnly": true,
            "type": "string"
          },
          "total_balance": {
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "readOnly": true,
            "type": "string"
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
          "value_usd": {
            "format": "decimal",
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "coin",
          "coin_info",
          "created_at",
          "id",
          "locked_balance",
          "total_balance",
          "updated_at",
          "user",
          "value_usd"
        ],
        "type": "object"
      }
    },
    "securitySchemes": {
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
        "crypto"
      ],
      "generator": "django-client",
      "generator_version": "1.0.0",
      "group": "crypto"
    }
  },
  "openapi": "3.0.3",
  "paths": {
    "/api/crypto/coins/": {
      "get": {
        "description": "ViewSet for cryptocurrency coins.",
        "operationId": "crypto_coins_list",
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
                  "$ref": "#/components/schemas/PaginatedCoinListList"
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
          {}
        ],
        "summary": "List coins",
        "tags": [
          "crypto"
        ],
        "x-async-capable": false
      }
    },
    "/api/crypto/coins/stats/": {
      "get": {
        "description": "Get cryptocurrency statistics.",
        "operationId": "crypto_coins_stats_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CoinStats"
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
          {}
        ],
        "summary": "Get coin statistics",
        "tags": [
          "crypto"
        ],
        "x-async-capable": false
      }
    },
    "/api/crypto/coins/{id}/": {
      "get": {
        "description": "ViewSet for cryptocurrency coins.",
        "operationId": "crypto_coins_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Coin.",
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
                  "$ref": "#/components/schemas/Coin"
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
          {}
        ],
        "summary": "Get coin details",
        "tags": [
          "crypto"
        ],
        "x-async-capable": false
      }
    },
    "/api/crypto/exchanges/": {
      "get": {
        "description": "ViewSet for cryptocurrency exchanges.",
        "operationId": "crypto_exchanges_list",
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
                  "$ref": "#/components/schemas/PaginatedExchangeList"
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
          {}
        ],
        "summary": "List exchanges",
        "tags": [
          "crypto"
        ],
        "x-async-capable": false
      }
    },
    "/api/crypto/exchanges/{slug}/": {
      "get": {
        "description": "ViewSet for cryptocurrency exchanges.",
        "operationId": "crypto_exchanges_retrieve",
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
                  "$ref": "#/components/schemas/Exchange"
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
          {}
        ],
        "summary": "Get exchange details",
        "tags": [
          "crypto"
        ],
        "x-async-capable": false
      }
    },
    "/api/crypto/wallets/": {
      "get": {
        "description": "ViewSet for user wallets.",
        "operationId": "crypto_wallets_list",
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
                  "$ref": "#/components/schemas/PaginatedWalletList"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "List wallets",
        "tags": [
          "crypto"
        ],
        "x-async-capable": false
      }
    },
    "/api/crypto/wallets/{id}/": {
      "get": {
        "description": "ViewSet for user wallets.",
        "operationId": "crypto_wallets_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
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
                  "$ref": "#/components/schemas/Wallet"
                }
              }
            },
            "description": ""
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Get wallet details",
        "tags": [
          "crypto"
        ],
        "x-async-capable": false
      }
    }
  }
};