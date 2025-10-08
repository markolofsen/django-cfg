/**
 * OpenAPI Schema Export
 *
 * Contains the complete OpenAPI specification for runtime access.
 */

export const OPENAPI_SCHEMA = {
  "components": {
    "schemas": {
      "APIKeyCreate": {
        "description": "API key creation serializer with service integration.\n\nCreates new API keys and returns the full key value (only once).",
        "properties": {
          "expires_in_days": {
            "description": "Expiration in days (optional, null for no expiration)",
            "maximum": 365,
            "minimum": 1,
            "nullable": true,
            "type": "integer"
          },
          "name": {
            "description": "Descriptive name for the API key",
            "maxLength": 100,
            "type": "string"
          }
        },
        "required": [
          "name"
        ],
        "type": "object"
      },
      "APIKeyCreateRequest": {
        "description": "API key creation serializer with service integration.\n\nCreates new API keys and returns the full key value (only once).",
        "properties": {
          "expires_in_days": {
            "description": "Expiration in days (optional, null for no expiration)",
            "maximum": 365,
            "minimum": 1,
            "nullable": true,
            "type": "integer"
          },
          "name": {
            "description": "Descriptive name for the API key",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "name"
        ],
        "type": "object"
      },
      "APIKeyDetail": {
        "description": "Complete API key serializer with full details.\n\nUsed for API key detail views (no key value for security).",
        "properties": {
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "days_until_expiry": {
            "readOnly": true,
            "type": "integer"
          },
          "expires_at": {
            "description": "When this API key expires (null = never expires)",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "description": "Unique identifier for this record",
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_active": {
            "description": "Whether this API key is active",
            "readOnly": true,
            "type": "boolean"
          },
          "is_expired": {
            "readOnly": true,
            "type": "boolean"
          },
          "is_valid": {
            "readOnly": true,
            "type": "boolean"
          },
          "key_preview": {
            "readOnly": true,
            "type": "string"
          },
          "last_used_at": {
            "description": "When this API key was last used",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "name": {
            "description": "Human-readable name for this API key",
            "readOnly": true,
            "type": "string"
          },
          "total_requests": {
            "description": "Total number of requests made with this key",
            "readOnly": true,
            "type": "integer"
          },
          "updated_at": {
            "description": "When this record was last updated",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "user": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "APIKeyList": {
        "description": "Lightweight API key serializer for lists.\n\nOptimized for API key lists with minimal data (no key value).",
        "properties": {
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "expires_at": {
            "description": "When this API key expires (null = never expires)",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "description": "Unique identifier for this record",
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_active": {
            "description": "Whether this API key is active",
            "readOnly": true,
            "type": "boolean"
          },
          "is_expired": {
            "readOnly": true,
            "type": "boolean"
          },
          "is_valid": {
            "readOnly": true,
            "type": "boolean"
          },
          "last_used_at": {
            "description": "When this API key was last used",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "name": {
            "description": "Human-readable name for this API key",
            "readOnly": true,
            "type": "string"
          },
          "total_requests": {
            "description": "Total number of requests made with this key",
            "readOnly": true,
            "type": "integer"
          },
          "user": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "APIKeyUpdate": {
        "description": "API key update serializer for modifying API key properties.\n\nAllows updating name and active status only.",
        "properties": {
          "is_active": {
            "description": "Whether this API key is active",
            "type": "boolean"
          },
          "name": {
            "description": "Human-readable name for this API key",
            "maxLength": 100,
            "type": "string"
          }
        },
        "required": [
          "name"
        ],
        "type": "object"
      },
      "APIKeyUpdateRequest": {
        "description": "API key update serializer for modifying API key properties.\n\nAllows updating name and active status only.",
        "properties": {
          "is_active": {
            "description": "Whether this API key is active",
            "type": "boolean"
          },
          "name": {
            "description": "Human-readable name for this API key",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "name"
        ],
        "type": "object"
      },
      "APIKeyValidationRequest": {
        "description": "API key validation serializer.\n\nValidates API key and returns key information.",
        "properties": {
          "key": {
            "description": "API key to validate",
            "maxLength": 64,
            "minLength": 32,
            "type": "string"
          }
        },
        "required": [
          "key"
        ],
        "type": "object"
      },
      "APIKeyValidationResponse": {
        "description": "API key validation response serializer.\n\nDefines the structure of API key validation response for OpenAPI schema.",
        "properties": {
          "api_key": {
            "allOf": [
              {
                "$ref": "#/components/schemas/APIKeyDetail"
              }
            ],
            "description": "API key details if valid",
            "nullable": true,
            "readOnly": true
          },
          "error": {
            "description": "Error message if validation failed",
            "type": "string"
          },
          "error_code": {
            "description": "Error code if validation failed",
            "type": "string"
          },
          "message": {
            "description": "Validation message",
            "type": "string"
          },
          "success": {
            "description": "Whether the validation was successful",
            "type": "boolean"
          },
          "valid": {
            "description": "Whether the API key is valid",
            "type": "boolean"
          }
        },
        "required": [
          "api_key",
          "message",
          "success",
          "valid"
        ],
        "type": "object"
      },
      "APIKeysOverview": {
        "description": "API keys overview metrics",
        "properties": {
          "active_keys": {
            "description": "Number of active API keys",
            "type": "integer"
          },
          "expired_keys": {
            "description": "Number of expired API keys",
            "type": "integer"
          },
          "expiring_soon_count": {
            "description": "Number of keys expiring within 7 days",
            "type": "integer"
          },
          "last_used_at": {
            "description": "When any key was last used",
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "most_used_key_name": {
            "description": "Name of most used API key",
            "nullable": true,
            "type": "string"
          },
          "most_used_key_requests": {
            "description": "Requests count for most used key",
            "type": "integer"
          },
          "total_keys": {
            "description": "Total number of API keys",
            "type": "integer"
          },
          "total_requests": {
            "description": "Total requests across all keys",
            "type": "integer"
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
        ],
        "type": "object"
      },
      "APIResponse": {
        "description": "Standard API response serializer.",
        "properties": {
          "data": {
            "additionalProperties": {},
            "description": "Response data",
            "type": "object"
          },
          "error": {
            "description": "Error message",
            "type": "string"
          },
          "message": {
            "description": "Success message",
            "type": "string"
          },
          "success": {
            "description": "Operation success status",
            "type": "boolean"
          }
        },
        "required": [
          "success"
        ],
        "type": "object"
      },
      "APIResponseRequest": {
        "description": "Standard API response serializer.",
        "properties": {
          "data": {
            "additionalProperties": {},
            "description": "Response data",
            "type": "object"
          },
          "error": {
            "description": "Error message",
            "minLength": 1,
            "type": "string"
          },
          "message": {
            "description": "Success message",
            "minLength": 1,
            "type": "string"
          },
          "success": {
            "description": "Operation success status",
            "type": "boolean"
          }
        },
        "required": [
          "success"
        ],
        "type": "object"
      },
      "BalanceOverview": {
        "description": "User balance overview metrics",
        "properties": {
          "balance_display": {
            "description": "Formatted balance display",
            "type": "string"
          },
          "current_balance": {
            "description": "Current balance in USD",
            "format": "double",
            "type": "number"
          },
          "has_transactions": {
            "description": "Whether user has any transactions",
            "type": "boolean"
          },
          "is_empty": {
            "description": "Whether balance is zero",
            "type": "boolean"
          },
          "last_transaction_at": {
            "description": "Last transaction timestamp",
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "total_deposited": {
            "description": "Total amount deposited (lifetime)",
            "format": "double",
            "type": "number"
          },
          "total_spent": {
            "description": "Total amount spent (lifetime)",
            "format": "double",
            "type": "number"
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
        ],
        "type": "object"
      },
      "BulkEmailRequest": {
        "description": "Simple serializer for bulk email.",
        "properties": {
          "button_text": {
            "maxLength": 100,
            "type": "string"
          },
          "button_url": {
            "format": "uri",
            "type": "string"
          },
          "email_title": {
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          },
          "main_html_content": {
            "type": "string"
          },
          "main_text": {
            "minLength": 1,
            "type": "string"
          },
          "recipients": {
            "items": {
              "format": "email",
              "minLength": 1,
              "type": "string"
            },
            "maxItems": 100,
            "minItems": 1,
            "type": "array"
          },
          "secondary_text": {
            "type": "string"
          },
          "subject": {
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "email_title",
          "main_text",
          "recipients",
          "subject"
        ],
        "type": "object"
      },
      "BulkEmailResponse": {
        "description": "Response for bulk email sending.",
        "properties": {
          "error": {
            "type": "string"
          },
          "failed_count": {
            "type": "integer"
          },
          "sent_count": {
            "type": "integer"
          },
          "success": {
            "type": "boolean"
          },
          "total_recipients": {
            "type": "integer"
          }
        },
        "required": [
          "failed_count",
          "sent_count",
          "success",
          "total_recipients"
        ],
        "type": "object"
      },
      "ChartDataPoint": {
        "description": "Chart data point for payments analytics",
        "properties": {
          "x": {
            "description": "X-axis value (date)",
            "type": "string"
          },
          "y": {
            "description": "Y-axis value (amount or count)",
            "format": "double",
            "type": "number"
          }
        },
        "required": [
          "x",
          "y"
        ],
        "type": "object"
      },
      "ChartSeries": {
        "description": "Chart series data for payments visualization",
        "properties": {
          "color": {
            "description": "Series color",
            "type": "string"
          },
          "data": {
            "description": "Data points",
            "items": {
              "$ref": "#/components/schemas/ChartDataPoint"
            },
            "type": "array"
          },
          "name": {
            "description": "Series name",
            "type": "string"
          }
        },
        "required": [
          "color",
          "data",
          "name"
        ],
        "type": "object"
      },
      "Currency": {
        "description": "Complete currency serializer with full details.\n\nUsed for currency information and management.",
        "properties": {
          "code": {
            "description": "Currency code (e.g., BTC, USD, ETH)",
            "readOnly": true,
            "type": "string"
          },
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "currency_type": {
            "description": "Type of currency\n\n* `fiat` - Fiat Currency\n* `crypto` - Cryptocurrency",
            "enum": [
              "fiat",
              "crypto"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "1fd14ececc7d641f"
          },
          "decimal_places": {
            "description": "Number of decimal places for this currency",
            "readOnly": true,
            "type": "integer"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_active": {
            "description": "Whether this currency is available for payments",
            "readOnly": true,
            "type": "boolean"
          },
          "is_crypto": {
            "description": "Check if this is a cryptocurrency.",
            "readOnly": true,
            "type": "boolean"
          },
          "is_fiat": {
            "description": "Check if this is a fiat currency.",
            "readOnly": true,
            "type": "boolean"
          },
          "name": {
            "description": "Full currency name (e.g., Bitcoin, US Dollar)",
            "readOnly": true,
            "type": "string"
          },
          "symbol": {
            "description": "Currency symbol (e.g., $, \u20bf, \u039e)",
            "readOnly": true,
            "type": "string"
          },
          "type_display": {
            "readOnly": true,
            "type": "string"
          },
          "updated_at": {
            "description": "When this record was last updated",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "CurrencyAnalyticsItem": {
        "description": "Analytics data for a single currency",
        "properties": {
          "average_amount": {
            "description": "Average payment amount in USD",
            "format": "double",
            "type": "number"
          },
          "completed_payments": {
            "description": "Number of completed payments",
            "type": "integer"
          },
          "currency_code": {
            "description": "Currency code (e.g., BTC)",
            "type": "string"
          },
          "currency_name": {
            "description": "Currency name (e.g., Bitcoin)",
            "type": "string"
          },
          "success_rate": {
            "description": "Success rate percentage",
            "format": "double",
            "type": "number"
          },
          "total_amount": {
            "description": "Total amount in USD",
            "format": "double",
            "type": "number"
          },
          "total_payments": {
            "description": "Total number of payments",
            "type": "integer"
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
        ],
        "type": "object"
      },
      "CurrencyList": {
        "description": "Lightweight currency serializer for lists.\n\nOptimized for currency selection and lists.",
        "properties": {
          "code": {
            "description": "Currency code (e.g., BTC, USD, ETH)",
            "readOnly": true,
            "type": "string"
          },
          "currency_type": {
            "description": "Type of currency\n\n* `fiat` - Fiat Currency\n* `crypto` - Cryptocurrency",
            "enum": [
              "fiat",
              "crypto"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "1fd14ececc7d641f"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_active": {
            "description": "Whether this currency is available for payments",
            "readOnly": true,
            "type": "boolean"
          },
          "name": {
            "description": "Full currency name (e.g., Bitcoin, US Dollar)",
            "readOnly": true,
            "type": "string"
          },
          "symbol": {
            "description": "Currency symbol (e.g., $, \u20bf, \u039e)",
            "readOnly": true,
            "type": "string"
          },
          "type_display": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "EmailLog": {
        "description": "Serializer for EmailLog model.",
        "properties": {
          "body": {
            "readOnly": true,
            "title": "Body (HTML)",
            "type": "string"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "error_message": {
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "newsletter": {
            "nullable": true,
            "readOnly": true,
            "title": "Related Newsletter",
            "type": "integer"
          },
          "newsletter_title": {
            "readOnly": true,
            "type": "string"
          },
          "recipient": {
            "description": "Comma-separated email addresses",
            "readOnly": true,
            "title": "Recipient(s)",
            "type": "string"
          },
          "sent_at": {
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "status": {
            "description": "* `pending` - Pending\n* `sent` - Sent\n* `failed` - Failed",
            "enum": [
              "pending",
              "sent",
              "failed"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "6c875617d5f34e96"
          },
          "subject": {
            "readOnly": true,
            "type": "string"
          },
          "user": {
            "nullable": true,
            "readOnly": true,
            "title": "User Account",
            "type": "integer"
          },
          "user_email": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "EndpointGroup": {
        "description": "Endpoint group serializer for API access management.\n\nUsed for subscription endpoint group configuration.",
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "description": {
            "description": "Description of what this endpoint group provides",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_enabled": {
            "description": "Whether this endpoint group is available",
            "readOnly": true,
            "type": "boolean"
          },
          "name": {
            "description": "Endpoint group name (e.g., \u0027Payment API\u0027, \u0027Balance API\u0027)",
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
          "description",
          "id",
          "is_enabled",
          "name",
          "updated_at"
        ],
        "type": "object"
      },
      "ErrorResponse": {
        "description": "Generic error response.",
        "properties": {
          "message": {
            "type": "string"
          },
          "success": {
            "default": false,
            "type": "boolean"
          }
        },
        "required": [
          "message"
        ],
        "type": "object"
      },
      "LeadSubmission": {
        "description": "Serializer for lead form submission from frontend.",
        "properties": {
          "company": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "company_site": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "contact_type": {
            "description": "* `email` - Email\n* `whatsapp` - WhatsApp\n* `telegram` - Telegram\n* `phone` - Phone\n* `other` - Other",
            "enum": [
              "email",
              "whatsapp",
              "telegram",
              "phone",
              "other"
            ],
            "type": "string",
            "x-spec-enum-id": "2d58a06dc3d54732"
          },
          "contact_value": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "email": {
            "format": "email",
            "maxLength": 254,
            "type": "string"
          },
          "extra": {
            "nullable": true,
            "title": "Extra Data"
          },
          "message": {
            "type": "string"
          },
          "name": {
            "maxLength": 200,
            "title": "Full Name",
            "type": "string"
          },
          "site_url": {
            "description": "Frontend URL where form was submitted",
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          },
          "subject": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          }
        },
        "required": [
          "email",
          "message",
          "name",
          "site_url"
        ],
        "type": "object"
      },
      "LeadSubmissionError": {
        "description": "Response serializer for lead submission errors.",
        "properties": {
          "details": {
            "additionalProperties": {},
            "type": "object"
          },
          "error": {
            "type": "string"
          },
          "success": {
            "type": "boolean"
          }
        },
        "required": [
          "error",
          "success"
        ],
        "type": "object"
      },
      "LeadSubmissionRequest": {
        "description": "Serializer for lead form submission from frontend.",
        "properties": {
          "company": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "company_site": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "contact_type": {
            "description": "* `email` - Email\n* `whatsapp` - WhatsApp\n* `telegram` - Telegram\n* `phone` - Phone\n* `other` - Other",
            "enum": [
              "email",
              "whatsapp",
              "telegram",
              "phone",
              "other"
            ],
            "type": "string",
            "x-spec-enum-id": "2d58a06dc3d54732"
          },
          "contact_value": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "email": {
            "format": "email",
            "maxLength": 254,
            "minLength": 1,
            "type": "string"
          },
          "extra": {
            "nullable": true,
            "title": "Extra Data"
          },
          "message": {
            "minLength": 1,
            "type": "string"
          },
          "name": {
            "maxLength": 200,
            "minLength": 1,
            "title": "Full Name",
            "type": "string"
          },
          "site_url": {
            "description": "Frontend URL where form was submitted",
            "format": "uri",
            "maxLength": 200,
            "minLength": 1,
            "type": "string"
          },
          "subject": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          }
        },
        "required": [
          "email",
          "message",
          "name",
          "site_url"
        ],
        "type": "object"
      },
      "LeadSubmissionResponse": {
        "description": "Response serializer for successful lead submission.",
        "properties": {
          "lead_id": {
            "type": "integer"
          },
          "message": {
            "type": "string"
          },
          "success": {
            "type": "boolean"
          }
        },
        "required": [
          "lead_id",
          "message",
          "success"
        ],
        "type": "object"
      },
      "Message": {
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "is_from_author": {
            "description": "Check if this message is from the ticket author.",
            "readOnly": true,
            "type": "boolean"
          },
          "sender": {
            "allOf": [
              {
                "$ref": "#/components/schemas/Sender"
              }
            ],
            "readOnly": true
          },
          "text": {
            "type": "string"
          },
          "ticket": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "uuid": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "created_at",
          "is_from_author",
          "sender",
          "text",
          "ticket",
          "uuid"
        ],
        "type": "object"
      },
      "MessageCreate": {
        "properties": {
          "text": {
            "type": "string"
          }
        },
        "required": [
          "text"
        ],
        "type": "object"
      },
      "MessageCreateRequest": {
        "properties": {
          "text": {
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "text"
        ],
        "type": "object"
      },
      "MessageRequest": {
        "properties": {
          "text": {
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "text"
        ],
        "type": "object"
      },
      "Network": {
        "description": "Network serializer for blockchain networks.\n\nUsed for network information and selection.",
        "properties": {
          "code": {
            "description": "Network code (e.g., ETH, BTC, MATIC)",
            "readOnly": true,
            "type": "string"
          },
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "currency": {
            "allOf": [
              {
                "$ref": "#/components/schemas/CurrencyList"
              }
            ],
            "readOnly": true
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_active": {
            "description": "Whether this network is available for payments",
            "readOnly": true,
            "type": "boolean"
          },
          "name": {
            "description": "Network name (e.g., Ethereum, Bitcoin, Polygon)",
            "readOnly": true,
            "type": "string"
          },
          "updated_at": {
            "description": "When this record was last updated",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "Newsletter": {
        "description": "Serializer for Newsletter model.",
        "properties": {
          "auto_subscribe": {
            "description": "Automatically subscribe new users to this newsletter",
            "title": "Auto Subscribe New Users",
            "type": "boolean"
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
            "title": "Active",
            "type": "boolean"
          },
          "subscribers_count": {
            "readOnly": true,
            "type": "integer"
          },
          "title": {
            "maxLength": 255,
            "title": "Newsletter Title",
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
          "id",
          "subscribers_count",
          "title",
          "updated_at"
        ],
        "type": "object"
      },
      "NewsletterCampaign": {
        "description": "Serializer for NewsletterCampaign model.",
        "properties": {
          "button_text": {
            "maxLength": 100,
            "type": "string"
          },
          "button_url": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "email_title": {
            "maxLength": 255,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "main_html_content": {
            "title": "HTML Content",
            "type": "string"
          },
          "main_text": {
            "type": "string"
          },
          "newsletter": {
            "type": "integer"
          },
          "newsletter_title": {
            "readOnly": true,
            "type": "string"
          },
          "recipient_count": {
            "readOnly": true,
            "type": "integer"
          },
          "secondary_text": {
            "type": "string"
          },
          "sent_at": {
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "status": {
            "description": "* `draft` - Draft\n* `sending` - Sending\n* `sent` - Sent\n* `failed` - Failed",
            "enum": [
              "draft",
              "sending",
              "sent",
              "failed"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "a459055d142d5a82"
          },
          "subject": {
            "maxLength": 255,
            "type": "string"
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
        ],
        "type": "object"
      },
      "NewsletterCampaignRequest": {
        "description": "Serializer for NewsletterCampaign model.",
        "properties": {
          "button_text": {
            "maxLength": 100,
            "type": "string"
          },
          "button_url": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          },
          "email_title": {
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          },
          "main_html_content": {
            "title": "HTML Content",
            "type": "string"
          },
          "main_text": {
            "minLength": 1,
            "type": "string"
          },
          "newsletter": {
            "type": "integer"
          },
          "secondary_text": {
            "type": "string"
          },
          "subject": {
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "email_title",
          "main_text",
          "newsletter",
          "subject"
        ],
        "type": "object"
      },
      "NewsletterSubscription": {
        "description": "Serializer for NewsletterSubscription model.",
        "properties": {
          "email": {
            "format": "email",
            "maxLength": 254,
            "title": "Email Address",
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_active": {
            "title": "Active",
            "type": "boolean"
          },
          "newsletter": {
            "type": "integer"
          },
          "newsletter_title": {
            "readOnly": true,
            "type": "string"
          },
          "subscribed_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "unsubscribed_at": {
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "user": {
            "nullable": true,
            "type": "integer"
          },
          "user_email": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "OTPErrorResponse": {
        "description": "Error response for OTP operations.",
        "properties": {
          "error": {
            "description": "Error message",
            "type": "string"
          }
        },
        "required": [
          "error"
        ],
        "type": "object"
      },
      "OTPRequestRequest": {
        "description": "Serializer for OTP request.",
        "properties": {
          "channel": {
            "description": "Delivery channel: \u0027email\u0027 or \u0027phone\u0027. Auto-detected if not provided.\n\n* `email` - Email\n* `phone` - Phone",
            "enum": [
              "email",
              "phone"
            ],
            "type": "string",
            "x-spec-enum-id": "17f11a3a6a4008ba"
          },
          "identifier": {
            "description": "Email address or phone number for OTP delivery",
            "minLength": 1,
            "type": "string"
          },
          "source_url": {
            "description": "Source URL for tracking registration (e.g., https://dashboard.unrealon.com)",
            "format": "uri",
            "type": "string"
          }
        },
        "required": [
          "identifier"
        ],
        "type": "object"
      },
      "OTPRequestResponse": {
        "description": "OTP request response.",
        "properties": {
          "message": {
            "description": "Success message",
            "type": "string"
          }
        },
        "required": [
          "message"
        ],
        "type": "object"
      },
      "OTPVerifyRequest": {
        "description": "Serializer for OTP verification.",
        "properties": {
          "channel": {
            "description": "Delivery channel: \u0027email\u0027 or \u0027phone\u0027. Auto-detected if not provided.\n\n* `email` - Email\n* `phone` - Phone",
            "enum": [
              "email",
              "phone"
            ],
            "type": "string",
            "x-spec-enum-id": "17f11a3a6a4008ba"
          },
          "identifier": {
            "description": "Email address or phone number used for OTP request",
            "minLength": 1,
            "type": "string"
          },
          "otp": {
            "maxLength": 6,
            "minLength": 6,
            "type": "string"
          },
          "source_url": {
            "description": "Source URL for tracking login (e.g., https://dashboard.unrealon.com)",
            "format": "uri",
            "type": "string"
          }
        },
        "required": [
          "identifier",
          "otp"
        ],
        "type": "object"
      },
      "OTPVerifyResponse": {
        "description": "OTP verification response.",
        "properties": {
          "access": {
            "description": "JWT access token",
            "type": "string"
          },
          "refresh": {
            "description": "JWT refresh token",
            "type": "string"
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
        ],
        "type": "object"
      },
      "PaginatedAPIKeyListList": {
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
              "$ref": "#/components/schemas/APIKeyList"
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
      "PaginatedCurrencyListList": {
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
              "$ref": "#/components/schemas/CurrencyList"
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
      "PaginatedEmailLogList": {
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
              "$ref": "#/components/schemas/EmailLog"
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
      "PaginatedEndpointGroupList": {
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
              "$ref": "#/components/schemas/EndpointGroup"
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
      "PaginatedLeadSubmissionList": {
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
              "$ref": "#/components/schemas/LeadSubmission"
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
      "PaginatedNetworkList": {
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
              "$ref": "#/components/schemas/Network"
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
      "PaginatedNewsletterCampaignList": {
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
              "$ref": "#/components/schemas/NewsletterCampaign"
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
      "PaginatedNewsletterList": {
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
              "$ref": "#/components/schemas/Newsletter"
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
      "PaginatedNewsletterSubscriptionList": {
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
              "$ref": "#/components/schemas/NewsletterSubscription"
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
      "PaginatedPaymentListList": {
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
              "$ref": "#/components/schemas/PaymentList"
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
      "PaginatedProviderCurrencyList": {
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
              "$ref": "#/components/schemas/ProviderCurrency"
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
      "PaginatedRecentPaymentList": {
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
              "$ref": "#/components/schemas/RecentPayment"
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
      "PaginatedRecentTransactionList": {
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
              "$ref": "#/components/schemas/RecentTransaction"
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
      "PaginatedSubscriptionListList": {
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
              "$ref": "#/components/schemas/SubscriptionList"
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
      "PaginatedTariffList": {
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
              "$ref": "#/components/schemas/Tariff"
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
      "PaginatedTransactionList": {
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
              "$ref": "#/components/schemas/Transaction"
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
      "PaginatedUserBalanceList": {
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
              "$ref": "#/components/schemas/UserBalance"
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
      "PatchedAPIKeyUpdateRequest": {
        "description": "API key update serializer for modifying API key properties.\n\nAllows updating name and active status only.",
        "properties": {
          "is_active": {
            "description": "Whether this API key is active",
            "type": "boolean"
          },
          "name": {
            "description": "Human-readable name for this API key",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PatchedLeadSubmissionRequest": {
        "description": "Serializer for lead form submission from frontend.",
        "properties": {
          "company": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "company_site": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "contact_type": {
            "description": "* `email` - Email\n* `whatsapp` - WhatsApp\n* `telegram` - Telegram\n* `phone` - Phone\n* `other` - Other",
            "enum": [
              "email",
              "whatsapp",
              "telegram",
              "phone",
              "other"
            ],
            "type": "string",
            "x-spec-enum-id": "2d58a06dc3d54732"
          },
          "contact_value": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "email": {
            "format": "email",
            "maxLength": 254,
            "minLength": 1,
            "type": "string"
          },
          "extra": {
            "nullable": true,
            "title": "Extra Data"
          },
          "message": {
            "minLength": 1,
            "type": "string"
          },
          "name": {
            "maxLength": 200,
            "minLength": 1,
            "title": "Full Name",
            "type": "string"
          },
          "site_url": {
            "description": "Frontend URL where form was submitted",
            "format": "uri",
            "maxLength": 200,
            "minLength": 1,
            "type": "string"
          },
          "subject": {
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PatchedMessageRequest": {
        "properties": {
          "text": {
            "minLength": 1,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PatchedNewsletterCampaignRequest": {
        "description": "Serializer for NewsletterCampaign model.",
        "properties": {
          "button_text": {
            "maxLength": 100,
            "type": "string"
          },
          "button_url": {
            "format": "uri",
            "maxLength": 200,
            "type": "string"
          },
          "email_title": {
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          },
          "main_html_content": {
            "title": "HTML Content",
            "type": "string"
          },
          "main_text": {
            "minLength": 1,
            "type": "string"
          },
          "newsletter": {
            "type": "integer"
          },
          "secondary_text": {
            "type": "string"
          },
          "subject": {
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PatchedPaymentRequest": {
        "description": "Complete payment serializer with full details.\n\nUsed for detail views and updates.",
        "properties": {
          "amount_usd": {
            "description": "Payment amount in USD (float for performance)",
            "format": "double",
            "maximum": 50000.0,
            "minimum": 1.0,
            "type": "number"
          },
          "callback_url": {
            "description": "Success callback URL",
            "format": "uri",
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "cancel_url": {
            "description": "Cancellation URL",
            "format": "uri",
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "currency": {
            "description": "Payment currency",
            "type": "integer"
          },
          "description": {
            "description": "Payment description",
            "type": "string"
          },
          "expires_at": {
            "description": "When this payment expires",
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "network": {
            "description": "Blockchain network (for crypto payments)",
            "nullable": true,
            "type": "integer"
          },
          "provider": {
            "description": "Payment provider\n\n* `nowpayments` - NowPayments",
            "enum": [
              "nowpayments"
            ],
            "type": "string",
            "x-spec-enum-id": "47694db6bd068cb3"
          },
          "status": {
            "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
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
            "x-spec-enum-id": "59d07a8608d1bdb9"
          }
        },
        "type": "object"
      },
      "PatchedSubscriptionRequest": {
        "description": "Complete subscription serializer with full details.\n\nUsed for subscription detail views and updates.",
        "properties": {
          "expires_at": {
            "description": "When this subscription expires",
            "format": "date-time",
            "type": "string"
          },
          "status": {
            "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired",
            "enum": [
              "active",
              "inactive",
              "suspended",
              "cancelled",
              "expired"
            ],
            "type": "string",
            "x-spec-enum-id": "20d0bcc8b3c2bafa"
          },
          "tier": {
            "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier",
            "enum": [
              "free",
              "basic",
              "pro",
              "enterprise"
            ],
            "type": "string",
            "x-spec-enum-id": "776e806f04431486"
          }
        },
        "type": "object"
      },
      "PatchedTicketRequest": {
        "properties": {
          "status": {
            "description": "* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed",
            "enum": [
              "open",
              "waiting_for_user",
              "waiting_for_admin",
              "resolved",
              "closed"
            ],
            "type": "string",
            "x-spec-enum-id": "c21b48fabf2398aa"
          },
          "subject": {
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          },
          "user": {
            "type": "integer"
          }
        },
        "type": "object"
      },
      "PatchedUnsubscribeRequest": {
        "description": "Simple serializer for unsubscribe.",
        "properties": {
          "subscription_id": {
            "type": "integer"
          }
        },
        "type": "object"
      },
      "PatchedUserProfileUpdateRequest": {
        "description": "Serializer for updating user profile.",
        "properties": {
          "company": {
            "maxLength": 100,
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
          "phone": {
            "maxLength": 20,
            "type": "string"
          },
          "position": {
            "maxLength": 100,
            "type": "string"
          }
        },
        "type": "object"
      },
      "Payment": {
        "description": "Complete payment serializer with full details.\n\nUsed for detail views and updates.",
        "properties": {
          "amount_display": {
            "description": "Get formatted amount display.",
            "readOnly": true,
            "type": "string"
          },
          "amount_usd": {
            "description": "Payment amount in USD (float for performance)",
            "format": "double",
            "maximum": 50000.0,
            "minimum": 1.0,
            "type": "number"
          },
          "callback_url": {
            "description": "Success callback URL",
            "format": "uri",
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "cancel_url": {
            "description": "Cancellation URL",
            "format": "uri",
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "completed_at": {
            "description": "When this payment was completed",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "confirmations_count": {
            "description": "Number of blockchain confirmations",
            "readOnly": true,
            "type": "integer"
          },
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "currency": {
            "description": "Payment currency",
            "type": "integer"
          },
          "description": {
            "description": "Payment description",
            "type": "string"
          },
          "expires_at": {
            "description": "When this payment expires",
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "id": {
            "description": "Unique identifier for this record",
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_completed": {
            "description": "Check if payment is completed.",
            "readOnly": true,
            "type": "boolean"
          },
          "is_expired": {
            "description": "Check if payment is expired.",
            "readOnly": true,
            "type": "boolean"
          },
          "is_failed": {
            "description": "Check if payment is failed.",
            "readOnly": true,
            "type": "boolean"
          },
          "is_pending": {
            "description": "Check if payment is pending.",
            "readOnly": true,
            "type": "boolean"
          },
          "network": {
            "description": "Blockchain network (for crypto payments)",
            "nullable": true,
            "type": "integer"
          },
          "pay_address": {
            "description": "Cryptocurrency payment address",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "payment_url": {
            "description": "Payment page URL",
            "format": "uri",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "provider": {
            "description": "Payment provider\n\n* `nowpayments` - NowPayments",
            "enum": [
              "nowpayments"
            ],
            "type": "string",
            "x-spec-enum-id": "47694db6bd068cb3"
          },
          "provider_payment_id": {
            "description": "Provider\u0027s payment ID",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "status": {
            "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
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
            "x-spec-enum-id": "59d07a8608d1bdb9"
          },
          "status_display": {
            "readOnly": true,
            "type": "string"
          },
          "transaction_hash": {
            "description": "Blockchain transaction hash",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "updated_at": {
            "description": "When this record was last updated",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "user": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "PaymentAnalyticsResponse": {
        "description": "Payment analytics response with currency and provider breakdown",
        "properties": {
          "currency_analytics": {
            "description": "Analytics by currency",
            "items": {
              "$ref": "#/components/schemas/CurrencyAnalyticsItem"
            },
            "type": "array"
          },
          "provider_analytics": {
            "description": "Analytics by provider",
            "items": {
              "$ref": "#/components/schemas/ProviderAnalyticsItem"
            },
            "type": "array"
          }
        },
        "required": [
          "currency_analytics",
          "provider_analytics"
        ],
        "type": "object"
      },
      "PaymentCreate": {
        "description": "Payment creation serializer with Pydantic integration.\n\nValidates input and delegates to PaymentService.",
        "properties": {
          "amount_usd": {
            "description": "Amount in USD (1.00 - 50,000.00)",
            "format": "double",
            "maximum": 50000.0,
            "minimum": 1.0,
            "type": "number"
          },
          "callback_url": {
            "description": "Success callback URL",
            "format": "uri",
            "type": "string"
          },
          "cancel_url": {
            "description": "Cancellation URL",
            "format": "uri",
            "type": "string"
          },
          "currency_code": {
            "description": "Cryptocurrency to receive\n\n* `BTC` - Bitcoin\n* `ETH` - Ethereum\n* `LTC` - Litecoin\n* `XMR` - Monero\n* `USDT` - Tether\n* `USDC` - USD Coin\n* `ADA` - Cardano\n* `DOT` - Polkadot",
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
            "x-spec-enum-id": "a26a773d0d4fed5c"
          },
          "description": {
            "description": "Payment description",
            "maxLength": 500,
            "type": "string"
          },
          "metadata": {
            "description": "Additional metadata"
          },
          "provider": {
            "default": "nowpayments",
            "description": "Payment provider\n\n* `nowpayments` - NowPayments",
            "enum": [
              "nowpayments"
            ],
            "type": "string",
            "x-spec-enum-id": "47694db6bd068cb3"
          }
        },
        "required": [
          "amount_usd",
          "currency_code"
        ],
        "type": "object"
      },
      "PaymentCreateRequest": {
        "description": "Payment creation serializer with Pydantic integration.\n\nValidates input and delegates to PaymentService.",
        "properties": {
          "amount_usd": {
            "description": "Amount in USD (1.00 - 50,000.00)",
            "format": "double",
            "maximum": 50000.0,
            "minimum": 1.0,
            "type": "number"
          },
          "callback_url": {
            "description": "Success callback URL",
            "format": "uri",
            "type": "string"
          },
          "cancel_url": {
            "description": "Cancellation URL",
            "format": "uri",
            "type": "string"
          },
          "currency_code": {
            "description": "Cryptocurrency to receive\n\n* `BTC` - Bitcoin\n* `ETH` - Ethereum\n* `LTC` - Litecoin\n* `XMR` - Monero\n* `USDT` - Tether\n* `USDC` - USD Coin\n* `ADA` - Cardano\n* `DOT` - Polkadot",
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
            "x-spec-enum-id": "a26a773d0d4fed5c"
          },
          "description": {
            "description": "Payment description",
            "maxLength": 500,
            "type": "string"
          },
          "metadata": {
            "description": "Additional metadata"
          },
          "provider": {
            "default": "nowpayments",
            "description": "Payment provider\n\n* `nowpayments` - NowPayments",
            "enum": [
              "nowpayments"
            ],
            "type": "string",
            "x-spec-enum-id": "47694db6bd068cb3"
          }
        },
        "required": [
          "amount_usd",
          "currency_code"
        ],
        "type": "object"
      },
      "PaymentList": {
        "description": "Lightweight serializer for payment lists.\n\nOptimized for list views with minimal data.",
        "properties": {
          "amount_display": {
            "description": "Get formatted amount display.",
            "readOnly": true,
            "type": "string"
          },
          "amount_usd": {
            "description": "Payment amount in USD (float for performance)",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "currency": {
            "description": "Payment currency",
            "readOnly": true,
            "type": "integer"
          },
          "expires_at": {
            "description": "When this payment expires",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "description": "Unique identifier for this record",
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "provider": {
            "description": "Payment provider\n\n* `nowpayments` - NowPayments",
            "enum": [
              "nowpayments"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "47694db6bd068cb3"
          },
          "status": {
            "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
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
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "59d07a8608d1bdb9"
          },
          "status_display": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "PaymentOverview": {
        "description": "Payments overview metrics",
        "properties": {
          "amount_this_month": {
            "description": "Total amount this month",
            "format": "double",
            "type": "number"
          },
          "average_payment_usd": {
            "description": "Average payment amount in USD",
            "format": "double",
            "type": "number"
          },
          "completed_amount_usd": {
            "description": "Total completed amount in USD",
            "format": "double",
            "type": "number"
          },
          "completed_payments": {
            "description": "Number of completed payments",
            "type": "integer"
          },
          "failed_payments": {
            "description": "Number of failed payments",
            "type": "integer"
          },
          "last_payment_at": {
            "description": "Last payment timestamp",
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "payments_this_month": {
            "description": "Number of payments this month",
            "type": "integer"
          },
          "pending_payments": {
            "description": "Number of pending payments",
            "type": "integer"
          },
          "success_rate": {
            "description": "Payment success rate percentage",
            "format": "double",
            "type": "number"
          },
          "top_currency": {
            "description": "Most used currency",
            "nullable": true,
            "type": "string"
          },
          "top_currency_count": {
            "description": "Usage count for top currency",
            "type": "integer"
          },
          "total_amount_usd": {
            "description": "Total payment amount in USD",
            "format": "double",
            "type": "number"
          },
          "total_payments": {
            "description": "Total number of payments",
            "type": "integer"
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
        ],
        "type": "object"
      },
      "PaymentRequest": {
        "description": "Complete payment serializer with full details.\n\nUsed for detail views and updates.",
        "properties": {
          "amount_usd": {
            "description": "Payment amount in USD (float for performance)",
            "format": "double",
            "maximum": 50000.0,
            "minimum": 1.0,
            "type": "number"
          },
          "callback_url": {
            "description": "Success callback URL",
            "format": "uri",
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "cancel_url": {
            "description": "Cancellation URL",
            "format": "uri",
            "maxLength": 200,
            "nullable": true,
            "type": "string"
          },
          "currency": {
            "description": "Payment currency",
            "type": "integer"
          },
          "description": {
            "description": "Payment description",
            "type": "string"
          },
          "expires_at": {
            "description": "When this payment expires",
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "network": {
            "description": "Blockchain network (for crypto payments)",
            "nullable": true,
            "type": "integer"
          },
          "provider": {
            "description": "Payment provider\n\n* `nowpayments` - NowPayments",
            "enum": [
              "nowpayments"
            ],
            "type": "string",
            "x-spec-enum-id": "47694db6bd068cb3"
          },
          "status": {
            "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
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
            "x-spec-enum-id": "59d07a8608d1bdb9"
          }
        },
        "required": [
          "amount_usd",
          "currency"
        ],
        "type": "object"
      },
      "PaymentsChartResponse": {
        "description": "Complete chart response for payments analytics",
        "properties": {
          "period": {
            "description": "Time period",
            "type": "string"
          },
          "series": {
            "description": "Chart series data",
            "items": {
              "$ref": "#/components/schemas/ChartSeries"
            },
            "type": "array"
          },
          "success_rate": {
            "description": "Success rate for period",
            "format": "double",
            "type": "number"
          },
          "total_amount": {
            "description": "Total amount for period",
            "format": "double",
            "type": "number"
          },
          "total_payments": {
            "description": "Total payments for period",
            "type": "integer"
          }
        },
        "required": [
          "period",
          "series",
          "success_rate",
          "total_amount",
          "total_payments"
        ],
        "type": "object"
      },
      "PaymentsDashboardOverview": {
        "description": "Complete payments dashboard overview response",
        "properties": {
          "chart_data": {
            "allOf": [
              {
                "$ref": "#/components/schemas/PaymentsChartResponse"
              }
            ],
            "description": "Chart data for analytics"
          },
          "metrics": {
            "allOf": [
              {
                "$ref": "#/components/schemas/PaymentsMetrics"
              }
            ],
            "description": "Dashboard metrics"
          },
          "recent_payments": {
            "description": "Recent payments",
            "items": {
              "$ref": "#/components/schemas/RecentPayment"
            },
            "type": "array"
          },
          "recent_transactions": {
            "description": "Recent transactions",
            "items": {
              "$ref": "#/components/schemas/RecentTransaction"
            },
            "type": "array"
          }
        },
        "required": [
          "chart_data",
          "metrics",
          "recent_payments",
          "recent_transactions"
        ],
        "type": "object"
      },
      "PaymentsMetrics": {
        "description": "Complete payments dashboard metrics",
        "properties": {
          "api_keys": {
            "allOf": [
              {
                "$ref": "#/components/schemas/APIKeysOverview"
              }
            ],
            "description": "API keys overview"
          },
          "balance": {
            "allOf": [
              {
                "$ref": "#/components/schemas/BalanceOverview"
              }
            ],
            "description": "Balance overview"
          },
          "payments": {
            "allOf": [
              {
                "$ref": "#/components/schemas/PaymentOverview"
              }
            ],
            "description": "Payments overview"
          },
          "subscription": {
            "allOf": [
              {
                "$ref": "#/components/schemas/SubscriptionOverview"
              }
            ],
            "description": "Subscription overview",
            "nullable": true
          }
        },
        "required": [
          "api_keys",
          "balance",
          "payments",
          "subscription"
        ],
        "type": "object"
      },
      "ProviderAnalyticsItem": {
        "description": "Analytics data for a single payment provider",
        "properties": {
          "completed_payments": {
            "description": "Number of completed payments",
            "type": "integer"
          },
          "provider": {
            "description": "Provider code",
            "type": "string"
          },
          "provider_display": {
            "description": "Provider display name",
            "type": "string"
          },
          "success_rate": {
            "description": "Success rate percentage",
            "format": "double",
            "type": "number"
          },
          "total_amount": {
            "description": "Total amount in USD",
            "format": "double",
            "type": "number"
          },
          "total_payments": {
            "description": "Total number of payments",
            "type": "integer"
          }
        },
        "required": [
          "completed_payments",
          "provider",
          "provider_display",
          "success_rate",
          "total_amount",
          "total_payments"
        ],
        "type": "object"
      },
      "ProviderCurrency": {
        "description": "Provider currency serializer for provider-specific currency info.\n\nUsed for provider currency management and rates.",
        "properties": {
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "currency": {
            "allOf": [
              {
                "$ref": "#/components/schemas/CurrencyList"
              }
            ],
            "readOnly": true
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_enabled": {
            "description": "Whether this currency is enabled for this provider",
            "readOnly": true,
            "type": "boolean"
          },
          "network": {
            "allOf": [
              {
                "$ref": "#/components/schemas/Network"
              }
            ],
            "readOnly": true
          },
          "provider": {
            "description": "Payment provider name (e.g., nowpayments)",
            "readOnly": true,
            "type": "string"
          },
          "provider_currency_code": {
            "description": "Currency code as used by the provider",
            "readOnly": true,
            "type": "string"
          },
          "provider_fee_percentage": {
            "description": "Get fee percentage from provider configuration.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "provider_fixed_fee_usd": {
            "description": "Get fixed fee from provider configuration.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "provider_max_amount_usd": {
            "description": "Get maximum amount from provider configuration.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "provider_min_amount_usd": {
            "description": "Get minimum amount from provider configuration.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "updated_at": {
            "description": "When this record was last updated",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "QueueAction": {
        "description": "Serializer for queue management actions.",
        "properties": {
          "action": {
            "description": "Action to perform on queues\n\n* `clear` - clear\n* `clear_all` - clear_all\n* `purge` - purge\n* `purge_failed` - purge_failed\n* `flush` - flush",
            "enum": [
              "clear",
              "clear_all",
              "purge",
              "purge_failed",
              "flush"
            ],
            "type": "string",
            "x-spec-enum-id": "4a60a2c6249b0803"
          },
          "queue_names": {
            "description": "Specific queues to target (empty = all queues)",
            "items": {
              "type": "string"
            },
            "type": "array"
          }
        },
        "required": [
          "action"
        ],
        "type": "object"
      },
      "QueueActionRequest": {
        "description": "Serializer for queue management actions.",
        "properties": {
          "action": {
            "description": "Action to perform on queues\n\n* `clear` - clear\n* `clear_all` - clear_all\n* `purge` - purge\n* `purge_failed` - purge_failed\n* `flush` - flush",
            "enum": [
              "clear",
              "clear_all",
              "purge",
              "purge_failed",
              "flush"
            ],
            "type": "string",
            "x-spec-enum-id": "4a60a2c6249b0803"
          },
          "queue_names": {
            "description": "Specific queues to target (empty = all queues)",
            "items": {
              "minLength": 1,
              "type": "string"
            },
            "type": "array"
          }
        },
        "required": [
          "action"
        ],
        "type": "object"
      },
      "QueueStatus": {
        "description": "Serializer for queue status data.",
        "properties": {
          "error": {
            "description": "Error message if any",
            "type": "string"
          },
          "queues": {
            "additionalProperties": {
              "additionalProperties": {
                "type": "integer"
              },
              "type": "object"
            },
            "description": "Queue information with pending/failed counts",
            "type": "object"
          },
          "redis_connected": {
            "description": "Redis connection status",
            "type": "boolean"
          },
          "timestamp": {
            "description": "Current timestamp",
            "type": "string"
          },
          "workers": {
            "description": "Number of active workers",
            "type": "integer"
          }
        },
        "required": [
          "queues",
          "redis_connected",
          "timestamp",
          "workers"
        ],
        "type": "object"
      },
      "RecentPayment": {
        "description": "Recent payment item",
        "properties": {
          "amount_display": {
            "description": "Formatted amount display",
            "type": "string"
          },
          "amount_usd": {
            "description": "Payment amount in USD",
            "format": "double",
            "type": "number"
          },
          "completed_at": {
            "description": "Payment completion timestamp",
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "created_at": {
            "description": "Payment creation timestamp",
            "format": "date-time",
            "type": "string"
          },
          "currency_code": {
            "description": "Currency code",
            "type": "string"
          },
          "id": {
            "description": "Payment ID",
            "format": "uuid",
            "type": "string"
          },
          "internal_payment_id": {
            "description": "Internal payment ID",
            "type": "string"
          },
          "is_completed": {
            "description": "Whether payment is completed",
            "type": "boolean"
          },
          "is_failed": {
            "description": "Whether payment failed",
            "type": "boolean"
          },
          "is_pending": {
            "description": "Whether payment is pending",
            "type": "boolean"
          },
          "provider": {
            "description": "Payment provider",
            "type": "string"
          },
          "status": {
            "description": "Payment status",
            "type": "string"
          },
          "status_color": {
            "description": "Color for status display",
            "type": "string"
          },
          "status_display": {
            "description": "Human-readable status",
            "type": "string"
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
        ],
        "type": "object"
      },
      "RecentTransaction": {
        "description": "Recent transaction item",
        "properties": {
          "amount_display": {
            "description": "Formatted amount display",
            "type": "string"
          },
          "amount_usd": {
            "description": "Transaction amount in USD",
            "format": "double",
            "type": "number"
          },
          "balance_after": {
            "description": "Balance after transaction",
            "format": "double",
            "type": "number"
          },
          "created_at": {
            "description": "Transaction timestamp",
            "format": "date-time",
            "type": "string"
          },
          "description": {
            "description": "Transaction description",
            "type": "string"
          },
          "id": {
            "description": "Transaction ID",
            "format": "uuid",
            "type": "string"
          },
          "is_credit": {
            "description": "Whether this is a credit transaction",
            "type": "boolean"
          },
          "is_debit": {
            "description": "Whether this is a debit transaction",
            "type": "boolean"
          },
          "payment_id": {
            "description": "Related payment ID",
            "nullable": true,
            "type": "string"
          },
          "transaction_type": {
            "description": "Transaction type",
            "type": "string"
          },
          "type_color": {
            "description": "Color for transaction type display",
            "type": "string"
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
        ],
        "type": "object"
      },
      "SendCampaignRequest": {
        "description": "Simple serializer for sending campaign.",
        "properties": {
          "campaign_id": {
            "type": "integer"
          }
        },
        "required": [
          "campaign_id"
        ],
        "type": "object"
      },
      "SendCampaignResponse": {
        "description": "Response for sending campaign.",
        "properties": {
          "error": {
            "type": "string"
          },
          "message": {
            "type": "string"
          },
          "sent_count": {
            "type": "integer"
          },
          "success": {
            "type": "boolean"
          }
        },
        "required": [
          "success"
        ],
        "type": "object"
      },
      "Sender": {
        "properties": {
          "avatar": {
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "display_username": {
            "description": "Get formatted username for display.",
            "readOnly": true,
            "type": "string"
          },
          "email": {
            "format": "email",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "initials": {
            "description": "Get user\u0027s initials for avatar fallback.",
            "readOnly": true,
            "type": "string"
          },
          "is_staff": {
            "description": "Designates whether the user can log into this admin site.",
            "readOnly": true,
            "title": "Staff status",
            "type": "boolean"
          },
          "is_superuser": {
            "description": "Designates that this user has all permissions without explicitly assigning them.",
            "readOnly": true,
            "title": "Superuser status",
            "type": "boolean"
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
        ],
        "type": "object"
      },
      "SubscribeRequest": {
        "description": "Simple serializer for newsletter subscription.",
        "properties": {
          "email": {
            "format": "email",
            "minLength": 1,
            "type": "string"
          },
          "newsletter_id": {
            "type": "integer"
          }
        },
        "required": [
          "email",
          "newsletter_id"
        ],
        "type": "object"
      },
      "SubscribeResponse": {
        "description": "Response for subscription.",
        "properties": {
          "message": {
            "type": "string"
          },
          "subscription_id": {
            "type": "integer"
          },
          "success": {
            "type": "boolean"
          }
        },
        "required": [
          "message",
          "success"
        ],
        "type": "object"
      },
      "Subscription": {
        "description": "Complete subscription serializer with full details.\n\nUsed for subscription detail views and updates.",
        "properties": {
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "endpoint_group": {
            "allOf": [
              {
                "$ref": "#/components/schemas/EndpointGroup"
              }
            ],
            "readOnly": true
          },
          "expires_at": {
            "description": "When this subscription expires",
            "format": "date-time",
            "type": "string"
          },
          "id": {
            "description": "Unique identifier for this record",
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_active": {
            "description": "Check if subscription is active and not expired.",
            "readOnly": true,
            "type": "boolean"
          },
          "is_expired": {
            "description": "Check if subscription is expired.",
            "readOnly": true,
            "type": "boolean"
          },
          "last_request_at": {
            "description": "When the last API request was made",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "status": {
            "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired",
            "enum": [
              "active",
              "inactive",
              "suspended",
              "cancelled",
              "expired"
            ],
            "type": "string",
            "x-spec-enum-id": "20d0bcc8b3c2bafa"
          },
          "status_color": {
            "description": "Get color for status display.",
            "readOnly": true,
            "type": "string"
          },
          "status_display": {
            "readOnly": true,
            "type": "string"
          },
          "tariff": {
            "allOf": [
              {
                "$ref": "#/components/schemas/Tariff"
              }
            ],
            "readOnly": true
          },
          "tier": {
            "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier",
            "enum": [
              "free",
              "basic",
              "pro",
              "enterprise"
            ],
            "type": "string",
            "x-spec-enum-id": "776e806f04431486"
          },
          "total_requests": {
            "description": "Total API requests made with this subscription",
            "readOnly": true,
            "type": "integer"
          },
          "updated_at": {
            "description": "When this record was last updated",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "usage_percentage": {
            "description": "Get usage percentage for current period.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "user": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "SubscriptionCreate": {
        "description": "Subscription creation serializer with service integration.\n\nValidates input and delegates to SubscriptionService.",
        "properties": {
          "duration_days": {
            "default": 30,
            "description": "Subscription duration in days",
            "maximum": 365,
            "minimum": 1,
            "type": "integer"
          },
          "endpoint_group_id": {
            "description": "Endpoint group ID (optional)",
            "minimum": 1,
            "nullable": true,
            "type": "integer"
          },
          "tariff_id": {
            "description": "Tariff ID for the subscription",
            "minimum": 1,
            "type": "integer"
          }
        },
        "required": [
          "tariff_id"
        ],
        "type": "object"
      },
      "SubscriptionCreateRequest": {
        "description": "Subscription creation serializer with service integration.\n\nValidates input and delegates to SubscriptionService.",
        "properties": {
          "duration_days": {
            "default": 30,
            "description": "Subscription duration in days",
            "maximum": 365,
            "minimum": 1,
            "type": "integer"
          },
          "endpoint_group_id": {
            "description": "Endpoint group ID (optional)",
            "minimum": 1,
            "nullable": true,
            "type": "integer"
          },
          "tariff_id": {
            "description": "Tariff ID for the subscription",
            "minimum": 1,
            "type": "integer"
          }
        },
        "required": [
          "tariff_id"
        ],
        "type": "object"
      },
      "SubscriptionList": {
        "description": "Lightweight subscription serializer for lists.\n\nOptimized for subscription lists with minimal data.",
        "properties": {
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "expires_at": {
            "description": "When this subscription expires",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "description": "Unique identifier for this record",
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_active": {
            "description": "Check if subscription is active and not expired.",
            "readOnly": true,
            "type": "boolean"
          },
          "is_expired": {
            "description": "Check if subscription is expired.",
            "readOnly": true,
            "type": "boolean"
          },
          "status": {
            "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired",
            "enum": [
              "active",
              "inactive",
              "suspended",
              "cancelled",
              "expired"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "20d0bcc8b3c2bafa"
          },
          "status_display": {
            "readOnly": true,
            "type": "string"
          },
          "tariff_name": {
            "readOnly": true,
            "type": "string"
          },
          "user": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "SubscriptionOverview": {
        "description": "Current subscription overview",
        "properties": {
          "cost_display": {
            "description": "Formatted cost display",
            "type": "string"
          },
          "days_remaining": {
            "description": "Days until expiration",
            "type": "integer"
          },
          "endpoint_groups": {
            "description": "List of accessible endpoint group names",
            "items": {
              "type": "string"
            },
            "type": "array"
          },
          "endpoint_groups_count": {
            "description": "Number of accessible endpoint groups",
            "type": "integer"
          },
          "expires_at": {
            "description": "Subscription expiration date",
            "format": "date-time",
            "type": "string"
          },
          "is_active": {
            "description": "Whether subscription is active",
            "type": "boolean"
          },
          "is_expired": {
            "description": "Whether subscription is expired",
            "type": "boolean"
          },
          "last_request_at": {
            "description": "Last API request timestamp",
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "monthly_cost_usd": {
            "description": "Monthly cost in USD",
            "format": "double",
            "type": "number"
          },
          "requests_per_day": {
            "description": "Daily request limit",
            "type": "integer"
          },
          "requests_per_hour": {
            "description": "Hourly request limit",
            "type": "integer"
          },
          "starts_at": {
            "description": "Subscription start date",
            "format": "date-time",
            "type": "string"
          },
          "status": {
            "description": "Subscription status",
            "type": "string"
          },
          "status_color": {
            "description": "Color for status display",
            "type": "string"
          },
          "status_display": {
            "description": "Human-readable status",
            "type": "string"
          },
          "tier": {
            "description": "Subscription tier",
            "type": "string"
          },
          "tier_display": {
            "description": "Human-readable tier name",
            "type": "string"
          },
          "total_requests": {
            "description": "Total requests made",
            "type": "integer"
          },
          "usage_percentage": {
            "description": "Usage percentage for current period",
            "format": "double",
            "type": "number"
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
        ],
        "type": "object"
      },
      "SubscriptionRequest": {
        "description": "Complete subscription serializer with full details.\n\nUsed for subscription detail views and updates.",
        "properties": {
          "expires_at": {
            "description": "When this subscription expires",
            "format": "date-time",
            "type": "string"
          },
          "status": {
            "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired",
            "enum": [
              "active",
              "inactive",
              "suspended",
              "cancelled",
              "expired"
            ],
            "type": "string",
            "x-spec-enum-id": "20d0bcc8b3c2bafa"
          },
          "tier": {
            "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier",
            "enum": [
              "free",
              "basic",
              "pro",
              "enterprise"
            ],
            "type": "string",
            "x-spec-enum-id": "776e806f04431486"
          }
        },
        "required": [
          "expires_at"
        ],
        "type": "object"
      },
      "SuccessResponse": {
        "description": "Generic success response.",
        "properties": {
          "message": {
            "type": "string"
          },
          "success": {
            "type": "boolean"
          }
        },
        "required": [
          "message",
          "success"
        ],
        "type": "object"
      },
      "SupportedProviders": {
        "description": "Serializer for supported providers response.",
        "properties": {
          "providers": {
            "description": "List of supported providers"
          },
          "success": {
            "description": "Request success status",
            "type": "boolean"
          },
          "timestamp": {
            "description": "Response timestamp",
            "format": "date-time",
            "type": "string"
          },
          "total_count": {
            "description": "Total number of providers",
            "type": "integer"
          }
        },
        "required": [
          "providers",
          "success",
          "timestamp",
          "total_count"
        ],
        "type": "object"
      },
      "Tariff": {
        "description": "Tariff serializer for subscription pricing.\n\nUsed for tariff information and selection.",
        "properties": {
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "description": {
            "description": "Detailed description of what this tariff includes",
            "readOnly": true,
            "type": "string"
          },
          "endpoint_groups": {
            "items": {
              "$ref": "#/components/schemas/EndpointGroup"
            },
            "readOnly": true,
            "type": "array"
          },
          "endpoint_groups_count": {
            "readOnly": true,
            "type": "integer"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "is_active": {
            "description": "Whether this tariff is available for new subscriptions",
            "readOnly": true,
            "type": "boolean"
          },
          "monthly_price_usd": {
            "description": "Monthly price in USD",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "name": {
            "description": "Tariff name (e.g., \u0027Free\u0027, \u0027Basic\u0027, \u0027Pro\u0027)",
            "readOnly": true,
            "type": "string"
          },
          "requests_per_hour": {
            "description": "API requests allowed per hour",
            "readOnly": true,
            "type": "integer"
          },
          "requests_per_month": {
            "description": "API requests allowed per month",
            "readOnly": true,
            "type": "integer"
          },
          "updated_at": {
            "description": "When this record was last updated",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "TaskStatistics": {
        "description": "Serializer for task statistics data.",
        "properties": {
          "error": {
            "description": "Error message if any",
            "type": "string"
          },
          "recent_tasks": {
            "description": "List of recent tasks",
            "items": {
              "additionalProperties": {},
              "type": "object"
            },
            "type": "array"
          },
          "statistics": {
            "additionalProperties": {
              "type": "integer"
            },
            "description": "Task count statistics",
            "type": "object"
          },
          "timestamp": {
            "description": "Current timestamp",
            "type": "string"
          }
        },
        "required": [
          "recent_tasks",
          "statistics",
          "timestamp"
        ],
        "type": "object"
      },
      "TestEmailRequest": {
        "description": "Simple serializer for test email.",
        "properties": {
          "email": {
            "format": "email",
            "minLength": 1,
            "type": "string"
          },
          "message": {
            "default": "This is a test email from Django CFG Newsletter.",
            "minLength": 1,
            "type": "string"
          },
          "subject": {
            "default": "Django CFG Newsletter Test",
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "email"
        ],
        "type": "object"
      },
      "Ticket": {
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "status": {
            "description": "* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed",
            "enum": [
              "open",
              "waiting_for_user",
              "waiting_for_admin",
              "resolved",
              "closed"
            ],
            "type": "string",
            "x-spec-enum-id": "c21b48fabf2398aa"
          },
          "subject": {
            "maxLength": 255,
            "type": "string"
          },
          "unanswered_messages_count": {
            "description": "Get count of unanswered messages for this specific ticket.",
            "readOnly": true,
            "type": "integer"
          },
          "user": {
            "type": "integer"
          },
          "uuid": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "created_at",
          "subject",
          "unanswered_messages_count",
          "user",
          "uuid"
        ],
        "type": "object"
      },
      "TicketRequest": {
        "properties": {
          "status": {
            "description": "* `open` - Open\n* `waiting_for_user` - Waiting for User\n* `waiting_for_admin` - Waiting for Admin\n* `resolved` - Resolved\n* `closed` - Closed",
            "enum": [
              "open",
              "waiting_for_user",
              "waiting_for_admin",
              "resolved",
              "closed"
            ],
            "type": "string",
            "x-spec-enum-id": "c21b48fabf2398aa"
          },
          "subject": {
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          },
          "user": {
            "type": "integer"
          }
        },
        "required": [
          "subject",
          "user"
        ],
        "type": "object"
      },
      "TokenRefresh": {
        "properties": {
          "access": {
            "readOnly": true,
            "type": "string"
          },
          "refresh": {
            "type": "string"
          }
        },
        "required": [
          "access",
          "refresh"
        ],
        "type": "object"
      },
      "TokenRefreshRequest": {
        "properties": {
          "refresh": {
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "refresh"
        ],
        "type": "object"
      },
      "Transaction": {
        "description": "Transaction serializer with full details.\n\nUsed for transaction history and details.",
        "properties": {
          "amount_display": {
            "readOnly": true,
            "type": "string"
          },
          "amount_usd": {
            "description": "Transaction amount in USD (positive=credit, negative=debit)",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "description": {
            "description": "Transaction description",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "description": "Unique identifier for this record",
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_credit": {
            "readOnly": true,
            "type": "boolean"
          },
          "is_debit": {
            "readOnly": true,
            "type": "boolean"
          },
          "metadata": {
            "description": "Additional transaction metadata",
            "readOnly": true
          },
          "payment_id": {
            "description": "Related payment ID (if applicable)",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "transaction_type": {
            "description": "Type of transaction\n\n* `deposit` - Deposit\n* `withdrawal` - Withdrawal\n* `payment` - Payment\n* `refund` - Refund\n* `fee` - Fee\n* `bonus` - Bonus\n* `adjustment` - Adjustment",
            "enum": [
              "deposit",
              "withdrawal",
              "payment",
              "refund",
              "fee",
              "bonus",
              "adjustment"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "25d1662d4db37694"
          },
          "type_color": {
            "readOnly": true,
            "type": "string"
          },
          "user": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "Unsubscribe": {
        "description": "Simple serializer for unsubscribe.",
        "properties": {
          "subscription_id": {
            "type": "integer"
          }
        },
        "required": [
          "subscription_id"
        ],
        "type": "object"
      },
      "UnsubscribeRequest": {
        "description": "Simple serializer for unsubscribe.",
        "properties": {
          "subscription_id": {
            "type": "integer"
          }
        },
        "required": [
          "subscription_id"
        ],
        "type": "object"
      },
      "User": {
        "description": "Serializer for user details.",
        "properties": {
          "avatar": {
            "format": "uri",
            "nullable": true,
            "type": "string"
          },
          "company": {
            "maxLength": 100,
            "type": "string"
          },
          "date_joined": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "display_username": {
            "description": "Get formatted username for display.",
            "readOnly": true,
            "type": "string"
          },
          "email": {
            "format": "email",
            "readOnly": true,
            "type": "string"
          },
          "first_name": {
            "maxLength": 50,
            "type": "string"
          },
          "full_name": {
            "description": "Get user\u0027s full name.",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "readOnly": true,
            "type": "integer"
          },
          "initials": {
            "description": "Get user\u0027s initials for avatar fallback.",
            "readOnly": true,
            "type": "string"
          },
          "is_staff": {
            "description": "Designates whether the user can log into this admin site.",
            "readOnly": true,
            "title": "Staff status",
            "type": "boolean"
          },
          "is_superuser": {
            "description": "Designates that this user has all permissions without explicitly assigning them.",
            "readOnly": true,
            "title": "Superuser status",
            "type": "boolean"
          },
          "last_login": {
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "last_name": {
            "maxLength": 50,
            "type": "string"
          },
          "phone": {
            "maxLength": 20,
            "type": "string"
          },
          "position": {
            "maxLength": 100,
            "type": "string"
          },
          "unanswered_messages_count": {
            "description": "Get count of unanswered messages for the user.",
            "readOnly": true,
            "type": "integer"
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
        ],
        "type": "object"
      },
      "UserBalance": {
        "description": "User balance serializer with computed fields.\n\nProvides balance information with display helpers.",
        "properties": {
          "balance_display": {
            "description": "Formatted balance display.",
            "readOnly": true,
            "type": "string"
          },
          "balance_usd": {
            "description": "Current balance in USD (float for performance)",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "has_transactions": {
            "description": "Check if user has any transactions.",
            "readOnly": true,
            "type": "boolean"
          },
          "is_empty": {
            "description": "Check if balance is zero.",
            "readOnly": true,
            "type": "boolean"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "user": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "UserProfileUpdateRequest": {
        "description": "Serializer for updating user profile.",
        "properties": {
          "company": {
            "maxLength": 100,
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
          "phone": {
            "maxLength": 20,
            "type": "string"
          },
          "position": {
            "maxLength": 100,
            "type": "string"
          }
        },
        "type": "object"
      },
      "WebhookHealth": {
        "description": "Serializer for webhook health check response.",
        "properties": {
          "providers": {
            "description": "Provider health status"
          },
          "status": {
            "description": "Health status",
            "maxLength": 20,
            "type": "string"
          },
          "timestamp": {
            "description": "Check timestamp",
            "format": "date-time",
            "type": "string"
          }
        },
        "required": [
          "providers",
          "status",
          "timestamp"
        ],
        "type": "object"
      },
      "WebhookResponse": {
        "description": "Serializer for webhook processing response.\n\nStandard response format for all webhook endpoints.",
        "properties": {
          "message": {
            "description": "Processing result message",
            "maxLength": 500,
            "type": "string"
          },
          "payment_id": {
            "description": "Internal payment ID",
            "maxLength": 256,
            "type": "string"
          },
          "processed_at": {
            "description": "Processing timestamp",
            "format": "date-time",
            "type": "string"
          },
          "provider_payment_id": {
            "description": "Provider payment ID",
            "maxLength": 256,
            "type": "string"
          },
          "success": {
            "description": "Whether webhook was processed successfully",
            "type": "boolean"
          }
        },
        "required": [
          "message",
          "success"
        ],
        "type": "object"
      },
      "WebhookResponseRequest": {
        "description": "Serializer for webhook processing response.\n\nStandard response format for all webhook endpoints.",
        "properties": {
          "message": {
            "description": "Processing result message",
            "maxLength": 500,
            "minLength": 1,
            "type": "string"
          },
          "payment_id": {
            "description": "Internal payment ID",
            "maxLength": 256,
            "minLength": 1,
            "type": "string"
          },
          "processed_at": {
            "description": "Processing timestamp",
            "format": "date-time",
            "type": "string"
          },
          "provider_payment_id": {
            "description": "Provider payment ID",
            "maxLength": 256,
            "minLength": 1,
            "type": "string"
          },
          "success": {
            "description": "Whether webhook was processed successfully",
            "type": "boolean"
          }
        },
        "required": [
          "message",
          "success"
        ],
        "type": "object"
      },
      "WebhookStats": {
        "description": "Serializer for webhook statistics response.",
        "properties": {
          "failed_webhooks": {
            "description": "Failed webhook processing attempts",
            "type": "integer"
          },
          "providers": {
            "description": "Per-provider statistics"
          },
          "success_rate": {
            "description": "Success rate percentage",
            "format": "double",
            "type": "number"
          },
          "successful_webhooks": {
            "description": "Successfully processed webhooks",
            "type": "integer"
          },
          "total_webhooks": {
            "description": "Total webhooks processed",
            "type": "integer"
          }
        },
        "required": [
          "failed_webhooks",
          "providers",
          "success_rate",
          "successful_webhooks",
          "total_webhooks"
        ],
        "type": "object"
      },
      "WorkerAction": {
        "description": "Serializer for worker management actions.",
        "properties": {
          "action": {
            "description": "Action to perform on workers\n\n* `start` - start\n* `stop` - stop\n* `restart` - restart",
            "enum": [
              "start",
              "stop",
              "restart"
            ],
            "type": "string",
            "x-spec-enum-id": "5d2b5c38703636f1"
          },
          "processes": {
            "default": 1,
            "description": "Number of worker processes",
            "maximum": 10,
            "minimum": 1,
            "type": "integer"
          },
          "threads": {
            "default": 2,
            "description": "Number of threads per process",
            "maximum": 20,
            "minimum": 1,
            "type": "integer"
          }
        },
        "required": [
          "action"
        ],
        "type": "object"
      },
      "WorkerActionRequest": {
        "description": "Serializer for worker management actions.",
        "properties": {
          "action": {
            "description": "Action to perform on workers\n\n* `start` - start\n* `stop` - stop\n* `restart` - restart",
            "enum": [
              "start",
              "stop",
              "restart"
            ],
            "type": "string",
            "x-spec-enum-id": "5d2b5c38703636f1"
          },
          "processes": {
            "default": 1,
            "description": "Number of worker processes",
            "maximum": 10,
            "minimum": 1,
            "type": "integer"
          },
          "threads": {
            "default": 2,
            "description": "Number of threads per process",
            "maximum": 20,
            "minimum": 1,
            "type": "integer"
          }
        },
        "required": [
          "action"
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
        "django_cfg_support",
        "django_cfg_accounts",
        "django_cfg_newsletter",
        "django_cfg_leads",
        "django_cfg_agents",
        "tasks",
        "payments"
      ],
      "generator": "django-client",
      "generator_version": "1.0.0",
      "group": "cfg"
    }
  },
  "openapi": "3.0.3",
  "paths": {
    "/django_cfg_accounts/otp/request/": {
      "post": {
        "description": "Request OTP code to email or phone.",
        "operationId": "django_cfg_accounts_otp_request_create",
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
          "required": true
        },
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
          "django_cfg_accounts"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_accounts/otp/verify/": {
      "post": {
        "description": "Verify OTP code and return JWT tokens.",
        "operationId": "django_cfg_accounts_otp_verify_create",
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
          "required": true
        },
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
          "django_cfg_accounts"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_accounts/profile/": {
      "get": {
        "description": "Retrieve the current authenticated user\u0027s profile information.",
        "operationId": "django_cfg_accounts_profile_retrieve",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Get current user profile",
        "tags": [
          "User Profile"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_accounts/profile/avatar/": {
      "post": {
        "description": "Upload avatar image for the current authenticated user. Accepts multipart/form-data with \u0027avatar\u0027 field.",
        "operationId": "django_cfg_accounts_profile_avatar_create",
        "requestBody": {
          "content": {
            "multipart/form-data": {
              "schema": {
                "properties": {
                  "avatar": {
                    "description": "Avatar image file (JPEG, PNG, GIF, WebP, max 5MB)",
                    "format": "binary",
                    "type": "string"
                  }
                },
                "required": [
                  "avatar"
                ],
                "type": "object"
              }
            }
          }
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Upload user avatar",
        "tags": [
          "User Profile"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_accounts/profile/partial/": {
      "patch": {
        "description": "Partially update the current authenticated user\u0027s profile information. Supports avatar upload.",
        "operationId": "django_cfg_accounts_profile_partial_partial_update",
        "requestBody": {
          "content": {
            "application/json": {
              "examples": {
                "ProfileUpdateWithAvatar": {
                  "summary": "Profile Update with Avatar",
                  "value": {
                    "company": "Tech Corp",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1 (555) 123-4567",
                    "position": "Software Engineer"
                  }
                }
              },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Partial update user profile",
        "tags": [
          "User Profile"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Partially update the current authenticated user\u0027s profile information. Supports avatar upload.",
        "operationId": "django_cfg_accounts_profile_partial_update",
        "requestBody": {
          "content": {
            "application/json": {
              "examples": {
                "ProfileUpdateWithAvatar": {
                  "summary": "Profile Update with Avatar",
                  "value": {
                    "company": "Tech Corp",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1 (555) 123-4567",
                    "position": "Software Engineer"
                  }
                }
              },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Partial update user profile",
        "tags": [
          "User Profile"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_accounts/profile/update/": {
      "patch": {
        "description": "Update the current authenticated user\u0027s profile information.",
        "operationId": "django_cfg_accounts_profile_update_partial_update",
        "requestBody": {
          "content": {
            "application/json": {
              "examples": {
                "ValidProfileUpdate": {
                  "summary": "Valid Profile Update",
                  "value": {
                    "company": "Tech Corp",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1 (555) 123-4567",
                    "position": "Software Engineer"
                  }
                }
              },
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
          "User Profile"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Update the current authenticated user\u0027s profile information.",
        "operationId": "django_cfg_accounts_profile_update_update",
        "requestBody": {
          "content": {
            "application/json": {
              "examples": {
                "ValidProfileUpdate": {
                  "summary": "Valid Profile Update",
                  "value": {
                    "company": "Tech Corp",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone": "+1 (555) 123-4567",
                    "position": "Software Engineer"
                  }
                }
              },
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
          "User Profile"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_accounts/token/refresh/": {
      "post": {
        "description": "Refresh JWT token.",
        "operationId": "django_cfg_accounts_token_refresh_create",
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
          "required": true
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
        "tags": [
          "Auth"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_leads/leads/": {
      "get": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "django_cfg_leads_leads_list",
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
                  "$ref": "#/components/schemas/PaginatedLeadSubmissionList"
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
          "django_cfg_leads"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "django_cfg_leads_leads_create",
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
          "required": true
        },
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
          "django_cfg_leads"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_leads/leads/submit/": {
      "post": {
        "description": "Submit a new lead from frontend contact form with automatic Telegram notifications.",
        "operationId": "django_cfg_leads_leads_submit_create",
        "requestBody": {
          "content": {
            "application/json": {
              "examples": {
                "ContactFormSubmission": {
                  "summary": "Contact Form Submission",
                  "value": {
                    "company": "Tech Corp",
                    "company_site": "https://techcorp.com",
                    "contact_type": "email",
                    "contact_value": "john@example.com",
                    "email": "john@example.com",
                    "message": "I\u0027m interested in discussing a potential partnership.",
                    "name": "John Doe",
                    "site_url": "https://mysite.com/contact",
                    "subject": "Partnership Inquiry"
                  }
                }
              },
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Submit Lead Form",
        "tags": [
          "Lead Submission"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_leads/leads/{id}/": {
      "delete": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "django_cfg_leads_leads_destroy",
        "parameters": [
          {
            "description": "A unique integer value identifying this Lead.",
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
          },
          {}
        ],
        "tags": [
          "django_cfg_leads"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "django_cfg_leads_leads_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Lead.",
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
                  "$ref": "#/components/schemas/LeadSubmission"
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
          "django_cfg_leads"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "django_cfg_leads_leads_partial_update",
        "parameters": [
          {
            "description": "A unique integer value identifying this Lead.",
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
          "django_cfg_leads"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "django_cfg_leads_leads_update",
        "parameters": [
          {
            "description": "A unique integer value identifying this Lead.",
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
          "required": true
        },
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
          "django_cfg_leads"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/bulk/": {
      "post": {
        "description": "Send bulk emails to multiple recipients using base email template.",
        "operationId": "django_cfg_newsletter_bulk_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Send Bulk Email",
        "tags": [
          "Bulk Email"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/campaigns/": {
      "get": {
        "description": "Get a list of all newsletter campaigns.",
        "operationId": "django_cfg_newsletter_campaigns_list",
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
                  "$ref": "#/components/schemas/PaginatedNewsletterCampaignList"
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
        "summary": "List Newsletter Campaigns",
        "tags": [
          "Campaigns"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Create a new newsletter campaign.",
        "operationId": "django_cfg_newsletter_campaigns_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Create Newsletter Campaign",
        "tags": [
          "Campaigns"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/campaigns/send/": {
      "post": {
        "description": "Send a newsletter campaign to all subscribers.",
        "operationId": "django_cfg_newsletter_campaigns_send_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Send Newsletter Campaign",
        "tags": [
          "Campaigns"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/campaigns/{id}/": {
      "delete": {
        "description": "Delete a newsletter campaign.",
        "operationId": "django_cfg_newsletter_campaigns_destroy",
        "parameters": [
          {
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
        "summary": "Delete Campaign",
        "tags": [
          "Campaigns"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Retrieve details of a specific newsletter campaign.",
        "operationId": "django_cfg_newsletter_campaigns_retrieve",
        "parameters": [
          {
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
                  "$ref": "#/components/schemas/NewsletterCampaign"
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
        "summary": "Get Campaign Details",
        "tags": [
          "Campaigns"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Retrieve, update, or delete a newsletter campaign.",
        "operationId": "django_cfg_newsletter_campaigns_partial_update",
        "parameters": [
          {
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "django_cfg_newsletter"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Update a newsletter campaign.",
        "operationId": "django_cfg_newsletter_campaigns_update",
        "parameters": [
          {
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Update Campaign",
        "tags": [
          "Campaigns"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/logs/": {
      "get": {
        "description": "Get a list of email sending logs.",
        "operationId": "django_cfg_newsletter_logs_list",
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
                  "$ref": "#/components/schemas/PaginatedEmailLogList"
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
        "summary": "List Email Logs",
        "tags": [
          "Logs"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/newsletters/": {
      "get": {
        "description": "Get a list of all active newsletters available for subscription.",
        "operationId": "django_cfg_newsletter_newsletters_list",
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
                  "$ref": "#/components/schemas/PaginatedNewsletterList"
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
        "summary": "List Active Newsletters",
        "tags": [
          "Newsletters"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/newsletters/{id}/": {
      "get": {
        "description": "Retrieve details of a specific newsletter.",
        "operationId": "django_cfg_newsletter_newsletters_retrieve",
        "parameters": [
          {
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
                  "$ref": "#/components/schemas/Newsletter"
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
        "summary": "Get Newsletter Details",
        "tags": [
          "Newsletters"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/subscribe/": {
      "post": {
        "description": "Subscribe an email address to a newsletter.",
        "operationId": "django_cfg_newsletter_subscribe_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Subscribe to Newsletter",
        "tags": [
          "Subscriptions"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/subscriptions/": {
      "get": {
        "description": "Get a list of current user\u0027s active newsletter subscriptions.",
        "operationId": "django_cfg_newsletter_subscriptions_list",
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
                  "$ref": "#/components/schemas/PaginatedNewsletterSubscriptionList"
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
        "summary": "List User Subscriptions",
        "tags": [
          "Subscriptions"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/test/": {
      "post": {
        "description": "Send a test email to verify mailer configuration.",
        "operationId": "django_cfg_newsletter_test_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Test Email Sending",
        "tags": [
          "Testing"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_newsletter/unsubscribe/": {
      "patch": {
        "description": "Handle newsletter unsubscriptions.",
        "operationId": "django_cfg_newsletter_unsubscribe_partial_update",
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
          "django_cfg_newsletter"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Unsubscribe from a newsletter using subscription ID.",
        "operationId": "django_cfg_newsletter_unsubscribe_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          },
          {}
        ],
        "summary": "Unsubscribe from Newsletter",
        "tags": [
          "Subscriptions"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Handle newsletter unsubscriptions.",
        "operationId": "django_cfg_newsletter_unsubscribe_update",
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
          "required": true
        },
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
          "django_cfg_newsletter"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_support/tickets/": {
      "get": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "django_cfg_support_tickets_list",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/Ticket"
                  },
                  "type": "array"
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
          "django_cfg_support"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "django_cfg_support_tickets_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "django_cfg_support"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_support/tickets/{ticket_uuid}/messages/": {
      "get": {
        "description": "ViewSet for managing support messages.",
        "operationId": "django_cfg_support_tickets_messages_list",
        "parameters": [
          {
            "description": "UUID of the ticket",
            "in": "path",
            "name": "ticket_uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/Message"
                  },
                  "type": "array"
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
          "django_cfg_support"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "ViewSet for managing support messages.",
        "operationId": "django_cfg_support_tickets_messages_create",
        "parameters": [
          {
            "description": "UUID of the ticket",
            "in": "path",
            "name": "ticket_uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "django_cfg_support"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/": {
      "delete": {
        "description": "ViewSet for managing support messages.",
        "operationId": "django_cfg_support_tickets_messages_destroy",
        "parameters": [
          {
            "description": "UUID of the ticket",
            "in": "path",
            "name": "ticket_uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "description": "UUID of the message",
            "in": "path",
            "name": "uuid",
            "required": true,
            "schema": {
              "format": "uuid",
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
          "django_cfg_support"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "ViewSet for managing support messages.",
        "operationId": "django_cfg_support_tickets_messages_retrieve",
        "parameters": [
          {
            "description": "UUID of the ticket",
            "in": "path",
            "name": "ticket_uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "description": "UUID of the message",
            "in": "path",
            "name": "uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "django_cfg_support"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "ViewSet for managing support messages.",
        "operationId": "django_cfg_support_tickets_messages_partial_update",
        "parameters": [
          {
            "description": "UUID of the ticket",
            "in": "path",
            "name": "ticket_uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "description": "UUID of the message",
            "in": "path",
            "name": "uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          }
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "django_cfg_support"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "ViewSet for managing support messages.",
        "operationId": "django_cfg_support_tickets_messages_update",
        "parameters": [
          {
            "description": "UUID of the ticket",
            "in": "path",
            "name": "ticket_uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "description": "UUID of the message",
            "in": "path",
            "name": "uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "django_cfg_support"
        ],
        "x-async-capable": false
      }
    },
    "/django_cfg_support/tickets/{uuid}/": {
      "delete": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "django_cfg_support_tickets_destroy",
        "parameters": [
          {
            "description": "A UUID string identifying this ticket.",
            "in": "path",
            "name": "uuid",
            "required": true,
            "schema": {
              "format": "uuid",
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
          "django_cfg_support"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "django_cfg_support_tickets_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this ticket.",
            "in": "path",
            "name": "uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "django_cfg_support"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "django_cfg_support_tickets_partial_update",
        "parameters": [
          {
            "description": "A UUID string identifying this ticket.",
            "in": "path",
            "name": "uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          }
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "django_cfg_support"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "django_cfg_support_tickets_update",
        "parameters": [
          {
            "description": "A UUID string identifying this ticket.",
            "in": "path",
            "name": "uuid",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "django_cfg_support"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/": {
      "get": {
        "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
        "operationId": "payments_api_keys_list",
        "parameters": [
          {
            "in": "query",
            "name": "is_active",
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
            "in": "query",
            "name": "user",
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
                  "$ref": "#/components/schemas/PaginatedAPIKeyListList"
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
          "payments"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
        "operationId": "payments_api_keys_create",
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/analytics/": {
      "get": {
        "description": "Get API key analytics.\n\nGET /api/api-keys/analytics/?days=30",
        "operationId": "payments_api_keys_analytics_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/by_user/": {
      "get": {
        "description": "Get API keys grouped by user.\n\nGET /api/api-keys/by_user/",
        "operationId": "payments_api_keys_by_user_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/create/": {
      "post": {
        "description": "Standalone API key creation endpoint: /api/api-keys/create/\n\nSimplified endpoint for API key creation.",
        "operationId": "payments_api_keys_create_create",
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/expiring_soon/": {
      "get": {
        "description": "Get API keys expiring soon.\n\nGET /api/api-keys/expiring_soon/?days=7",
        "operationId": "payments_api_keys_expiring_soon_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_api_keys_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_api_keys_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/validate/": {
      "post": {
        "description": "Standalone endpoint to validate an API key and return key information",
        "operationId": "payments_api_keys_validate_create",
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
          "required": true
        },
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Validate API Key (Standalone)",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/validate_key/": {
      "post": {
        "description": "Validate an API key and return key information",
        "operationId": "payments_api_keys_validate_key_create",
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
          "required": true
        },
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Validate API Key",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/{id}/": {
      "delete": {
        "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
        "operationId": "payments_api_keys_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
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
          "payments"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
        "operationId": "payments_api_keys_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
        "operationId": "payments_api_keys_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Global API Key ViewSet: /api/api-keys/\n\nProvides admin-level access to all API keys with filtering and stats.",
        "operationId": "payments_api_keys_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/api-keys/{id}/perform_action/": {
      "post": {
        "description": "Perform action on API key.\n\nPOST /api/api-keys/{id}/perform_action/",
        "operationId": "payments_api_keys_perform_action_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/balances/": {
      "get": {
        "description": "User balance ViewSet: /api/balances/\n\nRead-only access to user balances with statistics.",
        "operationId": "payments_balances_list",
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
          },
          {
            "in": "query",
            "name": "user",
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
                  "$ref": "#/components/schemas/PaginatedUserBalanceList"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/balances/analytics/": {
      "get": {
        "description": "Get balance analytics.\n\nGET /api/balances/analytics/?days=30",
        "operationId": "payments_balances_analytics_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/balances/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_balances_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/balances/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_balances_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/balances/summary/": {
      "get": {
        "description": "Get balance summary for all users.\n\nGET /api/balances/summary/",
        "operationId": "payments_balances_summary_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/balances/{id}/": {
      "get": {
        "description": "User balance ViewSet: /api/balances/\n\nRead-only access to user balances with statistics.",
        "operationId": "payments_balances_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this User Balance.",
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
                  "$ref": "#/components/schemas/UserBalance"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/": {
      "get": {
        "description": "Currency ViewSet: /api/currencies/\n\nRead-only access to currency information with conversion capabilities.",
        "operationId": "payments_currencies_list",
        "parameters": [
          {
            "description": "Type of currency\n\n* `fiat` - Fiat Currency\n* `crypto` - Cryptocurrency",
            "in": "query",
            "name": "currency_type",
            "schema": {
              "enum": [
                "crypto",
                "fiat"
              ],
              "type": "string",
              "x-spec-enum-id": "1fd14ececc7d641f"
            }
          },
          {
            "in": "query",
            "name": "is_active",
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
          "payments"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Disable create action.",
        "operationId": "payments_currencies_create",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/convert/": {
      "post": {
        "description": "Convert between currencies.\n\nPOST /api/currencies/convert/",
        "operationId": "payments_currencies_convert_create",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/crypto/": {
      "get": {
        "description": "Get only cryptocurrencies.\n\nGET /api/currencies/crypto/",
        "operationId": "payments_currencies_crypto_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/fiat/": {
      "get": {
        "description": "Get only fiat currencies.\n\nGET /api/currencies/fiat/",
        "operationId": "payments_currencies_fiat_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_currencies_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/rates/": {
      "get": {
        "description": "Get current exchange rates for specified currencies",
        "operationId": "payments_currencies_rates_retrieve",
        "parameters": [
          {
            "description": "Base currency code (e.g., USD)",
            "in": "query",
            "name": "base_currency",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "Comma-separated list of target currency codes (e.g., BTC,ETH,USDT)",
            "in": "query",
            "name": "currencies",
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
                  "$ref": "#/components/schemas/Currency"
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
        "summary": "Get exchange rates",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/stable/": {
      "get": {
        "description": "Get only stablecoins.\n\nGET /api/currencies/stable/",
        "operationId": "payments_currencies_stable_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_currencies_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/supported/": {
      "get": {
        "description": "Get list of supported currencies from payment providers",
        "operationId": "payments_currencies_supported_retrieve",
        "parameters": [
          {
            "description": "Currency type filter: crypto, fiat, or stablecoin",
            "in": "query",
            "name": "currency_type",
            "schema": {
              "enum": [
                "crypto",
                "fiat",
                "stablecoin"
              ],
              "type": "string"
            }
          },
          {
            "description": "Payment provider name (e.g., nowpayments)",
            "in": "query",
            "name": "provider",
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
                  "$ref": "#/components/schemas/Currency"
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
        "summary": "Get supported currencies",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/{id}/": {
      "get": {
        "description": "Currency ViewSet: /api/currencies/\n\nRead-only access to currency information with conversion capabilities.",
        "operationId": "payments_currencies_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Currency.",
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
                  "$ref": "#/components/schemas/Currency"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/{id}/networks/": {
      "get": {
        "description": "Get networks for specific currency.\n\nGET /api/currencies/{id}/networks/",
        "operationId": "payments_currencies_networks_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Currency.",
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
                  "$ref": "#/components/schemas/Currency"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/currencies/{id}/providers/": {
      "get": {
        "description": "Get providers supporting specific currency.\n\nGET /api/currencies/{id}/providers/",
        "operationId": "payments_currencies_providers_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Currency.",
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
                  "$ref": "#/components/schemas/Currency"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/endpoint-groups/": {
      "get": {
        "description": "Endpoint Group ViewSet: /api/endpoint-groups/\n\nRead-only access to endpoint group information.",
        "operationId": "payments_endpoint_groups_list",
        "parameters": [
          {
            "in": "query",
            "name": "is_enabled",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/endpoint-groups/available/": {
      "get": {
        "description": "Get available endpoint groups for subscription.\n\nGET /api/endpoint-groups/available/",
        "operationId": "payments_endpoint_groups_available_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/endpoint-groups/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_endpoint_groups_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/endpoint-groups/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_endpoint_groups_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/endpoint-groups/{id}/": {
      "get": {
        "description": "Endpoint Group ViewSet: /api/endpoint-groups/\n\nRead-only access to endpoint group information.",
        "operationId": "payments_endpoint_groups_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Endpoint Group.",
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
                  "$ref": "#/components/schemas/EndpointGroup"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/networks/": {
      "get": {
        "description": "Network ViewSet: /api/networks/\n\nRead-only access to blockchain network information.",
        "operationId": "payments_networks_list",
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
                  "$ref": "#/components/schemas/PaginatedNetworkList"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/networks/by_currency/": {
      "get": {
        "description": "Get networks grouped by currency.\n\nGET /api/networks/by_currency/",
        "operationId": "payments_networks_by_currency_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/networks/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_networks_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/networks/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_networks_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/networks/{id}/": {
      "get": {
        "description": "Network ViewSet: /api/networks/\n\nRead-only access to blockchain network information.",
        "operationId": "payments_networks_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Network.",
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
                  "$ref": "#/components/schemas/Network"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/overview/dashboard/api_keys_overview/": {
      "get": {
        "description": "Get API keys overview",
        "operationId": "payments_overview_dashboard_api_keys_overview_retrieve",
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "API Keys Overview",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/overview/dashboard/balance_overview/": {
      "get": {
        "description": "Get user balance overview",
        "operationId": "payments_overview_dashboard_balance_overview_retrieve",
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Balance Overview",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/overview/dashboard/chart_data/": {
      "get": {
        "description": "Get chart data for payments visualization",
        "operationId": "payments_overview_dashboard_chart_data_retrieve",
        "parameters": [
          {
            "description": "Time period for chart data",
            "in": "query",
            "name": "period",
            "schema": {
              "default": "30d",
              "enum": [
                "1y",
                "30d",
                "7d",
                "90d"
              ],
              "type": "string"
            }
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Payments Chart Data",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/overview/dashboard/metrics/": {
      "get": {
        "description": "Get payments dashboard metrics including balance, subscriptions, API keys, and payments",
        "operationId": "payments_overview_dashboard_metrics_retrieve",
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Payments Dashboard Metrics",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/overview/dashboard/overview/": {
      "get": {
        "description": "Get complete payments dashboard overview with metrics, recent payments, and analytics",
        "operationId": "payments_overview_dashboard_overview_retrieve",
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Payments Dashboard Overview",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/overview/dashboard/payment_analytics/": {
      "get": {
        "description": "Get analytics for payments by currency and provider",
        "operationId": "payments_overview_dashboard_payment_analytics_retrieve",
        "parameters": [
          {
            "description": "Number of analytics items to return",
            "in": "query",
            "name": "limit",
            "schema": {
              "default": 10,
              "type": "integer"
            }
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Payment Analytics",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/overview/dashboard/recent_payments/": {
      "get": {
        "description": "Get recent payments for the user",
        "operationId": "payments_overview_dashboard_recent_payments_list",
        "parameters": [
          {
            "description": "Number of payments to return",
            "in": "query",
            "name": "limit",
            "schema": {
              "default": 10,
              "type": "integer"
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Recent Payments",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/overview/dashboard/recent_transactions/": {
      "get": {
        "description": "Get recent balance transactions for the user",
        "operationId": "payments_overview_dashboard_recent_transactions_list",
        "parameters": [
          {
            "description": "Number of transactions to return",
            "in": "query",
            "name": "limit",
            "schema": {
              "default": 10,
              "type": "integer"
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Recent Transactions",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/overview/dashboard/subscription_overview/": {
      "get": {
        "description": "Get current subscription overview",
        "operationId": "payments_overview_dashboard_subscription_overview_retrieve",
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
        },
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "summary": "Subscription Overview",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/": {
      "get": {
        "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
        "operationId": "payments_payments_list",
        "parameters": [
          {
            "in": "query",
            "name": "currency__code",
            "schema": {
              "type": "string"
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
            "description": "Payment provider\n\n* `nowpayments` - NowPayments",
            "in": "query",
            "name": "provider",
            "schema": {
              "enum": [
                "nowpayments"
              ],
              "type": "string",
              "x-spec-enum-id": "47694db6bd068cb3"
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
            "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
            "in": "query",
            "name": "status",
            "schema": {
              "enum": [
                "cancelled",
                "completed",
                "confirmed",
                "confirming",
                "expired",
                "failed",
                "pending",
                "refunded"
              ],
              "type": "string",
              "x-spec-enum-id": "59d07a8608d1bdb9"
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
        "operationId": "payments_payments_create",
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/analytics/": {
      "get": {
        "description": "Get payment analytics.\n\nGET /api/v1/payments/analytics/?days=30",
        "operationId": "payments_payments_analytics_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/by_provider/": {
      "get": {
        "description": "Get payments grouped by provider.\n\nGET /api/v1/payments/by_provider/",
        "operationId": "payments_payments_by_provider_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/create/": {
      "post": {
        "description": "Standalone payment creation endpoint: /api/v1/payments/create/\n\nSimplified endpoint for payment creation without full ViewSet overhead.",
        "operationId": "payments_payments_create_create",
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_payments_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_payments_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/status/{id}/": {
      "get": {
        "description": "Standalone payment status endpoint: /api/v1/payments/{id}/status/\n\nQuick status check without full ViewSet overhead.",
        "operationId": "payments_payments_status_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "format": "uuid",
              "type": "string"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/{id}/": {
      "delete": {
        "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
        "operationId": "payments_payments_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
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
          "payments"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
        "operationId": "payments_payments_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
        "operationId": "payments_payments_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Global payment ViewSet: /api/v1/payments/\n\nProvides admin-level access to all payments with filtering and stats.",
        "operationId": "payments_payments_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/{id}/cancel/": {
      "post": {
        "description": "Cancel payment.\n\nPOST /api/v1/payments/{id}/cancel/",
        "operationId": "payments_payments_cancel_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/payments/{id}/check_status/": {
      "post": {
        "description": "Check payment status with provider.\n\nPOST /api/v1/payments/{id}/check_status/",
        "operationId": "payments_payments_check_status_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/provider-currencies/": {
      "get": {
        "description": "Provider Currency ViewSet: /api/provider-currencies/\n\nRead-only access to provider-specific currency information.",
        "operationId": "payments_provider_currencies_list",
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
            "name": "provider",
            "schema": {
              "type": "string"
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
                  "$ref": "#/components/schemas/PaginatedProviderCurrencyList"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/provider-currencies/by_provider/": {
      "get": {
        "description": "Get provider currencies grouped by provider.\n\nGET /api/provider-currencies/by_provider/",
        "operationId": "payments_provider_currencies_by_provider_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/provider-currencies/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_provider_currencies_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/provider-currencies/limits/": {
      "get": {
        "description": "Get currency limits by provider.\n\nGET /api/provider-currencies/limits/?provider=nowpayments",
        "operationId": "payments_provider_currencies_limits_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/provider-currencies/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_provider_currencies_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/provider-currencies/{id}/": {
      "get": {
        "description": "Provider Currency ViewSet: /api/provider-currencies/\n\nRead-only access to provider-specific currency information.",
        "operationId": "payments_provider_currencies_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Provider Currency.",
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
                  "$ref": "#/components/schemas/ProviderCurrency"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/subscriptions/": {
      "get": {
        "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
        "operationId": "payments_subscriptions_list",
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
          },
          {
            "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired",
            "in": "query",
            "name": "status",
            "schema": {
              "enum": [
                "active",
                "cancelled",
                "expired",
                "inactive",
                "suspended"
              ],
              "type": "string",
              "x-spec-enum-id": "20d0bcc8b3c2bafa"
            }
          },
          {
            "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier",
            "in": "query",
            "name": "tier",
            "schema": {
              "enum": [
                "basic",
                "enterprise",
                "free",
                "pro"
              ],
              "type": "string",
              "x-spec-enum-id": "776e806f04431486"
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
          "payments"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
        "operationId": "payments_subscriptions_create",
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/subscriptions/analytics/": {
      "get": {
        "description": "Get subscription analytics.\n\nGET /api/subscriptions/analytics/?days=30",
        "operationId": "payments_subscriptions_analytics_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/subscriptions/by_status/": {
      "get": {
        "description": "Get subscriptions grouped by status.\n\nGET /api/subscriptions/by_status/",
        "operationId": "payments_subscriptions_by_status_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/subscriptions/by_tier/": {
      "get": {
        "description": "Get subscriptions grouped by tier.\n\nGET /api/subscriptions/by_tier/",
        "operationId": "payments_subscriptions_by_tier_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/subscriptions/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_subscriptions_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/subscriptions/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_subscriptions_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/subscriptions/{id}/": {
      "delete": {
        "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
        "operationId": "payments_subscriptions_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
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
          "payments"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
        "operationId": "payments_subscriptions_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
        "operationId": "payments_subscriptions_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Global subscription ViewSet: /api/subscriptions/\n\nProvides admin-level access to all subscriptions with filtering and stats.",
        "operationId": "payments_subscriptions_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/subscriptions/{id}/increment_usage/": {
      "post": {
        "description": "Increment subscription usage.\n\nPOST /api/subscriptions/{id}/increment_usage/",
        "operationId": "payments_subscriptions_increment_usage_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/subscriptions/{id}/update_status/": {
      "post": {
        "description": "Update subscription status.\n\nPOST /api/subscriptions/{id}/update_status/",
        "operationId": "payments_subscriptions_update_status_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/tariffs/": {
      "get": {
        "description": "Tariff ViewSet: /api/tariffs/\n\nRead-only access to tariff information for subscription selection.",
        "operationId": "payments_tariffs_list",
        "parameters": [
          {
            "in": "query",
            "name": "is_active",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/tariffs/free/": {
      "get": {
        "description": "Get free tariffs.\n\nGET /api/tariffs/free/",
        "operationId": "payments_tariffs_free_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/tariffs/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_tariffs_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/tariffs/paid/": {
      "get": {
        "description": "Get paid tariffs.\n\nGET /api/tariffs/paid/",
        "operationId": "payments_tariffs_paid_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/tariffs/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_tariffs_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/tariffs/{id}/": {
      "get": {
        "description": "Tariff ViewSet: /api/tariffs/\n\nRead-only access to tariff information for subscription selection.",
        "operationId": "payments_tariffs_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Tariff.",
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
                  "$ref": "#/components/schemas/Tariff"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/tariffs/{id}/endpoint_groups/": {
      "get": {
        "description": "Get endpoint groups for specific tariff.\n\nGET /api/tariffs/{id}/endpoint_groups/",
        "operationId": "payments_tariffs_endpoint_groups_retrieve",
        "parameters": [
          {
            "description": "A unique integer value identifying this Tariff.",
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
                  "$ref": "#/components/schemas/Tariff"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/transactions/": {
      "get": {
        "description": "Transaction ViewSet: /api/transactions/\n\nRead-only access to transaction history with filtering.",
        "operationId": "payments_transactions_list",
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
            "in": "query",
            "name": "payment_id",
            "schema": {
              "type": "string"
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
            "description": "Type of transaction\n\n* `deposit` - Deposit\n* `withdrawal` - Withdrawal\n* `payment` - Payment\n* `refund` - Refund\n* `fee` - Fee\n* `bonus` - Bonus\n* `adjustment` - Adjustment",
            "in": "query",
            "name": "transaction_type",
            "schema": {
              "enum": [
                "adjustment",
                "bonus",
                "deposit",
                "fee",
                "payment",
                "refund",
                "withdrawal"
              ],
              "type": "string",
              "x-spec-enum-id": "25d1662d4db37694"
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/transactions/by_type/": {
      "get": {
        "description": "Get transactions grouped by type.\n\nGET /api/transactions/by_type/",
        "operationId": "payments_transactions_by_type_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/transactions/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_transactions_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/transactions/recent/": {
      "get": {
        "description": "Get recent transactions.\n\nGET /api/transactions/recent/?limit=10",
        "operationId": "payments_transactions_recent_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/transactions/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_transactions_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/transactions/{id}/": {
      "get": {
        "description": "Transaction ViewSet: /api/transactions/\n\nRead-only access to transaction history with filtering.",
        "operationId": "payments_transactions_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/": {
      "get": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_list",
        "parameters": [
          {
            "in": "query",
            "name": "currency__code",
            "schema": {
              "type": "string"
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
            "description": "Payment provider\n\n* `nowpayments` - NowPayments",
            "in": "query",
            "name": "provider",
            "schema": {
              "enum": [
                "nowpayments"
              ],
              "type": "string",
              "x-spec-enum-id": "47694db6bd068cb3"
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
            "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
            "in": "query",
            "name": "status",
            "schema": {
              "enum": [
                "cancelled",
                "completed",
                "confirmed",
                "confirming",
                "expired",
                "failed",
                "pending",
                "refunded"
              ],
              "type": "string",
              "x-spec-enum-id": "59d07a8608d1bdb9"
            }
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_create",
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_users_health_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_users_stats_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/summary/": {
      "get": {
        "description": "Get user payment summary.\n\nGET /api/v1/users/{user_id}/payments/summary/",
        "operationId": "payments_users_summary_retrieve",
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{id}/": {
      "delete": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
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
          "payments"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{id}/cancel/": {
      "post": {
        "description": "Cancel payment.\n\nPOST /api/v1/users/{user_id}/payments/{id}/cancel/",
        "operationId": "payments_users_cancel_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{id}/check_status/": {
      "post": {
        "description": "Check payment status with provider.\n\nPOST /api/v1/users/{user_id}/payments/{id}/check_status/",
        "operationId": "payments_users_check_status_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/api-keys/": {
      "get": {
        "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
        "operationId": "payments_users_api_keys_list",
        "parameters": [
          {
            "in": "query",
            "name": "is_active",
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
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
        "operationId": "payments_users_api_keys_create",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/api-keys/active/": {
      "get": {
        "description": "Get user\u0027s active API keys.\n\nGET /api/users/{user_id}/api-keys/active/",
        "operationId": "payments_users_api_keys_active_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/api-keys/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_users_api_keys_health_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/api-keys/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_users_api_keys_stats_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/api-keys/summary/": {
      "get": {
        "description": "Get user API key summary.\n\nGET /api/users/{user_id}/api-keys/summary/",
        "operationId": "payments_users_api_keys_summary_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/api-keys/{id}/": {
      "delete": {
        "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
        "operationId": "payments_users_api_keys_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
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
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
        "operationId": "payments_users_api_keys_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
        "operationId": "payments_users_api_keys_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
          }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "User-specific API Key ViewSet: /api/users/{user_id}/api-keys/\n\nProvides user-scoped access to API keys with full CRUD operations.",
        "operationId": "payments_users_api_keys_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/api-keys/{id}/perform_action/": {
      "post": {
        "description": "Perform action on API key.\n\nPOST /api/users/{user_id}/api-keys/{id}/perform_action/",
        "operationId": "payments_users_api_keys_perform_action_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this API key",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/payments/": {
      "get": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_payments_list",
        "parameters": [
          {
            "in": "query",
            "name": "currency__code",
            "schema": {
              "type": "string"
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
            "description": "Payment provider\n\n* `nowpayments` - NowPayments",
            "in": "query",
            "name": "provider",
            "schema": {
              "enum": [
                "nowpayments"
              ],
              "type": "string",
              "x-spec-enum-id": "47694db6bd068cb3"
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
            "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled\n* `refunded` - Refunded",
            "in": "query",
            "name": "status",
            "schema": {
              "enum": [
                "cancelled",
                "completed",
                "confirmed",
                "confirming",
                "expired",
                "failed",
                "pending",
                "refunded"
              ],
              "type": "string",
              "x-spec-enum-id": "59d07a8608d1bdb9"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_payments_create",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/payments/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_users_payments_health_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/payments/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_users_payments_stats_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/payments/summary/": {
      "get": {
        "description": "Get user payment summary.\n\nGET /api/v1/users/{user_id}/payments/summary/",
        "operationId": "payments_users_payments_summary_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/payments/{id}/": {
      "delete": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_payments_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
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
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_payments_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_payments_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
          }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "User-specific payment ViewSet: /api/v1/users/{user_id}/payments/\n\nProvides user-scoped access to payments with full CRUD operations.",
        "operationId": "payments_users_payments_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/payments/{id}/cancel/": {
      "post": {
        "description": "Cancel payment.\n\nPOST /api/v1/users/{user_id}/payments/{id}/cancel/",
        "operationId": "payments_users_payments_cancel_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/payments/{id}/check_status/": {
      "post": {
        "description": "Check payment status with provider.\n\nPOST /api/v1/users/{user_id}/payments/{id}/check_status/",
        "operationId": "payments_users_payments_check_status_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who created this payment",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/subscriptions/": {
      "get": {
        "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
        "operationId": "payments_users_subscriptions_list",
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
          },
          {
            "description": "Subscription status\n\n* `active` - Active\n* `inactive` - Inactive\n* `suspended` - Suspended\n* `cancelled` - Cancelled\n* `expired` - Expired",
            "in": "query",
            "name": "status",
            "schema": {
              "enum": [
                "active",
                "cancelled",
                "expired",
                "inactive",
                "suspended"
              ],
              "type": "string",
              "x-spec-enum-id": "20d0bcc8b3c2bafa"
            }
          },
          {
            "description": "Subscription tier\n\n* `free` - Free Tier\n* `basic` - Basic Tier\n* `pro` - Pro Tier\n* `enterprise` - Enterprise Tier",
            "in": "query",
            "name": "tier",
            "schema": {
              "enum": [
                "basic",
                "enterprise",
                "free",
                "pro"
              ],
              "type": "string",
              "x-spec-enum-id": "776e806f04431486"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
        "operationId": "payments_users_subscriptions_create",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/subscriptions/active/": {
      "get": {
        "description": "Get user\u0027s active subscription.\n\nGET /api/users/{user_id}/subscriptions/active/",
        "operationId": "payments_users_subscriptions_active_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/subscriptions/health/": {
      "get": {
        "description": "Health check for the ViewSet and related services.\n\nReturns service status and basic metrics.",
        "operationId": "payments_users_subscriptions_health_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/subscriptions/stats/": {
      "get": {
        "description": "Get statistics for the current queryset.\n\nReturns counts, aggregates, and breakdowns.",
        "operationId": "payments_users_subscriptions_stats_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/subscriptions/summary/": {
      "get": {
        "description": "Get user subscription summary.\n\nGET /api/users/{user_id}/subscriptions/summary/",
        "operationId": "payments_users_subscriptions_summary_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/subscriptions/{id}/": {
      "delete": {
        "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
        "operationId": "payments_users_subscriptions_destroy",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
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
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
        "operationId": "payments_users_subscriptions_retrieve",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
        "operationId": "payments_users_subscriptions_partial_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
          }
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
          "payments"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "User-specific subscription ViewSet: /api/users/{user_id}/subscriptions/\n\nProvides user-scoped access to subscriptions with full CRUD operations.",
        "operationId": "payments_users_subscriptions_update",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/subscriptions/{id}/increment_usage/": {
      "post": {
        "description": "Increment subscription usage.\n\nPOST /api/users/{user_id}/subscriptions/{id}/increment_usage/",
        "operationId": "payments_users_subscriptions_increment_usage_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/users/{user_pk}/subscriptions/{id}/update_status/": {
      "post": {
        "description": "Update subscription status.\n\nPOST /api/users/{user_id}/subscriptions/{id}/update_status/",
        "operationId": "payments_users_subscriptions_update_status_create",
        "parameters": [
          {
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "description": "Unique identifier for this record",
              "format": "uuid",
              "type": "string"
            }
          },
          {
            "in": "path",
            "name": "user_pk",
            "required": true,
            "schema": {
              "description": "User who owns this subscription",
              "type": "integer"
            }
          }
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
          "required": true
        },
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
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/payments/webhooks/health/": {
      "get": {
        "description": "Check webhook service health status and recent activity metrics",
        "operationId": "payments_webhooks_health_retrieve",
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
        "summary": "Webhook Health Check",
        "tags": [
          "Webhooks"
        ],
        "x-async-capable": false
      }
    },
    "/payments/webhooks/providers/": {
      "get": {
        "description": "Get list of supported webhook providers with configuration details",
        "operationId": "payments_webhooks_providers_retrieve",
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
        "summary": "Supported Webhook Providers",
        "tags": [
          "Webhooks"
        ],
        "x-async-capable": false
      }
    },
    "/payments/webhooks/stats/": {
      "get": {
        "description": "Get webhook processing statistics for a given time period",
        "operationId": "payments_webhooks_stats_retrieve",
        "parameters": [
          {
            "description": "Number of days to analyze (1-365)",
            "in": "query",
            "name": "days",
            "schema": {
              "default": 30,
              "type": "integer"
            }
          }
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
        "summary": "Webhook Statistics",
        "tags": [
          "Webhooks"
        ],
        "x-async-capable": false
      }
    },
    "/payments/webhooks/{provider}/": {
      "get": {
        "description": "Get webhook endpoint information for debugging and configuration",
        "operationId": "payments_webhooks_retrieve",
        "parameters": [
          {
            "description": "Payment provider name",
            "in": "path",
            "name": "provider",
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
                  "$ref": "#/components/schemas/WebhookResponse"
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
        "summary": "Webhook Endpoint Info",
        "tags": [
          "Webhooks"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Process incoming webhook from payment provider",
        "operationId": "payments_webhooks_create",
        "parameters": [
          {
            "description": "Payment provider name (nowpayments, stripe, etc.)",
            "in": "path",
            "name": "provider",
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
          "required": true
        },
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
        "summary": "Process Webhook",
        "tags": [
          "Webhooks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/clear-queues/": {
      "post": {
        "description": "Clear all tasks from all Dramatiq queues.",
        "operationId": "tasks_api_clear_queues_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/clear/": {
      "post": {
        "description": "Clear all test data from Redis.",
        "operationId": "tasks_api_clear_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/purge-failed/": {
      "post": {
        "description": "Purge all failed tasks from queues.",
        "operationId": "tasks_api_purge_failed_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/queues/manage/": {
      "post": {
        "description": "Manage queue operations (clear, purge, etc.).",
        "operationId": "tasks_api_queues_manage_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/queues/status/": {
      "get": {
        "description": "Get current status of all queues.",
        "operationId": "tasks_api_queues_status_retrieve",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/simulate/": {
      "post": {
        "description": "Simulate test data for dashboard testing.",
        "operationId": "tasks_api_simulate_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/tasks/list/": {
      "get": {
        "description": "Get paginated task list with filtering.",
        "operationId": "tasks_api_tasks_list_retrieve",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/tasks/stats/": {
      "get": {
        "description": "Get task execution statistics.",
        "operationId": "tasks_api_tasks_stats_retrieve",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/workers/list/": {
      "get": {
        "description": "Get detailed list of workers.",
        "operationId": "tasks_api_workers_list_retrieve",
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    },
    "/tasks/api/workers/manage/": {
      "post": {
        "description": "Manage worker operations.",
        "operationId": "tasks_api_workers_manage_create",
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
          "required": true
        },
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
        "security": [
          {
            "cookieAuth": []
          },
          {
            "basicAuth": []
          }
        ],
        "tags": [
          "tasks"
        ],
        "x-async-capable": false
      }
    }
  }
};