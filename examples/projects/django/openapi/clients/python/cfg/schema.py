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
            "group": "cfg",
            "apps": [
                "django_cfg_accounts",
                "django_cfg_knowbase",
                "django_cfg_support",
                "django_cfg_newsletter",
                "django_cfg_leads",
                "django_cfg_agents",
                "tasks",
                "payments"
            ],
            "generator": "django-client",
            "generator_version": "1.0.0"
        }
    },
    "paths": {
        "/cfg/accounts/otp/request/": {
            "post": {
                "operationId": "cfg_accounts_otp_request_create",
                "description": "Request OTP code to email or phone.",
                "tags": [
                    "accounts"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/OTPRequestRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/OTPRequestRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/OTPRequestRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/OTPRequestResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/OTPErrorResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "500": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/OTPErrorResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/accounts/otp/verify/": {
            "post": {
                "operationId": "cfg_accounts_otp_verify_create",
                "description": "Verify OTP code and return JWT tokens.",
                "tags": [
                    "accounts"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/OTPVerifyRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/OTPVerifyRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/OTPVerifyRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/OTPVerifyResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/OTPErrorResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "410": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/OTPErrorResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/accounts/profile/": {
            "get": {
                "operationId": "cfg_accounts_profile_retrieve",
                "description": "Retrieve the current authenticated user's profile information.",
                "summary": "Get current user profile",
                "tags": [
                    "User Profile"
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
                                    "$ref": "#/components/schemas/User"
                                }
                            }
                        },
                        "description": ""
                    },
                    "401": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Authentication credentials were not provided."
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/accounts/profile/avatar/": {
            "post": {
                "operationId": "cfg_accounts_profile_avatar_create",
                "description": "Upload avatar image for the current authenticated user. Accepts multipart/form-data with 'avatar' field.",
                "summary": "Upload user avatar",
                "tags": [
                    "User Profile"
                ],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "avatar": {
                                        "type": "string",
                                        "format": "binary",
                                        "description": "Avatar image file (JPEG, PNG, GIF, WebP, max 5MB)"
                                    }
                                },
                                "required": [
                                    "avatar"
                                ]
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/User"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Invalid file or validation error."
                                }
                            }
                        },
                        "description": ""
                    },
                    "401": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Authentication credentials were not provided."
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/accounts/profile/partial/": {
            "put": {
                "operationId": "cfg_accounts_profile_partial_update",
                "description": "Partially update the current authenticated user's profile information. Supports avatar upload.",
                "summary": "Partial update user profile",
                "tags": [
                    "User Profile"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileUpdateRequest"
                            },
                            "examples": {
                                "ProfileUpdateWithAvatar": {
                                    "value": {
                                        "first_name": "John",
                                        "last_name": "Doe",
                                        "company": "Tech Corp",
                                        "phone": "+1 (555) 123-4567",
                                        "position": "Software Engineer"
                                    },
                                    "summary": "Profile Update with Avatar"
                                }
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileUpdateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileUpdateRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/User"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Invalid data provided."
                                }
                            }
                        },
                        "description": ""
                    },
                    "401": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Authentication credentials were not provided."
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_accounts_profile_partial_partial_update",
                "description": "Partially update the current authenticated user's profile information. Supports avatar upload.",
                "summary": "Partial update user profile",
                "tags": [
                    "User Profile"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileUpdateRequest"
                            },
                            "examples": {
                                "ProfileUpdateWithAvatar": {
                                    "value": {
                                        "first_name": "John",
                                        "last_name": "Doe",
                                        "company": "Tech Corp",
                                        "phone": "+1 (555) 123-4567",
                                        "position": "Software Engineer"
                                    },
                                    "summary": "Profile Update with Avatar"
                                }
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileUpdateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileUpdateRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/User"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Invalid data provided."
                                }
                            }
                        },
                        "description": ""
                    },
                    "401": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Authentication credentials were not provided."
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/accounts/profile/update/": {
            "put": {
                "operationId": "cfg_accounts_profile_update_update",
                "description": "Update the current authenticated user's profile information.",
                "summary": "Update user profile",
                "tags": [
                    "User Profile"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileUpdateRequest"
                            },
                            "examples": {
                                "ValidProfileUpdate": {
                                    "value": {
                                        "first_name": "John",
                                        "last_name": "Doe",
                                        "company": "Tech Corp",
                                        "phone": "+1 (555) 123-4567",
                                        "position": "Software Engineer"
                                    },
                                    "summary": "Valid Profile Update"
                                }
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileUpdateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileUpdateRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/User"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Invalid data provided."
                                }
                            }
                        },
                        "description": ""
                    },
                    "401": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Authentication credentials were not provided."
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_accounts_profile_update_partial_update",
                "description": "Update the current authenticated user's profile information.",
                "summary": "Update user profile",
                "tags": [
                    "User Profile"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileUpdateRequest"
                            },
                            "examples": {
                                "ValidProfileUpdate": {
                                    "value": {
                                        "first_name": "John",
                                        "last_name": "Doe",
                                        "company": "Tech Corp",
                                        "phone": "+1 (555) 123-4567",
                                        "position": "Software Engineer"
                                    },
                                    "summary": "Valid Profile Update"
                                }
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileUpdateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileUpdateRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/User"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Invalid data provided."
                                }
                            }
                        },
                        "description": ""
                    },
                    "401": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "Authentication credentials were not provided."
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/accounts/token/refresh/": {
            "post": {
                "operationId": "cfg_accounts_token_refresh_create",
                "description": "Refresh JWT token.",
                "tags": [
                    "Auth"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/TokenRefreshRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/TokenRefreshRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/TokenRefreshRequest"
                            }
                        }
                    },
                    "required": True
                },
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/TokenRefresh"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/endpoints/drf/": {
            "get": {
                "operationId": "cfg_endpoints_drf_retrieve",
                "description": "Return endpoints status data.",
                "tags": [
                    "endpoints"
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
                                    "$ref": "#/components/schemas/EndpointsStatus"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/health/drf/": {
            "get": {
                "operationId": "cfg_health_drf_retrieve",
                "description": "Return comprehensive health check data.",
                "tags": [
                    "health"
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
                                    "$ref": "#/components/schemas/HealthCheck"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/health/drf/quick/": {
            "get": {
                "operationId": "cfg_health_drf_quick_retrieve",
                "description": "Return minimal health status.",
                "tags": [
                    "health"
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
                                    "$ref": "#/components/schemas/QuickHealth"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/chat/": {
            "get": {
                "operationId": "cfg_knowbase_admin_chat_list",
                "description": "Chat query endpoints.",
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
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedChatResponseList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_knowbase_admin_chat_create",
                "description": "Chat query endpoints.",
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatResponseRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatResponseRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatResponseRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    }
                ],
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/chat/{id}/": {
            "get": {
                "operationId": "cfg_knowbase_admin_chat_retrieve",
                "description": "Chat query endpoints.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/ChatResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_knowbase_admin_chat_update",
                "description": "Chat query endpoints.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatResponseRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatResponseRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatResponseRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/ChatResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_knowbase_admin_chat_partial_update",
                "description": "Chat query endpoints.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedChatResponseRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedChatResponseRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedChatResponseRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_knowbase_admin_chat_destroy",
                "description": "Chat query endpoints.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/chat/{id}/history/": {
            "get": {
                "operationId": "cfg_knowbase_admin_chat_history_retrieve",
                "description": "Get chat session history.",
                "summary": "Get chat history",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/ChatHistory"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/chat/query/": {
            "post": {
                "operationId": "cfg_knowbase_admin_chat_query_create",
                "description": "Process chat query with RAG context.",
                "summary": "Process chat query with RAG",
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatQueryRequest"
                            },
                            "examples": {
                                "SimpleQuery": {
                                    "value": {
                                        "query": "What is machine learning?",
                                        "max_tokens": 1000,
                                        "include_sources": True
                                    },
                                    "summary": "Simple Query"
                                }
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatQueryRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatQueryRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/ChatResponse"
                                },
                                "examples": {
                                    "SimpleQuery": {
                                        "value": {
                                            "query": "What is machine learning?",
                                            "max_tokens": 1000,
                                            "include_sources": True
                                        },
                                        "summary": "Simple Query"
                                    }
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/documents/": {
            "get": {
                "operationId": "cfg_knowbase_admin_documents_list",
                "description": "List user documents with filtering and pagination.",
                "summary": "List user documents",
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
                    },
                    {
                        "in": "query",
                        "name": "status",
                        "schema": {
                            "type": "string"
                        },
                        "description": "Filter by processing status"
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedDocumentList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_knowbase_admin_documents_create",
                "description": "Upload and process a new knowledge document",
                "summary": "Upload new document",
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentCreateRequest"
                            },
                            "examples": {
                                "TextDocument": {
                                    "value": {
                                        "title": "API Documentation",
                                        "content": "# API Guide\n\nThis guide explains...",
                                        "file_type": "text/markdown"
                                    },
                                    "summary": "Text Document"
                                }
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentCreateRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    }
                ],
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Document"
                                },
                                "examples": {
                                    "TextDocument": {
                                        "value": {
                                            "title": "API Documentation",
                                            "content": "# API Guide\n\nThis guide explains...",
                                            "file_type": "text/markdown"
                                        },
                                        "summary": "Text Document"
                                    }
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "description": "Validation errors"
                    },
                    "413": {
                        "description": "File too large"
                    },
                    "429": {
                        "description": "Rate limit exceeded"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/documents/{id}/": {
            "get": {
                "operationId": "cfg_knowbase_admin_documents_retrieve",
                "description": "Get document by ID.",
                "summary": "Get document details",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this document.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/Document"
                                }
                            }
                        },
                        "description": ""
                    },
                    "404": {
                        "description": "Document not found"
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_knowbase_admin_documents_update",
                "description": "Document management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this document.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/Document"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_knowbase_admin_documents_partial_update",
                "description": "Document management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this document.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedDocumentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedDocumentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedDocumentRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Document"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_knowbase_admin_documents_destroy",
                "description": "Delete document and all associated chunks.",
                "summary": "Delete document",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this document.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                    "204": {
                        "description": "Document deleted successfully"
                    },
                    "404": {
                        "description": "Document not found"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/documents/{id}/reprocess/": {
            "post": {
                "operationId": "cfg_knowbase_admin_documents_reprocess_create",
                "description": "Trigger reprocessing of document chunks and embeddings",
                "summary": "Reprocess document",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this document.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/Document"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/documents/{id}/status/": {
            "get": {
                "operationId": "cfg_knowbase_admin_documents_status_retrieve",
                "description": "Get document processing status.",
                "summary": "Get document processing status",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this document.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/DocumentProcessingStatus"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/documents/stats/": {
            "get": {
                "operationId": "cfg_knowbase_admin_documents_stats_retrieve",
                "description": "Get user's document processing statistics.",
                "summary": "Get processing statistics",
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/DocumentStats"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/sessions/": {
            "get": {
                "operationId": "cfg_knowbase_admin_sessions_list",
                "description": "List user chat sessions with filtering.",
                "summary": "List user chat sessions",
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
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedChatSessionList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_knowbase_admin_sessions_create",
                "description": "Create new chat session.",
                "summary": "Create new chat session",
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionCreateRequest"
                            }
                        }
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
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatSession"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/sessions/{id}/": {
            "get": {
                "operationId": "cfg_knowbase_admin_sessions_retrieve",
                "description": "Chat session management endpoints.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/ChatSession"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_knowbase_admin_sessions_update",
                "description": "Chat session management endpoints.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatSession"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_knowbase_admin_sessions_partial_update",
                "description": "Chat session management endpoints.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedChatSessionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedChatSessionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedChatSessionRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatSession"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_knowbase_admin_sessions_destroy",
                "description": "Chat session management endpoints.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/sessions/{id}/activate/": {
            "post": {
                "operationId": "cfg_knowbase_admin_sessions_activate_create",
                "description": "Activate chat session.",
                "summary": "Activate chat session",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatSession"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/admin/sessions/{id}/archive/": {
            "post": {
                "operationId": "cfg_knowbase_admin_sessions_archive_create",
                "description": "Archive (deactivate) chat session.",
                "summary": "Archive chat session",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this chat session.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatSessionRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatSession"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/categories/": {
            "get": {
                "operationId": "cfg_knowbase_categories_list",
                "description": "Get list of all public categories",
                "summary": "List public categories",
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
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedPublicCategoryList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/categories/{id}/": {
            "get": {
                "operationId": "cfg_knowbase_categories_retrieve",
                "description": "Get category details by ID (public access)",
                "summary": "Get public category details",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Document Category.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PublicCategory"
                                }
                            }
                        },
                        "description": ""
                    },
                    "404": {
                        "description": "Category not found"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/documents/": {
            "get": {
                "operationId": "cfg_knowbase_documents_list",
                "description": "Get list of all completed and publicly accessible documents",
                "summary": "List public documents",
                "parameters": [
                    {
                        "in": "query",
                        "name": "category",
                        "schema": {
                            "type": "string"
                        },
                        "description": "Filter by category name"
                    },
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
                    },
                    {
                        "in": "query",
                        "name": "search",
                        "schema": {
                            "type": "string"
                        },
                        "description": "Search in title and content"
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedPublicDocumentListList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/documents/{id}/": {
            "get": {
                "operationId": "cfg_knowbase_documents_retrieve",
                "description": "Get document details by ID (public access)",
                "summary": "Get public document details",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this document.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PublicDocument"
                                }
                            }
                        },
                        "description": ""
                    },
                    "404": {
                        "description": "Document not found"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/archives/": {
            "get": {
                "operationId": "cfg_knowbase_system_archives_list",
                "description": "Document archive management endpoints - Admin only.",
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
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedDocumentArchiveListList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_knowbase_system_archives_create",
                "description": "Upload archive file and process it synchronously",
                "summary": "Upload and process archive",
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {
                                        "type": "string",
                                        "format": "binary"
                                    },
                                    "title": {
                                        "type": "string"
                                    },
                                    "description": {
                                        "type": "string"
                                    },
                                    "category_ids": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "is_public": {
                                        "type": "boolean"
                                    },
                                    "process_immediately": {
                                        "type": "boolean"
                                    }
                                }
                            }
                        }
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
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ArchiveProcessingResult"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "description": "Validation errors"
                    },
                    "413": {
                        "description": "File too large"
                    },
                    "429": {
                        "description": "Rate limit exceeded"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/archives/{id}/": {
            "get": {
                "operationId": "cfg_knowbase_system_archives_retrieve",
                "description": "Document archive management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Document Archive.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/DocumentArchiveDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_knowbase_system_archives_update",
                "description": "Document archive management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Document Archive.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentArchiveRequest"
                            }
                        },
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/DocumentArchiveRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/DocumentArchive"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_knowbase_system_archives_partial_update",
                "description": "Document archive management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Document Archive.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedDocumentArchiveRequest"
                            }
                        },
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedDocumentArchiveRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/DocumentArchive"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_knowbase_system_archives_destroy",
                "description": "Document archive management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Document Archive.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/archives/{id}/file_tree/": {
            "get": {
                "operationId": "cfg_knowbase_system_archives_file_tree_retrieve",
                "description": "Get hierarchical file tree structure",
                "summary": "Get archive file tree",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Document Archive.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "type": "object"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/archives/{id}/items/": {
            "get": {
                "operationId": "cfg_knowbase_system_archives_items_list",
                "description": "Get all items in the archive",
                "summary": "Get archive items",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Document Archive.",
                        "required": True
                    },
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
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedArchiveItemList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/archives/{id}/search/": {
            "post": {
                "operationId": "cfg_knowbase_system_archives_search_create",
                "description": "Semantic search within archive chunks",
                "summary": "Search archive chunks",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Document Archive.",
                        "required": True
                    },
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
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveSearchRequestRequest"
                            }
                        },
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveSearchRequestRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/PaginatedArchiveSearchResultList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/archives/revectorize/": {
            "post": {
                "operationId": "cfg_knowbase_system_archives_revectorize_create",
                "description": "Re-vectorize specific chunks",
                "summary": "Re-vectorize chunks",
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ChunkRevectorizationRequestRequest"
                            }
                        },
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChunkRevectorizationRequestRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/VectorizationResult"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/archives/statistics/": {
            "get": {
                "operationId": "cfg_knowbase_system_archives_statistics_retrieve",
                "description": "Get processing and vectorization statistics",
                "summary": "Get archive statistics",
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/ArchiveStatistics"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/archives/vectorization_stats/": {
            "get": {
                "operationId": "cfg_knowbase_system_archives_vectorization_stats_retrieve",
                "description": "Get vectorization statistics for archives",
                "summary": "Get vectorization statistics",
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/VectorizationStatistics"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/chunks/": {
            "get": {
                "operationId": "cfg_knowbase_system_chunks_list",
                "description": "Archive item chunk management endpoints - Admin only.",
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
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedArchiveItemChunkList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_knowbase_system_chunks_create",
                "description": "Archive item chunk management endpoints - Admin only.",
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemChunkRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemChunkRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemChunkRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    }
                ],
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ArchiveItemChunk"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/chunks/{id}/": {
            "get": {
                "operationId": "cfg_knowbase_system_chunks_retrieve",
                "description": "Archive item chunk management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item Chunk.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/ArchiveItemChunkDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_knowbase_system_chunks_update",
                "description": "Archive item chunk management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item Chunk.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemChunkRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemChunkRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemChunkRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/ArchiveItemChunk"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_knowbase_system_chunks_partial_update",
                "description": "Archive item chunk management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item Chunk.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedArchiveItemChunkRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedArchiveItemChunkRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedArchiveItemChunkRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ArchiveItemChunk"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_knowbase_system_chunks_destroy",
                "description": "Archive item chunk management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item Chunk.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/chunks/{id}/context/": {
            "get": {
                "operationId": "cfg_knowbase_system_chunks_context_retrieve",
                "description": "Get full context metadata for chunk",
                "summary": "Get chunk context",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item Chunk.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/ArchiveItemChunkDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/chunks/{id}/vectorize/": {
            "post": {
                "operationId": "cfg_knowbase_system_chunks_vectorize_create",
                "description": "Generate embedding for specific chunk",
                "summary": "Vectorize chunk",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item Chunk.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemChunkRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemChunkRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemChunkRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "type": "object"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/items/": {
            "get": {
                "operationId": "cfg_knowbase_system_items_list",
                "description": "Archive item management endpoints - Admin only.",
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
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedArchiveItemList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_knowbase_system_items_create",
                "description": "Archive item management endpoints - Admin only.",
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    }
                ],
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ArchiveItem"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/items/{id}/": {
            "get": {
                "operationId": "cfg_knowbase_system_items_retrieve",
                "description": "Archive item management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/ArchiveItemDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_knowbase_system_items_update",
                "description": "Archive item management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/ArchiveItemRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/ArchiveItem"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_knowbase_system_items_partial_update",
                "description": "Archive item management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedArchiveItemRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedArchiveItemRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedArchiveItemRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ArchiveItem"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_knowbase_system_items_destroy",
                "description": "Archive item management endpoints - Admin only.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/items/{id}/chunks/": {
            "get": {
                "operationId": "cfg_knowbase_system_items_chunks_list",
                "description": "Get all chunks for this item",
                "summary": "Get item chunks",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item.",
                        "required": True
                    },
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
                    "knowbase"
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
                                    "$ref": "#/components/schemas/PaginatedArchiveItemChunkList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/knowbase/system/items/{id}/content/": {
            "get": {
                "operationId": "cfg_knowbase_system_items_content_retrieve",
                "description": "Get full content of archive item",
                "summary": "Get item content",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this Archive Item.",
                        "required": True
                    }
                ],
                "tags": [
                    "knowbase"
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
                                    "$ref": "#/components/schemas/ArchiveItemDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/leads/": {
            "get": {
                "operationId": "cfg_leads_list",
                "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
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
                    "leads"
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
                                    "$ref": "#/components/schemas/PaginatedLeadSubmissionList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_leads_create",
                "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
                "tags": [
                    "leads"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/LeadSubmissionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/LeadSubmissionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/LeadSubmissionRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LeadSubmission"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/leads/{id}/": {
            "get": {
                "operationId": "cfg_leads_retrieve",
                "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Lead.",
                        "required": True
                    }
                ],
                "tags": [
                    "leads"
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
                                    "$ref": "#/components/schemas/LeadSubmission"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_leads_update",
                "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Lead.",
                        "required": True
                    }
                ],
                "tags": [
                    "leads"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/LeadSubmissionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/LeadSubmissionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/LeadSubmissionRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/LeadSubmission"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_leads_partial_update",
                "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Lead.",
                        "required": True
                    }
                ],
                "tags": [
                    "leads"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedLeadSubmissionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedLeadSubmissionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedLeadSubmissionRequest"
                            }
                        }
                    }
                },
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
                                    "$ref": "#/components/schemas/LeadSubmission"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_leads_destroy",
                "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Lead.",
                        "required": True
                    }
                ],
                "tags": [
                    "leads"
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
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/leads/submit/": {
            "post": {
                "operationId": "cfg_leads_submit_create",
                "description": "Submit a new lead from frontend contact form with automatic Telegram notifications.",
                "summary": "Submit Lead Form",
                "tags": [
                    "Lead Submission"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/LeadSubmissionRequest"
                            },
                            "examples": {
                                "ContactFormSubmission": {
                                    "value": {
                                        "name": "John Doe",
                                        "email": "john@example.com",
                                        "company": "Tech Corp",
                                        "company_site": "https://techcorp.com",
                                        "contact_type": "email",
                                        "contact_value": "john@example.com",
                                        "subject": "Partnership Inquiry",
                                        "message": "I'm interested in discussing a potential partnership.",
                                        "site_url": "https://mysite.com/contact"
                                    },
                                    "summary": "Contact Form Submission"
                                }
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/LeadSubmissionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/LeadSubmissionRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LeadSubmissionResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LeadSubmissionError"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/bulk/": {
            "post": {
                "operationId": "cfg_newsletter_bulk_create",
                "description": "Send bulk emails to multiple recipients using base email template.",
                "summary": "Send Bulk Email",
                "tags": [
                    "Bulk Email"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/BulkEmailRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/BulkEmailRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/BulkEmailRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/BulkEmailResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/BulkEmailResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/campaigns/": {
            "get": {
                "operationId": "cfg_newsletter_campaigns_list",
                "description": "Get a list of all newsletter campaigns.",
                "summary": "List Newsletter Campaigns",
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
                    "Campaigns"
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
                                    "$ref": "#/components/schemas/PaginatedNewsletterCampaignList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_newsletter_campaigns_create",
                "description": "Create a new newsletter campaign.",
                "summary": "Create Newsletter Campaign",
                "tags": [
                    "Campaigns"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/NewsletterCampaignRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/NewsletterCampaignRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/NewsletterCampaignRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    }
                ],
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/NewsletterCampaign"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/campaigns/{id}/": {
            "get": {
                "operationId": "cfg_newsletter_campaigns_retrieve",
                "description": "Retrieve details of a specific newsletter campaign.",
                "summary": "Get Campaign Details",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "Campaigns"
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
                                    "$ref": "#/components/schemas/NewsletterCampaign"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_newsletter_campaigns_update",
                "description": "Update a newsletter campaign.",
                "summary": "Update Campaign",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "Campaigns"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/NewsletterCampaignRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/NewsletterCampaignRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/NewsletterCampaignRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/NewsletterCampaign"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_newsletter_campaigns_partial_update",
                "description": "Retrieve, update, or delete a newsletter campaign.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "newsletter"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedNewsletterCampaignRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedNewsletterCampaignRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedNewsletterCampaignRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/NewsletterCampaign"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_newsletter_campaigns_destroy",
                "description": "Delete a newsletter campaign.",
                "summary": "Delete Campaign",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "Campaigns"
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
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/campaigns/send/": {
            "post": {
                "operationId": "cfg_newsletter_campaigns_send_create",
                "description": "Send a newsletter campaign to all subscribers.",
                "summary": "Send Newsletter Campaign",
                "tags": [
                    "Campaigns"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SendCampaignRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SendCampaignRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SendCampaignRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/SendCampaignResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "404": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/logs/": {
            "get": {
                "operationId": "cfg_newsletter_logs_list",
                "description": "Get a list of email sending logs.",
                "summary": "List Email Logs",
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
                    "Logs"
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
                                    "$ref": "#/components/schemas/PaginatedEmailLogList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/newsletters/": {
            "get": {
                "operationId": "cfg_newsletter_newsletters_list",
                "description": "Get a list of all active newsletters available for subscription.",
                "summary": "List Active Newsletters",
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
                    "Newsletters"
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
                                    "$ref": "#/components/schemas/PaginatedNewsletterList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/newsletters/{id}/": {
            "get": {
                "operationId": "cfg_newsletter_newsletters_retrieve",
                "description": "Retrieve details of a specific newsletter.",
                "summary": "Get Newsletter Details",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "Newsletters"
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
                                    "$ref": "#/components/schemas/Newsletter"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/subscribe/": {
            "post": {
                "operationId": "cfg_newsletter_subscribe_create",
                "description": "Subscribe an email address to a newsletter.",
                "summary": "Subscribe to Newsletter",
                "tags": [
                    "Subscriptions"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscribeRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscribeRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscribeRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SubscribeResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "404": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/subscriptions/": {
            "get": {
                "operationId": "cfg_newsletter_subscriptions_list",
                "description": "Get a list of current user's active newsletter subscriptions.",
                "summary": "List User Subscriptions",
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
                    "Subscriptions"
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
                                    "$ref": "#/components/schemas/PaginatedNewsletterSubscriptionList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/test/": {
            "post": {
                "operationId": "cfg_newsletter_test_create",
                "description": "Send a test email to verify mailer configuration.",
                "summary": "Test Email Sending",
                "tags": [
                    "Testing"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/TestEmailRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/TestEmailRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/TestEmailRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/BulkEmailResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "400": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/BulkEmailResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/newsletter/unsubscribe/": {
            "post": {
                "operationId": "cfg_newsletter_unsubscribe_create",
                "description": "Unsubscribe from a newsletter using subscription ID.",
                "summary": "Unsubscribe from Newsletter",
                "tags": [
                    "Subscriptions"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UnsubscribeRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/UnsubscribeRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/UnsubscribeRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/SuccessResponse"
                                }
                            }
                        },
                        "description": ""
                    },
                    "404": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_newsletter_unsubscribe_update",
                "description": "Handle newsletter unsubscriptions.",
                "tags": [
                    "newsletter"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UnsubscribeRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/UnsubscribeRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/UnsubscribeRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/Unsubscribe"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_newsletter_unsubscribe_partial_update",
                "description": "Handle newsletter unsubscriptions.",
                "tags": [
                    "newsletter"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUnsubscribeRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUnsubscribeRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUnsubscribeRequest"
                            }
                        }
                    }
                },
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
                                    "$ref": "#/components/schemas/Unsubscribe"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/payments/balance/": {
            "get": {
                "operationId": "cfg_payments_balance_retrieve",
                "description": "Get current user balance and transaction statistics",
                "summary": "Get user balance",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Balance"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/payments/currencies/": {
            "get": {
                "operationId": "cfg_payments_currencies_list",
                "description": "Returns list of available currencies with token+network info",
                "summary": "Get available currencies",
                "tags": [
                    "payments"
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
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/Currency"
                                    }
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/payments/payments/": {
            "get": {
                "operationId": "cfg_payments_payments_list",
                "description": "ViewSet for payment operations.\n\nEndpoints:\n- GET /payments/ - List user's payments\n- GET /payments/{id}/ - Get payment details\n- POST /payments/create/ - Create new payment\n- GET /payments/{id}/status/ - Check payment status\n- POST /payments/{id}/confirm/ - Confirm payment",
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
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedPaymentListList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/payments/payments/{id}/": {
            "get": {
                "operationId": "cfg_payments_payments_retrieve",
                "description": "ViewSet for payment operations.\n\nEndpoints:\n- GET /payments/ - List user's payments\n- GET /payments/{id}/ - Get payment details\n- POST /payments/create/ - Create new payment\n- GET /payments/{id}/status/ - Check payment status\n- POST /payments/{id}/confirm/ - Confirm payment",
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
                    "payments"
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
                                    "$ref": "#/components/schemas/PaymentDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/payments/payments/{id}/confirm/": {
            "post": {
                "operationId": "cfg_payments_payments_confirm_create",
                "description": "POST /api/v1/payments/{id}/confirm/\n\nConfirm payment (user clicked \"I have paid\").\nChecks status with provider and creates transaction if completed.",
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
                    "payments"
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
                                    "$ref": "#/components/schemas/PaymentList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/payments/payments/{id}/status/": {
            "get": {
                "operationId": "cfg_payments_payments_status_retrieve",
                "description": "GET /api/v1/payments/{id}/status/?refresh=True\n\nCheck payment status (with optional refresh from provider).\n\nQuery params:\n- refresh: boolean (default: False) - Force refresh from provider",
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
                    "payments"
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
                                    "$ref": "#/components/schemas/PaymentList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/payments/payments/create/": {
            "post": {
                "operationId": "cfg_payments_payments_create_create",
                "description": "POST /api/v1/payments/create/\n\nCreate new payment.\n\nRequest body:\n{\n    \"amount_usd\": \"100.00\",\n    \"currency_code\": \"USDTTRC20\",\n    \"description\": \"Optional description\"\n}",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaymentList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/payments/transactions/": {
            "get": {
                "operationId": "cfg_payments_transactions_list",
                "description": "Get user transactions with pagination and filtering",
                "summary": "Get user transactions",
                "parameters": [
                    {
                        "in": "query",
                        "name": "limit",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "Number of transactions to return (max 100)"
                    },
                    {
                        "in": "query",
                        "name": "offset",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "Offset for pagination"
                    },
                    {
                        "in": "query",
                        "name": "type",
                        "schema": {
                            "type": "string"
                        },
                        "description": "Filter by transaction type (deposit/withdrawal)"
                    }
                ],
                "tags": [
                    "payments"
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
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/Transaction"
                                    }
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/support/tickets/": {
            "get": {
                "operationId": "cfg_support_tickets_list",
                "description": "ViewSet for managing support tickets.",
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
                    "support"
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
                                    "$ref": "#/components/schemas/PaginatedTicketList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_support_tickets_create",
                "description": "ViewSet for managing support tickets.",
                "tags": [
                    "support"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/TicketRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/TicketRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/TicketRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    }
                ],
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Ticket"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/support/tickets/{ticket_uuid}/messages/": {
            "get": {
                "operationId": "cfg_support_tickets_messages_list",
                "description": "ViewSet for managing support messages.",
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
                    },
                    {
                        "in": "path",
                        "name": "ticket_uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the ticket",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
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
                                    "$ref": "#/components/schemas/PaginatedMessageList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "cfg_support_tickets_messages_create",
                "description": "ViewSet for managing support messages.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "ticket_uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the ticket",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/MessageCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/MessageCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/MessageCreateRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "jwtAuth": []
                    },
                    {
                        "cookieAuth": []
                    }
                ],
                "responses": {
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/MessageCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/support/tickets/{ticket_uuid}/messages/{uuid}/": {
            "get": {
                "operationId": "cfg_support_tickets_messages_retrieve",
                "description": "ViewSet for managing support messages.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "ticket_uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the ticket",
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the message",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
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
                                    "$ref": "#/components/schemas/Message"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_support_tickets_messages_update",
                "description": "ViewSet for managing support messages.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "ticket_uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the ticket",
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the message",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/MessageRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/MessageRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/MessageRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/Message"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_support_tickets_messages_partial_update",
                "description": "ViewSet for managing support messages.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "ticket_uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the ticket",
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the message",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedMessageRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedMessageRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedMessageRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Message"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_support_tickets_messages_destroy",
                "description": "ViewSet for managing support messages.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "ticket_uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the ticket",
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "UUID of the message",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
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
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/support/tickets/{uuid}/": {
            "get": {
                "operationId": "cfg_support_tickets_retrieve",
                "description": "ViewSet for managing support tickets.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this ticket.",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
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
                                    "$ref": "#/components/schemas/Ticket"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "cfg_support_tickets_update",
                "description": "ViewSet for managing support tickets.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this ticket.",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/TicketRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/TicketRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/TicketRequest"
                            }
                        }
                    },
                    "required": True
                },
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
                                    "$ref": "#/components/schemas/Ticket"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "cfg_support_tickets_partial_update",
                "description": "ViewSet for managing support tickets.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this ticket.",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedTicketRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedTicketRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedTicketRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Ticket"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "cfg_support_tickets_destroy",
                "description": "ViewSet for managing support tickets.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "uuid",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "A UUID string identifying this ticket.",
                        "required": True
                    }
                ],
                "tags": [
                    "support"
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
                    "204": {
                        "description": "No response body"
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/clear/": {
            "post": {
                "operationId": "cfg_tasks_api_clear_create",
                "description": "Clear all test data from Redis.",
                "tags": [
                    "tasks"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/clear-queues/": {
            "post": {
                "operationId": "cfg_tasks_api_clear_queues_create",
                "description": "Clear all tasks from all Dramatiq queues.",
                "tags": [
                    "tasks"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/purge-failed/": {
            "post": {
                "operationId": "cfg_tasks_api_purge_failed_create",
                "description": "Purge all failed tasks from queues.",
                "tags": [
                    "tasks"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/queues/manage/": {
            "post": {
                "operationId": "cfg_tasks_api_queues_manage_create",
                "description": "Manage queue operations (clear, purge, etc.).",
                "tags": [
                    "tasks"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/QueueActionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/QueueActionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/QueueActionRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/QueueAction"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/queues/status/": {
            "get": {
                "operationId": "cfg_tasks_api_queues_status_retrieve",
                "description": "Get current status of all queues.",
                "tags": [
                    "tasks"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/QueueStatus"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/simulate/": {
            "post": {
                "operationId": "cfg_tasks_api_simulate_create",
                "description": "Simulate test data for dashboard testing.",
                "tags": [
                    "tasks"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIResponseRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/tasks/list/": {
            "get": {
                "operationId": "cfg_tasks_api_tasks_list_retrieve",
                "description": "Get paginated task list with filtering.",
                "tags": [
                    "tasks"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/tasks/stats/": {
            "get": {
                "operationId": "cfg_tasks_api_tasks_stats_retrieve",
                "description": "Get task execution statistics.",
                "tags": [
                    "tasks"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/TaskStatistics"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/workers/list/": {
            "get": {
                "operationId": "cfg_tasks_api_workers_list_retrieve",
                "description": "Get detailed list of workers.",
                "tags": [
                    "tasks"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/cfg/tasks/api/workers/manage/": {
            "post": {
                "operationId": "cfg_tasks_api_workers_manage_create",
                "description": "Manage worker operations.",
                "tags": [
                    "tasks"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/WorkerActionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/WorkerActionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/WorkerActionRequest"
                            }
                        }
                    },
                    "required": True
                },
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/WorkerAction"
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
            "APIResponse": {
                "type": "object",
                "description": "Standard API response serializer.",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Operation success status"
                    },
                    "message": {
                        "type": "string",
                        "description": "Success message"
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message"
                    },
                    "data": {
                        "type": "object",
                        "additionalProperties": {},
                        "description": "Response data"
                    }
                },
                "required": [
                    "success"
                ]
            },
            "APIResponseRequest": {
                "type": "object",
                "description": "Standard API response serializer.",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Operation success status"
                    },
                    "message": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Success message"
                    },
                    "error": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Error message"
                    },
                    "data": {
                        "type": "object",
                        "additionalProperties": {},
                        "description": "Response data"
                    }
                },
                "required": [
                    "success"
                ]
            },
            "ArchiveItem": {
                "type": "object",
                "description": "Archive item serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "Path within archive",
                        "maxLength": 1024
                    },
                    "item_name": {
                        "type": "string",
                        "description": "Item name",
                        "maxLength": 255
                    },
                    "item_type": {
                        "type": "string",
                        "description": "MIME type",
                        "maxLength": 100
                    },
                    "content_type": {
                        "enum": [
                            "document",
                            "code",
                            "image",
                            "data",
                            "archive",
                            "unknown"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "e6657d144665c87e",
                        "readOnly": True,
                        "description": "Content classification\n\n* `document` - Document\n* `code` - Code\n* `image` - Image\n* `data` - Data\n* `archive` - Archive\n* `unknown` - Unknown"
                    },
                    "file_size": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Item size in bytes"
                    },
                    "is_processable": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether item can be processed for chunks"
                    },
                    "language": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Programming language or document language"
                    },
                    "encoding": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Character encoding"
                    },
                    "chunks_count": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Number of chunks created"
                    },
                    "total_tokens": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total tokens in all chunks"
                    },
                    "processing_cost": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Processing cost for this item"
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
                    "chunks_count",
                    "content_type",
                    "created_at",
                    "encoding",
                    "id",
                    "is_processable",
                    "item_name",
                    "item_type",
                    "language",
                    "processing_cost",
                    "relative_path",
                    "total_tokens",
                    "updated_at"
                ]
            },
            "ArchiveItemChunk": {
                "type": "object",
                "description": "Archive item chunk serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "content": {
                        "type": "string",
                        "description": "Chunk text content"
                    },
                    "chunk_index": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Sequential chunk number within item"
                    },
                    "chunk_type": {
                        "enum": [
                            "text",
                            "code",
                            "heading",
                            "metadata",
                            "table",
                            "list"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "660846bb1567d97b",
                        "description": "Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List"
                    },
                    "token_count": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Number of tokens in chunk"
                    },
                    "character_count": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Number of characters in chunk"
                    },
                    "embedding_model": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Model used for embedding generation"
                    },
                    "embedding_cost": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Cost in USD for embedding generation"
                    },
                    "context_summary": {
                        "type": "object",
                        "additionalProperties": {},
                        "description": "Get context summary for display.",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    }
                },
                "required": [
                    "character_count",
                    "chunk_index",
                    "content",
                    "context_summary",
                    "created_at",
                    "embedding_cost",
                    "embedding_model",
                    "id",
                    "token_count"
                ]
            },
            "ArchiveItemChunkDetail": {
                "type": "object",
                "description": "Detailed chunk serializer with full context.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "content": {
                        "type": "string",
                        "description": "Chunk text content"
                    },
                    "chunk_index": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Sequential chunk number within item"
                    },
                    "chunk_type": {
                        "enum": [
                            "text",
                            "code",
                            "heading",
                            "metadata",
                            "table",
                            "list"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "660846bb1567d97b",
                        "description": "Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List"
                    },
                    "token_count": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Number of tokens in chunk"
                    },
                    "character_count": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Number of characters in chunk"
                    },
                    "embedding_model": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Model used for embedding generation"
                    },
                    "embedding_cost": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Cost in USD for embedding generation"
                    },
                    "context_summary": {
                        "type": "object",
                        "additionalProperties": {},
                        "description": "Get context summary for display.",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "context_metadata": {
                        "readOnly": True
                    }
                },
                "required": [
                    "character_count",
                    "chunk_index",
                    "content",
                    "context_metadata",
                    "context_summary",
                    "created_at",
                    "embedding_cost",
                    "embedding_model",
                    "id",
                    "token_count"
                ]
            },
            "ArchiveItemChunkRequest": {
                "type": "object",
                "description": "Archive item chunk serializer.",
                "properties": {
                    "content": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Chunk text content"
                    },
                    "chunk_index": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Sequential chunk number within item"
                    },
                    "chunk_type": {
                        "enum": [
                            "text",
                            "code",
                            "heading",
                            "metadata",
                            "table",
                            "list"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "660846bb1567d97b",
                        "description": "Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List"
                    }
                },
                "required": [
                    "chunk_index",
                    "content"
                ]
            },
            "ArchiveItemDetail": {
                "type": "object",
                "description": "Detailed archive item serializer with content.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "Path within archive",
                        "maxLength": 1024
                    },
                    "item_name": {
                        "type": "string",
                        "description": "Item name",
                        "maxLength": 255
                    },
                    "item_type": {
                        "type": "string",
                        "description": "MIME type",
                        "maxLength": 100
                    },
                    "content_type": {
                        "enum": [
                            "document",
                            "code",
                            "image",
                            "data",
                            "archive",
                            "unknown"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "e6657d144665c87e",
                        "readOnly": True,
                        "description": "Content classification\n\n* `document` - Document\n* `code` - Code\n* `image` - Image\n* `data` - Data\n* `archive` - Archive\n* `unknown` - Unknown"
                    },
                    "file_size": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Item size in bytes"
                    },
                    "is_processable": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether item can be processed for chunks"
                    },
                    "language": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Programming language or document language"
                    },
                    "encoding": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Character encoding"
                    },
                    "chunks_count": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Number of chunks created"
                    },
                    "total_tokens": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total tokens in all chunks"
                    },
                    "processing_cost": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Processing cost for this item"
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
                    },
                    "raw_content": {
                        "type": "string",
                        "readOnly": True
                    },
                    "metadata": {
                        "readOnly": True
                    }
                },
                "required": [
                    "chunks_count",
                    "content_type",
                    "created_at",
                    "encoding",
                    "id",
                    "is_processable",
                    "item_name",
                    "item_type",
                    "language",
                    "metadata",
                    "processing_cost",
                    "raw_content",
                    "relative_path",
                    "total_tokens",
                    "updated_at"
                ]
            },
            "ArchiveItemRequest": {
                "type": "object",
                "description": "Archive item serializer.",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Path within archive",
                        "maxLength": 1024
                    },
                    "item_name": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Item name",
                        "maxLength": 255
                    },
                    "item_type": {
                        "type": "string",
                        "minLength": 1,
                        "description": "MIME type",
                        "maxLength": 100
                    },
                    "file_size": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Item size in bytes"
                    }
                },
                "required": [
                    "item_name",
                    "item_type",
                    "relative_path"
                ]
            },
            "ArchiveProcessingResult": {
                "type": "object",
                "description": "Archive processing result serializer.",
                "properties": {
                    "archive_id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "status": {
                        "type": "string",
                        "readOnly": True
                    },
                    "processing_time_ms": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "items_processed": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "chunks_created": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "vectorized_chunks": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_cost_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "error_message": {
                        "type": "string",
                        "readOnly": True
                    }
                },
                "required": [
                    "archive_id",
                    "chunks_created",
                    "error_message",
                    "items_processed",
                    "processing_time_ms",
                    "status",
                    "total_cost_usd",
                    "vectorized_chunks"
                ]
            },
            "ArchiveSearchRequestRequest": {
                "type": "object",
                "description": "Archive search request serializer.",
                "properties": {
                    "query": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Search query",
                        "maxLength": 500
                    },
                    "content_types": {
                        "type": "array",
                        "items": {
                            "enum": [
                                "document",
                                "code",
                                "image",
                                "data",
                                "archive",
                                "unknown"
                            ],
                            "type": "string",
                            "description": "* `document` - Document\n* `code` - Code\n* `image` - Image\n* `data` - Data\n* `archive` - Archive\n* `unknown` - Unknown",
                            "x-spec-enum-id": "e6657d144665c87e"
                        },
                        "description": "Filter by content types"
                    },
                    "languages": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": 50
                        },
                        "description": "Filter by programming languages"
                    },
                    "chunk_types": {
                        "type": "array",
                        "items": {
                            "enum": [
                                "text",
                                "code",
                                "heading",
                                "metadata",
                                "table",
                                "list"
                            ],
                            "type": "string",
                            "description": "* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List",
                            "x-spec-enum-id": "660846bb1567d97b"
                        },
                        "description": "Filter by chunk types"
                    },
                    "archive_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "Search within specific archives"
                    },
                    "limit": {
                        "type": "integer",
                        "maximum": 50,
                        "minimum": 1,
                        "default": 10,
                        "description": "Maximum number of results"
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "format": "double",
                        "maximum": 1.0,
                        "minimum": 0.0,
                        "default": 0.7,
                        "description": "Minimum similarity threshold"
                    }
                },
                "required": [
                    "query"
                ]
            },
            "ArchiveSearchResult": {
                "type": "object",
                "description": "Archive search result serializer.",
                "properties": {
                    "chunk": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/ArchiveItemChunk"
                            }
                        ],
                        "readOnly": True
                    },
                    "similarity_score": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "context_summary": {
                        "type": "object",
                        "additionalProperties": {},
                        "readOnly": True
                    },
                    "archive_info": {
                        "type": "object",
                        "additionalProperties": {},
                        "readOnly": True
                    },
                    "item_info": {
                        "type": "object",
                        "additionalProperties": {},
                        "readOnly": True
                    }
                },
                "required": [
                    "archive_info",
                    "chunk",
                    "context_summary",
                    "item_info",
                    "similarity_score"
                ]
            },
            "ArchiveStatistics": {
                "type": "object",
                "description": "Archive statistics serializer.",
                "properties": {
                    "total_archives": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "processed_archives": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "failed_archives": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_items": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_chunks": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_tokens": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_cost": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "avg_processing_time": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "avg_items_per_archive": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "avg_chunks_per_archive": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    }
                },
                "required": [
                    "avg_chunks_per_archive",
                    "avg_items_per_archive",
                    "avg_processing_time",
                    "failed_archives",
                    "processed_archives",
                    "total_archives",
                    "total_chunks",
                    "total_cost",
                    "total_items",
                    "total_tokens"
                ]
            },
            "Balance": {
                "type": "object",
                "description": "User balance serializer.",
                "properties": {
                    "balance_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "description": "Current balance in USD"
                    },
                    "balance_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "total_deposited": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "description": "Total amount deposited (lifetime)"
                    },
                    "total_withdrawn": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "description": "Total amount withdrawn (lifetime)"
                    },
                    "last_transaction_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When the last transaction occurred"
                    }
                },
                "required": [
                    "balance_display",
                    "balance_usd",
                    "last_transaction_at",
                    "total_deposited",
                    "total_withdrawn"
                ]
            },
            "BulkEmailRequest": {
                "type": "object",
                "description": "Simple serializer for bulk email.",
                "properties": {
                    "recipients": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "email",
                            "minLength": 1
                        },
                        "maxItems": 100,
                        "minItems": 1
                    },
                    "subject": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255
                    },
                    "email_title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255
                    },
                    "main_text": {
                        "type": "string",
                        "minLength": 1
                    },
                    "main_html_content": {
                        "type": "string"
                    },
                    "button_text": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "button_url": {
                        "type": "string",
                        "format": "uri"
                    },
                    "secondary_text": {
                        "type": "string"
                    }
                },
                "required": [
                    "email_title",
                    "main_text",
                    "recipients",
                    "subject"
                ]
            },
            "BulkEmailResponse": {
                "type": "object",
                "description": "Response for bulk email sending.",
                "properties": {
                    "success": {
                        "type": "boolean"
                    },
                    "sent_count": {
                        "type": "integer"
                    },
                    "failed_count": {
                        "type": "integer"
                    },
                    "total_recipients": {
                        "type": "integer"
                    },
                    "error": {
                        "type": "string"
                    }
                },
                "required": [
                    "failed_count",
                    "sent_count",
                    "success",
                    "total_recipients"
                ]
            },
            "ChatHistory": {
                "type": "object",
                "description": "Chat history response serializer.",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "messages": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ChatMessage"
                        }
                    },
                    "total_messages": {
                        "type": "integer"
                    }
                },
                "required": [
                    "messages",
                    "session_id",
                    "total_messages"
                ]
            },
            "ChatMessage": {
                "type": "object",
                "description": "Chat message response serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "role": {
                        "enum": [
                            "user",
                            "assistant",
                            "system"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "6a92eb3ff78a3708",
                        "description": "Message sender role\n\n* `user` - User\n* `assistant` - Assistant\n* `system` - System"
                    },
                    "content": {
                        "type": "string",
                        "description": "Message content"
                    },
                    "tokens_used": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Tokens used for this message"
                    },
                    "cost_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "processing_time_ms": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Processing time in milliseconds"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "context_chunks": {
                        "description": "IDs of chunks used for context"
                    }
                },
                "required": [
                    "content",
                    "cost_usd",
                    "created_at",
                    "id",
                    "role"
                ]
            },
            "ChatQueryRequest": {
                "type": "object",
                "description": "Chat query request serializer.",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "format": "uuid",
                        "nullable": True,
                        "description": "Chat session ID (creates new if not provided)"
                    },
                    "query": {
                        "type": "string",
                        "minLength": 1,
                        "description": "User query",
                        "maxLength": 2000
                    },
                    "max_tokens": {
                        "type": "integer",
                        "maximum": 4000,
                        "minimum": 1,
                        "default": 1000,
                        "description": "Maximum response tokens"
                    },
                    "include_sources": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include source documents in response"
                    }
                },
                "required": [
                    "query"
                ]
            },
            "ChatResponse": {
                "type": "object",
                "description": "Chat response serializer.",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "content": {
                        "type": "string"
                    },
                    "tokens_used": {
                        "type": "integer"
                    },
                    "cost_usd": {
                        "type": "number",
                        "format": "double"
                    },
                    "processing_time_ms": {
                        "type": "integer"
                    },
                    "model_used": {
                        "type": "string"
                    },
                    "sources": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ChatSource"
                        },
                        "nullable": True
                    }
                },
                "required": [
                    "content",
                    "cost_usd",
                    "message_id",
                    "model_used",
                    "processing_time_ms",
                    "tokens_used"
                ]
            },
            "ChatResponseRequest": {
                "type": "object",
                "description": "Chat response serializer.",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "content": {
                        "type": "string",
                        "minLength": 1
                    },
                    "tokens_used": {
                        "type": "integer"
                    },
                    "cost_usd": {
                        "type": "number",
                        "format": "double"
                    },
                    "processing_time_ms": {
                        "type": "integer"
                    },
                    "model_used": {
                        "type": "string",
                        "minLength": 1
                    },
                    "sources": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ChatSourceRequest"
                        },
                        "nullable": True
                    }
                },
                "required": [
                    "content",
                    "cost_usd",
                    "message_id",
                    "model_used",
                    "processing_time_ms",
                    "tokens_used"
                ]
            },
            "ChatSession": {
                "type": "object",
                "description": "Chat session response serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "title": {
                        "type": "string",
                        "description": "Session title (auto-generated if empty)",
                        "maxLength": 255
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether session accepts new messages"
                    },
                    "messages_count": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0
                    },
                    "total_tokens_used": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0
                    },
                    "total_cost_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "model_name": {
                        "type": "string",
                        "description": "LLM model used for this session",
                        "maxLength": 100
                    },
                    "temperature": {
                        "type": "number",
                        "format": "double",
                        "description": "Temperature setting for LLM"
                    },
                    "max_context_chunks": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Maximum chunks to include in context"
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
                    "total_cost_usd",
                    "updated_at"
                ]
            },
            "ChatSessionCreateRequest": {
                "type": "object",
                "description": "Chat session creation request serializer.",
                "properties": {
                    "title": {
                        "type": "string",
                        "default": "",
                        "description": "Session title",
                        "maxLength": 255
                    },
                    "model_name": {
                        "type": "string",
                        "minLength": 1,
                        "default": "openai/gpt-4o-mini",
                        "description": "LLM model to use",
                        "maxLength": 100
                    },
                    "temperature": {
                        "type": "number",
                        "format": "double",
                        "maximum": 2.0,
                        "minimum": 0.0,
                        "default": 0.7,
                        "description": "Response creativity"
                    },
                    "max_context_chunks": {
                        "type": "integer",
                        "maximum": 10,
                        "minimum": 1,
                        "default": 5,
                        "description": "Maximum context chunks"
                    }
                }
            },
            "ChatSessionRequest": {
                "type": "object",
                "description": "Chat session response serializer.",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Session title (auto-generated if empty)",
                        "maxLength": 255
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether session accepts new messages"
                    },
                    "messages_count": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0
                    },
                    "total_tokens_used": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0
                    },
                    "model_name": {
                        "type": "string",
                        "minLength": 1,
                        "description": "LLM model used for this session",
                        "maxLength": 100
                    },
                    "temperature": {
                        "type": "number",
                        "format": "double",
                        "description": "Temperature setting for LLM"
                    },
                    "max_context_chunks": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Maximum chunks to include in context"
                    }
                }
            },
            "ChatSource": {
                "type": "object",
                "description": "Chat source document information serializer.",
                "properties": {
                    "document_title": {
                        "type": "string"
                    },
                    "chunk_content": {
                        "type": "string"
                    },
                    "similarity": {
                        "type": "number",
                        "format": "double"
                    }
                },
                "required": [
                    "chunk_content",
                    "document_title",
                    "similarity"
                ]
            },
            "ChatSourceRequest": {
                "type": "object",
                "description": "Chat source document information serializer.",
                "properties": {
                    "document_title": {
                        "type": "string",
                        "minLength": 1
                    },
                    "chunk_content": {
                        "type": "string",
                        "minLength": 1
                    },
                    "similarity": {
                        "type": "number",
                        "format": "double"
                    }
                },
                "required": [
                    "chunk_content",
                    "document_title",
                    "similarity"
                ]
            },
            "ChunkRevectorizationRequestRequest": {
                "type": "object",
                "description": "Chunk re-vectorization request serializer.",
                "properties": {
                    "chunk_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "description": "List of chunk IDs to re-vectorize",
                        "minItems": 1
                    },
                    "force": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force re-vectorization even if already vectorized"
                    }
                },
                "required": [
                    "chunk_ids"
                ]
            },
            "Currency": {
                "type": "object",
                "description": "Currency list serializer.",
                "properties": {
                    "code": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Currency code from provider (e.g., USDTTRC20, BTC, ETH)"
                    },
                    "name": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Full currency name (e.g., USDT (TRC20), Bitcoin)"
                    },
                    "token": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Token symbol (e.g., USDT, BTC, ETH)"
                    },
                    "network": {
                        "type": "string",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Network name (e.g., TRC20, ERC20, Bitcoin)"
                    },
                    "display_name": {
                        "type": "string",
                        "readOnly": True
                    },
                    "symbol": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Currency symbol (e.g., ₮, ₿, Ξ)"
                    },
                    "decimal_places": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Number of decimal places for this currency"
                    },
                    "is_active": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether this currency is available for payments"
                    },
                    "min_amount_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "description": "Minimum payment amount in USD"
                    },
                    "sort_order": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Sort order for currency list (lower = higher priority)"
                    }
                },
                "required": [
                    "code",
                    "decimal_places",
                    "display_name",
                    "is_active",
                    "min_amount_usd",
                    "name",
                    "network",
                    "sort_order",
                    "symbol",
                    "token"
                ]
            },
            "Document": {
                "type": "object",
                "description": "Document response serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "title": {
                        "type": "string",
                        "description": "Document title",
                        "maxLength": 512
                    },
                    "file_type": {
                        "type": "string",
                        "description": "MIME type of original file",
                        "maxLength": 100
                    },
                    "file_size": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Original file size in bytes"
                    },
                    "processing_status": {
                        "type": "string",
                        "readOnly": True
                    },
                    "chunks_count": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_tokens": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_cost_usd": {
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
                    },
                    "processing_started_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "processing_completed_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "processing_error": {
                        "type": "string",
                        "readOnly": True
                    },
                    "metadata": {
                        "nullable": True,
                        "description": "Additional document metadata"
                    }
                },
                "required": [
                    "chunks_count",
                    "created_at",
                    "id",
                    "processing_completed_at",
                    "processing_error",
                    "processing_started_at",
                    "processing_status",
                    "title",
                    "total_cost_usd",
                    "total_tokens",
                    "updated_at"
                ]
            },
            "DocumentArchive": {
                "type": "object",
                "description": "Document archive serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "title": {
                        "type": "string",
                        "description": "Archive title",
                        "maxLength": 512
                    },
                    "description": {
                        "type": "string",
                        "description": "Archive description"
                    },
                    "categories": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/DocumentCategory"
                        },
                        "readOnly": True
                    },
                    "is_public": {
                        "type": "boolean",
                        "description": "Whether this archive is publicly accessible"
                    },
                    "archive_file": {
                        "type": "string",
                        "format": "uri",
                        "readOnly": True,
                        "description": "Uploaded archive file"
                    },
                    "original_filename": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Original uploaded filename"
                    },
                    "file_size": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Archive size in bytes"
                    },
                    "archive_type": {
                        "enum": [
                            "zip",
                            "tar",
                            "tar.gz",
                            "tar.bz2"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "51253f4da98c0846",
                        "readOnly": True,
                        "description": "Archive format\n\n* `zip` - ZIP\n* `tar` - TAR\n* `tar.gz` - TAR GZ\n* `tar.bz2` - TAR BZ2"
                    },
                    "processing_status": {
                        "enum": [
                            "pending",
                            "processing",
                            "completed",
                            "failed",
                            "cancelled"
                        ],
                        "type": "string",
                        "description": "* `pending` - Pending\n* `processing` - Processing\n* `completed` - Completed\n* `failed` - Failed\n* `cancelled` - Cancelled",
                        "x-spec-enum-id": "9c61eae888c009aa",
                        "readOnly": True
                    },
                    "processed_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When processing completed"
                    },
                    "processing_duration_ms": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Processing time in milliseconds"
                    },
                    "processing_error": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Error message if processing failed"
                    },
                    "total_items": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total items in archive"
                    },
                    "processed_items": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Successfully processed items"
                    },
                    "total_chunks": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total chunks created"
                    },
                    "vectorized_chunks": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Chunks with embeddings"
                    },
                    "total_tokens": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total tokens across all chunks"
                    },
                    "total_cost_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Total processing cost in USD"
                    },
                    "processing_progress": {
                        "type": "number",
                        "format": "double",
                        "description": "Calculate processing progress as percentage.",
                        "readOnly": True
                    },
                    "vectorization_progress": {
                        "type": "number",
                        "format": "double",
                        "description": "Calculate vectorization progress as percentage.",
                        "readOnly": True
                    },
                    "is_processed": {
                        "type": "boolean",
                        "description": "Check if archive processing is completed.",
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
                    "archive_file",
                    "archive_type",
                    "categories",
                    "created_at",
                    "file_size",
                    "id",
                    "is_processed",
                    "original_filename",
                    "processed_at",
                    "processed_items",
                    "processing_duration_ms",
                    "processing_error",
                    "processing_progress",
                    "processing_status",
                    "title",
                    "total_chunks",
                    "total_cost_usd",
                    "total_items",
                    "total_tokens",
                    "updated_at",
                    "vectorization_progress",
                    "vectorized_chunks"
                ]
            },
            "DocumentArchiveDetail": {
                "type": "object",
                "description": "Detailed archive serializer with items.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "title": {
                        "type": "string",
                        "description": "Archive title",
                        "maxLength": 512
                    },
                    "description": {
                        "type": "string",
                        "description": "Archive description"
                    },
                    "categories": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/DocumentCategory"
                        },
                        "readOnly": True
                    },
                    "is_public": {
                        "type": "boolean",
                        "description": "Whether this archive is publicly accessible"
                    },
                    "archive_file": {
                        "type": "string",
                        "format": "uri",
                        "readOnly": True,
                        "description": "Uploaded archive file"
                    },
                    "original_filename": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Original uploaded filename"
                    },
                    "file_size": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Archive size in bytes"
                    },
                    "archive_type": {
                        "enum": [
                            "zip",
                            "tar",
                            "tar.gz",
                            "tar.bz2"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "51253f4da98c0846",
                        "readOnly": True,
                        "description": "Archive format\n\n* `zip` - ZIP\n* `tar` - TAR\n* `tar.gz` - TAR GZ\n* `tar.bz2` - TAR BZ2"
                    },
                    "processing_status": {
                        "enum": [
                            "pending",
                            "processing",
                            "completed",
                            "failed",
                            "cancelled"
                        ],
                        "type": "string",
                        "description": "* `pending` - Pending\n* `processing` - Processing\n* `completed` - Completed\n* `failed` - Failed\n* `cancelled` - Cancelled",
                        "x-spec-enum-id": "9c61eae888c009aa",
                        "readOnly": True
                    },
                    "processed_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When processing completed"
                    },
                    "processing_duration_ms": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Processing time in milliseconds"
                    },
                    "processing_error": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Error message if processing failed"
                    },
                    "total_items": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total items in archive"
                    },
                    "processed_items": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Successfully processed items"
                    },
                    "total_chunks": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total chunks created"
                    },
                    "vectorized_chunks": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Chunks with embeddings"
                    },
                    "total_tokens": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total tokens across all chunks"
                    },
                    "total_cost_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Total processing cost in USD"
                    },
                    "processing_progress": {
                        "type": "number",
                        "format": "double",
                        "description": "Calculate processing progress as percentage.",
                        "readOnly": True
                    },
                    "vectorization_progress": {
                        "type": "number",
                        "format": "double",
                        "description": "Calculate vectorization progress as percentage.",
                        "readOnly": True
                    },
                    "is_processed": {
                        "type": "boolean",
                        "description": "Check if archive processing is completed.",
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
                    },
                    "items": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ArchiveItem"
                        },
                        "readOnly": True
                    },
                    "file_tree": {
                        "type": "object",
                        "additionalProperties": {},
                        "description": "Get hierarchical file tree.",
                        "readOnly": True
                    },
                    "metadata": {
                        "nullable": True,
                        "description": "Additional archive metadata"
                    }
                },
                "required": [
                    "archive_file",
                    "archive_type",
                    "categories",
                    "created_at",
                    "file_size",
                    "file_tree",
                    "id",
                    "is_processed",
                    "items",
                    "original_filename",
                    "processed_at",
                    "processed_items",
                    "processing_duration_ms",
                    "processing_error",
                    "processing_progress",
                    "processing_status",
                    "title",
                    "total_chunks",
                    "total_cost_usd",
                    "total_items",
                    "total_tokens",
                    "updated_at",
                    "vectorization_progress",
                    "vectorized_chunks"
                ]
            },
            "DocumentArchiveList": {
                "type": "object",
                "description": "Simplified archive serializer for list views.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "title": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Archive title"
                    },
                    "description": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Archive description"
                    },
                    "categories": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/DocumentCategory"
                        },
                        "readOnly": True
                    },
                    "is_public": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether this archive is publicly accessible"
                    },
                    "original_filename": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Original uploaded filename"
                    },
                    "file_size": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Archive size in bytes"
                    },
                    "archive_type": {
                        "enum": [
                            "zip",
                            "tar",
                            "tar.gz",
                            "tar.bz2"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "51253f4da98c0846",
                        "readOnly": True,
                        "description": "Archive format\n\n* `zip` - ZIP\n* `tar` - TAR\n* `tar.gz` - TAR GZ\n* `tar.bz2` - TAR BZ2"
                    },
                    "processing_status": {
                        "enum": [
                            "pending",
                            "processing",
                            "completed",
                            "failed",
                            "cancelled"
                        ],
                        "type": "string",
                        "description": "* `pending` - Pending\n* `processing` - Processing\n* `completed` - Completed\n* `failed` - Failed\n* `cancelled` - Cancelled",
                        "x-spec-enum-id": "9c61eae888c009aa",
                        "readOnly": True
                    },
                    "processed_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When processing completed"
                    },
                    "total_items": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total items in archive"
                    },
                    "total_chunks": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total chunks created"
                    },
                    "total_cost_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Total processing cost in USD"
                    },
                    "processing_progress": {
                        "type": "number",
                        "format": "double",
                        "description": "Calculate processing progress as percentage.",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    }
                },
                "required": [
                    "archive_type",
                    "categories",
                    "created_at",
                    "description",
                    "file_size",
                    "id",
                    "is_public",
                    "original_filename",
                    "processed_at",
                    "processing_progress",
                    "processing_status",
                    "title",
                    "total_chunks",
                    "total_cost_usd",
                    "total_items"
                ]
            },
            "DocumentArchiveRequest": {
                "type": "object",
                "description": "Document archive serializer.",
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Archive title",
                        "maxLength": 512
                    },
                    "description": {
                        "type": "string",
                        "description": "Archive description"
                    },
                    "is_public": {
                        "type": "boolean",
                        "description": "Whether this archive is publicly accessible"
                    }
                },
                "required": [
                    "title"
                ]
            },
            "DocumentCategory": {
                "type": "object",
                "description": "Document category serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "name": {
                        "type": "string",
                        "description": "Category name",
                        "maxLength": 255
                    },
                    "description": {
                        "type": "string",
                        "description": "Category description"
                    },
                    "is_public": {
                        "type": "boolean",
                        "description": "Whether documents in this category are publicly accessible"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    }
                },
                "required": [
                    "created_at",
                    "id",
                    "name"
                ]
            },
            "DocumentCategoryRequest": {
                "type": "object",
                "description": "Document category serializer.",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Category name",
                        "maxLength": 255
                    },
                    "description": {
                        "type": "string",
                        "description": "Category description"
                    },
                    "is_public": {
                        "type": "boolean",
                        "description": "Whether documents in this category are publicly accessible"
                    }
                },
                "required": [
                    "name"
                ]
            },
            "DocumentCreateRequest": {
                "type": "object",
                "description": "Document creation request serializer.",
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Document title",
                        "maxLength": 512
                    },
                    "content": {
                        "type": "string",
                        "minLength": 10,
                        "description": "Document content",
                        "maxLength": 1000000
                    },
                    "file_type": {
                        "type": "string",
                        "minLength": 1,
                        "default": "text/plain",
                        "description": "MIME type",
                        "pattern": "^[a-z]+/[a-z0-9\\-\\+\\.]+$"
                    },
                    "metadata": {
                        "description": "Additional metadata"
                    }
                },
                "required": [
                    "content",
                    "title"
                ]
            },
            "DocumentProcessingStatus": {
                "type": "object",
                "description": "Document processing status serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "status": {
                        "type": "string"
                    },
                    "progress": {},
                    "error": {
                        "type": "string",
                        "nullable": True
                    },
                    "processing_time_seconds": {
                        "type": "number",
                        "format": "double",
                        "nullable": True
                    }
                },
                "required": [
                    "id",
                    "progress",
                    "status"
                ]
            },
            "DocumentRequest": {
                "type": "object",
                "description": "Document response serializer.",
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Document title",
                        "maxLength": 512
                    },
                    "file_type": {
                        "type": "string",
                        "minLength": 1,
                        "description": "MIME type of original file",
                        "maxLength": 100
                    },
                    "file_size": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Original file size in bytes"
                    },
                    "metadata": {
                        "nullable": True,
                        "description": "Additional document metadata"
                    }
                },
                "required": [
                    "title"
                ]
            },
            "DocumentStats": {
                "type": "object",
                "description": "Document processing statistics serializer.",
                "properties": {
                    "total_documents": {
                        "type": "integer"
                    },
                    "completed_documents": {
                        "type": "integer"
                    },
                    "processing_success_rate": {
                        "type": "number",
                        "format": "double"
                    },
                    "total_chunks": {
                        "type": "integer"
                    },
                    "total_tokens": {
                        "type": "integer"
                    },
                    "total_cost_usd": {
                        "type": "number",
                        "format": "double"
                    },
                    "avg_processing_time_seconds": {
                        "type": "number",
                        "format": "double"
                    }
                },
                "required": [
                    "avg_processing_time_seconds",
                    "completed_documents",
                    "processing_success_rate",
                    "total_chunks",
                    "total_cost_usd",
                    "total_documents",
                    "total_tokens"
                ]
            },
            "EmailLog": {
                "type": "object",
                "description": "Serializer for EmailLog model.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "user": {
                        "type": "integer",
                        "readOnly": True,
                        "nullable": True,
                        "title": "User Account"
                    },
                    "user_email": {
                        "type": "string",
                        "readOnly": True
                    },
                    "newsletter": {
                        "type": "integer",
                        "readOnly": True,
                        "nullable": True,
                        "title": "Related Newsletter"
                    },
                    "newsletter_title": {
                        "type": "string",
                        "readOnly": True
                    },
                    "recipient": {
                        "type": "string",
                        "readOnly": True,
                        "title": "Recipient(s)",
                        "description": "Comma-separated email addresses"
                    },
                    "subject": {
                        "type": "string",
                        "readOnly": True
                    },
                    "body": {
                        "type": "string",
                        "readOnly": True,
                        "title": "Body (HTML)"
                    },
                    "status": {
                        "enum": [
                            "pending",
                            "sent",
                            "failed"
                        ],
                        "type": "string",
                        "description": "* `pending` - Pending\n* `sent` - Sent\n* `failed` - Failed",
                        "x-spec-enum-id": "6c875617d5f34e96",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "sent_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True
                    },
                    "error_message": {
                        "type": "string",
                        "readOnly": True,
                        "nullable": True
                    }
                },
                "required": [
                    "body",
                    "created_at",
                    "error_message",
                    "id",
                    "newsletter",
                    "newsletter_title",
                    "recipient",
                    "sent_at",
                    "status",
                    "subject",
                    "user",
                    "user_email"
                ]
            },
            "Endpoint": {
                "type": "object",
                "description": "Serializer for single endpoint status.",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Resolved URL (for parametrized URLs) or URL pattern"
                    },
                    "url_pattern": {
                        "type": "string",
                        "nullable": True,
                        "description": "Original URL pattern (for parametrized URLs)"
                    },
                    "url_name": {
                        "type": "string",
                        "nullable": True,
                        "description": "Django URL name (if available)"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "URL namespace"
                    },
                    "group": {
                        "type": "string",
                        "description": "URL group (up to 3 depth)"
                    },
                    "view": {
                        "type": "string",
                        "description": "View function/class name"
                    },
                    "status": {
                        "type": "string",
                        "description": "Status: healthy, unhealthy, warning, error, skipped, pending"
                    },
                    "status_code": {
                        "type": "integer",
                        "nullable": True,
                        "description": "HTTP status code"
                    },
                    "response_time_ms": {
                        "type": "number",
                        "format": "double",
                        "nullable": True,
                        "description": "Response time in milliseconds"
                    },
                    "is_healthy": {
                        "type": "boolean",
                        "nullable": True,
                        "description": "Whether endpoint is healthy"
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message if check failed"
                    },
                    "error_type": {
                        "type": "string",
                        "description": "Error type: database, general, etc."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for warning/skip"
                    },
                    "last_checked": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "Timestamp of last check"
                    },
                    "has_parameters": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether URL has parameters that were resolved with test values"
                    },
                    "required_auth": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether endpoint required JWT authentication"
                    },
                    "rate_limited": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether endpoint returned 429 (rate limited)"
                    }
                },
                "required": [
                    "group",
                    "status",
                    "url"
                ]
            },
            "EndpointsStatus": {
                "type": "object",
                "description": "Serializer for overall endpoints status response.",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Overall status: healthy, degraded, or unhealthy"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Timestamp of the check"
                    },
                    "total_endpoints": {
                        "type": "integer",
                        "description": "Total number of endpoints checked"
                    },
                    "healthy": {
                        "type": "integer",
                        "description": "Number of healthy endpoints"
                    },
                    "unhealthy": {
                        "type": "integer",
                        "description": "Number of unhealthy endpoints"
                    },
                    "warnings": {
                        "type": "integer",
                        "description": "Number of endpoints with warnings"
                    },
                    "errors": {
                        "type": "integer",
                        "description": "Number of endpoints with errors"
                    },
                    "skipped": {
                        "type": "integer",
                        "description": "Number of skipped endpoints"
                    },
                    "endpoints": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/Endpoint"
                        },
                        "description": "List of all endpoints with their status"
                    }
                },
                "required": [
                    "endpoints",
                    "errors",
                    "healthy",
                    "skipped",
                    "status",
                    "timestamp",
                    "total_endpoints",
                    "unhealthy",
                    "warnings"
                ]
            },
            "ErrorResponse": {
                "type": "object",
                "description": "Generic error response.",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "default": False
                    },
                    "message": {
                        "type": "string"
                    }
                },
                "required": [
                    "message"
                ]
            },
            "HealthCheck": {
                "type": "object",
                "description": "Serializer for health check response.",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Overall health status: healthy, degraded, or unhealthy"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Timestamp of the health check"
                    },
                    "service": {
                        "type": "string",
                        "description": "Service name"
                    },
                    "version": {
                        "type": "string",
                        "description": "Django-CFG version"
                    },
                    "checks": {
                        "type": "object",
                        "additionalProperties": {},
                        "description": "Detailed health checks for databases, cache, and system"
                    },
                    "environment": {
                        "type": "object",
                        "additionalProperties": {},
                        "description": "Environment information"
                    }
                },
                "required": [
                    "checks",
                    "environment",
                    "service",
                    "status",
                    "timestamp",
                    "version"
                ]
            },
            "LeadSubmission": {
                "type": "object",
                "description": "Serializer for lead form submission from frontend.",
                "properties": {
                    "name": {
                        "type": "string",
                        "title": "Full Name",
                        "maxLength": 200
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "maxLength": 254
                    },
                    "company": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "company_site": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "contact_type": {
                        "enum": [
                            "email",
                            "whatsapp",
                            "telegram",
                            "phone",
                            "other"
                        ],
                        "type": "string",
                        "description": "* `email` - Email\n* `whatsapp` - WhatsApp\n* `telegram` - Telegram\n* `phone` - Phone\n* `other` - Other",
                        "x-spec-enum-id": "2d58a06dc3d54732"
                    },
                    "contact_value": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "subject": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "message": {
                        "type": "string"
                    },
                    "extra": {
                        "nullable": True,
                        "title": "Extra Data"
                    },
                    "site_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Frontend URL where form was submitted",
                        "maxLength": 200
                    }
                },
                "required": [
                    "email",
                    "message",
                    "name",
                    "site_url"
                ]
            },
            "LeadSubmissionError": {
                "type": "object",
                "description": "Response serializer for lead submission errors.",
                "properties": {
                    "success": {
                        "type": "boolean"
                    },
                    "error": {
                        "type": "string"
                    },
                    "details": {
                        "type": "object",
                        "additionalProperties": {}
                    }
                },
                "required": [
                    "error",
                    "success"
                ]
            },
            "LeadSubmissionRequest": {
                "type": "object",
                "description": "Serializer for lead form submission from frontend.",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "title": "Full Name",
                        "maxLength": 200
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "minLength": 1,
                        "maxLength": 254
                    },
                    "company": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "company_site": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "contact_type": {
                        "enum": [
                            "email",
                            "whatsapp",
                            "telegram",
                            "phone",
                            "other"
                        ],
                        "type": "string",
                        "description": "* `email` - Email\n* `whatsapp` - WhatsApp\n* `telegram` - Telegram\n* `phone` - Phone\n* `other` - Other",
                        "x-spec-enum-id": "2d58a06dc3d54732"
                    },
                    "contact_value": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "subject": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "message": {
                        "type": "string",
                        "minLength": 1
                    },
                    "extra": {
                        "nullable": True,
                        "title": "Extra Data"
                    },
                    "site_url": {
                        "type": "string",
                        "format": "uri",
                        "minLength": 1,
                        "description": "Frontend URL where form was submitted",
                        "maxLength": 200
                    }
                },
                "required": [
                    "email",
                    "message",
                    "name",
                    "site_url"
                ]
            },
            "LeadSubmissionResponse": {
                "type": "object",
                "description": "Response serializer for successful lead submission.",
                "properties": {
                    "success": {
                        "type": "boolean"
                    },
                    "message": {
                        "type": "string"
                    },
                    "lead_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "lead_id",
                    "message",
                    "success"
                ]
            },
            "Message": {
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "ticket": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "sender": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/Sender"
                            }
                        ],
                        "readOnly": True
                    },
                    "is_from_author": {
                        "type": "boolean",
                        "description": "Check if this message is from the ticket author.",
                        "readOnly": True
                    },
                    "text": {
                        "type": "string"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    }
                },
                "required": [
                    "created_at",
                    "is_from_author",
                    "sender",
                    "text",
                    "ticket",
                    "uuid"
                ]
            },
            "MessageCreate": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string"
                    }
                },
                "required": [
                    "text"
                ]
            },
            "MessageCreateRequest": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": [
                    "text"
                ]
            },
            "MessageRequest": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": [
                    "text"
                ]
            },
            "Newsletter": {
                "type": "object",
                "description": "Serializer for Newsletter model.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "title": {
                        "type": "string",
                        "title": "Newsletter Title",
                        "maxLength": 255
                    },
                    "description": {
                        "type": "string"
                    },
                    "is_active": {
                        "type": "boolean",
                        "title": "Active"
                    },
                    "auto_subscribe": {
                        "type": "boolean",
                        "title": "Auto Subscribe New Users",
                        "description": "Automatically subscribe new users to this newsletter"
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
                    },
                    "subscribers_count": {
                        "type": "integer",
                        "readOnly": True
                    }
                },
                "required": [
                    "created_at",
                    "id",
                    "subscribers_count",
                    "title",
                    "updated_at"
                ]
            },
            "NewsletterCampaign": {
                "type": "object",
                "description": "Serializer for NewsletterCampaign model.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "newsletter": {
                        "type": "integer"
                    },
                    "newsletter_title": {
                        "type": "string",
                        "readOnly": True
                    },
                    "subject": {
                        "type": "string",
                        "maxLength": 255
                    },
                    "email_title": {
                        "type": "string",
                        "maxLength": 255
                    },
                    "main_text": {
                        "type": "string"
                    },
                    "main_html_content": {
                        "type": "string",
                        "title": "HTML Content"
                    },
                    "button_text": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "button_url": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "secondary_text": {
                        "type": "string"
                    },
                    "status": {
                        "enum": [
                            "draft",
                            "sending",
                            "sent",
                            "failed"
                        ],
                        "type": "string",
                        "description": "* `draft` - Draft\n* `sending` - Sending\n* `sent` - Sent\n* `failed` - Failed",
                        "x-spec-enum-id": "a459055d142d5a82",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "sent_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True
                    },
                    "recipient_count": {
                        "type": "integer",
                        "readOnly": True
                    }
                },
                "required": [
                    "created_at",
                    "email_title",
                    "id",
                    "main_text",
                    "newsletter",
                    "newsletter_title",
                    "recipient_count",
                    "sent_at",
                    "status",
                    "subject"
                ]
            },
            "NewsletterCampaignRequest": {
                "type": "object",
                "description": "Serializer for NewsletterCampaign model.",
                "properties": {
                    "newsletter": {
                        "type": "integer"
                    },
                    "subject": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255
                    },
                    "email_title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255
                    },
                    "main_text": {
                        "type": "string",
                        "minLength": 1
                    },
                    "main_html_content": {
                        "type": "string",
                        "title": "HTML Content"
                    },
                    "button_text": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "button_url": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "secondary_text": {
                        "type": "string"
                    }
                },
                "required": [
                    "email_title",
                    "main_text",
                    "newsletter",
                    "subject"
                ]
            },
            "NewsletterSubscription": {
                "type": "object",
                "description": "Serializer for NewsletterSubscription model.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "newsletter": {
                        "type": "integer"
                    },
                    "newsletter_title": {
                        "type": "string",
                        "readOnly": True
                    },
                    "user": {
                        "type": "integer",
                        "nullable": True
                    },
                    "user_email": {
                        "type": "string",
                        "readOnly": True
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "title": "Email Address",
                        "maxLength": 254
                    },
                    "is_active": {
                        "type": "boolean",
                        "title": "Active"
                    },
                    "subscribed_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "unsubscribed_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True
                    }
                },
                "required": [
                    "email",
                    "id",
                    "newsletter",
                    "newsletter_title",
                    "subscribed_at",
                    "unsubscribed_at",
                    "user_email"
                ]
            },
            "OTPErrorResponse": {
                "type": "object",
                "description": "Error response for OTP operations.",
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Error message"
                    }
                },
                "required": [
                    "error"
                ]
            },
            "OTPRequestRequest": {
                "type": "object",
                "description": "Serializer for OTP request.",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Email address or phone number for OTP delivery"
                    },
                    "channel": {
                        "enum": [
                            "email",
                            "phone"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "17f11a3a6a4008ba",
                        "description": "Delivery channel: 'email' or 'phone'. Auto-detected if not provided.\n\n* `email` - Email\n* `phone` - Phone"
                    },
                    "source_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Source URL for tracking registration (e.g., https://dashboard.unrealon.com)"
                    }
                },
                "required": [
                    "identifier"
                ]
            },
            "OTPRequestResponse": {
                "type": "object",
                "description": "OTP request response.",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Success message"
                    }
                },
                "required": [
                    "message"
                ]
            },
            "OTPVerifyRequest": {
                "type": "object",
                "description": "Serializer for OTP verification.",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Email address or phone number used for OTP request"
                    },
                    "otp": {
                        "type": "string",
                        "minLength": 6,
                        "maxLength": 6
                    },
                    "channel": {
                        "enum": [
                            "email",
                            "phone"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "17f11a3a6a4008ba",
                        "description": "Delivery channel: 'email' or 'phone'. Auto-detected if not provided.\n\n* `email` - Email\n* `phone` - Phone"
                    },
                    "source_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Source URL for tracking login (e.g., https://dashboard.unrealon.com)"
                    }
                },
                "required": [
                    "identifier",
                    "otp"
                ]
            },
            "OTPVerifyResponse": {
                "type": "object",
                "description": "OTP verification response.",
                "properties": {
                    "refresh": {
                        "type": "string",
                        "description": "JWT refresh token"
                    },
                    "access": {
                        "type": "string",
                        "description": "JWT access token"
                    },
                    "user": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/User"
                            }
                        ],
                        "description": "User information"
                    }
                },
                "required": [
                    "access",
                    "refresh",
                    "user"
                ]
            },
            "PaginatedArchiveItemChunkList": {
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
                            "$ref": "#/components/schemas/ArchiveItemChunk"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedArchiveItemList": {
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
                            "$ref": "#/components/schemas/ArchiveItem"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedArchiveSearchResultList": {
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
                            "$ref": "#/components/schemas/ArchiveSearchResult"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedChatResponseList": {
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
                            "$ref": "#/components/schemas/ChatResponse"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedChatSessionList": {
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
                            "$ref": "#/components/schemas/ChatSession"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedDocumentArchiveListList": {
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
                            "$ref": "#/components/schemas/DocumentArchiveList"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedDocumentList": {
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
                            "$ref": "#/components/schemas/Document"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedEmailLogList": {
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
                            "$ref": "#/components/schemas/EmailLog"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedLeadSubmissionList": {
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
                            "$ref": "#/components/schemas/LeadSubmission"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedMessageList": {
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
                            "$ref": "#/components/schemas/Message"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedNewsletterCampaignList": {
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
                            "$ref": "#/components/schemas/NewsletterCampaign"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedNewsletterList": {
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
                            "$ref": "#/components/schemas/Newsletter"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedNewsletterSubscriptionList": {
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
                            "$ref": "#/components/schemas/NewsletterSubscription"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedPaymentListList": {
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
                            "$ref": "#/components/schemas/PaymentList"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedPublicCategoryList": {
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
                            "$ref": "#/components/schemas/PublicCategory"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedPublicDocumentListList": {
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
                            "$ref": "#/components/schemas/PublicDocumentList"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedTicketList": {
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
                            "$ref": "#/components/schemas/Ticket"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PatchedArchiveItemChunkRequest": {
                "type": "object",
                "description": "Archive item chunk serializer.",
                "properties": {
                    "content": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Chunk text content"
                    },
                    "chunk_index": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Sequential chunk number within item"
                    },
                    "chunk_type": {
                        "enum": [
                            "text",
                            "code",
                            "heading",
                            "metadata",
                            "table",
                            "list"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "660846bb1567d97b",
                        "description": "Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List"
                    }
                }
            },
            "PatchedArchiveItemRequest": {
                "type": "object",
                "description": "Archive item serializer.",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Path within archive",
                        "maxLength": 1024
                    },
                    "item_name": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Item name",
                        "maxLength": 255
                    },
                    "item_type": {
                        "type": "string",
                        "minLength": 1,
                        "description": "MIME type",
                        "maxLength": 100
                    },
                    "file_size": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Item size in bytes"
                    }
                }
            },
            "PatchedChatResponseRequest": {
                "type": "object",
                "description": "Chat response serializer.",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "content": {
                        "type": "string",
                        "minLength": 1
                    },
                    "tokens_used": {
                        "type": "integer"
                    },
                    "cost_usd": {
                        "type": "number",
                        "format": "double"
                    },
                    "processing_time_ms": {
                        "type": "integer"
                    },
                    "model_used": {
                        "type": "string",
                        "minLength": 1
                    },
                    "sources": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ChatSourceRequest"
                        },
                        "nullable": True
                    }
                }
            },
            "PatchedChatSessionRequest": {
                "type": "object",
                "description": "Chat session response serializer.",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Session title (auto-generated if empty)",
                        "maxLength": 255
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether session accepts new messages"
                    },
                    "messages_count": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0
                    },
                    "total_tokens_used": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0
                    },
                    "model_name": {
                        "type": "string",
                        "minLength": 1,
                        "description": "LLM model used for this session",
                        "maxLength": 100
                    },
                    "temperature": {
                        "type": "number",
                        "format": "double",
                        "description": "Temperature setting for LLM"
                    },
                    "max_context_chunks": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Maximum chunks to include in context"
                    }
                }
            },
            "PatchedDocumentArchiveRequest": {
                "type": "object",
                "description": "Document archive serializer.",
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Archive title",
                        "maxLength": 512
                    },
                    "description": {
                        "type": "string",
                        "description": "Archive description"
                    },
                    "is_public": {
                        "type": "boolean",
                        "description": "Whether this archive is publicly accessible"
                    }
                }
            },
            "PatchedDocumentRequest": {
                "type": "object",
                "description": "Document response serializer.",
                "properties": {
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Document title",
                        "maxLength": 512
                    },
                    "file_type": {
                        "type": "string",
                        "minLength": 1,
                        "description": "MIME type of original file",
                        "maxLength": 100
                    },
                    "file_size": {
                        "type": "integer",
                        "maximum": 2147483647,
                        "minimum": 0,
                        "description": "Original file size in bytes"
                    },
                    "metadata": {
                        "nullable": True,
                        "description": "Additional document metadata"
                    }
                }
            },
            "PatchedLeadSubmissionRequest": {
                "type": "object",
                "description": "Serializer for lead form submission from frontend.",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "title": "Full Name",
                        "maxLength": 200
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "minLength": 1,
                        "maxLength": 254
                    },
                    "company": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "company_site": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "contact_type": {
                        "enum": [
                            "email",
                            "whatsapp",
                            "telegram",
                            "phone",
                            "other"
                        ],
                        "type": "string",
                        "description": "* `email` - Email\n* `whatsapp` - WhatsApp\n* `telegram` - Telegram\n* `phone` - Phone\n* `other` - Other",
                        "x-spec-enum-id": "2d58a06dc3d54732"
                    },
                    "contact_value": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "subject": {
                        "type": "string",
                        "nullable": True,
                        "maxLength": 200
                    },
                    "message": {
                        "type": "string",
                        "minLength": 1
                    },
                    "extra": {
                        "nullable": True,
                        "title": "Extra Data"
                    },
                    "site_url": {
                        "type": "string",
                        "format": "uri",
                        "minLength": 1,
                        "description": "Frontend URL where form was submitted",
                        "maxLength": 200
                    }
                }
            },
            "PatchedMessageRequest": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 1
                    }
                }
            },
            "PatchedNewsletterCampaignRequest": {
                "type": "object",
                "description": "Serializer for NewsletterCampaign model.",
                "properties": {
                    "newsletter": {
                        "type": "integer"
                    },
                    "subject": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255
                    },
                    "email_title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255
                    },
                    "main_text": {
                        "type": "string",
                        "minLength": 1
                    },
                    "main_html_content": {
                        "type": "string",
                        "title": "HTML Content"
                    },
                    "button_text": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "button_url": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "secondary_text": {
                        "type": "string"
                    }
                }
            },
            "PatchedTicketRequest": {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "integer"
                    },
                    "subject": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255
                    },
                    "status": {
                        "enum": [
                            "open",
                            "waiting_for_user",
                            "waiting_for_admin",
                            "resolved",
                            "closed"
                        ],
                        "type": "string",
                        "description": "* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed",
                        "x-spec-enum-id": "c21b48fabf2398aa"
                    }
                }
            },
            "PatchedUnsubscribeRequest": {
                "type": "object",
                "description": "Simple serializer for unsubscribe.",
                "properties": {
                    "subscription_id": {
                        "type": "integer"
                    }
                }
            },
            "PatchedUserProfileUpdateRequest": {
                "type": "object",
                "description": "Serializer for updating user profile.",
                "properties": {
                    "first_name": {
                        "type": "string",
                        "maxLength": 50
                    },
                    "last_name": {
                        "type": "string",
                        "maxLength": 50
                    },
                    "company": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "phone": {
                        "type": "string",
                        "maxLength": 20
                    },
                    "position": {
                        "type": "string",
                        "maxLength": 100
                    }
                }
            },
            "PaymentDetail": {
                "type": "object",
                "description": "Detailed payment information.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "internal_payment_id": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID)"
                    },
                    "amount_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "description": "Payment amount in USD"
                    },
                    "currency_code": {
                        "type": "string",
                        "readOnly": True
                    },
                    "currency_name": {
                        "type": "string",
                        "readOnly": True
                    },
                    "currency_token": {
                        "type": "string",
                        "readOnly": True
                    },
                    "currency_network": {
                        "type": "string",
                        "readOnly": True
                    },
                    "pay_amount": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Amount to pay in cryptocurrency"
                    },
                    "actual_amount": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Actual amount received in cryptocurrency"
                    },
                    "actual_amount_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Actual amount received in USD"
                    },
                    "status": {
                        "enum": [
                            "pending",
                            "confirming",
                            "confirmed",
                            "completed",
                            "partially_paid",
                            "failed",
                            "expired",
                            "cancelled"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "a2aa9a45c3061ad0",
                        "readOnly": True,
                        "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `partially_paid` - Partially Paid\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled"
                    },
                    "status_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "pay_address": {
                        "type": "string",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Cryptocurrency payment address"
                    },
                    "qr_code_url": {
                        "type": "string",
                        "nullable": True,
                        "description": "Get QR code URL.",
                        "readOnly": True
                    },
                    "payment_url": {
                        "type": "string",
                        "format": "uri",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Payment page URL (if provided by provider)"
                    },
                    "transaction_hash": {
                        "type": "string",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Blockchain transaction hash"
                    },
                    "explorer_link": {
                        "type": "string",
                        "nullable": True,
                        "description": "Get blockchain explorer link.",
                        "readOnly": True
                    },
                    "confirmations_count": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Number of blockchain confirmations"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When this payment expires (typically 30 minutes)"
                    },
                    "completed_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When this payment was completed"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "is_completed": {
                        "type": "boolean",
                        "readOnly": True
                    },
                    "is_failed": {
                        "type": "boolean",
                        "readOnly": True
                    },
                    "is_expired": {
                        "type": "boolean",
                        "readOnly": True
                    },
                    "description": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Payment description"
                    }
                },
                "required": [
                    "actual_amount",
                    "actual_amount_usd",
                    "amount_usd",
                    "completed_at",
                    "confirmations_count",
                    "created_at",
                    "currency_code",
                    "currency_name",
                    "currency_network",
                    "currency_token",
                    "description",
                    "expires_at",
                    "explorer_link",
                    "id",
                    "internal_payment_id",
                    "is_completed",
                    "is_expired",
                    "is_failed",
                    "pay_address",
                    "pay_amount",
                    "payment_url",
                    "qr_code_url",
                    "status",
                    "status_display",
                    "transaction_hash"
                ]
            },
            "PaymentList": {
                "type": "object",
                "description": "Payment list item (lighter than detail).",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "internal_payment_id": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID)"
                    },
                    "amount_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "description": "Payment amount in USD"
                    },
                    "currency_code": {
                        "type": "string",
                        "readOnly": True
                    },
                    "currency_token": {
                        "type": "string",
                        "readOnly": True
                    },
                    "status": {
                        "enum": [
                            "pending",
                            "confirming",
                            "confirmed",
                            "completed",
                            "partially_paid",
                            "failed",
                            "expired",
                            "cancelled"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "a2aa9a45c3061ad0",
                        "readOnly": True,
                        "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `partially_paid` - Partially Paid\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled"
                    },
                    "status_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "completed_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When this payment was completed"
                    }
                },
                "required": [
                    "amount_usd",
                    "completed_at",
                    "created_at",
                    "currency_code",
                    "currency_token",
                    "id",
                    "internal_payment_id",
                    "status",
                    "status_display"
                ]
            },
            "PublicCategory": {
                "type": "object",
                "description": "Public category serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "name": {
                        "type": "string",
                        "description": "Category name",
                        "maxLength": 255
                    },
                    "description": {
                        "type": "string",
                        "description": "Category description"
                    }
                },
                "required": [
                    "id",
                    "name"
                ]
            },
            "PublicDocument": {
                "type": "object",
                "description": "Public document detail serializer - only essential data for clients.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "title": {
                        "type": "string",
                        "description": "Document title",
                        "maxLength": 512
                    },
                    "content": {
                        "type": "string",
                        "description": "Full document content"
                    },
                    "category": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/PublicCategory"
                            }
                        ],
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
                    "category",
                    "content",
                    "created_at",
                    "id",
                    "title",
                    "updated_at"
                ]
            },
            "PublicDocumentList": {
                "type": "object",
                "description": "Public document list serializer - minimal fields for listing.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "title": {
                        "type": "string",
                        "description": "Document title",
                        "maxLength": 512
                    },
                    "category": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/PublicCategory"
                            }
                        ],
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
                    "category",
                    "created_at",
                    "id",
                    "title",
                    "updated_at"
                ]
            },
            "QueueAction": {
                "type": "object",
                "description": "Serializer for queue management actions.",
                "properties": {
                    "action": {
                        "enum": [
                            "clear",
                            "clear_all",
                            "purge",
                            "purge_failed",
                            "flush"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "4a60a2c6249b0803",
                        "description": "Action to perform on queues\n\n* `clear` - clear\n* `clear_all` - clear_all\n* `purge` - purge\n* `purge_failed` - purge_failed\n* `flush` - flush"
                    },
                    "queue_names": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Specific queues to target (empty = all queues)"
                    }
                },
                "required": [
                    "action"
                ]
            },
            "QueueActionRequest": {
                "type": "object",
                "description": "Serializer for queue management actions.",
                "properties": {
                    "action": {
                        "enum": [
                            "clear",
                            "clear_all",
                            "purge",
                            "purge_failed",
                            "flush"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "4a60a2c6249b0803",
                        "description": "Action to perform on queues\n\n* `clear` - clear\n* `clear_all` - clear_all\n* `purge` - purge\n* `purge_failed` - purge_failed\n* `flush` - flush"
                    },
                    "queue_names": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 1
                        },
                        "description": "Specific queues to target (empty = all queues)"
                    }
                },
                "required": [
                    "action"
                ]
            },
            "QueueStatus": {
                "type": "object",
                "description": "Serializer for queue status data.",
                "properties": {
                    "queues": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "integer"
                            }
                        },
                        "description": "Queue information with pending/failed counts"
                    },
                    "workers": {
                        "type": "integer",
                        "description": "Number of active workers"
                    },
                    "redis_connected": {
                        "type": "boolean",
                        "description": "Redis connection status"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Current timestamp"
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message if any"
                    }
                },
                "required": [
                    "queues",
                    "redis_connected",
                    "timestamp",
                    "workers"
                ]
            },
            "QuickHealth": {
                "type": "object",
                "description": "Serializer for quick health check response.",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Quick health status: ok or error"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Timestamp of the health check"
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message if health check failed"
                    }
                },
                "required": [
                    "status",
                    "timestamp"
                ]
            },
            "SendCampaignRequest": {
                "type": "object",
                "description": "Simple serializer for sending campaign.",
                "properties": {
                    "campaign_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "campaign_id"
                ]
            },
            "SendCampaignResponse": {
                "type": "object",
                "description": "Response for sending campaign.",
                "properties": {
                    "success": {
                        "type": "boolean"
                    },
                    "message": {
                        "type": "string"
                    },
                    "sent_count": {
                        "type": "integer"
                    },
                    "error": {
                        "type": "string"
                    }
                },
                "required": [
                    "success"
                ]
            },
            "Sender": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "display_username": {
                        "type": "string",
                        "description": "Get formatted username for display.",
                        "readOnly": True
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "readOnly": True
                    },
                    "avatar": {
                        "type": "string",
                        "nullable": True,
                        "readOnly": True
                    },
                    "initials": {
                        "type": "string",
                        "description": "Get user's initials for avatar fallback.",
                        "readOnly": True
                    },
                    "is_staff": {
                        "type": "boolean",
                        "readOnly": True,
                        "title": "Staff status",
                        "description": "Designates whether the user can log into this admin site."
                    },
                    "is_superuser": {
                        "type": "boolean",
                        "readOnly": True,
                        "title": "Superuser status",
                        "description": "Designates that this user has all permissions without explicitly assigning them."
                    }
                },
                "required": [
                    "avatar",
                    "display_username",
                    "email",
                    "id",
                    "initials",
                    "is_staff",
                    "is_superuser"
                ]
            },
            "SubscribeRequest": {
                "type": "object",
                "description": "Simple serializer for newsletter subscription.",
                "properties": {
                    "newsletter_id": {
                        "type": "integer"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "minLength": 1
                    }
                },
                "required": [
                    "email",
                    "newsletter_id"
                ]
            },
            "SubscribeResponse": {
                "type": "object",
                "description": "Response for subscription.",
                "properties": {
                    "success": {
                        "type": "boolean"
                    },
                    "message": {
                        "type": "string"
                    },
                    "subscription_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "message",
                    "success"
                ]
            },
            "SuccessResponse": {
                "type": "object",
                "description": "Generic success response.",
                "properties": {
                    "success": {
                        "type": "boolean"
                    },
                    "message": {
                        "type": "string"
                    }
                },
                "required": [
                    "message",
                    "success"
                ]
            },
            "TaskStatistics": {
                "type": "object",
                "description": "Serializer for task statistics data.",
                "properties": {
                    "statistics": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "integer"
                        },
                        "description": "Task count statistics"
                    },
                    "recent_tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": {}
                        },
                        "description": "List of recent tasks"
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Current timestamp"
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message if any"
                    }
                },
                "required": [
                    "recent_tasks",
                    "statistics",
                    "timestamp"
                ]
            },
            "TestEmailRequest": {
                "type": "object",
                "description": "Simple serializer for test email.",
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "minLength": 1
                    },
                    "subject": {
                        "type": "string",
                        "minLength": 1,
                        "default": "Django CFG Newsletter Test",
                        "maxLength": 255
                    },
                    "message": {
                        "type": "string",
                        "minLength": 1,
                        "default": "This is a test email from Django CFG Newsletter."
                    }
                },
                "required": [
                    "email"
                ]
            },
            "Ticket": {
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True
                    },
                    "user": {
                        "type": "integer"
                    },
                    "subject": {
                        "type": "string",
                        "maxLength": 255
                    },
                    "status": {
                        "enum": [
                            "open",
                            "waiting_for_user",
                            "waiting_for_admin",
                            "resolved",
                            "closed"
                        ],
                        "type": "string",
                        "description": "* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed",
                        "x-spec-enum-id": "c21b48fabf2398aa"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "unanswered_messages_count": {
                        "type": "integer",
                        "description": "Get count of unanswered messages for this specific ticket.",
                        "readOnly": True
                    }
                },
                "required": [
                    "created_at",
                    "subject",
                    "unanswered_messages_count",
                    "user",
                    "uuid"
                ]
            },
            "TicketRequest": {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "integer"
                    },
                    "subject": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255
                    },
                    "status": {
                        "enum": [
                            "open",
                            "waiting_for_user",
                            "waiting_for_admin",
                            "resolved",
                            "closed"
                        ],
                        "type": "string",
                        "description": "* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed",
                        "x-spec-enum-id": "c21b48fabf2398aa"
                    }
                },
                "required": [
                    "subject",
                    "user"
                ]
            },
            "TokenRefresh": {
                "type": "object",
                "properties": {
                    "access": {
                        "type": "string",
                        "readOnly": True
                    },
                    "refresh": {
                        "type": "string"
                    }
                },
                "required": [
                    "access",
                    "refresh"
                ]
            },
            "TokenRefreshRequest": {
                "type": "object",
                "properties": {
                    "refresh": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": [
                    "refresh"
                ]
            },
            "Transaction": {
                "type": "object",
                "description": "Transaction serializer.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "transaction_type": {
                        "enum": [
                            "deposit",
                            "withdrawal",
                            "payment",
                            "refund",
                            "fee",
                            "bonus",
                            "adjustment"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "25d1662d4db37694",
                        "readOnly": True,
                        "description": "Type of transaction\n\n* `deposit` - Deposit\n* `withdrawal` - Withdrawal\n* `payment` - Payment\n* `refund` - Refund\n* `fee` - Fee\n* `bonus` - Bonus\n* `adjustment` - Adjustment"
                    },
                    "type_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "amount_usd": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "description": "Transaction amount in USD (positive=credit, negative=debit)"
                    },
                    "amount_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "balance_after": {
                        "type": "string",
                        "format": "decimal",
                        "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
                        "readOnly": True,
                        "description": "User balance after this transaction"
                    },
                    "payment_id": {
                        "type": "string",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Related payment ID (if applicable)"
                    },
                    "description": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Transaction description"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    }
                },
                "required": [
                    "amount_display",
                    "amount_usd",
                    "balance_after",
                    "created_at",
                    "description",
                    "id",
                    "payment_id",
                    "transaction_type",
                    "type_display"
                ]
            },
            "Unsubscribe": {
                "type": "object",
                "description": "Simple serializer for unsubscribe.",
                "properties": {
                    "subscription_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "subscription_id"
                ]
            },
            "UnsubscribeRequest": {
                "type": "object",
                "description": "Simple serializer for unsubscribe.",
                "properties": {
                    "subscription_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "subscription_id"
                ]
            },
            "User": {
                "type": "object",
                "description": "Serializer for user details.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "readOnly": True
                    },
                    "first_name": {
                        "type": "string",
                        "maxLength": 50
                    },
                    "last_name": {
                        "type": "string",
                        "maxLength": 50
                    },
                    "full_name": {
                        "type": "string",
                        "description": "Get user's full name.",
                        "readOnly": True
                    },
                    "initials": {
                        "type": "string",
                        "description": "Get user's initials for avatar fallback.",
                        "readOnly": True
                    },
                    "display_username": {
                        "type": "string",
                        "description": "Get formatted username for display.",
                        "readOnly": True
                    },
                    "company": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "phone": {
                        "type": "string",
                        "maxLength": 20
                    },
                    "position": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "avatar": {
                        "type": "string",
                        "format": "uri",
                        "nullable": True,
                        "readOnly": True
                    },
                    "is_staff": {
                        "type": "boolean",
                        "readOnly": True,
                        "title": "Staff status",
                        "description": "Designates whether the user can log into this admin site."
                    },
                    "is_superuser": {
                        "type": "boolean",
                        "readOnly": True,
                        "title": "Superuser status",
                        "description": "Designates that this user has all permissions without explicitly assigning them."
                    },
                    "date_joined": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "last_login": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True
                    },
                    "unanswered_messages_count": {
                        "type": "integer",
                        "description": "Get count of unanswered messages for the user.",
                        "readOnly": True
                    }
                },
                "required": [
                    "avatar",
                    "date_joined",
                    "display_username",
                    "email",
                    "full_name",
                    "id",
                    "initials",
                    "is_staff",
                    "is_superuser",
                    "last_login",
                    "unanswered_messages_count"
                ]
            },
            "UserProfileUpdateRequest": {
                "type": "object",
                "description": "Serializer for updating user profile.",
                "properties": {
                    "first_name": {
                        "type": "string",
                        "maxLength": 50
                    },
                    "last_name": {
                        "type": "string",
                        "maxLength": 50
                    },
                    "company": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "phone": {
                        "type": "string",
                        "maxLength": 20
                    },
                    "position": {
                        "type": "string",
                        "maxLength": 100
                    }
                }
            },
            "VectorizationResult": {
                "type": "object",
                "description": "Vectorization result serializer.",
                "properties": {
                    "vectorized_count": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "failed_count": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_tokens": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_cost": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "success_rate": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "errors": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "readOnly": True
                    }
                },
                "required": [
                    "errors",
                    "failed_count",
                    "success_rate",
                    "total_cost",
                    "total_tokens",
                    "vectorized_count"
                ]
            },
            "VectorizationStatistics": {
                "type": "object",
                "description": "Vectorization statistics serializer.",
                "properties": {
                    "total_chunks": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "vectorized_chunks": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "pending_chunks": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "vectorization_rate": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "total_tokens": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_cost": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "avg_tokens_per_chunk": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    },
                    "avg_cost_per_chunk": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True
                    }
                },
                "required": [
                    "avg_cost_per_chunk",
                    "avg_tokens_per_chunk",
                    "pending_chunks",
                    "total_chunks",
                    "total_cost",
                    "total_tokens",
                    "vectorization_rate",
                    "vectorized_chunks"
                ]
            },
            "WorkerAction": {
                "type": "object",
                "description": "Serializer for worker management actions.",
                "properties": {
                    "action": {
                        "enum": [
                            "start",
                            "stop",
                            "restart"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "5d2b5c38703636f1",
                        "description": "Action to perform on workers\n\n* `start` - start\n* `stop` - stop\n* `restart` - restart"
                    },
                    "processes": {
                        "type": "integer",
                        "maximum": 10,
                        "minimum": 1,
                        "default": 1,
                        "description": "Number of worker processes"
                    },
                    "threads": {
                        "type": "integer",
                        "maximum": 20,
                        "minimum": 1,
                        "default": 2,
                        "description": "Number of threads per process"
                    }
                },
                "required": [
                    "action"
                ]
            },
            "WorkerActionRequest": {
                "type": "object",
                "description": "Serializer for worker management actions.",
                "properties": {
                    "action": {
                        "enum": [
                            "start",
                            "stop",
                            "restart"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "5d2b5c38703636f1",
                        "description": "Action to perform on workers\n\n* `start` - start\n* `stop` - stop\n* `restart` - restart"
                    },
                    "processes": {
                        "type": "integer",
                        "maximum": 10,
                        "minimum": 1,
                        "default": 1,
                        "description": "Number of worker processes"
                    },
                    "threads": {
                        "type": "integer",
                        "maximum": 20,
                        "minimum": 1,
                        "default": 2,
                        "description": "Number of threads per process"
                    }
                },
                "required": [
                    "action"
                ]
            }
        },
        "securitySchemes": {
            "basicAuth": {
                "type": "http",
                "scheme": "basic"
            },
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