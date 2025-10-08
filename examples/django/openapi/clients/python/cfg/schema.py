"""
OpenAPI Schema

This file contains the complete OpenAPI specification for this API.
It can be used for documentation, validation, or code generation.
"""

from typing import Any, Dict

OPENAPI_SCHEMA: Dict[str, Any] = {
    "openapi": "3.0.3",
    "info": {
        "title": "Django CFG Sample API",
        "version": "1.0.0",
        "description": "Complete API documentation for Django CFG sample project",
        "x-django-metadata": {
            "group": "cfg",
            "apps": [
                "django_cfg_support",
                "django_cfg_accounts",
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
        "/django_cfg_accounts/otp/request/": {
            "post": {
                "operationId": "django_cfg_accounts_otp_request_create",
                "description": "Request OTP code to email or phone.",
                "tags": [
                    "django_cfg_accounts"
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_accounts/otp/verify/": {
            "post": {
                "operationId": "django_cfg_accounts_otp_verify_create",
                "description": "Verify OTP code and return JWT tokens.",
                "tags": [
                    "django_cfg_accounts"
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_accounts/profile/": {
            "get": {
                "operationId": "django_cfg_accounts_profile_retrieve",
                "description": "Retrieve the current authenticated user's profile information.",
                "summary": "Get current user profile",
                "tags": [
                    "User Profile"
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
                }
            }
        },
        "/django_cfg_accounts/profile/avatar/": {
            "post": {
                "operationId": "django_cfg_accounts_profile_avatar_create",
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
                }
            }
        },
        "/django_cfg_accounts/profile/partial/": {
            "put": {
                "operationId": "django_cfg_accounts_profile_partial_update",
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
                }
            },
            "patch": {
                "operationId": "django_cfg_accounts_profile_partial_partial_update",
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
                }
            }
        },
        "/django_cfg_accounts/profile/update/": {
            "put": {
                "operationId": "django_cfg_accounts_profile_update_update",
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
                }
            },
            "patch": {
                "operationId": "django_cfg_accounts_profile_update_partial_update",
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
                }
            }
        },
        "/django_cfg_accounts/token/refresh/": {
            "post": {
                "operationId": "django_cfg_accounts_token_refresh_create",
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
                }
            }
        },
        "/django_cfg_leads/leads/": {
            "get": {
                "operationId": "django_cfg_leads_leads_list",
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
                    "django_cfg_leads"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            },
            "post": {
                "operationId": "django_cfg_leads_leads_create",
                "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
                "tags": [
                    "django_cfg_leads"
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_leads/leads/{id}/": {
            "get": {
                "operationId": "django_cfg_leads_leads_retrieve",
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
                    "django_cfg_leads"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            },
            "put": {
                "operationId": "django_cfg_leads_leads_update",
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
                    "django_cfg_leads"
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            },
            "patch": {
                "operationId": "django_cfg_leads_leads_partial_update",
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
                    "django_cfg_leads"
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            },
            "delete": {
                "operationId": "django_cfg_leads_leads_destroy",
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
                    "django_cfg_leads"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    },
                    {}
                ],
                "responses": {
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/django_cfg_leads/leads/submit/": {
            "post": {
                "operationId": "django_cfg_leads_leads_submit_create",
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_newsletter/bulk/": {
            "post": {
                "operationId": "django_cfg_newsletter_bulk_create",
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
                }
            }
        },
        "/django_cfg_newsletter/campaigns/": {
            "get": {
                "operationId": "django_cfg_newsletter_campaigns_list",
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
                                    "$ref": "#/components/schemas/PaginatedNewsletterCampaignList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "django_cfg_newsletter_campaigns_create",
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_newsletter/campaigns/{id}/": {
            "get": {
                "operationId": "django_cfg_newsletter_campaigns_retrieve",
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
                                    "$ref": "#/components/schemas/NewsletterCampaign"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "django_cfg_newsletter_campaigns_update",
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
                                    "$ref": "#/components/schemas/NewsletterCampaign"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "django_cfg_newsletter_campaigns_partial_update",
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
                    "django_cfg_newsletter"
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
                                    "$ref": "#/components/schemas/NewsletterCampaign"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "django_cfg_newsletter_campaigns_destroy",
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    }
                ],
                "responses": {
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/django_cfg_newsletter/campaigns/send/": {
            "post": {
                "operationId": "django_cfg_newsletter_campaigns_send_create",
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
                }
            }
        },
        "/django_cfg_newsletter/logs/": {
            "get": {
                "operationId": "django_cfg_newsletter_logs_list",
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
                                    "$ref": "#/components/schemas/PaginatedEmailLogList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/django_cfg_newsletter/newsletters/": {
            "get": {
                "operationId": "django_cfg_newsletter_newsletters_list",
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_newsletter/newsletters/{id}/": {
            "get": {
                "operationId": "django_cfg_newsletter_newsletters_retrieve",
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_newsletter/subscribe/": {
            "post": {
                "operationId": "django_cfg_newsletter_subscribe_create",
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_newsletter/subscriptions/": {
            "get": {
                "operationId": "django_cfg_newsletter_subscriptions_list",
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
                                    "$ref": "#/components/schemas/PaginatedNewsletterSubscriptionList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/django_cfg_newsletter/test/": {
            "post": {
                "operationId": "django_cfg_newsletter_test_create",
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_newsletter/unsubscribe/": {
            "post": {
                "operationId": "django_cfg_newsletter_unsubscribe_create",
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            },
            "put": {
                "operationId": "django_cfg_newsletter_unsubscribe_update",
                "description": "Handle newsletter unsubscriptions.",
                "tags": [
                    "django_cfg_newsletter"
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            },
            "patch": {
                "operationId": "django_cfg_newsletter_unsubscribe_partial_update",
                "description": "Handle newsletter unsubscriptions.",
                "tags": [
                    "django_cfg_newsletter"
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_support/tickets/": {
            "get": {
                "operationId": "django_cfg_support_tickets_list",
                "description": "ViewSet for managing support tickets.",
                "tags": [
                    "django_cfg_support"
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
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/Ticket"
                                    }
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "django_cfg_support_tickets_create",
                "description": "ViewSet for managing support tickets.",
                "tags": [
                    "django_cfg_support"
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_support/tickets/{ticket_uuid}/messages/": {
            "get": {
                "operationId": "django_cfg_support_tickets_messages_list",
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
                    "django_cfg_support"
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
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/Message"
                                    }
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "django_cfg_support_tickets_messages_create",
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
                    "django_cfg_support"
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
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
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
                }
            }
        },
        "/django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/": {
            "get": {
                "operationId": "django_cfg_support_tickets_messages_retrieve",
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
                    "django_cfg_support"
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
                                    "$ref": "#/components/schemas/Message"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "django_cfg_support_tickets_messages_update",
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
                    "django_cfg_support"
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
                                    "$ref": "#/components/schemas/Message"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "django_cfg_support_tickets_messages_partial_update",
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
                    "django_cfg_support"
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
                                    "$ref": "#/components/schemas/Message"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "django_cfg_support_tickets_messages_destroy",
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
                    "django_cfg_support"
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
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/django_cfg_support/tickets/{uuid}/": {
            "get": {
                "operationId": "django_cfg_support_tickets_retrieve",
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
                    "django_cfg_support"
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
                                    "$ref": "#/components/schemas/Ticket"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "django_cfg_support_tickets_update",
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
                    "django_cfg_support"
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
                                    "$ref": "#/components/schemas/Ticket"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "django_cfg_support_tickets_partial_update",
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
                    "django_cfg_support"
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
                                    "$ref": "#/components/schemas/Ticket"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "django_cfg_support_tickets_destroy",
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
                    "django_cfg_support"
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
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/payments/api-keys/": {
            "get": {
                "operationId": "payments_api_keys_list",
                "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "is_active",
                        "schema": {
                            "type": "boolean"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "query",
                        "name": "user",
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
                                    "$ref": "#/components/schemas/PaginatedAPIKeyListList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "payments_api_keys_create",
                "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyCreateRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIKeyCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/api-keys/{id}/": {
            "get": {
                "operationId": "payments_api_keys_retrieve",
                "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "payments_api_keys_update",
                "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyUpdateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyUpdateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyUpdateRequest"
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
                                    "$ref": "#/components/schemas/APIKeyUpdate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "payments_api_keys_partial_update",
                "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedAPIKeyUpdateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedAPIKeyUpdateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedAPIKeyUpdateRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIKeyUpdate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "payments_api_keys_destroy",
                "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/payments/api-keys/{id}/perform_action/": {
            "post": {
                "operationId": "payments_api_keys_perform_action_create",
                "description": "Perform action on API key.\n\nPOST /api/api-keys/{id}/perform_action/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/api-keys/analytics/": {
            "get": {
                "operationId": "payments_api_keys_analytics_retrieve",
                "description": "Get API key analytics.\n\nGET /api/api-keys/analytics/?days=30",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/api-keys/by_user/": {
            "get": {
                "operationId": "payments_api_keys_by_user_retrieve",
                "description": "Get API keys grouped by user.\n\nGET /api/api-keys/by_user/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/api-keys/create/": {
            "post": {
                "operationId": "payments_api_keys_create_create",
                "description": "Standalone API key creation endpoint: /api/api-keys/create/\n\nSimplified endpoint for API key creation.",
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyCreateRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIKeyCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/api-keys/expiring_soon/": {
            "get": {
                "operationId": "payments_api_keys_expiring_soon_retrieve",
                "description": "Get API keys expiring soon.\n\nGET /api/api-keys/expiring_soon/?days=7",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/api-keys/health/": {
            "get": {
                "operationId": "payments_api_keys_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/api-keys/stats/": {
            "get": {
                "operationId": "payments_api_keys_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/api-keys/validate/": {
            "post": {
                "operationId": "payments_api_keys_validate_create",
                "description": "Standalone endpoint to validate an API key and return key information",
                "summary": "Validate API Key (Standalone)",
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyValidationRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyValidationRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyValidationRequest"
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
                                    "$ref": "#/components/schemas/APIKeyValidationResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/api-keys/validate_key/": {
            "post": {
                "operationId": "payments_api_keys_validate_key_create",
                "description": "Validate an API key and return key information",
                "summary": "Validate API Key",
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyValidationRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyValidationRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyValidationRequest"
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
                                    "$ref": "#/components/schemas/APIKeyValidationResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/balances/": {
            "get": {
                "operationId": "payments_balances_list",
                "description": "User balance ViewSet: /api/balances/\n\nRead-only access to user balances with statistics.",
                "parameters": [
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "query",
                        "name": "user",
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
                                    "$ref": "#/components/schemas/PaginatedUserBalanceList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/balances/{id}/": {
            "get": {
                "operationId": "payments_balances_retrieve",
                "description": "User balance ViewSet: /api/balances/\n\nRead-only access to user balances with statistics.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this User Balance.",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/UserBalance"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/balances/analytics/": {
            "get": {
                "operationId": "payments_balances_analytics_retrieve",
                "description": "Get balance analytics.\n\nGET /api/balances/analytics/?days=30",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/UserBalance"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/balances/health/": {
            "get": {
                "operationId": "payments_balances_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/UserBalance"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/balances/stats/": {
            "get": {
                "operationId": "payments_balances_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/UserBalance"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/balances/summary/": {
            "get": {
                "operationId": "payments_balances_summary_retrieve",
                "description": "Get balance summary for all users.\n\nGET /api/balances/summary/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/UserBalance"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/": {
            "get": {
                "operationId": "payments_currencies_list",
                "description": "Currency ViewSet: /api/currencies/\n\nRead-only access to currency information with conversion capabilities.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "currency_type",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "1fd14ececc7d641f",
                            "enum": [
                                "crypto",
                                "fiat"
                            ]
                        },
                        "description": "Type of currency\n\n* `fiat` - Fiat Currency\n* `crypto` - Cryptocurrency"
                    },
                    {
                        "in": "query",
                        "name": "is_active",
                        "schema": {
                            "type": "boolean"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedCurrencyListList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "payments_currencies_create",
                "description": "Disable create action.",
                "tags": [
                    "payments"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/{id}/": {
            "get": {
                "operationId": "payments_currencies_retrieve",
                "description": "Currency ViewSet: /api/currencies/\n\nRead-only access to currency information with conversion capabilities.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Currency.",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/{id}/networks/": {
            "get": {
                "operationId": "payments_currencies_networks_retrieve",
                "description": "Get networks for specific currency.\n\nGET /api/currencies/{id}/networks/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Currency.",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/{id}/providers/": {
            "get": {
                "operationId": "payments_currencies_providers_retrieve",
                "description": "Get providers supporting specific currency.\n\nGET /api/currencies/{id}/providers/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Currency.",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/convert/": {
            "post": {
                "operationId": "payments_currencies_convert_create",
                "description": "Convert between currencies.\n\nPOST /api/currencies/convert/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/crypto/": {
            "get": {
                "operationId": "payments_currencies_crypto_retrieve",
                "description": "Get only cryptocurrencies.\n\nGET /api/currencies/crypto/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/fiat/": {
            "get": {
                "operationId": "payments_currencies_fiat_retrieve",
                "description": "Get only fiat currencies.\n\nGET /api/currencies/fiat/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/health/": {
            "get": {
                "operationId": "payments_currencies_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/rates/": {
            "get": {
                "operationId": "payments_currencies_rates_retrieve",
                "description": "Get current exchange rates for specified currencies",
                "summary": "Get exchange rates",
                "parameters": [
                    {
                        "in": "query",
                        "name": "base_currency",
                        "schema": {
                            "type": "string"
                        },
                        "description": "Base currency code (e.g., USD)",
                        "required": True
                    },
                    {
                        "in": "query",
                        "name": "currencies",
                        "schema": {
                            "type": "string"
                        },
                        "description": "Comma-separated list of target currency codes (e.g., BTC,ETH,USDT)",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/stable/": {
            "get": {
                "operationId": "payments_currencies_stable_retrieve",
                "description": "Get only stablecoins.\n\nGET /api/currencies/stable/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/stats/": {
            "get": {
                "operationId": "payments_currencies_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/currencies/supported/": {
            "get": {
                "operationId": "payments_currencies_supported_retrieve",
                "description": "Get list of supported currencies from payment providers",
                "summary": "Get supported currencies",
                "parameters": [
                    {
                        "in": "query",
                        "name": "currency_type",
                        "schema": {
                            "type": "string",
                            "enum": [
                                "crypto",
                                "fiat",
                                "stablecoin"
                            ]
                        },
                        "description": "Currency type filter: crypto, fiat, or stablecoin"
                    },
                    {
                        "in": "query",
                        "name": "provider",
                        "schema": {
                            "type": "string"
                        },
                        "description": "Payment provider name (e.g., nowpayments)"
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Currency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/endpoint-groups/": {
            "get": {
                "operationId": "payments_endpoint_groups_list",
                "description": "Endpoint Group ViewSet: /api/endpoint-groups/\n\nRead-only access to endpoint group information.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "is_enabled",
                        "schema": {
                            "type": "boolean"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedEndpointGroupList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/endpoint-groups/{id}/": {
            "get": {
                "operationId": "payments_endpoint_groups_retrieve",
                "description": "Endpoint Group ViewSet: /api/endpoint-groups/\n\nRead-only access to endpoint group information.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Endpoint Group.",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/EndpointGroup"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/endpoint-groups/available/": {
            "get": {
                "operationId": "payments_endpoint_groups_available_retrieve",
                "description": "Get available endpoint groups for subscription.\n\nGET /api/endpoint-groups/available/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/EndpointGroup"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/endpoint-groups/health/": {
            "get": {
                "operationId": "payments_endpoint_groups_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/EndpointGroup"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/endpoint-groups/stats/": {
            "get": {
                "operationId": "payments_endpoint_groups_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/EndpointGroup"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/health/": {
            "get": {
                "operationId": "payments_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/networks/": {
            "get": {
                "operationId": "payments_networks_list",
                "description": "Network ViewSet: /api/networks/\n\nRead-only access to blockchain network information.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "is_active",
                        "schema": {
                            "type": "boolean"
                        }
                    },
                    {
                        "in": "query",
                        "name": "native_currency__code",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedNetworkList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/networks/{id}/": {
            "get": {
                "operationId": "payments_networks_retrieve",
                "description": "Network ViewSet: /api/networks/\n\nRead-only access to blockchain network information.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Network.",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Network"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/networks/by_currency/": {
            "get": {
                "operationId": "payments_networks_by_currency_retrieve",
                "description": "Get networks grouped by currency.\n\nGET /api/networks/by_currency/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Network"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/networks/health/": {
            "get": {
                "operationId": "payments_networks_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Network"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/networks/stats/": {
            "get": {
                "operationId": "payments_networks_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Network"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/overview/dashboard/api_keys_overview/": {
            "get": {
                "operationId": "payments_overview_dashboard_api_keys_overview_retrieve",
                "description": "Get API keys overview",
                "summary": "API Keys Overview",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeysOverview"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/overview/dashboard/balance_overview/": {
            "get": {
                "operationId": "payments_overview_dashboard_balance_overview_retrieve",
                "description": "Get user balance overview",
                "summary": "Balance Overview",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/BalanceOverview"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/overview/dashboard/chart_data/": {
            "get": {
                "operationId": "payments_overview_dashboard_chart_data_retrieve",
                "description": "Get chart data for payments visualization",
                "summary": "Payments Chart Data",
                "parameters": [
                    {
                        "in": "query",
                        "name": "period",
                        "schema": {
                            "type": "string",
                            "enum": [
                                "1y",
                                "30d",
                                "7d",
                                "90d"
                            ],
                            "default": "30d"
                        },
                        "description": "Time period for chart data"
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaymentsChartResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/overview/dashboard/metrics/": {
            "get": {
                "operationId": "payments_overview_dashboard_metrics_retrieve",
                "description": "Get payments dashboard metrics including balance, subscriptions, API keys, and payments",
                "summary": "Payments Dashboard Metrics",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaymentsMetrics"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/overview/dashboard/overview/": {
            "get": {
                "operationId": "payments_overview_dashboard_overview_retrieve",
                "description": "Get complete payments dashboard overview with metrics, recent payments, and analytics",
                "summary": "Payments Dashboard Overview",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaymentsDashboardOverview"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/overview/dashboard/payment_analytics/": {
            "get": {
                "operationId": "payments_overview_dashboard_payment_analytics_retrieve",
                "description": "Get analytics for payments by currency and provider",
                "summary": "Payment Analytics",
                "parameters": [
                    {
                        "in": "query",
                        "name": "limit",
                        "schema": {
                            "type": "integer",
                            "default": 10
                        },
                        "description": "Number of analytics items to return"
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaymentAnalyticsResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/overview/dashboard/recent_payments/": {
            "get": {
                "operationId": "payments_overview_dashboard_recent_payments_list",
                "description": "Get recent payments for the user",
                "summary": "Recent Payments",
                "parameters": [
                    {
                        "in": "query",
                        "name": "limit",
                        "schema": {
                            "type": "integer",
                            "default": 10
                        },
                        "description": "Number of payments to return"
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
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedRecentPaymentList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/overview/dashboard/recent_transactions/": {
            "get": {
                "operationId": "payments_overview_dashboard_recent_transactions_list",
                "description": "Get recent balance transactions for the user",
                "summary": "Recent Transactions",
                "parameters": [
                    {
                        "in": "query",
                        "name": "limit",
                        "schema": {
                            "type": "integer",
                            "default": 10
                        },
                        "description": "Number of transactions to return"
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
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedRecentTransactionList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/overview/dashboard/subscription_overview/": {
            "get": {
                "operationId": "payments_overview_dashboard_subscription_overview_retrieve",
                "description": "Get current subscription overview",
                "summary": "Subscription Overview",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/SubscriptionOverview"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/payments/": {
            "get": {
                "operationId": "payments_payments_list",
                "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "currency__code",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "provider",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "47694db6bd068cb3",
                            "enum": [
                                "nowpayments"
                            ]
                        },
                        "description": "Payment provider\n\n* `nowpayments` - NowPayments"
                    },
                    {
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "query",
                        "name": "status",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "59d07a8608d1bdb9",
                            "enum": [
                                "cancelled",
                                "completed",
                                "confirmed",
                                "confirming",
                                "expired",
                                "failed",
                                "pending",
                                "refunded"
                            ]
                        },
                        "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded"
                    },
                    {
                        "in": "query",
                        "name": "user",
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
                                    "$ref": "#/components/schemas/PaginatedPaymentListList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "payments_payments_create",
                "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PaymentCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/payments/{id}/": {
            "get": {
                "operationId": "payments_payments_retrieve",
                "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "payments_payments_update",
                "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "payments_payments_partial_update",
                "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedPaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedPaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedPaymentRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "payments_payments_destroy",
                "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/payments/payments/{id}/cancel/": {
            "post": {
                "operationId": "payments_payments_cancel_create",
                "description": "Cancel payment.\n\nPOST /api/v1/payments/{id}/cancel/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/payments/{id}/check_status/": {
            "post": {
                "operationId": "payments_payments_check_status_create",
                "description": "Check payment status with provider.\n\nPOST /api/v1/payments/{id}/check_status/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/payments/analytics/": {
            "get": {
                "operationId": "payments_payments_analytics_retrieve",
                "description": "Get payment analytics.\n\nGET /api/v1/payments/analytics/?days=30",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/payments/by_provider/": {
            "get": {
                "operationId": "payments_payments_by_provider_retrieve",
                "description": "Get payments grouped by provider.\n\nGET /api/v1/payments/by_provider/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/payments/create/": {
            "post": {
                "operationId": "payments_payments_create_create",
                "description": "Standalone payment creation endpoint: /api/v1/payments/create/\n\nSimplified endpoint for payment creation without full ViewSet overhead.",
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PaymentCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/payments/health/": {
            "get": {
                "operationId": "payments_payments_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/payments/stats/": {
            "get": {
                "operationId": "payments_payments_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/payments/status/{id}/": {
            "get": {
                "operationId": "payments_payments_status_retrieve",
                "description": "Standalone payment status endpoint: /api/v1/payments/{id}/status/\n\nQuick status check without full ViewSet overhead.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/provider-currencies/": {
            "get": {
                "operationId": "payments_provider_currencies_list",
                "description": "Provider Currency ViewSet: /api/provider-currencies/\n\nRead-only access to provider-specific currency information.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "currency__code",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "query",
                        "name": "is_enabled",
                        "schema": {
                            "type": "boolean"
                        }
                    },
                    {
                        "in": "query",
                        "name": "network__code",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "provider",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedProviderCurrencyList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/provider-currencies/{id}/": {
            "get": {
                "operationId": "payments_provider_currencies_retrieve",
                "description": "Provider Currency ViewSet: /api/provider-currencies/\n\nRead-only access to provider-specific currency information.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Provider Currency.",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/ProviderCurrency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/provider-currencies/by_provider/": {
            "get": {
                "operationId": "payments_provider_currencies_by_provider_retrieve",
                "description": "Get provider currencies grouped by provider.\n\nGET /api/provider-currencies/by_provider/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/ProviderCurrency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/provider-currencies/health/": {
            "get": {
                "operationId": "payments_provider_currencies_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/ProviderCurrency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/provider-currencies/limits/": {
            "get": {
                "operationId": "payments_provider_currencies_limits_retrieve",
                "description": "Get currency limits by provider.\n\nGET /api/provider-currencies/limits/?provider=nowpayments",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/ProviderCurrency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/provider-currencies/stats/": {
            "get": {
                "operationId": "payments_provider_currencies_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/ProviderCurrency"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/subscriptions/": {
            "get": {
                "operationId": "payments_subscriptions_list",
                "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
                "parameters": [
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "query",
                        "name": "status",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "20d0bcc8b3c2bafa",
                            "enum": [
                                "active",
                                "cancelled",
                                "expired",
                                "inactive",
                                "suspended"
                            ]
                        },
                        "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired"
                    },
                    {
                        "in": "query",
                        "name": "tier",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "776e806f04431486",
                            "enum": [
                                "basic",
                                "enterprise",
                                "free",
                                "pro"
                            ]
                        },
                        "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier"
                    },
                    {
                        "in": "query",
                        "name": "user",
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
                                    "$ref": "#/components/schemas/PaginatedSubscriptionListList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "payments_subscriptions_create",
                "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionCreateRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SubscriptionCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/subscriptions/{id}/": {
            "get": {
                "operationId": "payments_subscriptions_retrieve",
                "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "payments_subscriptions_update",
                "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "payments_subscriptions_partial_update",
                "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedSubscriptionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedSubscriptionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedSubscriptionRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "payments_subscriptions_destroy",
                "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/payments/subscriptions/{id}/increment_usage/": {
            "post": {
                "operationId": "payments_subscriptions_increment_usage_create",
                "description": "Increment subscription usage.\n\nPOST /api/subscriptions/{id}/increment_usage/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/subscriptions/{id}/update_status/": {
            "post": {
                "operationId": "payments_subscriptions_update_status_create",
                "description": "Update subscription status.\n\nPOST /api/subscriptions/{id}/update_status/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/subscriptions/analytics/": {
            "get": {
                "operationId": "payments_subscriptions_analytics_retrieve",
                "description": "Get subscription analytics.\n\nGET /api/subscriptions/analytics/?days=30",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/subscriptions/by_status/": {
            "get": {
                "operationId": "payments_subscriptions_by_status_retrieve",
                "description": "Get subscriptions grouped by status.\n\nGET /api/subscriptions/by_status/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/subscriptions/by_tier/": {
            "get": {
                "operationId": "payments_subscriptions_by_tier_retrieve",
                "description": "Get subscriptions grouped by tier.\n\nGET /api/subscriptions/by_tier/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/subscriptions/health/": {
            "get": {
                "operationId": "payments_subscriptions_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/subscriptions/stats/": {
            "get": {
                "operationId": "payments_subscriptions_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/tariffs/": {
            "get": {
                "operationId": "payments_tariffs_list",
                "description": "Tariff ViewSet: /api/tariffs/\n\nRead-only access to tariff information for subscription selection.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "is_active",
                        "schema": {
                            "type": "boolean"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedTariffList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/tariffs/{id}/": {
            "get": {
                "operationId": "payments_tariffs_retrieve",
                "description": "Tariff ViewSet: /api/tariffs/\n\nRead-only access to tariff information for subscription selection.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Tariff.",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Tariff"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/tariffs/{id}/endpoint_groups/": {
            "get": {
                "operationId": "payments_tariffs_endpoint_groups_retrieve",
                "description": "Get endpoint groups for specific tariff.\n\nGET /api/tariffs/{id}/endpoint_groups/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "integer"
                        },
                        "description": "A unique integer value identifying this Tariff.",
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Tariff"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/tariffs/free/": {
            "get": {
                "operationId": "payments_tariffs_free_retrieve",
                "description": "Get free tariffs.\n\nGET /api/tariffs/free/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Tariff"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/tariffs/health/": {
            "get": {
                "operationId": "payments_tariffs_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Tariff"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/tariffs/paid/": {
            "get": {
                "operationId": "payments_tariffs_paid_retrieve",
                "description": "Get paid tariffs.\n\nGET /api/tariffs/paid/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Tariff"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/tariffs/stats/": {
            "get": {
                "operationId": "payments_tariffs_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Tariff"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/transactions/": {
            "get": {
                "operationId": "payments_transactions_list",
                "description": "Transaction ViewSet: /api/transactions/\n\nRead-only access to transaction history with filtering.",
                "parameters": [
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "payment_id",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "query",
                        "name": "transaction_type",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "25d1662d4db37694",
                            "enum": [
                                "adjustment",
                                "bonus",
                                "deposit",
                                "fee",
                                "payment",
                                "refund",
                                "withdrawal"
                            ]
                        },
                        "description": "Type of transaction\n\n* `deposit` - Deposit\n* `withdrawal` - Withdrawal\n* `payment` - Payment\n* `refund` - Refund\n* `fee` - Fee\n* `bonus` - Bonus\n* `adjustment` - Adjustment"
                    },
                    {
                        "in": "query",
                        "name": "user",
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
                                    "$ref": "#/components/schemas/PaginatedTransactionList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/transactions/{id}/": {
            "get": {
                "operationId": "payments_transactions_retrieve",
                "description": "Transaction ViewSet: /api/transactions/\n\nRead-only access to transaction history with filtering.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Transaction"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/transactions/by_type/": {
            "get": {
                "operationId": "payments_transactions_by_type_retrieve",
                "description": "Get transactions grouped by type.\n\nGET /api/transactions/by_type/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Transaction"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/transactions/health/": {
            "get": {
                "operationId": "payments_transactions_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Transaction"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/transactions/recent/": {
            "get": {
                "operationId": "payments_transactions_recent_retrieve",
                "description": "Get recent transactions.\n\nGET /api/transactions/recent/?limit=10",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Transaction"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/transactions/stats/": {
            "get": {
                "operationId": "payments_transactions_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Transaction"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/": {
            "get": {
                "operationId": "payments_users_list",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "currency__code",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "provider",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "47694db6bd068cb3",
                            "enum": [
                                "nowpayments"
                            ]
                        },
                        "description": "Payment provider\n\n* `nowpayments` - NowPayments"
                    },
                    {
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "query",
                        "name": "status",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "59d07a8608d1bdb9",
                            "enum": [
                                "cancelled",
                                "completed",
                                "confirmed",
                                "confirming",
                                "expired",
                                "failed",
                                "pending",
                                "refunded"
                            ]
                        },
                        "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded"
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedPaymentListList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "payments_users_create",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PaymentCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{id}/": {
            "get": {
                "operationId": "payments_users_retrieve",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "payments_users_update",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "payments_users_partial_update",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedPaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedPaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedPaymentRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "payments_users_destroy",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/payments/users/{id}/cancel/": {
            "post": {
                "operationId": "payments_users_cancel_create",
                "description": "Cancel payment.\n\nPOST /api/v1/users/{user_id}/payments/{id}/cancel/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{id}/check_status/": {
            "post": {
                "operationId": "payments_users_check_status_create",
                "description": "Check payment status with provider.\n\nPOST /api/v1/users/{user_id}/payments/{id}/check_status/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/api-keys/": {
            "get": {
                "operationId": "payments_users_api_keys_list",
                "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "is_active",
                        "schema": {
                            "type": "boolean"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedAPIKeyListList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "payments_users_api_keys_create",
                "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyCreateRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIKeyCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/api-keys/{id}/": {
            "get": {
                "operationId": "payments_users_api_keys_retrieve",
                "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "payments_users_api_keys_update",
                "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyUpdateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyUpdateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/APIKeyUpdateRequest"
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
                                    "$ref": "#/components/schemas/APIKeyUpdate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "payments_users_api_keys_partial_update",
                "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedAPIKeyUpdateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedAPIKeyUpdateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedAPIKeyUpdateRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/APIKeyUpdate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "payments_users_api_keys_destroy",
                "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/payments/users/{user_pk}/api-keys/{id}/perform_action/": {
            "post": {
                "operationId": "payments_users_api_keys_perform_action_create",
                "description": "Perform action on API key.\n\nPOST /api/users/{user_id}/api-keys/{id}/perform_action/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/api-keys/active/": {
            "get": {
                "operationId": "payments_users_api_keys_active_retrieve",
                "description": "Get user's active API keys.\n\nGET /api/users/{user_id}/api-keys/active/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/api-keys/health/": {
            "get": {
                "operationId": "payments_users_api_keys_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/api-keys/stats/": {
            "get": {
                "operationId": "payments_users_api_keys_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/api-keys/summary/": {
            "get": {
                "operationId": "payments_users_api_keys_summary_retrieve",
                "description": "Get user API key summary.\n\nGET /api/users/{user_id}/api-keys/summary/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this API key"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/APIKeyDetail"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/payments/": {
            "get": {
                "operationId": "payments_users_payments_list",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "currency__code",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "provider",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "47694db6bd068cb3",
                            "enum": [
                                "nowpayments"
                            ]
                        },
                        "description": "Payment provider\n\n* `nowpayments` - NowPayments"
                    },
                    {
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "query",
                        "name": "status",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "59d07a8608d1bdb9",
                            "enum": [
                                "cancelled",
                                "completed",
                                "confirmed",
                                "confirming",
                                "expired",
                                "failed",
                                "pending",
                                "refunded"
                            ]
                        },
                        "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded"
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedPaymentListList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "payments_users_payments_create",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentCreateRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PaymentCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/payments/{id}/": {
            "get": {
                "operationId": "payments_users_payments_retrieve",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "payments_users_payments_update",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "payments_users_payments_partial_update",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedPaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedPaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedPaymentRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "payments_users_payments_destroy",
                "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/payments/users/{user_pk}/payments/{id}/cancel/": {
            "post": {
                "operationId": "payments_users_payments_cancel_create",
                "description": "Cancel payment.\n\nPOST /api/v1/users/{user_id}/payments/{id}/cancel/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/payments/{id}/check_status/": {
            "post": {
                "operationId": "payments_users_payments_check_status_create",
                "description": "Check payment status with provider.\n\nPOST /api/v1/users/{user_id}/payments/{id}/check_status/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PaymentRequest"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/payments/health/": {
            "get": {
                "operationId": "payments_users_payments_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/payments/stats/": {
            "get": {
                "operationId": "payments_users_payments_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/payments/summary/": {
            "get": {
                "operationId": "payments_users_payments_summary_retrieve",
                "description": "Get user payment summary.\n\nGET /api/v1/users/{user_id}/payments/summary/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who created this payment"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/subscriptions/": {
            "get": {
                "operationId": "payments_users_subscriptions_list",
                "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
                "parameters": [
                    {
                        "name": "ordering",
                        "required": False,
                        "in": "query",
                        "description": "Which field to use when ordering the results.",
                        "schema": {
                            "type": "string"
                        }
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
                        "name": "search",
                        "required": False,
                        "in": "query",
                        "description": "A search term.",
                        "schema": {
                            "type": "string"
                        }
                    },
                    {
                        "in": "query",
                        "name": "status",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "20d0bcc8b3c2bafa",
                            "enum": [
                                "active",
                                "cancelled",
                                "expired",
                                "inactive",
                                "suspended"
                            ]
                        },
                        "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired"
                    },
                    {
                        "in": "query",
                        "name": "tier",
                        "schema": {
                            "type": "string",
                            "x-spec-enum-id": "776e806f04431486",
                            "enum": [
                                "basic",
                                "enterprise",
                                "free",
                                "pro"
                            ]
                        },
                        "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier"
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/PaginatedSubscriptionListList"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "payments_users_subscriptions_create",
                "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionCreateRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionCreateRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionCreateRequest"
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
                    "201": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SubscriptionCreate"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/subscriptions/{id}/": {
            "get": {
                "operationId": "payments_users_subscriptions_retrieve",
                "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "put": {
                "operationId": "payments_users_subscriptions_update",
                "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "patch": {
                "operationId": "payments_users_subscriptions_partial_update",
                "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedSubscriptionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedSubscriptionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/PatchedSubscriptionRequest"
                            }
                        }
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
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "delete": {
                "operationId": "payments_users_subscriptions_destroy",
                "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                    "204": {
                        "description": "No response body"
                    }
                }
            }
        },
        "/payments/users/{user_pk}/subscriptions/{id}/increment_usage/": {
            "post": {
                "operationId": "payments_users_subscriptions_increment_usage_create",
                "description": "Increment subscription usage.\n\nPOST /api/users/{user_id}/subscriptions/{id}/increment_usage/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/subscriptions/{id}/update_status/": {
            "post": {
                "operationId": "payments_users_subscriptions_update_status_create",
                "description": "Update subscription status.\n\nPOST /api/users/{user_id}/subscriptions/{id}/update_status/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for this record"
                        },
                        "required": True
                    },
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/SubscriptionRequest"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/subscriptions/active/": {
            "get": {
                "operationId": "payments_users_subscriptions_active_retrieve",
                "description": "Get user's active subscription.\n\nGET /api/users/{user_id}/subscriptions/active/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/subscriptions/health/": {
            "get": {
                "operationId": "payments_users_subscriptions_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/subscriptions/stats/": {
            "get": {
                "operationId": "payments_users_subscriptions_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/{user_pk}/subscriptions/summary/": {
            "get": {
                "operationId": "payments_users_subscriptions_summary_retrieve",
                "description": "Get user subscription summary.\n\nGET /api/users/{user_id}/subscriptions/summary/",
                "parameters": [
                    {
                        "in": "path",
                        "name": "user_pk",
                        "schema": {
                            "type": "integer",
                            "description": "User who owns this subscription"
                        },
                        "required": True
                    }
                ],
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Subscription"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/health/": {
            "get": {
                "operationId": "payments_users_health_retrieve",
                "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/stats/": {
            "get": {
                "operationId": "payments_users_stats_retrieve",
                "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/users/summary/": {
            "get": {
                "operationId": "payments_users_summary_retrieve",
                "description": "Get user payment summary.\n\nGET /api/v1/users/{user_id}/payments/summary/",
                "tags": [
                    "payments"
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
                                    "$ref": "#/components/schemas/Payment"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/webhooks/{provider}/": {
            "get": {
                "operationId": "payments_webhooks_retrieve",
                "description": "Get webhook endpoint information for debugging and configuration",
                "summary": "Webhook Endpoint Info",
                "parameters": [
                    {
                        "in": "path",
                        "name": "provider",
                        "schema": {
                            "type": "string"
                        },
                        "description": "Payment provider name",
                        "required": True
                    }
                ],
                "tags": [
                    "Webhooks"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    },
                    {}
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/WebhookResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            },
            "post": {
                "operationId": "payments_webhooks_create",
                "description": "Process incoming webhook from payment provider",
                "summary": "Process Webhook",
                "parameters": [
                    {
                        "in": "path",
                        "name": "provider",
                        "schema": {
                            "type": "string"
                        },
                        "description": "Payment provider name (nowpayments, stripe, etc.)",
                        "required": True
                    }
                ],
                "tags": [
                    "Webhooks"
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/WebhookResponseRequest"
                            }
                        },
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "$ref": "#/components/schemas/WebhookResponseRequest"
                            }
                        },
                        "multipart/form-data": {
                            "schema": {
                                "$ref": "#/components/schemas/WebhookResponseRequest"
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
                    },
                    {}
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/WebhookResponse"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/webhooks/health/": {
            "get": {
                "operationId": "payments_webhooks_health_retrieve",
                "description": "Check webhook service health status and recent activity metrics",
                "summary": "Webhook Health Check",
                "tags": [
                    "Webhooks"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    },
                    {}
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/WebhookHealth"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/webhooks/providers/": {
            "get": {
                "operationId": "payments_webhooks_providers_retrieve",
                "description": "Get list of supported webhook providers with configuration details",
                "summary": "Supported Webhook Providers",
                "tags": [
                    "Webhooks"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    },
                    {}
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SupportedProviders"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/payments/webhooks/stats/": {
            "get": {
                "operationId": "payments_webhooks_stats_retrieve",
                "description": "Get webhook processing statistics for a given time period",
                "summary": "Webhook Statistics",
                "parameters": [
                    {
                        "in": "query",
                        "name": "days",
                        "schema": {
                            "type": "integer",
                            "default": 30
                        },
                        "description": "Number of days to analyze (1-365)"
                    }
                ],
                "tags": [
                    "Webhooks"
                ],
                "security": [
                    {
                        "cookieAuth": []
                    },
                    {
                        "basicAuth": []
                    },
                    {}
                ],
                "responses": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/WebhookStats"
                                }
                            }
                        },
                        "description": ""
                    }
                }
            }
        },
        "/tasks/api/clear/": {
            "post": {
                "operationId": "tasks_api_clear_create",
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
                }
            }
        },
        "/tasks/api/clear-queues/": {
            "post": {
                "operationId": "tasks_api_clear_queues_create",
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
                }
            }
        },
        "/tasks/api/purge-failed/": {
            "post": {
                "operationId": "tasks_api_purge_failed_create",
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
                }
            }
        },
        "/tasks/api/queues/manage/": {
            "post": {
                "operationId": "tasks_api_queues_manage_create",
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
                }
            }
        },
        "/tasks/api/queues/status/": {
            "get": {
                "operationId": "tasks_api_queues_status_retrieve",
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
                }
            }
        },
        "/tasks/api/simulate/": {
            "post": {
                "operationId": "tasks_api_simulate_create",
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
                }
            }
        },
        "/tasks/api/tasks/list/": {
            "get": {
                "operationId": "tasks_api_tasks_list_retrieve",
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
                }
            }
        },
        "/tasks/api/tasks/stats/": {
            "get": {
                "operationId": "tasks_api_tasks_stats_retrieve",
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
                }
            }
        },
        "/tasks/api/workers/list/": {
            "get": {
                "operationId": "tasks_api_workers_list_retrieve",
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
                }
            }
        },
        "/tasks/api/workers/manage/": {
            "post": {
                "operationId": "tasks_api_workers_manage_create",
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
                }
            }
        }
    },
    "components": {
        "schemas": {
            "APIKeyCreate": {
                "type": "object",
                "description": "API key creation serializer with service integration.\n\nCreates new API keys and returns the full key value (only once).",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Descriptive name for the API key",
                        "maxLength": 100
                    },
                    "expires_in_days": {
                        "type": "integer",
                        "maximum": 365,
                        "minimum": 1,
                        "nullable": True,
                        "description": "Expiration in days (optional, None for no expiration)"
                    }
                },
                "required": [
                    "name"
                ]
            },
            "APIKeyCreateRequest": {
                "type": "object",
                "description": "API key creation serializer with service integration.\n\nCreates new API keys and returns the full key value (only once).",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Descriptive name for the API key",
                        "maxLength": 100
                    },
                    "expires_in_days": {
                        "type": "integer",
                        "maximum": 365,
                        "minimum": 1,
                        "nullable": True,
                        "description": "Expiration in days (optional, None for no expiration)"
                    }
                },
                "required": [
                    "name"
                ]
            },
            "APIKeyDetail": {
                "type": "object",
                "description": "Complete API key serializer with full details.\n\nUsed for API key detail views (no key value for security).",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "user": {
                        "type": "string",
                        "readOnly": True
                    },
                    "name": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Human-readable name for this API key"
                    },
                    "key_preview": {
                        "type": "string",
                        "readOnly": True
                    },
                    "is_active": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether this API key is active"
                    },
                    "is_expired": {
                        "type": "boolean",
                        "readOnly": True
                    },
                    "is_valid": {
                        "type": "boolean",
                        "readOnly": True
                    },
                    "days_until_expiry": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "total_requests": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total number of requests made with this key"
                    },
                    "last_used_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When this API key was last used"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When this API key expires (None = never expires)"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was last updated"
                    }
                },
                "required": [
                    "created_at",
                    "days_until_expiry",
                    "expires_at",
                    "id",
                    "is_active",
                    "is_expired",
                    "is_valid",
                    "key_preview",
                    "last_used_at",
                    "name",
                    "total_requests",
                    "updated_at",
                    "user"
                ]
            },
            "APIKeyList": {
                "type": "object",
                "description": "Lightweight API key serializer for lists.\n\nOptimized for API key lists with minimal data (no key value).",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "user": {
                        "type": "string",
                        "readOnly": True
                    },
                    "name": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Human-readable name for this API key"
                    },
                    "is_active": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether this API key is active"
                    },
                    "is_expired": {
                        "type": "boolean",
                        "readOnly": True
                    },
                    "is_valid": {
                        "type": "boolean",
                        "readOnly": True
                    },
                    "total_requests": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total number of requests made with this key"
                    },
                    "last_used_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When this API key was last used"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When this API key expires (None = never expires)"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    }
                },
                "required": [
                    "created_at",
                    "expires_at",
                    "id",
                    "is_active",
                    "is_expired",
                    "is_valid",
                    "last_used_at",
                    "name",
                    "total_requests",
                    "user"
                ]
            },
            "APIKeyUpdate": {
                "type": "object",
                "description": "API key update serializer for modifying API key properties.\n\nAllows updating name and active status only.",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Human-readable name for this API key",
                        "maxLength": 100
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether this API key is active"
                    }
                },
                "required": [
                    "name"
                ]
            },
            "APIKeyUpdateRequest": {
                "type": "object",
                "description": "API key update serializer for modifying API key properties.\n\nAllows updating name and active status only.",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Human-readable name for this API key",
                        "maxLength": 100
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether this API key is active"
                    }
                },
                "required": [
                    "name"
                ]
            },
            "APIKeyValidationRequest": {
                "type": "object",
                "description": "API key validation serializer.\n\nValidates API key and returns key information.",
                "properties": {
                    "key": {
                        "type": "string",
                        "minLength": 32,
                        "description": "API key to validate",
                        "maxLength": 64
                    }
                },
                "required": [
                    "key"
                ]
            },
            "APIKeyValidationResponse": {
                "type": "object",
                "description": "API key validation response serializer.\n\nDefines the structure of API key validation response for OpenAPI schema.",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether the validation was successful"
                    },
                    "valid": {
                        "type": "boolean",
                        "description": "Whether the API key is valid"
                    },
                    "api_key": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/APIKeyDetail"
                            }
                        ],
                        "readOnly": True,
                        "nullable": True,
                        "description": "API key details if valid"
                    },
                    "message": {
                        "type": "string",
                        "description": "Validation message"
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message if validation failed"
                    },
                    "error_code": {
                        "type": "string",
                        "description": "Error code if validation failed"
                    }
                },
                "required": [
                    "api_key",
                    "message",
                    "success",
                    "valid"
                ]
            },
            "APIKeysOverview": {
                "type": "object",
                "description": "API keys overview metrics",
                "properties": {
                    "total_keys": {
                        "type": "integer",
                        "description": "Total number of API keys"
                    },
                    "active_keys": {
                        "type": "integer",
                        "description": "Number of active API keys"
                    },
                    "expired_keys": {
                        "type": "integer",
                        "description": "Number of expired API keys"
                    },
                    "total_requests": {
                        "type": "integer",
                        "description": "Total requests across all keys"
                    },
                    "last_used_at": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "When any key was last used"
                    },
                    "most_used_key_name": {
                        "type": "string",
                        "nullable": True,
                        "description": "Name of most used API key"
                    },
                    "most_used_key_requests": {
                        "type": "integer",
                        "description": "Requests count for most used key"
                    },
                    "expiring_soon_count": {
                        "type": "integer",
                        "description": "Number of keys expiring within 7 days"
                    }
                },
                "required": [
                    "active_keys",
                    "expired_keys",
                    "expiring_soon_count",
                    "last_used_at",
                    "most_used_key_name",
                    "most_used_key_requests",
                    "total_keys",
                    "total_requests"
                ]
            },
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
            "BalanceOverview": {
                "type": "object",
                "description": "User balance overview metrics",
                "properties": {
                    "current_balance": {
                        "type": "number",
                        "format": "double",
                        "description": "Current balance in USD"
                    },
                    "balance_display": {
                        "type": "string",
                        "description": "Formatted balance display"
                    },
                    "total_deposited": {
                        "type": "number",
                        "format": "double",
                        "description": "Total amount deposited (lifetime)"
                    },
                    "total_spent": {
                        "type": "number",
                        "format": "double",
                        "description": "Total amount spent (lifetime)"
                    },
                    "last_transaction_at": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "Last transaction timestamp"
                    },
                    "has_transactions": {
                        "type": "boolean",
                        "description": "Whether user has any transactions"
                    },
                    "is_empty": {
                        "type": "boolean",
                        "description": "Whether balance is zero"
                    }
                },
                "required": [
                    "balance_display",
                    "current_balance",
                    "has_transactions",
                    "is_empty",
                    "last_transaction_at",
                    "total_deposited",
                    "total_spent"
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
            "ChartDataPoint": {
                "type": "object",
                "description": "Chart data point for payments analytics",
                "properties": {
                    "x": {
                        "type": "string",
                        "description": "X-axis value (date)"
                    },
                    "y": {
                        "type": "number",
                        "format": "double",
                        "description": "Y-axis value (amount or count)"
                    }
                },
                "required": [
                    "x",
                    "y"
                ]
            },
            "ChartSeries": {
                "type": "object",
                "description": "Chart series data for payments visualization",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Series name"
                    },
                    "data": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ChartDataPoint"
                        },
                        "description": "Data points"
                    },
                    "color": {
                        "type": "string",
                        "description": "Series color"
                    }
                },
                "required": [
                    "color",
                    "data",
                    "name"
                ]
            },
            "Currency": {
                "type": "object",
                "description": "Complete currency serializer with full details.\n\nUsed for currency information and management.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "code": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Currency code (e.g., BTC, USD, ETH)"
                    },
                    "name": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Full currency name (e.g., Bitcoin, US Dollar)"
                    },
                    "symbol": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Currency symbol (e.g., $, ₿, Ξ)"
                    },
                    "currency_type": {
                        "enum": [
                            "fiat",
                            "crypto"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "1fd14ececc7d641f",
                        "readOnly": True,
                        "description": "Type of currency\n\n* `fiat` - Fiat Currency\n* `crypto` - Cryptocurrency"
                    },
                    "type_display": {
                        "type": "string",
                        "readOnly": True
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
                    "is_crypto": {
                        "type": "boolean",
                        "description": "Check if this is a cryptocurrency.",
                        "readOnly": True
                    },
                    "is_fiat": {
                        "type": "boolean",
                        "description": "Check if this is a fiat currency.",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was last updated"
                    }
                },
                "required": [
                    "code",
                    "created_at",
                    "currency_type",
                    "decimal_places",
                    "id",
                    "is_active",
                    "is_crypto",
                    "is_fiat",
                    "name",
                    "symbol",
                    "type_display",
                    "updated_at"
                ]
            },
            "CurrencyAnalyticsItem": {
                "type": "object",
                "description": "Analytics data for a single currency",
                "properties": {
                    "currency_code": {
                        "type": "string",
                        "description": "Currency code (e.g., BTC)"
                    },
                    "currency_name": {
                        "type": "string",
                        "description": "Currency name (e.g., Bitcoin)"
                    },
                    "total_payments": {
                        "type": "integer",
                        "description": "Total number of payments"
                    },
                    "total_amount": {
                        "type": "number",
                        "format": "double",
                        "description": "Total amount in USD"
                    },
                    "completed_payments": {
                        "type": "integer",
                        "description": "Number of completed payments"
                    },
                    "average_amount": {
                        "type": "number",
                        "format": "double",
                        "description": "Average payment amount in USD"
                    },
                    "success_rate": {
                        "type": "number",
                        "format": "double",
                        "description": "Success rate percentage"
                    }
                },
                "required": [
                    "average_amount",
                    "completed_payments",
                    "currency_code",
                    "currency_name",
                    "success_rate",
                    "total_amount",
                    "total_payments"
                ]
            },
            "CurrencyList": {
                "type": "object",
                "description": "Lightweight currency serializer for lists.\n\nOptimized for currency selection and lists.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "code": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Currency code (e.g., BTC, USD, ETH)"
                    },
                    "name": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Full currency name (e.g., Bitcoin, US Dollar)"
                    },
                    "symbol": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Currency symbol (e.g., $, ₿, Ξ)"
                    },
                    "currency_type": {
                        "enum": [
                            "fiat",
                            "crypto"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "1fd14ececc7d641f",
                        "readOnly": True,
                        "description": "Type of currency\n\n* `fiat` - Fiat Currency\n* `crypto` - Cryptocurrency"
                    },
                    "type_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "is_active": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether this currency is available for payments"
                    }
                },
                "required": [
                    "code",
                    "currency_type",
                    "id",
                    "is_active",
                    "name",
                    "symbol",
                    "type_display"
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
            "EndpointGroup": {
                "type": "object",
                "description": "Endpoint group serializer for API access management.\n\nUsed for subscription endpoint group configuration.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "name": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Endpoint group name (e.g., 'Payment API', 'Balance API')"
                    },
                    "description": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Description of what this endpoint group provides"
                    },
                    "is_enabled": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether this endpoint group is available"
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
                    "description",
                    "id",
                    "is_enabled",
                    "name",
                    "updated_at"
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
            "Network": {
                "type": "object",
                "description": "Network serializer for blockchain networks.\n\nUsed for network information and selection.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "currency": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/CurrencyList"
                            }
                        ],
                        "readOnly": True
                    },
                    "name": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Network name (e.g., Ethereum, Bitcoin, Polygon)"
                    },
                    "code": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Network code (e.g., ETH, BTC, MATIC)"
                    },
                    "is_active": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether this network is available for payments"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was last updated"
                    }
                },
                "required": [
                    "code",
                    "created_at",
                    "currency",
                    "id",
                    "is_active",
                    "name",
                    "updated_at"
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
            "PaginatedAPIKeyListList": {
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
                            "$ref": "#/components/schemas/APIKeyList"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedCurrencyListList": {
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
                            "$ref": "#/components/schemas/CurrencyList"
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
            "PaginatedEndpointGroupList": {
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
                            "$ref": "#/components/schemas/EndpointGroup"
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
            "PaginatedNetworkList": {
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
                            "$ref": "#/components/schemas/Network"
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
            "PaginatedProviderCurrencyList": {
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
                            "$ref": "#/components/schemas/ProviderCurrency"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedRecentPaymentList": {
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
                            "$ref": "#/components/schemas/RecentPayment"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedRecentTransactionList": {
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
                            "$ref": "#/components/schemas/RecentTransaction"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedSubscriptionListList": {
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
                            "$ref": "#/components/schemas/SubscriptionList"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedTariffList": {
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
                            "$ref": "#/components/schemas/Tariff"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedTransactionList": {
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
                            "$ref": "#/components/schemas/Transaction"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PaginatedUserBalanceList": {
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
                            "$ref": "#/components/schemas/UserBalance"
                        },
                        "description": "Array of items for current page"
                    }
                }
            },
            "PatchedAPIKeyUpdateRequest": {
                "type": "object",
                "description": "API key update serializer for modifying API key properties.\n\nAllows updating name and active status only.",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Human-readable name for this API key",
                        "maxLength": 100
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether this API key is active"
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
            "PatchedPaymentRequest": {
                "type": "object",
                "description": "Complete payment serializer with full details.\n\nUsed for detail views and updates.",
                "properties": {
                    "amount_usd": {
                        "type": "number",
                        "format": "double",
                        "maximum": 50000.0,
                        "minimum": 1.0,
                        "description": "Payment amount in USD (float for performance)"
                    },
                    "currency": {
                        "type": "integer",
                        "description": "Payment currency"
                    },
                    "network": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Blockchain network (for crypto payments)"
                    },
                    "provider": {
                        "enum": [
                            "nowpayments"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "47694db6bd068cb3",
                        "description": "Payment provider\n\n* `nowpayments` - NowPayments"
                    },
                    "status": {
                        "enum": [
                            "pending",
                            "confirming",
                            "confirmed",
                            "completed",
                            "failed",
                            "expired",
                            "cancelled",
                            "refunded"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "59d07a8608d1bdb9",
                        "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded"
                    },
                    "callback_url": {
                        "type": "string",
                        "format": "uri",
                        "nullable": True,
                        "description": "Success callback URL",
                        "maxLength": 200
                    },
                    "cancel_url": {
                        "type": "string",
                        "format": "uri",
                        "nullable": True,
                        "description": "Cancellation URL",
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "Payment description"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "When this payment expires"
                    }
                }
            },
            "PatchedSubscriptionRequest": {
                "type": "object",
                "description": "Complete subscription serializer with full details.\n\nUsed for subscription detail views and updates.",
                "properties": {
                    "status": {
                        "enum": [
                            "active",
                            "inactive",
                            "suspended",
                            "cancelled",
                            "expired"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "20d0bcc8b3c2bafa",
                        "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired"
                    },
                    "tier": {
                        "enum": [
                            "free",
                            "basic",
                            "pro",
                            "enterprise"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "776e806f04431486",
                        "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "When this subscription expires"
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
            "Payment": {
                "type": "object",
                "description": "Complete payment serializer with full details.\n\nUsed for detail views and updates.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "user": {
                        "type": "string",
                        "readOnly": True
                    },
                    "amount_usd": {
                        "type": "number",
                        "format": "double",
                        "maximum": 50000.0,
                        "minimum": 1.0,
                        "description": "Payment amount in USD (float for performance)"
                    },
                    "currency": {
                        "type": "integer",
                        "description": "Payment currency"
                    },
                    "network": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Blockchain network (for crypto payments)"
                    },
                    "provider": {
                        "enum": [
                            "nowpayments"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "47694db6bd068cb3",
                        "description": "Payment provider\n\n* `nowpayments` - NowPayments"
                    },
                    "status": {
                        "enum": [
                            "pending",
                            "confirming",
                            "confirmed",
                            "completed",
                            "failed",
                            "expired",
                            "cancelled",
                            "refunded"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "59d07a8608d1bdb9",
                        "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded"
                    },
                    "status_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "amount_display": {
                        "type": "string",
                        "description": "Get formatted amount display.",
                        "readOnly": True
                    },
                    "provider_payment_id": {
                        "type": "string",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Provider's payment ID"
                    },
                    "payment_url": {
                        "type": "string",
                        "format": "uri",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Payment page URL"
                    },
                    "pay_address": {
                        "type": "string",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Cryptocurrency payment address"
                    },
                    "callback_url": {
                        "type": "string",
                        "format": "uri",
                        "nullable": True,
                        "description": "Success callback URL",
                        "maxLength": 200
                    },
                    "cancel_url": {
                        "type": "string",
                        "format": "uri",
                        "nullable": True,
                        "description": "Cancellation URL",
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "Payment description"
                    },
                    "transaction_hash": {
                        "type": "string",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Blockchain transaction hash"
                    },
                    "confirmations_count": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Number of blockchain confirmations"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was last updated"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "When this payment expires"
                    },
                    "completed_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When this payment was completed"
                    },
                    "is_pending": {
                        "type": "boolean",
                        "description": "Check if payment is pending.",
                        "readOnly": True
                    },
                    "is_completed": {
                        "type": "boolean",
                        "description": "Check if payment is completed.",
                        "readOnly": True
                    },
                    "is_failed": {
                        "type": "boolean",
                        "description": "Check if payment is failed.",
                        "readOnly": True
                    },
                    "is_expired": {
                        "type": "boolean",
                        "description": "Check if payment is expired.",
                        "readOnly": True
                    }
                },
                "required": [
                    "amount_display",
                    "amount_usd",
                    "completed_at",
                    "confirmations_count",
                    "created_at",
                    "currency",
                    "id",
                    "is_completed",
                    "is_expired",
                    "is_failed",
                    "is_pending",
                    "pay_address",
                    "payment_url",
                    "provider_payment_id",
                    "status_display",
                    "transaction_hash",
                    "updated_at",
                    "user"
                ]
            },
            "PaymentAnalyticsResponse": {
                "type": "object",
                "description": "Payment analytics response with currency and provider breakdown",
                "properties": {
                    "currency_analytics": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/CurrencyAnalyticsItem"
                        },
                        "description": "Analytics by currency"
                    },
                    "provider_analytics": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ProviderAnalyticsItem"
                        },
                        "description": "Analytics by provider"
                    }
                },
                "required": [
                    "currency_analytics",
                    "provider_analytics"
                ]
            },
            "PaymentCreate": {
                "type": "object",
                "description": "Payment creation serializer with Pydantic integration.\n\nValidates input and delegates to PaymentService.",
                "properties": {
                    "amount_usd": {
                        "type": "number",
                        "format": "double",
                        "maximum": 50000.0,
                        "minimum": 1.0,
                        "description": "Amount in USD (1.00 - 50,000.00)"
                    },
                    "currency_code": {
                        "enum": [
                            "BTC",
                            "ETH",
                            "LTC",
                            "XMR",
                            "USDT",
                            "USDC",
                            "ADA",
                            "DOT"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "a26a773d0d4fed5c",
                        "description": "Cryptocurrency to receive\n\n* `BTC` - Bitcoin\n* `ETH` - Ethereum\n* `LTC` - Litecoin\n* `XMR` - Monero\n* `USDT` - Tether\n* `USDC` - USD Coin\n* `ADA` - Cardano\n* `DOT` - Polkadot"
                    },
                    "provider": {
                        "enum": [
                            "nowpayments"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "47694db6bd068cb3",
                        "default": "nowpayments",
                        "description": "Payment provider\n\n* `nowpayments` - NowPayments"
                    },
                    "callback_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Success callback URL"
                    },
                    "cancel_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Cancellation URL"
                    },
                    "description": {
                        "type": "string",
                        "description": "Payment description",
                        "maxLength": 500
                    },
                    "metadata": {
                        "description": "Additional metadata"
                    }
                },
                "required": [
                    "amount_usd",
                    "currency_code"
                ]
            },
            "PaymentCreateRequest": {
                "type": "object",
                "description": "Payment creation serializer with Pydantic integration.\n\nValidates input and delegates to PaymentService.",
                "properties": {
                    "amount_usd": {
                        "type": "number",
                        "format": "double",
                        "maximum": 50000.0,
                        "minimum": 1.0,
                        "description": "Amount in USD (1.00 - 50,000.00)"
                    },
                    "currency_code": {
                        "enum": [
                            "BTC",
                            "ETH",
                            "LTC",
                            "XMR",
                            "USDT",
                            "USDC",
                            "ADA",
                            "DOT"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "a26a773d0d4fed5c",
                        "description": "Cryptocurrency to receive\n\n* `BTC` - Bitcoin\n* `ETH` - Ethereum\n* `LTC` - Litecoin\n* `XMR` - Monero\n* `USDT` - Tether\n* `USDC` - USD Coin\n* `ADA` - Cardano\n* `DOT` - Polkadot"
                    },
                    "provider": {
                        "enum": [
                            "nowpayments"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "47694db6bd068cb3",
                        "default": "nowpayments",
                        "description": "Payment provider\n\n* `nowpayments` - NowPayments"
                    },
                    "callback_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Success callback URL"
                    },
                    "cancel_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "Cancellation URL"
                    },
                    "description": {
                        "type": "string",
                        "description": "Payment description",
                        "maxLength": 500
                    },
                    "metadata": {
                        "description": "Additional metadata"
                    }
                },
                "required": [
                    "amount_usd",
                    "currency_code"
                ]
            },
            "PaymentList": {
                "type": "object",
                "description": "Lightweight serializer for payment lists.\n\nOptimized for list views with minimal data.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "amount_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Payment amount in USD (float for performance)"
                    },
                    "currency": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Payment currency"
                    },
                    "provider": {
                        "enum": [
                            "nowpayments"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "47694db6bd068cb3",
                        "readOnly": True,
                        "description": "Payment provider\n\n* `nowpayments` - NowPayments"
                    },
                    "status": {
                        "enum": [
                            "pending",
                            "confirming",
                            "confirmed",
                            "completed",
                            "failed",
                            "expired",
                            "cancelled",
                            "refunded"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "59d07a8608d1bdb9",
                        "readOnly": True,
                        "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded"
                    },
                    "status_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "amount_display": {
                        "type": "string",
                        "description": "Get formatted amount display.",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When this payment expires"
                    }
                },
                "required": [
                    "amount_display",
                    "amount_usd",
                    "created_at",
                    "currency",
                    "expires_at",
                    "id",
                    "provider",
                    "status",
                    "status_display"
                ]
            },
            "PaymentOverview": {
                "type": "object",
                "description": "Payments overview metrics",
                "properties": {
                    "total_payments": {
                        "type": "integer",
                        "description": "Total number of payments"
                    },
                    "completed_payments": {
                        "type": "integer",
                        "description": "Number of completed payments"
                    },
                    "pending_payments": {
                        "type": "integer",
                        "description": "Number of pending payments"
                    },
                    "failed_payments": {
                        "type": "integer",
                        "description": "Number of failed payments"
                    },
                    "total_amount_usd": {
                        "type": "number",
                        "format": "double",
                        "description": "Total payment amount in USD"
                    },
                    "completed_amount_usd": {
                        "type": "number",
                        "format": "double",
                        "description": "Total completed amount in USD"
                    },
                    "average_payment_usd": {
                        "type": "number",
                        "format": "double",
                        "description": "Average payment amount in USD"
                    },
                    "success_rate": {
                        "type": "number",
                        "format": "double",
                        "description": "Payment success rate percentage"
                    },
                    "last_payment_at": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "Last payment timestamp"
                    },
                    "payments_this_month": {
                        "type": "integer",
                        "description": "Number of payments this month"
                    },
                    "amount_this_month": {
                        "type": "number",
                        "format": "double",
                        "description": "Total amount this month"
                    },
                    "top_currency": {
                        "type": "string",
                        "nullable": True,
                        "description": "Most used currency"
                    },
                    "top_currency_count": {
                        "type": "integer",
                        "description": "Usage count for top currency"
                    }
                },
                "required": [
                    "amount_this_month",
                    "average_payment_usd",
                    "completed_amount_usd",
                    "completed_payments",
                    "failed_payments",
                    "last_payment_at",
                    "payments_this_month",
                    "pending_payments",
                    "success_rate",
                    "top_currency",
                    "top_currency_count",
                    "total_amount_usd",
                    "total_payments"
                ]
            },
            "PaymentRequest": {
                "type": "object",
                "description": "Complete payment serializer with full details.\n\nUsed for detail views and updates.",
                "properties": {
                    "amount_usd": {
                        "type": "number",
                        "format": "double",
                        "maximum": 50000.0,
                        "minimum": 1.0,
                        "description": "Payment amount in USD (float for performance)"
                    },
                    "currency": {
                        "type": "integer",
                        "description": "Payment currency"
                    },
                    "network": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Blockchain network (for crypto payments)"
                    },
                    "provider": {
                        "enum": [
                            "nowpayments"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "47694db6bd068cb3",
                        "description": "Payment provider\n\n* `nowpayments` - NowPayments"
                    },
                    "status": {
                        "enum": [
                            "pending",
                            "confirming",
                            "confirmed",
                            "completed",
                            "failed",
                            "expired",
                            "cancelled",
                            "refunded"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "59d07a8608d1bdb9",
                        "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded"
                    },
                    "callback_url": {
                        "type": "string",
                        "format": "uri",
                        "nullable": True,
                        "description": "Success callback URL",
                        "maxLength": 200
                    },
                    "cancel_url": {
                        "type": "string",
                        "format": "uri",
                        "nullable": True,
                        "description": "Cancellation URL",
                        "maxLength": 200
                    },
                    "description": {
                        "type": "string",
                        "description": "Payment description"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "When this payment expires"
                    }
                },
                "required": [
                    "amount_usd",
                    "currency"
                ]
            },
            "PaymentsChartResponse": {
                "type": "object",
                "description": "Complete chart response for payments analytics",
                "properties": {
                    "series": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ChartSeries"
                        },
                        "description": "Chart series data"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period"
                    },
                    "total_amount": {
                        "type": "number",
                        "format": "double",
                        "description": "Total amount for period"
                    },
                    "total_payments": {
                        "type": "integer",
                        "description": "Total payments for period"
                    },
                    "success_rate": {
                        "type": "number",
                        "format": "double",
                        "description": "Success rate for period"
                    }
                },
                "required": [
                    "period",
                    "series",
                    "success_rate",
                    "total_amount",
                    "total_payments"
                ]
            },
            "PaymentsDashboardOverview": {
                "type": "object",
                "description": "Complete payments dashboard overview response",
                "properties": {
                    "metrics": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/PaymentsMetrics"
                            }
                        ],
                        "description": "Dashboard metrics"
                    },
                    "recent_payments": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/RecentPayment"
                        },
                        "description": "Recent payments"
                    },
                    "recent_transactions": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/RecentTransaction"
                        },
                        "description": "Recent transactions"
                    },
                    "chart_data": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/PaymentsChartResponse"
                            }
                        ],
                        "description": "Chart data for analytics"
                    }
                },
                "required": [
                    "chart_data",
                    "metrics",
                    "recent_payments",
                    "recent_transactions"
                ]
            },
            "PaymentsMetrics": {
                "type": "object",
                "description": "Complete payments dashboard metrics",
                "properties": {
                    "balance": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/BalanceOverview"
                            }
                        ],
                        "description": "Balance overview"
                    },
                    "subscription": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/SubscriptionOverview"
                            }
                        ],
                        "nullable": True,
                        "description": "Subscription overview"
                    },
                    "api_keys": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/APIKeysOverview"
                            }
                        ],
                        "description": "API keys overview"
                    },
                    "payments": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/PaymentOverview"
                            }
                        ],
                        "description": "Payments overview"
                    }
                },
                "required": [
                    "api_keys",
                    "balance",
                    "payments",
                    "subscription"
                ]
            },
            "ProviderAnalyticsItem": {
                "type": "object",
                "description": "Analytics data for a single payment provider",
                "properties": {
                    "provider": {
                        "type": "string",
                        "description": "Provider code"
                    },
                    "provider_display": {
                        "type": "string",
                        "description": "Provider display name"
                    },
                    "total_payments": {
                        "type": "integer",
                        "description": "Total number of payments"
                    },
                    "total_amount": {
                        "type": "number",
                        "format": "double",
                        "description": "Total amount in USD"
                    },
                    "completed_payments": {
                        "type": "integer",
                        "description": "Number of completed payments"
                    },
                    "success_rate": {
                        "type": "number",
                        "format": "double",
                        "description": "Success rate percentage"
                    }
                },
                "required": [
                    "completed_payments",
                    "provider",
                    "provider_display",
                    "success_rate",
                    "total_amount",
                    "total_payments"
                ]
            },
            "ProviderCurrency": {
                "type": "object",
                "description": "Provider currency serializer for provider-specific currency info.\n\nUsed for provider currency management and rates.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "currency": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/CurrencyList"
                            }
                        ],
                        "readOnly": True
                    },
                    "network": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/Network"
                            }
                        ],
                        "readOnly": True
                    },
                    "provider": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Payment provider name (e.g., nowpayments)"
                    },
                    "provider_currency_code": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Currency code as used by the provider"
                    },
                    "provider_min_amount_usd": {
                        "type": "number",
                        "format": "double",
                        "description": "Get minimum amount from provider configuration.",
                        "readOnly": True
                    },
                    "provider_max_amount_usd": {
                        "type": "number",
                        "format": "double",
                        "description": "Get maximum amount from provider configuration.",
                        "readOnly": True
                    },
                    "provider_fee_percentage": {
                        "type": "number",
                        "format": "double",
                        "description": "Get fee percentage from provider configuration.",
                        "readOnly": True
                    },
                    "provider_fixed_fee_usd": {
                        "type": "number",
                        "format": "double",
                        "description": "Get fixed fee from provider configuration.",
                        "readOnly": True
                    },
                    "is_enabled": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether this currency is enabled for this provider"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was last updated"
                    }
                },
                "required": [
                    "created_at",
                    "currency",
                    "id",
                    "is_enabled",
                    "network",
                    "provider",
                    "provider_currency_code",
                    "provider_fee_percentage",
                    "provider_fixed_fee_usd",
                    "provider_max_amount_usd",
                    "provider_min_amount_usd",
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
            "RecentPayment": {
                "type": "object",
                "description": "Recent payment item",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Payment ID"
                    },
                    "internal_payment_id": {
                        "type": "string",
                        "description": "Internal payment ID"
                    },
                    "amount_usd": {
                        "type": "number",
                        "format": "double",
                        "description": "Payment amount in USD"
                    },
                    "amount_display": {
                        "type": "string",
                        "description": "Formatted amount display"
                    },
                    "currency_code": {
                        "type": "string",
                        "description": "Currency code"
                    },
                    "status": {
                        "type": "string",
                        "description": "Payment status"
                    },
                    "status_display": {
                        "type": "string",
                        "description": "Human-readable status"
                    },
                    "status_color": {
                        "type": "string",
                        "description": "Color for status display"
                    },
                    "provider": {
                        "type": "string",
                        "description": "Payment provider"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Payment creation timestamp"
                    },
                    "completed_at": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "Payment completion timestamp"
                    },
                    "is_pending": {
                        "type": "boolean",
                        "description": "Whether payment is pending"
                    },
                    "is_completed": {
                        "type": "boolean",
                        "description": "Whether payment is completed"
                    },
                    "is_failed": {
                        "type": "boolean",
                        "description": "Whether payment failed"
                    }
                },
                "required": [
                    "amount_display",
                    "amount_usd",
                    "completed_at",
                    "created_at",
                    "currency_code",
                    "id",
                    "internal_payment_id",
                    "is_completed",
                    "is_failed",
                    "is_pending",
                    "provider",
                    "status",
                    "status_color",
                    "status_display"
                ]
            },
            "RecentTransaction": {
                "type": "object",
                "description": "Recent transaction item",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Transaction ID"
                    },
                    "transaction_type": {
                        "type": "string",
                        "description": "Transaction type"
                    },
                    "amount_usd": {
                        "type": "number",
                        "format": "double",
                        "description": "Transaction amount in USD"
                    },
                    "amount_display": {
                        "type": "string",
                        "description": "Formatted amount display"
                    },
                    "balance_after": {
                        "type": "number",
                        "format": "double",
                        "description": "Balance after transaction"
                    },
                    "description": {
                        "type": "string",
                        "description": "Transaction description"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Transaction timestamp"
                    },
                    "payment_id": {
                        "type": "string",
                        "nullable": True,
                        "description": "Related payment ID"
                    },
                    "is_credit": {
                        "type": "boolean",
                        "description": "Whether this is a credit transaction"
                    },
                    "is_debit": {
                        "type": "boolean",
                        "description": "Whether this is a debit transaction"
                    },
                    "type_color": {
                        "type": "string",
                        "description": "Color for transaction type display"
                    }
                },
                "required": [
                    "amount_display",
                    "amount_usd",
                    "balance_after",
                    "created_at",
                    "description",
                    "id",
                    "is_credit",
                    "is_debit",
                    "payment_id",
                    "transaction_type",
                    "type_color"
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
            "Subscription": {
                "type": "object",
                "description": "Complete subscription serializer with full details.\n\nUsed for subscription detail views and updates.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "user": {
                        "type": "string",
                        "readOnly": True
                    },
                    "tariff": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/Tariff"
                            }
                        ],
                        "readOnly": True
                    },
                    "endpoint_group": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/EndpointGroup"
                            }
                        ],
                        "readOnly": True
                    },
                    "status": {
                        "enum": [
                            "active",
                            "inactive",
                            "suspended",
                            "cancelled",
                            "expired"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "20d0bcc8b3c2bafa",
                        "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired"
                    },
                    "status_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "status_color": {
                        "type": "string",
                        "description": "Get color for status display.",
                        "readOnly": True
                    },
                    "tier": {
                        "enum": [
                            "free",
                            "basic",
                            "pro",
                            "enterprise"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "776e806f04431486",
                        "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier"
                    },
                    "total_requests": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "Total API requests made with this subscription"
                    },
                    "usage_percentage": {
                        "type": "number",
                        "format": "double",
                        "description": "Get usage percentage for current period.",
                        "readOnly": True
                    },
                    "last_request_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "nullable": True,
                        "description": "When the last API request was made"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "When this subscription expires"
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Check if subscription is active and not expired.",
                        "readOnly": True
                    },
                    "is_expired": {
                        "type": "boolean",
                        "description": "Check if subscription is expired.",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was last updated"
                    }
                },
                "required": [
                    "created_at",
                    "endpoint_group",
                    "expires_at",
                    "id",
                    "is_active",
                    "is_expired",
                    "last_request_at",
                    "status_color",
                    "status_display",
                    "tariff",
                    "total_requests",
                    "updated_at",
                    "usage_percentage",
                    "user"
                ]
            },
            "SubscriptionCreate": {
                "type": "object",
                "description": "Subscription creation serializer with service integration.\n\nValidates input and delegates to SubscriptionService.",
                "properties": {
                    "tariff_id": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Tariff ID for the subscription"
                    },
                    "endpoint_group_id": {
                        "type": "integer",
                        "minimum": 1,
                        "nullable": True,
                        "description": "Endpoint group ID (optional)"
                    },
                    "duration_days": {
                        "type": "integer",
                        "maximum": 365,
                        "minimum": 1,
                        "default": 30,
                        "description": "Subscription duration in days"
                    }
                },
                "required": [
                    "tariff_id"
                ]
            },
            "SubscriptionCreateRequest": {
                "type": "object",
                "description": "Subscription creation serializer with service integration.\n\nValidates input and delegates to SubscriptionService.",
                "properties": {
                    "tariff_id": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Tariff ID for the subscription"
                    },
                    "endpoint_group_id": {
                        "type": "integer",
                        "minimum": 1,
                        "nullable": True,
                        "description": "Endpoint group ID (optional)"
                    },
                    "duration_days": {
                        "type": "integer",
                        "maximum": 365,
                        "minimum": 1,
                        "default": 30,
                        "description": "Subscription duration in days"
                    }
                },
                "required": [
                    "tariff_id"
                ]
            },
            "SubscriptionList": {
                "type": "object",
                "description": "Lightweight subscription serializer for lists.\n\nOptimized for subscription lists with minimal data.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "user": {
                        "type": "string",
                        "readOnly": True
                    },
                    "tariff_name": {
                        "type": "string",
                        "readOnly": True
                    },
                    "status": {
                        "enum": [
                            "active",
                            "inactive",
                            "suspended",
                            "cancelled",
                            "expired"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "20d0bcc8b3c2bafa",
                        "readOnly": True,
                        "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired"
                    },
                    "status_display": {
                        "type": "string",
                        "readOnly": True
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Check if subscription is active and not expired.",
                        "readOnly": True
                    },
                    "is_expired": {
                        "type": "boolean",
                        "description": "Check if subscription is expired.",
                        "readOnly": True
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this subscription expires"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    }
                },
                "required": [
                    "created_at",
                    "expires_at",
                    "id",
                    "is_active",
                    "is_expired",
                    "status",
                    "status_display",
                    "tariff_name",
                    "user"
                ]
            },
            "SubscriptionOverview": {
                "type": "object",
                "description": "Current subscription overview",
                "properties": {
                    "tier": {
                        "type": "string",
                        "description": "Subscription tier"
                    },
                    "tier_display": {
                        "type": "string",
                        "description": "Human-readable tier name"
                    },
                    "status": {
                        "type": "string",
                        "description": "Subscription status"
                    },
                    "status_display": {
                        "type": "string",
                        "description": "Human-readable status"
                    },
                    "status_color": {
                        "type": "string",
                        "description": "Color for status display"
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Whether subscription is active"
                    },
                    "is_expired": {
                        "type": "boolean",
                        "description": "Whether subscription is expired"
                    },
                    "days_remaining": {
                        "type": "integer",
                        "description": "Days until expiration"
                    },
                    "requests_per_hour": {
                        "type": "integer",
                        "description": "Hourly request limit"
                    },
                    "requests_per_day": {
                        "type": "integer",
                        "description": "Daily request limit"
                    },
                    "total_requests": {
                        "type": "integer",
                        "description": "Total requests made"
                    },
                    "usage_percentage": {
                        "type": "number",
                        "format": "double",
                        "description": "Usage percentage for current period"
                    },
                    "monthly_cost_usd": {
                        "type": "number",
                        "format": "double",
                        "description": "Monthly cost in USD"
                    },
                    "cost_display": {
                        "type": "string",
                        "description": "Formatted cost display"
                    },
                    "starts_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Subscription start date"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Subscription expiration date"
                    },
                    "last_request_at": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                        "description": "Last API request timestamp"
                    },
                    "endpoint_groups_count": {
                        "type": "integer",
                        "description": "Number of accessible endpoint groups"
                    },
                    "endpoint_groups": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of accessible endpoint group names"
                    }
                },
                "required": [
                    "cost_display",
                    "days_remaining",
                    "endpoint_groups",
                    "endpoint_groups_count",
                    "expires_at",
                    "is_active",
                    "is_expired",
                    "last_request_at",
                    "monthly_cost_usd",
                    "requests_per_day",
                    "requests_per_hour",
                    "starts_at",
                    "status",
                    "status_color",
                    "status_display",
                    "tier",
                    "tier_display",
                    "total_requests",
                    "usage_percentage"
                ]
            },
            "SubscriptionRequest": {
                "type": "object",
                "description": "Complete subscription serializer with full details.\n\nUsed for subscription detail views and updates.",
                "properties": {
                    "status": {
                        "enum": [
                            "active",
                            "inactive",
                            "suspended",
                            "cancelled",
                            "expired"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "20d0bcc8b3c2bafa",
                        "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired"
                    },
                    "tier": {
                        "enum": [
                            "free",
                            "basic",
                            "pro",
                            "enterprise"
                        ],
                        "type": "string",
                        "x-spec-enum-id": "776e806f04431486",
                        "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier"
                    },
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "When this subscription expires"
                    }
                },
                "required": [
                    "expires_at"
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
            "SupportedProviders": {
                "type": "object",
                "description": "Serializer for supported providers response.",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Request success status"
                    },
                    "providers": {
                        "description": "List of supported providers"
                    },
                    "total_count": {
                        "type": "integer",
                        "description": "Total number of providers"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Response timestamp"
                    }
                },
                "required": [
                    "providers",
                    "success",
                    "timestamp",
                    "total_count"
                ]
            },
            "Tariff": {
                "type": "object",
                "description": "Tariff serializer for subscription pricing.\n\nUsed for tariff information and selection.",
                "properties": {
                    "id": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "name": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Tariff name (e.g., 'Free', 'Basic', 'Pro')"
                    },
                    "description": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Detailed description of what this tariff includes"
                    },
                    "monthly_price_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Monthly price in USD"
                    },
                    "requests_per_month": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "API requests allowed per month"
                    },
                    "requests_per_hour": {
                        "type": "integer",
                        "readOnly": True,
                        "description": "API requests allowed per hour"
                    },
                    "is_active": {
                        "type": "boolean",
                        "readOnly": True,
                        "description": "Whether this tariff is available for new subscriptions"
                    },
                    "endpoint_groups": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/EndpointGroup"
                        },
                        "readOnly": True
                    },
                    "endpoint_groups_count": {
                        "type": "integer",
                        "readOnly": True
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was created"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True,
                        "description": "When this record was last updated"
                    }
                },
                "required": [
                    "created_at",
                    "description",
                    "endpoint_groups",
                    "endpoint_groups_count",
                    "id",
                    "is_active",
                    "monthly_price_usd",
                    "name",
                    "requests_per_hour",
                    "requests_per_month",
                    "updated_at"
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
                "description": "Transaction serializer with full details.\n\nUsed for transaction history and details.",
                "properties": {
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "readOnly": True,
                        "description": "Unique identifier for this record"
                    },
                    "user": {
                        "type": "string",
                        "readOnly": True
                    },
                    "amount_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Transaction amount in USD (positive=credit, negative=debit)"
                    },
                    "amount_display": {
                        "type": "string",
                        "readOnly": True
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
                    "type_color": {
                        "type": "string",
                        "readOnly": True
                    },
                    "description": {
                        "type": "string",
                        "readOnly": True,
                        "description": "Transaction description"
                    },
                    "payment_id": {
                        "type": "string",
                        "readOnly": True,
                        "nullable": True,
                        "description": "Related payment ID (if applicable)"
                    },
                    "metadata": {
                        "readOnly": True,
                        "description": "Additional transaction metadata"
                    },
                    "is_credit": {
                        "type": "boolean",
                        "readOnly": True
                    },
                    "is_debit": {
                        "type": "boolean",
                        "readOnly": True
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
                    "created_at",
                    "description",
                    "id",
                    "is_credit",
                    "is_debit",
                    "metadata",
                    "payment_id",
                    "transaction_type",
                    "type_color",
                    "user"
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
                        "nullable": True
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
            "UserBalance": {
                "type": "object",
                "description": "User balance serializer with computed fields.\n\nProvides balance information with display helpers.",
                "properties": {
                    "user": {
                        "type": "string",
                        "readOnly": True
                    },
                    "balance_usd": {
                        "type": "number",
                        "format": "double",
                        "readOnly": True,
                        "description": "Current balance in USD (float for performance)"
                    },
                    "balance_display": {
                        "type": "string",
                        "description": "Formatted balance display.",
                        "readOnly": True
                    },
                    "is_empty": {
                        "type": "boolean",
                        "description": "Check if balance is zero.",
                        "readOnly": True
                    },
                    "has_transactions": {
                        "type": "boolean",
                        "description": "Check if user has any transactions.",
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
                    "balance_display",
                    "balance_usd",
                    "created_at",
                    "has_transactions",
                    "is_empty",
                    "updated_at",
                    "user"
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
            "WebhookHealth": {
                "type": "object",
                "description": "Serializer for webhook health check response.",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Health status",
                        "maxLength": 20
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Check timestamp"
                    },
                    "providers": {
                        "description": "Provider health status"
                    }
                },
                "required": [
                    "providers",
                    "status",
                    "timestamp"
                ]
            },
            "WebhookResponse": {
                "type": "object",
                "description": "Serializer for webhook processing response.\n\nStandard response format for all webhook endpoints.",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether webhook was processed successfully"
                    },
                    "message": {
                        "type": "string",
                        "description": "Processing result message",
                        "maxLength": 500
                    },
                    "payment_id": {
                        "type": "string",
                        "description": "Internal payment ID",
                        "maxLength": 256
                    },
                    "provider_payment_id": {
                        "type": "string",
                        "description": "Provider payment ID",
                        "maxLength": 256
                    },
                    "processed_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Processing timestamp"
                    }
                },
                "required": [
                    "message",
                    "success"
                ]
            },
            "WebhookResponseRequest": {
                "type": "object",
                "description": "Serializer for webhook processing response.\n\nStandard response format for all webhook endpoints.",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Whether webhook was processed successfully"
                    },
                    "message": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Processing result message",
                        "maxLength": 500
                    },
                    "payment_id": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Internal payment ID",
                        "maxLength": 256
                    },
                    "provider_payment_id": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Provider payment ID",
                        "maxLength": 256
                    },
                    "processed_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Processing timestamp"
                    }
                },
                "required": [
                    "message",
                    "success"
                ]
            },
            "WebhookStats": {
                "type": "object",
                "description": "Serializer for webhook statistics response.",
                "properties": {
                    "total_webhooks": {
                        "type": "integer",
                        "description": "Total webhooks processed"
                    },
                    "successful_webhooks": {
                        "type": "integer",
                        "description": "Successfully processed webhooks"
                    },
                    "failed_webhooks": {
                        "type": "integer",
                        "description": "Failed webhook processing attempts"
                    },
                    "success_rate": {
                        "type": "number",
                        "format": "double",
                        "description": "Success rate percentage"
                    },
                    "providers": {
                        "description": "Per-provider statistics"
                    }
                },
                "required": [
                    "failed_webhooks",
                    "providers",
                    "success_rate",
                    "successful_webhooks",
                    "total_webhooks"
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
            }
        }
    }
}

__all__ = ["OPENAPI_SCHEMA"]