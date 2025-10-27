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
            "group": "trading",
            "apps": [
                "trading"
            ],
            "generator": "django-client",
            "generator_version": "1.0.0"
        }
    },
    "paths": {
        "/api/trading/orders/": {
            "get": {
                "operationId": "trading_orders_list",
                "description": "ViewSet for trading orders.",
                "summary": "List orders",
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
                    "trading"
                ],
                "security": [
                    {
                        "jwtAuth": []
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
                "x-async-capable": False
            },
            "post": {
                "operationId": "trading_orders_create",
                "description": "ViewSet for trading orders.",
                "summary": "Create order",
                "tags": [
                    "trading"
                ],
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
                    "required": True
                },
                "security": [
                    {
                        "jwtAuth": []
                    }
                ],
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
                "x-async-capable": False
            }
        },
        "/api/trading/orders/{id}/": {
            "get": {
                "operationId": "trading_orders_retrieve",
                "description": "ViewSet for trading orders.",
                "summary": "Get order",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Order.",
                        "required": True
                    }
                ],
                "tags": [
                    "trading"
                ],
                "security": [
                    {
                        "jwtAuth": []
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
                "x-async-capable": False
            },
            "put": {
                "operationId": "trading_orders_update",
                "description": "ViewSet for trading orders.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Order.",
                        "required": True
                    }
                ],
                "tags": [
                    "trading"
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
                    "required": True
                },
                "security": [
                    {
                        "jwtAuth": []
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
                "x-async-capable": False
            },
            "patch": {
                "operationId": "trading_orders_partial_update",
                "description": "ViewSet for trading orders.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Order.",
                        "required": True
                    }
                ],
                "tags": [
                    "trading"
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
                "security": [
                    {
                        "jwtAuth": []
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
                "x-async-capable": False
            },
            "delete": {
                "operationId": "trading_orders_destroy",
                "description": "ViewSet for trading orders.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Order.",
                        "required": True
                    }
                ],
                "tags": [
                    "trading"
                ],
                "security": [
                    {
                        "jwtAuth": []
                    }
                ],
                "responses": {
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/api/trading/portfolios/": {
            "get": {
                "operationId": "trading_portfolios_list",
                "description": "ViewSet for trading portfolios.",
                "summary": "List portfolios",
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
                    "trading"
                ],
                "security": [
                    {
                        "jwtAuth": []
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
                "x-async-capable": False
            }
        },
        "/api/trading/portfolios/{id}/": {
            "get": {
                "operationId": "trading_portfolios_retrieve",
                "description": "ViewSet for trading portfolios.",
                "summary": "Get portfolio",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Portfolio.",
                        "required": True
                    }
                ],
                "tags": [
                    "trading"
                ],
                "security": [
                    {
                        "jwtAuth": []
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
                "x-async-capable": False
            }
        },
        "/api/trading/portfolios/me/": {
            "get": {
                "operationId": "trading_portfolios_me_retrieve",
                "description": "Get current user's portfolio.",
                "summary": "Get my portfolio",
                "tags": [
                    "trading"
                ],
                "security": [
                    {
                        "jwtAuth": []
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
                "x-async-capable": False
            }
        },
        "/api/trading/portfolios/stats/": {
            "get": {
                "operationId": "trading_portfolios_stats_retrieve",
                "description": "Get portfolio statistics.",
                "summary": "Get portfolio statistics",
                "tags": [
                    "trading"
                ],
                "security": [
                    {
                        "jwtAuth": []
                    }
                ],
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
                "x-async-capable": False
            }
        }
    },
    "components": {
        "schemas": {
            "Order": {
                "type": "object",
                "description": "Serializer for orders.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "portfolio": {
                        "type": "integer"
                    },
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair (e.g., BTC/USDT)",
                        "maxLength": 20
                    },
                    "order_type": {
                        "enum": [
                            "market",
                            "limit",
                            "stop_loss"
                        ],
                        "type": "string",
                        "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
                        "x-spec-enum-id": "7ae341549edd1dc5"
                    },
                    "side": {
                        "enum": [
                            "buy",
                            "sell"
                        ],
                        "type": "string",
                        "description": "* `buy` - Buy\n* `sell` - Sell",
                        "x-spec-enum-id": "920814eb0ee9f573"
                    },
                    "quantity": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$"
                    },
                    "price": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "nullable": True
                    },
                    "filled_quantity": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "readOnly": True
                    },
                    "status": {
                        "enum": [
                            "pending",
                            "filled",
                            "cancelled"
                        ],
                        "type": "string",
                        "description": "* `pending` - Pending\n* `filled` - Filled\n* `cancelled` - Cancelled",
                        "x-spec-enum-id": "7146ae5d4fbefc4c",
                        "readOnly": True
                    },
                    "total_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
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
                    "filled_quantity",
                    "id",
                    "portfolio",
                    "quantity",
                    "side",
                    "status",
                    "symbol",
                    "total_usd",
                    "updated_at"
                ]
            },
            "OrderCreate": {
                "type": "object",
                "description": "Serializer for creating orders.",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair (e.g., BTC/USDT)",
                        "maxLength": 20
                    },
                    "order_type": {
                        "enum": [
                            "market",
                            "limit",
                            "stop_loss"
                        ],
                        "type": "string",
                        "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
                        "x-spec-enum-id": "7ae341549edd1dc5"
                    },
                    "side": {
                        "enum": [
                            "buy",
                            "sell"
                        ],
                        "type": "string",
                        "description": "* `buy` - Buy\n* `sell` - Sell",
                        "x-spec-enum-id": "920814eb0ee9f573"
                    },
                    "quantity": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$"
                    },
                    "price": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "nullable": True
                    }
                },
                "required": [
                    "quantity",
                    "side",
                    "symbol"
                ]
            },
            "OrderCreateRequest": {
                "type": "object",
                "description": "Serializer for creating orders.",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Trading pair (e.g., BTC/USDT)",
                        "maxLength": 20
                    },
                    "order_type": {
                        "enum": [
                            "market",
                            "limit",
                            "stop_loss"
                        ],
                        "type": "string",
                        "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
                        "x-spec-enum-id": "7ae341549edd1dc5"
                    },
                    "side": {
                        "enum": [
                            "buy",
                            "sell"
                        ],
                        "type": "string",
                        "description": "* `buy` - Buy\n* `sell` - Sell",
                        "x-spec-enum-id": "920814eb0ee9f573"
                    },
                    "quantity": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$"
                    },
                    "price": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "nullable": True
                    }
                },
                "required": [
                    "quantity",
                    "side",
                    "symbol"
                ]
            },
            "OrderRequest": {
                "type": "object",
                "description": "Serializer for orders.",
                "properties": {
                    "portfolio": {
                        "type": "integer"
                    },
                    "symbol": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Trading pair (e.g., BTC/USDT)",
                        "maxLength": 20
                    },
                    "order_type": {
                        "enum": [
                            "market",
                            "limit",
                            "stop_loss"
                        ],
                        "type": "string",
                        "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
                        "x-spec-enum-id": "7ae341549edd1dc5"
                    },
                    "side": {
                        "enum": [
                            "buy",
                            "sell"
                        ],
                        "type": "string",
                        "description": "* `buy` - Buy\n* `sell` - Sell",
                        "x-spec-enum-id": "920814eb0ee9f573"
                    },
                    "quantity": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$"
                    },
                    "price": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "nullable": True
                    }
                },
                "required": [
                    "portfolio",
                    "quantity",
                    "side",
                    "symbol"
                ]
            },
            "PaginatedOrderList": {
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
                            "$ref": "#/components/schemas/Order"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedPortfolioList": {
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
                            "$ref": "#/components/schemas/Portfolio"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PatchedOrderRequest": {
                "type": "object",
                "description": "Serializer for orders.",
                "properties": {
                    "portfolio": {
                        "type": "integer"
                    },
                    "symbol": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Trading pair (e.g., BTC/USDT)",
                        "maxLength": 20
                    },
                    "order_type": {
                        "enum": [
                            "market",
                            "limit",
                            "stop_loss"
                        ],
                        "type": "string",
                        "description": "* `market` - Market\n* `limit` - Limit\n* `stop_loss` - Stop Loss",
                        "x-spec-enum-id": "7ae341549edd1dc5"
                    },
                    "side": {
                        "enum": [
                            "buy",
                            "sell"
                        ],
                        "type": "string",
                        "description": "* `buy` - Buy\n* `sell` - Sell",
                        "x-spec-enum-id": "920814eb0ee9f573"
                    },
                    "quantity": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$"
                    },
                    "price": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "nullable": True
                    }
                }
            },
            "Portfolio": {
                "type": "object",
                "description": "Serializer for trading portfolios.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "user": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "user_info": {
                        "type": "object",
                        "additionalProperties": {},
                        "readOnly": True
                    },
                    "total_balance_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "description": "Total portfolio value in USD"
                    },
                    "available_balance_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
                        "description": "Available balance for trading"
                    },
                    "total_profit_loss": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$",
                        "readOnly": True
                    },
                    "total_trades": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "winning_trades": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "losing_trades": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "win_rate": {
                        "type": "number",
                        "format": "double",
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
                    "losing_trades",
                    "total_balance_usd",
                    "total_profit_loss",
                    "total_trades",
                    "updated_at",
                    "user",
                    "user_info",
                    "win_rate",
                    "winning_trades"
                ]
            },
            "PortfolioStats": {
                "type": "object",
                "description": "Serializer for portfolio statistics.",
                "properties": {
                    "total_portfolios": {
                        "type": "integer"
                    },
                    "total_volume_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,18}(?:\\.\\d{0,2})?$"
                    },
                    "total_orders": {
                        "type": "integer"
                    }
                },
                "required": [
                    "total_orders",
                    "total_portfolios",
                    "total_volume_usd"
                ]
            }
        },
        "securitySchemes": {
            "jwtAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    }
}

__all__ = ["OPENAPI_SCHEMA"]