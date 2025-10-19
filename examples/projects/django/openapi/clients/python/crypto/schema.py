"""
OpenAPI Schema

This file contains the complete OpenAPI specification for this API.
It can be used for documentation, validation, or code generation.
"""

from typing import Any, Dict

OPENAPI_SCHEMA: Dict[str, Any] = {
    "openapi": "3.0.3",
    "info": {
        "title": "Django CFG API",
        "version": "1.0.0",
        "description": "Complete API documentation for Django CFG Demo Project",
        "x-django-metadata": {
            "group": "crypto",
            "apps": [
                "crypto"
            ],
            "generator": "django-client",
            "generator_version": "1.0.0"
        }
    },
    "paths": {
        "/api/crypto/coins/": {
            "get": {
                "operationId": "crypto_coins_list",
                "description": "ViewSet for cryptocurrency coins.",
                "summary": "List coins",
                "parameters": [
                    {
                        "name": "page",
                        "required": False,
                        "in": "query",
                        "description": "A page number within the paginated result set.",
                        "schema": {
                            "type": "integer"
                        }
                    },
                    {
                        "name": "page_size",
                        "required": False,
                        "in": "query",
                        "description": "Number of results to return per page.",
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "tags": [
                    "crypto"
                ],
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    },
                    {}
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
                "x-async-capable": False
            }
        },
        "/api/crypto/coins/{id}/": {
            "get": {
                "operationId": "crypto_coins_retrieve",
                "description": "ViewSet for cryptocurrency coins.",
                "summary": "Get coin details",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Coin.",
                        "required": True
                    }
                ],
                "tags": [
                    "crypto"
                ],
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    },
                    {}
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
                "x-async-capable": False
            }
        },
        "/api/crypto/coins/stats/": {
            "get": {
                "operationId": "crypto_coins_stats_retrieve",
                "description": "Get cryptocurrency statistics.",
                "summary": "Get coin statistics",
                "tags": [
                    "crypto"
                ],
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    },
                    {}
                ],
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
                "x-async-capable": False
            }
        },
        "/api/crypto/exchanges/": {
            "get": {
                "operationId": "crypto_exchanges_list",
                "description": "ViewSet for cryptocurrency exchanges.",
                "summary": "List exchanges",
                "parameters": [
                    {
                        "name": "page",
                        "required": False,
                        "in": "query",
                        "description": "A page number within the paginated result set.",
                        "schema": {
                            "type": "integer"
                        }
                    },
                    {
                        "name": "page_size",
                        "required": False,
                        "in": "query",
                        "description": "Number of results to return per page.",
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "tags": [
                    "crypto"
                ],
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    },
                    {}
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
                "x-async-capable": False
            }
        },
        "/api/crypto/exchanges/{slug}/": {
            "get": {
                "operationId": "crypto_exchanges_retrieve",
                "description": "ViewSet for cryptocurrency exchanges.",
                "summary": "Get exchange details",
                "parameters": [
                    {
                        "in": "path",
                        "name": "slug",
                        "schema": {
                            "type": "string"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "crypto"
                ],
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    },
                    {}
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
                "x-async-capable": False
            }
        },
        "/api/crypto/wallets/": {
            "get": {
                "operationId": "crypto_wallets_list",
                "description": "ViewSet for user wallets.",
                "summary": "List wallets",
                "parameters": [
                    {
                        "name": "page",
                        "required": False,
                        "in": "query",
                        "description": "A page number within the paginated result set.",
                        "schema": {
                            "type": "integer"
                        }
                    },
                    {
                        "name": "page_size",
                        "required": False,
                        "in": "query",
                        "description": "Number of results to return per page.",
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "tags": [
                    "crypto"
                ],
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
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
                "x-async-capable": False
            }
        },
        "/api/crypto/wallets/{id}/": {
            "get": {
                "operationId": "crypto_wallets_retrieve",
                "description": "ViewSet for user wallets.",
                "summary": "Get wallet details",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "crypto"
                ],
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
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
                "x-async-capable": False
            }
        }
    },
    "components": {
        "schemas": {
            "Coin": {
                "type": "object",
                "description": "Serializer for coins.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "symbol": {
                        "type": "string",
                        "description": "Coin symbol (e.g., BTC, ETH)",
                        "maxLength": 10
                    },
                    "name": {
                        "type": "string",
                        "description": "Full name (e.g., Bitcoin, Ethereum)",
                        "maxLength": 100
                    },
                    "slug": {
                        "type": "string",
                        "maxLength": 100,
                        "pattern": "^[-a-zA-Z0-9_]+$"
                    },
                    "current_price_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "description": "Current price in USD"
                    },
                    "market_cap_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
                        "description": "Market capitalization"
                    },
                    "volume_24h_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
                        "description": "24h trading volume"
                    },
                    "price_change_24h_percent": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$"
                    },
                    "price_change_7d_percent": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$"
                    },
                    "price_change_30d_percent": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$"
                    },
                    "logo_url": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string"
                    },
                    "website": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "whitepaper_url": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "rank": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Market cap rank"
                    },
                    "is_active": {
                        "type": "boolean"
                    },
                    "is_tradeable": {
                        "type": "boolean"
                    },
                    "is_price_up_24h": {
                        "type": "boolean",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
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
                ]
            },
            "CoinList": {
                "type": "object",
                "description": "Lightweight serializer for coin lists.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "symbol": {
                        "type": "string",
                        "description": "Coin symbol (e.g., BTC, ETH)",
                        "maxLength": 10
                    },
                    "name": {
                        "type": "string",
                        "description": "Full name (e.g., Bitcoin, Ethereum)",
                        "maxLength": 100
                    },
                    "slug": {
                        "type": "string",
                        "maxLength": 100,
                        "pattern": "^[-a-zA-Z0-9_]+$"
                    },
                    "current_price_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "description": "Current price in USD"
                    },
                    "market_cap_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
                        "description": "Market capitalization"
                    },
                    "price_change_24h_percent": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$"
                    },
                    "logo_url": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "rank": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Market cap rank"
                    },
                    "is_price_up_24h": {
                        "type": "boolean",
                        "readOnly": True
                    }
                },
                "required": [
                    "id",
                    "is_price_up_24h",
                    "name",
                    "slug",
                    "symbol"
                ]
            },
            "CoinStats": {
                "type": "object",
                "description": "Serializer for coin statistics.",
                "properties": {
                    "total_coins": {
                        "type": "integer"
                    },
                    "total_market_cap_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$"
                    },
                    "total_volume_24h_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$"
                    },
                    "trending_coins": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/CoinList"
                        }
                    }
                },
                "required": [
                    "total_coins",
                    "total_market_cap_usd",
                    "total_volume_24h_usd",
                    "trending_coins"
                ]
            },
            "Exchange": {
                "type": "object",
                "description": "Serializer for exchanges.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "name": {
                        "type": "string",
                        "description": "Exchange name",
                        "maxLength": 100
                    },
                    "slug": {
                        "type": "string",
                        "maxLength": 100,
                        "pattern": "^[-a-zA-Z0-9_]+$"
                    },
                    "code": {
                        "type": "string",
                        "description": "Exchange code (e.g., BINANCE, COINBASE)",
                        "maxLength": 20
                    },
                    "description": {
                        "type": "string"
                    },
                    "website": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "logo_url": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "volume_24h_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
                        "description": "24h trading volume"
                    },
                    "num_markets": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Number of trading pairs"
                    },
                    "num_coins": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Number of supported coins"
                    },
                    "maker_fee_percent": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,1}(?:\\.\\d{0,4})?$"
                    },
                    "taker_fee_percent": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,1}(?:\\.\\d{0,4})?$"
                    },
                    "is_active": {
                        "type": "boolean"
                    },
                    "is_verified": {
                        "type": "boolean"
                    },
                    "supports_api": {
                        "type": "boolean"
                    },
                    "rank": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Exchange rank by volume"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    }
                },
                "required": [
                    "code",
                    "created_at",
                    "id",
                    "name",
                    "slug",
                    "updated_at"
                ]
            },
            "PaginatedCoinListList": {
                "type": "object",
                "required": [
                    "count",
                    "page",
                    "pages",
                    "page_size",
                    "has_next",
                    "has_previous",
                    "results"
                ],
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Total number of items across all pages",
                        "example": 150
                    },
                    "page": {
                        "type": "integer",
                        "description": "Current page number (1-based)",
                        "example": 2
                    },
                    "pages": {
                        "type": "integer",
                        "description": "Total number of pages",
                        "example": 15
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of items per page",
                        "example": 10
                    },
                    "has_next": {
                        "type": "boolean",
                        "description": "Whether there is a next page",
                        "example": True
                    },
                    "has_previous": {
                        "type": "boolean",
                        "description": "Whether there is a previous page",
                        "example": True
                    },
                    "next_page": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Next page number (None if no next page)",
                        "example": 3
                    },
                    "previous_page": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Previous page number (None if no previous page)",
                        "example": 1
                    },
                    "results": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/CoinList"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedExchangeList": {
                "type": "object",
                "required": [
                    "count",
                    "page",
                    "pages",
                    "page_size",
                    "has_next",
                    "has_previous",
                    "results"
                ],
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Total number of items across all pages",
                        "example": 150
                    },
                    "page": {
                        "type": "integer",
                        "description": "Current page number (1-based)",
                        "example": 2
                    },
                    "pages": {
                        "type": "integer",
                        "description": "Total number of pages",
                        "example": 15
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of items per page",
                        "example": 10
                    },
                    "has_next": {
                        "type": "boolean",
                        "description": "Whether there is a next page",
                        "example": True
                    },
                    "has_previous": {
                        "type": "boolean",
                        "description": "Whether there is a previous page",
                        "example": True
                    },
                    "next_page": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Next page number (None if no next page)",
                        "example": 3
                    },
                    "previous_page": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Previous page number (None if no previous page)",
                        "example": 1
                    },
                    "results": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Exchange"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedWalletList": {
                "type": "object",
                "required": [
                    "count",
                    "page",
                    "pages",
                    "page_size",
                    "has_next",
                    "has_previous",
                    "results"
                ],
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Total number of items across all pages",
                        "example": 150
                    },
                    "page": {
                        "type": "integer",
                        "description": "Current page number (1-based)",
                        "example": 2
                    },
                    "pages": {
                        "type": "integer",
                        "description": "Total number of pages",
                        "example": 15
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of items per page",
                        "example": 10
                    },
                    "has_next": {
                        "type": "boolean",
                        "description": "Whether there is a next page",
                        "example": True
                    },
                    "has_previous": {
                        "type": "boolean",
                        "description": "Whether there is a previous page",
                        "example": True
                    },
                    "next_page": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Next page number (None if no next page)",
                        "example": 3
                    },
                    "previous_page": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Previous page number (None if no previous page)",
                        "example": 1
                    },
                    "results": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Wallet"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "Wallet": {
                "type": "object",
                "description": "Serializer for wallets.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "user": {
                        "type": "integer",
                        "readOnly": True
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
                        "readOnly": True
                    },
                    "balance": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "description": "Available balance"
                    },
                    "locked_balance": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "readOnly": True,
                        "description": "Locked balance (in orders)"
                    },
                    "total_balance": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "readOnly": True
                    },
                    "value_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "readOnly": True
                    },
                    "address": {
                        "type": "string",
                        "description": "Deposit address",
                        "maxLength": 200
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
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
                ]
            }
        },
        "securitySchemes": {
            "cookieAuth": {
                "type": "apiKey",
                "in": "cookie",
                "name": "sessionid"
            },
            "jwtAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    }
}

__all__ = ["OPENAPI_SCHEMA"]