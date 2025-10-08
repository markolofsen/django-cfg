/**
 * OpenAPI Schema Export
 *
 * Contains the complete OpenAPI specification for runtime access.
 */

export const OPENAPI_SCHEMA = {
  "components": {
    "schemas": {
      "PaginatedUserProfileList": {
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
              "$ref": "#/components/schemas/UserProfile"
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
      "PatchedUserProfileRequest": {
        "description": "Serializer for user profiles.",
        "properties": {
          "company": {
            "maxLength": 100,
            "type": "string"
          },
          "github": {
            "maxLength": 100,
            "type": "string"
          },
          "job_title": {
            "maxLength": 100,
            "type": "string"
          },
          "linkedin": {
            "maxLength": 100,
            "type": "string"
          },
          "twitter": {
            "maxLength": 100,
            "type": "string"
          },
          "website": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PatchedUserProfileUpdateRequest": {
        "description": "Serializer for updating user profiles.",
        "properties": {
          "company": {
            "maxLength": 100,
            "type": "string"
          },
          "github": {
            "maxLength": 100,
            "type": "string"
          },
          "job_title": {
            "maxLength": 100,
            "type": "string"
          },
          "linkedin": {
            "maxLength": 100,
            "type": "string"
          },
          "twitter": {
            "maxLength": 100,
            "type": "string"
          },
          "website": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          }
        },
        "type": "object"
      },
      "UserProfile": {
        "description": "Serializer for user profiles.",
        "properties": {
          "comments_count": {
            "readOnly": true,
            "type": "integer"
          },
          "company": {
            "maxLength": 100,
            "type": "string"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "github": {
            "maxLength": 100,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "job_title": {
            "maxLength": 100,
            "type": "string"
          },
          "linkedin": {
            "maxLength": 100,
            "type": "string"
          },
          "orders_count": {
            "readOnly": true,
            "type": "integer"
          },
          "posts_count": {
            "readOnly": true,
            "type": "integer"
          },
          "twitter": {
            "maxLength": 100,
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
          "user_info": {
            "additionalProperties": {},
            "description": "Get basic user information.",
            "readOnly": true,
            "type": "object"
          },
          "website": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
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
        ],
        "type": "object"
      },
      "UserProfileRequest": {
        "description": "Serializer for user profiles.",
        "properties": {
          "company": {
            "maxLength": 100,
            "type": "string"
          },
          "github": {
            "maxLength": 100,
            "type": "string"
          },
          "job_title": {
            "maxLength": 100,
            "type": "string"
          },
          "linkedin": {
            "maxLength": 100,
            "type": "string"
          },
          "twitter": {
            "maxLength": 100,
            "type": "string"
          },
          "website": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          }
        },
        "type": "object"
      },
      "UserProfileStats": {
        "description": "Serializer for profile statistics.",
        "properties": {
          "most_active_users": {
            "items": {
              "$ref": "#/components/schemas/UserProfile"
            },
            "type": "array"
          },
          "profiles_with_company": {
            "type": "integer"
          },
          "profiles_with_social_links": {
            "type": "integer"
          },
          "total_profiles": {
            "type": "integer"
          }
        },
        "required": [
          "most_active_users",
          "profiles_with_company",
          "profiles_with_social_links",
          "total_profiles"
        ],
        "type": "object"
      },
      "UserProfileUpdate": {
        "description": "Serializer for updating user profiles.",
        "properties": {
          "company": {
            "maxLength": 100,
            "type": "string"
          },
          "github": {
            "maxLength": 100,
            "type": "string"
          },
          "job_title": {
            "maxLength": 100,
            "type": "string"
          },
          "linkedin": {
            "maxLength": 100,
            "type": "string"
          },
          "twitter": {
            "maxLength": 100,
            "type": "string"
          },
          "website": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          }
        },
        "type": "object"
      },
      "UserProfileUpdateRequest": {
        "description": "Serializer for updating user profiles.",
        "properties": {
          "company": {
            "maxLength": 100,
            "type": "string"
          },
          "github": {
            "maxLength": 100,
            "type": "string"
          },
          "job_title": {
            "maxLength": 100,
            "type": "string"
          },
          "linkedin": {
            "maxLength": 100,
            "type": "string"
          },
          "twitter": {
            "maxLength": 100,
            "type": "string"
          },
          "website": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          }
        },
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
        "profiles"
      ],
      "generator": "django-client",
      "generator_version": "1.0.0",
      "group": "profiles"
    }
  },
  "openapi": "3.0.3",
  "paths": {
    "/profiles/profiles/": {
      "get": {
        "description": "Get a paginated list of all user profiles",
        "operationId": "profiles_profiles_list",
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
                  "$ref": "#/components/schemas/PaginatedUserProfileList"
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
        "summary": "List user profiles",
        "tags": [
          "Profiles"
        ]
      },
      "post": {
        "description": "Create a new user profile",
        "operationId": "profiles_profiles_create",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Create user profile",
        "tags": [
          "Profiles"
        ]
      }
    },
    "/profiles/profiles/me/": {
      "get": {
        "description": "Get current user\u0027s profile",
        "operationId": "profiles_profiles_me_retrieve",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Get my profile",
        "tags": [
          "Profiles"
        ]
      },
      "patch": {
        "description": "Get current user\u0027s profile",
        "operationId": "profiles_profiles_me_partial_update",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Get my profile",
        "tags": [
          "Profiles"
        ]
      },
      "put": {
        "description": "Get current user\u0027s profile",
        "operationId": "profiles_profiles_me_update",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Get my profile",
        "tags": [
          "Profiles"
        ]
      }
    },
    "/profiles/profiles/stats/": {
      "get": {
        "description": "Get comprehensive profile statistics",
        "operationId": "profiles_profiles_stats_retrieve",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Get profile statistics",
        "tags": [
          "Profiles"
        ]
      }
    },
    "/profiles/profiles/{id}/": {
      "delete": {
        "description": "Delete a user profile",
        "operationId": "profiles_profiles_destroy",
        "parameters": [
          {
            "description": "A unique integer value identifying this User Profile.",
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
        "summary": "Delete user profile",
        "tags": [
          "Profiles"
        ]
      },
      "get": {
        "description": "Get detailed information about a specific user profile",
        "operationId": "profiles_profiles_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this User Profile.",
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
                  "$ref": "#/components/schemas/UserProfile"
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
        "summary": "Get user profile",
        "tags": [
          "Profiles"
        ]
      },
      "patch": {
        "description": "Partially update user profile information",
        "operationId": "profiles_profiles_partial_update",
        "parameters": [
          {
            "description": "A unique integer value identifying this User Profile.",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Partially update user profile",
        "tags": [
          "Profiles"
        ]
      },
      "put": {
        "description": "Update user profile information",
        "operationId": "profiles_profiles_update",
        "parameters": [
          {
            "description": "A unique integer value identifying this User Profile.",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Update user profile",
        "tags": [
          "Profiles"
        ]
      }
    }
  }
};