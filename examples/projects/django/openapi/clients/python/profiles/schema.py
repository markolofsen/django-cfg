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
            "group": "profiles",
            "apps": [
                "profiles"
            ],
            "generator": "django-client",
            "generator_version": "1.0.0"
        }
    },
    "paths": {
        "/api/profiles/profiles/": {
            "get": {
                "operationId": "profiles_profiles_list",
                "description": "Get a paginated list of all user profiles",
                "summary": "List user profiles",
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
                    "Profiles"
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
                                    "$ref": "#/components/schemas/PaginatedUserProfileList"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "post": {
                "operationId": "profiles_profiles_create",
                "description": "Create a new user profile",
                "summary": "Create user profile",
                "tags": [
                    "Profiles"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UserProfile"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/api/profiles/profiles/{id}/": {
            "get": {
                "operationId": "profiles_profiles_retrieve",
                "description": "Get detailed information about a specific user profile",
                "summary": "Get user profile",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this User Profile.",
                        "required": True
                    }
                ],
                "tags": [
                    "Profiles"
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
                                    "$ref": "#/components/schemas/UserProfile"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "profiles_profiles_update",
                "description": "Update user profile information",
                "summary": "Update user profile",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this User Profile.",
                        "required": True
                    }
                ],
                "tags": [
                    "Profiles"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileUpdateRequest"
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
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UserProfileUpdate"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "profiles_profiles_partial_update",
                "description": "Partially update user profile information",
                "summary": "Partially update user profile",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this User Profile.",
                        "required": True
                    }
                ],
                "tags": [
                    "Profiles"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileUpdateRequest"
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
                    }
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/UserProfileUpdate"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "delete": {
                "operationId": "profiles_profiles_destroy",
                "description": "Delete a user profile",
                "summary": "Delete user profile",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this User Profile.",
                        "required": True
                    }
                ],
                "tags": [
                    "Profiles"
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
        "/api/profiles/profiles/me/": {
            "get": {
                "operationId": "profiles_profiles_me_retrieve",
                "description": "Get current user's profile",
                "summary": "Get my profile",
                "tags": [
                    "Profiles"
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
                                    "$ref": "#/components/schemas/UserProfile"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "put": {
                "operationId": "profiles_profiles_me_update",
                "description": "Get current user's profile",
                "summary": "Get my profile",
                "tags": [
                    "Profiles"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/UserProfileRequest"
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
                                    "$ref": "#/components/schemas/UserProfile"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            },
            "patch": {
                "operationId": "profiles_profiles_me_partial_update",
                "description": "Get current user's profile",
                "summary": "Get my profile",
                "tags": [
                    "Profiles"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedUserProfileRequest"
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
                                    "$ref": "#/components/schemas/UserProfile"
                                }
                            }
                        },
                        "description": ""
                    }
                },
                "x-async-capable": False
            }
        },
        "/api/profiles/profiles/stats/": {
            "get": {
                "operationId": "profiles_profiles_stats_retrieve",
                "description": "Get comprehensive profile statistics",
                "summary": "Get profile statistics",
                "tags": [
                    "Profiles"
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
                                    "$ref": "#/components/schemas/UserProfileStats"
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
            "PaginatedUserProfileList": {
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
                            "$ref": "#/components/schemas/UserProfile"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PatchedUserProfileRequest": {
                "type": "object",
                "description": "Serializer for user profiles.",
                "properties": {
                    "website": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "github": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "twitter": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "linkedin": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "company": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "job_title": {
                        "type": "string",
                        "maxLength": 100
                    }
                }
            },
            "PatchedUserProfileUpdateRequest": {
                "type": "object",
                "description": "Serializer for updating user profiles.",
                "properties": {
                    "website": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "github": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "twitter": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "linkedin": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "company": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "job_title": {
                        "type": "string",
                        "maxLength": 100
                    }
                }
            },
            "UserProfile": {
                "type": "object",
                "description": "Serializer for user profiles.",
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
                        "description": "Get basic user information.",
                        "readOnly": True
                    },
                    "website": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "github": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "twitter": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "linkedin": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "company": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "job_title": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "posts_count": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "comments_count": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "orders_count": {
                        "type": "integer",
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
                    "comments_count",
                    "created_at",
                    "id",
                    "orders_count",
                    "posts_count",
                    "updated_at",
                    "user",
                    "user_info"
                ]
            },
            "UserProfileRequest": {
                "type": "object",
                "description": "Serializer for user profiles.",
                "properties": {
                    "website": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "github": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "twitter": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "linkedin": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "company": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "job_title": {
                        "type": "string",
                        "maxLength": 100
                    }
                }
            },
            "UserProfileStats": {
                "type": "object",
                "description": "Serializer for profile statistics.",
                "properties": {
                    "total_profiles": {
                        "type": "integer"
                    },
                    "profiles_with_company": {
                        "type": "integer"
                    },
                    "profiles_with_social_links": {
                        "type": "integer"
                    },
                    "most_active_users": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/UserProfile"
                        }
                    }
                },
                "required": [
                    "most_active_users",
                    "profiles_with_company",
                    "profiles_with_social_links",
                    "total_profiles"
                ]
            },
            "UserProfileUpdate": {
                "type": "object",
                "description": "Serializer for updating user profiles.",
                "properties": {
                    "website": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "github": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "twitter": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "linkedin": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "company": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "job_title": {
                        "type": "string",
                        "maxLength": 100
                    }
                }
            },
            "UserProfileUpdateRequest": {
                "type": "object",
                "description": "Serializer for updating user profiles.",
                "properties": {
                    "website": {
                        "type": "string",
                        "format": "uri",
                        "maxLength": 200
                    },
                    "github": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "twitter": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "linkedin": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "company": {
                        "type": "string",
                        "maxLength": 100
                    },
                    "job_title": {
                        "type": "string",
                        "maxLength": 100
                    }
                }
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