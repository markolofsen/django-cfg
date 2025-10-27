/**
 * OpenAPI Schema Export
 *
 * Contains the complete OpenAPI specification for runtime access.
 */

export const OPENAPI_SCHEMA = {
  "components": {
    "schemas": {
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
      "APIZone": {
        "description": "OpenAPI zone/group serializer.",
        "properties": {
          "api_url": {
            "type": "string"
          },
          "app_count": {
            "type": "integer"
          },
          "apps": {
            "items": {
              "type": "string"
            },
            "type": "array"
          },
          "description": {
            "type": "string"
          },
          "endpoint_count": {
            "type": "integer"
          },
          "name": {
            "type": "string"
          },
          "schema_url": {
            "type": "string"
          },
          "status": {
            "type": "string"
          },
          "title": {
            "type": "string"
          }
        },
        "required": [
          "api_url",
          "app_count",
          "apps",
          "description",
          "endpoint_count",
          "name",
          "schema_url",
          "status",
          "title"
        ],
        "type": "object"
      },
      "APIZonesSummary": {
        "description": "API zones summary serializer.",
        "properties": {
          "summary": {
            "additionalProperties": {},
            "type": "object"
          },
          "zones": {
            "items": {
              "$ref": "#/components/schemas/APIZone"
            },
            "type": "array"
          }
        },
        "required": [
          "summary",
          "zones"
        ],
        "type": "object"
      },
      "ActivityEntry": {
        "description": "Serializer for recent activity entries.",
        "properties": {
          "action": {
            "description": "Action type (created, updated, deleted, etc.)",
            "type": "string"
          },
          "color": {
            "description": "Icon color",
            "type": "string"
          },
          "icon": {
            "description": "Material icon name",
            "type": "string"
          },
          "id": {
            "description": "Activity ID",
            "type": "integer"
          },
          "resource": {
            "description": "Resource affected",
            "type": "string"
          },
          "timestamp": {
            "description": "Activity timestamp (ISO format)",
            "type": "string"
          },
          "user": {
            "description": "User who performed the action",
            "type": "string"
          }
        },
        "required": [
          "action",
          "color",
          "icon",
          "id",
          "resource",
          "timestamp",
          "user"
        ],
        "type": "object"
      },
      "ActivityTrackerDay": {
        "description": "Activity tracker single day serializer.",
        "properties": {
          "color": {
            "type": "string"
          },
          "count": {
            "type": "integer"
          },
          "date": {
            "format": "date",
            "type": "string"
          },
          "level": {
            "type": "integer"
          },
          "tooltip": {
            "type": "string"
          }
        },
        "required": [
          "color",
          "count",
          "date",
          "level",
          "tooltip"
        ],
        "type": "object"
      },
      "AppStatistics": {
        "description": "Serializer for application-specific statistics.",
        "properties": {
          "app_name": {
            "description": "Application name",
            "type": "string"
          },
          "statistics": {
            "additionalProperties": {
              "type": "integer"
            },
            "description": "Application statistics",
            "type": "object"
          }
        },
        "required": [
          "app_name",
          "statistics"
        ],
        "type": "object"
      },
      "ArchiveItem": {
        "description": "Archive item serializer.",
        "properties": {
          "chunks_count": {
            "description": "Number of chunks created",
            "readOnly": true,
            "type": "integer"
          },
          "content_type": {
            "description": "Content classification\n\n* `document` - Document\n* `code` - Code\n* `image` - Image\n* `data` - Data\n* `archive` - Archive\n* `unknown` - Unknown",
            "enum": [
              "document",
              "code",
              "image",
              "data",
              "archive",
              "unknown"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "e6657d144665c87e"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "encoding": {
            "description": "Character encoding",
            "readOnly": true,
            "type": "string"
          },
          "file_size": {
            "description": "Item size in bytes",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_processable": {
            "description": "Whether item can be processed for chunks",
            "readOnly": true,
            "type": "boolean"
          },
          "item_name": {
            "description": "Item name",
            "maxLength": 255,
            "type": "string"
          },
          "item_type": {
            "description": "MIME type",
            "maxLength": 100,
            "type": "string"
          },
          "language": {
            "description": "Programming language or document language",
            "readOnly": true,
            "type": "string"
          },
          "processing_cost": {
            "description": "Processing cost for this item",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "relative_path": {
            "description": "Path within archive",
            "maxLength": 1024,
            "type": "string"
          },
          "total_tokens": {
            "description": "Total tokens in all chunks",
            "readOnly": true,
            "type": "integer"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "ArchiveItemChunk": {
        "description": "Archive item chunk serializer.",
        "properties": {
          "character_count": {
            "description": "Number of characters in chunk",
            "readOnly": true,
            "type": "integer"
          },
          "chunk_index": {
            "description": "Sequential chunk number within item",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "chunk_type": {
            "description": "Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List",
            "enum": [
              "text",
              "code",
              "heading",
              "metadata",
              "table",
              "list"
            ],
            "type": "string",
            "x-spec-enum-id": "660846bb1567d97b"
          },
          "content": {
            "description": "Chunk text content",
            "type": "string"
          },
          "context_summary": {
            "additionalProperties": {},
            "description": "Get context summary for display.",
            "readOnly": true,
            "type": "object"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "embedding_cost": {
            "description": "Cost in USD for embedding generation",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "embedding_model": {
            "description": "Model used for embedding generation",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "token_count": {
            "description": "Number of tokens in chunk",
            "readOnly": true,
            "type": "integer"
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
        ],
        "type": "object"
      },
      "ArchiveItemChunkDetail": {
        "description": "Detailed chunk serializer with full context.",
        "properties": {
          "character_count": {
            "description": "Number of characters in chunk",
            "readOnly": true,
            "type": "integer"
          },
          "chunk_index": {
            "description": "Sequential chunk number within item",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "chunk_type": {
            "description": "Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List",
            "enum": [
              "text",
              "code",
              "heading",
              "metadata",
              "table",
              "list"
            ],
            "type": "string",
            "x-spec-enum-id": "660846bb1567d97b"
          },
          "content": {
            "description": "Chunk text content",
            "type": "string"
          },
          "context_metadata": {
            "readOnly": true
          },
          "context_summary": {
            "additionalProperties": {},
            "description": "Get context summary for display.",
            "readOnly": true,
            "type": "object"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "embedding_cost": {
            "description": "Cost in USD for embedding generation",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "embedding_model": {
            "description": "Model used for embedding generation",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "token_count": {
            "description": "Number of tokens in chunk",
            "readOnly": true,
            "type": "integer"
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
        ],
        "type": "object"
      },
      "ArchiveItemChunkRequest": {
        "description": "Archive item chunk serializer.",
        "properties": {
          "chunk_index": {
            "description": "Sequential chunk number within item",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "chunk_type": {
            "description": "Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List",
            "enum": [
              "text",
              "code",
              "heading",
              "metadata",
              "table",
              "list"
            ],
            "type": "string",
            "x-spec-enum-id": "660846bb1567d97b"
          },
          "content": {
            "description": "Chunk text content",
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "chunk_index",
          "content"
        ],
        "type": "object"
      },
      "ArchiveItemDetail": {
        "description": "Detailed archive item serializer with content.",
        "properties": {
          "chunks_count": {
            "description": "Number of chunks created",
            "readOnly": true,
            "type": "integer"
          },
          "content_type": {
            "description": "Content classification\n\n* `document` - Document\n* `code` - Code\n* `image` - Image\n* `data` - Data\n* `archive` - Archive\n* `unknown` - Unknown",
            "enum": [
              "document",
              "code",
              "image",
              "data",
              "archive",
              "unknown"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "e6657d144665c87e"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "encoding": {
            "description": "Character encoding",
            "readOnly": true,
            "type": "string"
          },
          "file_size": {
            "description": "Item size in bytes",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_processable": {
            "description": "Whether item can be processed for chunks",
            "readOnly": true,
            "type": "boolean"
          },
          "item_name": {
            "description": "Item name",
            "maxLength": 255,
            "type": "string"
          },
          "item_type": {
            "description": "MIME type",
            "maxLength": 100,
            "type": "string"
          },
          "language": {
            "description": "Programming language or document language",
            "readOnly": true,
            "type": "string"
          },
          "metadata": {
            "readOnly": true
          },
          "processing_cost": {
            "description": "Processing cost for this item",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "raw_content": {
            "readOnly": true,
            "type": "string"
          },
          "relative_path": {
            "description": "Path within archive",
            "maxLength": 1024,
            "type": "string"
          },
          "total_tokens": {
            "description": "Total tokens in all chunks",
            "readOnly": true,
            "type": "integer"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "ArchiveItemRequest": {
        "description": "Archive item serializer.",
        "properties": {
          "file_size": {
            "description": "Item size in bytes",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "item_name": {
            "description": "Item name",
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          },
          "item_type": {
            "description": "MIME type",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          },
          "relative_path": {
            "description": "Path within archive",
            "maxLength": 1024,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "item_name",
          "item_type",
          "relative_path"
        ],
        "type": "object"
      },
      "ArchiveProcessingResult": {
        "description": "Archive processing result serializer.",
        "properties": {
          "archive_id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "chunks_created": {
            "readOnly": true,
            "type": "integer"
          },
          "error_message": {
            "readOnly": true,
            "type": "string"
          },
          "items_processed": {
            "readOnly": true,
            "type": "integer"
          },
          "processing_time_ms": {
            "readOnly": true,
            "type": "integer"
          },
          "status": {
            "readOnly": true,
            "type": "string"
          },
          "total_cost_usd": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "vectorized_chunks": {
            "readOnly": true,
            "type": "integer"
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
        ],
        "type": "object"
      },
      "ArchiveSearchRequestRequest": {
        "description": "Archive search request serializer.",
        "properties": {
          "archive_ids": {
            "description": "Search within specific archives",
            "items": {
              "format": "uuid",
              "type": "string"
            },
            "type": "array"
          },
          "chunk_types": {
            "description": "Filter by chunk types",
            "items": {
              "description": "* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List",
              "enum": [
                "text",
                "code",
                "heading",
                "metadata",
                "table",
                "list"
              ],
              "type": "string",
              "x-spec-enum-id": "660846bb1567d97b"
            },
            "type": "array"
          },
          "content_types": {
            "description": "Filter by content types",
            "items": {
              "description": "* `document` - Document\n* `code` - Code\n* `image` - Image\n* `data` - Data\n* `archive` - Archive\n* `unknown` - Unknown",
              "enum": [
                "document",
                "code",
                "image",
                "data",
                "archive",
                "unknown"
              ],
              "type": "string",
              "x-spec-enum-id": "e6657d144665c87e"
            },
            "type": "array"
          },
          "languages": {
            "description": "Filter by programming languages",
            "items": {
              "maxLength": 50,
              "minLength": 1,
              "type": "string"
            },
            "type": "array"
          },
          "limit": {
            "default": 10,
            "description": "Maximum number of results",
            "maximum": 50,
            "minimum": 1,
            "type": "integer"
          },
          "query": {
            "description": "Search query",
            "maxLength": 500,
            "minLength": 1,
            "type": "string"
          },
          "similarity_threshold": {
            "default": 0.7,
            "description": "Minimum similarity threshold",
            "format": "double",
            "maximum": 1.0,
            "minimum": 0.0,
            "type": "number"
          }
        },
        "required": [
          "query"
        ],
        "type": "object"
      },
      "ArchiveSearchResult": {
        "description": "Archive search result serializer.",
        "properties": {
          "archive_info": {
            "additionalProperties": {},
            "readOnly": true,
            "type": "object"
          },
          "chunk": {
            "allOf": [
              {
                "$ref": "#/components/schemas/ArchiveItemChunk"
              }
            ],
            "readOnly": true
          },
          "context_summary": {
            "additionalProperties": {},
            "readOnly": true,
            "type": "object"
          },
          "item_info": {
            "additionalProperties": {},
            "readOnly": true,
            "type": "object"
          },
          "similarity_score": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          }
        },
        "required": [
          "archive_info",
          "chunk",
          "context_summary",
          "item_info",
          "similarity_score"
        ],
        "type": "object"
      },
      "ArchiveStatistics": {
        "description": "Archive statistics serializer.",
        "properties": {
          "avg_chunks_per_archive": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "avg_items_per_archive": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "avg_processing_time": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "failed_archives": {
            "readOnly": true,
            "type": "integer"
          },
          "processed_archives": {
            "readOnly": true,
            "type": "integer"
          },
          "total_archives": {
            "readOnly": true,
            "type": "integer"
          },
          "total_chunks": {
            "readOnly": true,
            "type": "integer"
          },
          "total_cost": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "total_items": {
            "readOnly": true,
            "type": "integer"
          },
          "total_tokens": {
            "readOnly": true,
            "type": "integer"
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
        ],
        "type": "object"
      },
      "Balance": {
        "description": "User balance serializer.",
        "properties": {
          "balance_display": {
            "readOnly": true,
            "type": "string"
          },
          "balance_usd": {
            "description": "Current balance in USD",
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "last_transaction_at": {
            "description": "When the last transaction occurred",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "total_deposited": {
            "description": "Total amount deposited (lifetime)",
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "total_withdrawn": {
            "description": "Total amount withdrawn (lifetime)",
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "balance_display",
          "balance_usd",
          "last_transaction_at",
          "total_deposited",
          "total_withdrawn"
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
      "CentrifugoChannelInfo": {
        "description": "Information about a single channel.",
        "properties": {
          "num_clients": {
            "description": "Number of connected clients in channel",
            "title": "Num Clients",
            "type": "integer"
          }
        },
        "required": [
          "num_clients"
        ],
        "title": "CentrifugoChannelInfo",
        "type": "object"
      },
      "CentrifugoChannelsRequestRequest": {
        "description": "Request to list active channels.",
        "properties": {
          "pattern": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Pattern to filter channels (e.g., \u0027user:*\u0027)",
            "title": "Pattern"
          }
        },
        "title": "CentrifugoChannelsRequest",
        "type": "object"
      },
      "CentrifugoChannelsResponse": {
        "description": "List of active channels response.",
        "properties": {
          "error": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoError"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Error if any"
          },
          "result": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoChannelsResult"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Result data"
          }
        },
        "title": "CentrifugoChannelsResponse",
        "type": "object"
      },
      "CentrifugoChannelsResult": {
        "description": "Channels result wrapper.",
        "properties": {
          "channels": {
            "additionalProperties": {
              "$ref": "#/components/schemas/CentrifugoChannelInfo"
            },
            "description": "Map of channel names to channel info",
            "title": "Channels",
            "type": "object"
          }
        },
        "required": [
          "channels"
        ],
        "title": "CentrifugoChannelsResult",
        "type": "object"
      },
      "CentrifugoClientInfo": {
        "description": "Information about connected client.",
        "properties": {
          "chan_info": {
            "anyOf": [
              {
                "additionalProperties": true,
                "type": "object"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Channel-specific metadata",
            "title": "Chan Info"
          },
          "client": {
            "description": "Client UUID",
            "title": "Client",
            "type": "string"
          },
          "conn_info": {
            "anyOf": [
              {
                "additionalProperties": true,
                "type": "object"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Connection metadata",
            "title": "Conn Info"
          },
          "user": {
            "description": "User ID",
            "title": "User",
            "type": "string"
          }
        },
        "required": [
          "user",
          "client"
        ],
        "title": "CentrifugoClientInfo",
        "type": "object"
      },
      "CentrifugoError": {
        "description": "Centrifugo API error structure.",
        "properties": {
          "code": {
            "default": 0,
            "description": "Error code (0 = no error)",
            "title": "Code",
            "type": "integer"
          },
          "message": {
            "default": "",
            "description": "Error message",
            "title": "Message",
            "type": "string"
          }
        },
        "title": "CentrifugoError",
        "type": "object"
      },
      "CentrifugoHistoryRequestRequest": {
        "description": "Request to get channel history.",
        "properties": {
          "channel": {
            "description": "Channel name",
            "title": "Channel",
            "type": "string"
          },
          "limit": {
            "anyOf": [
              {
                "maximum": 1000,
                "minimum": 1,
                "type": "integer"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Maximum number of messages to return",
            "title": "Limit"
          },
          "reverse": {
            "anyOf": [
              {
                "type": "boolean"
              },
              {
                "type": "null"
              }
            ],
            "default": false,
            "description": "Reverse message order (newest first)",
            "title": "Reverse"
          },
          "since": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoStreamPosition"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Stream position to get messages since"
          }
        },
        "required": [
          "channel"
        ],
        "title": "CentrifugoHistoryRequest",
        "type": "object"
      },
      "CentrifugoHistoryResponse": {
        "description": "Channel history response.",
        "properties": {
          "error": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoError"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Error if any"
          },
          "result": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoHistoryResult"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Result data"
          }
        },
        "title": "CentrifugoHistoryResponse",
        "type": "object"
      },
      "CentrifugoHistoryResult": {
        "description": "History result wrapper.",
        "properties": {
          "epoch": {
            "description": "Current stream epoch",
            "title": "Epoch",
            "type": "string"
          },
          "offset": {
            "description": "Latest stream offset",
            "title": "Offset",
            "type": "integer"
          },
          "publications": {
            "description": "List of publications",
            "items": {
              "$ref": "#/components/schemas/CentrifugoPublication"
            },
            "title": "Publications",
            "type": "array"
          }
        },
        "required": [
          "publications",
          "epoch",
          "offset"
        ],
        "title": "CentrifugoHistoryResult",
        "type": "object"
      },
      "CentrifugoInfoResponse": {
        "description": "Server info response.",
        "properties": {
          "error": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoError"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Error if any"
          },
          "result": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoInfoResult"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Result data"
          }
        },
        "title": "CentrifugoInfoResponse",
        "type": "object"
      },
      "CentrifugoInfoResult": {
        "description": "Info result wrapper.",
        "properties": {
          "nodes": {
            "description": "List of Centrifugo nodes",
            "items": {
              "$ref": "#/components/schemas/CentrifugoNodeInfo"
            },
            "title": "Nodes",
            "type": "array"
          }
        },
        "required": [
          "nodes"
        ],
        "title": "CentrifugoInfoResult",
        "type": "object"
      },
      "CentrifugoMetrics": {
        "description": "Server metrics.",
        "properties": {
          "interval": {
            "description": "Metrics collection interval",
            "title": "Interval",
            "type": "number"
          },
          "items": {
            "additionalProperties": {
              "type": "number"
            },
            "description": "Metric name to value mapping",
            "title": "Items",
            "type": "object"
          }
        },
        "required": [
          "interval",
          "items"
        ],
        "title": "CentrifugoMetrics",
        "type": "object"
      },
      "CentrifugoNodeInfo": {
        "description": "Information about a single Centrifugo node.",
        "properties": {
          "metrics": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoMetrics"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Server metrics"
          },
          "name": {
            "description": "Node name",
            "title": "Name",
            "type": "string"
          },
          "num_channels": {
            "description": "Number of active channels",
            "title": "Num Channels",
            "type": "integer"
          },
          "num_clients": {
            "description": "Number of connected clients",
            "title": "Num Clients",
            "type": "integer"
          },
          "num_subs": {
            "description": "Total number of subscriptions",
            "title": "Num Subs",
            "type": "integer"
          },
          "num_users": {
            "description": "Number of unique users",
            "title": "Num Users",
            "type": "integer"
          },
          "process": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoProcess"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Process information"
          },
          "uid": {
            "description": "Unique node identifier",
            "title": "Uid",
            "type": "string"
          },
          "uptime": {
            "description": "Node uptime in seconds",
            "title": "Uptime",
            "type": "integer"
          },
          "version": {
            "description": "Centrifugo version",
            "title": "Version",
            "type": "string"
          }
        },
        "required": [
          "uid",
          "name",
          "version",
          "num_clients",
          "num_users",
          "num_channels",
          "uptime",
          "num_subs"
        ],
        "title": "CentrifugoNodeInfo",
        "type": "object"
      },
      "CentrifugoPresenceRequestRequest": {
        "description": "Request to get channel presence.",
        "properties": {
          "channel": {
            "description": "Channel name",
            "title": "Channel",
            "type": "string"
          }
        },
        "required": [
          "channel"
        ],
        "title": "CentrifugoPresenceRequest",
        "type": "object"
      },
      "CentrifugoPresenceResponse": {
        "description": "Channel presence response.",
        "properties": {
          "error": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoError"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Error if any"
          },
          "result": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoPresenceResult"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Result data"
          }
        },
        "title": "CentrifugoPresenceResponse",
        "type": "object"
      },
      "CentrifugoPresenceResult": {
        "description": "Presence result wrapper.",
        "properties": {
          "presence": {
            "additionalProperties": {
              "$ref": "#/components/schemas/CentrifugoClientInfo"
            },
            "description": "Map of client IDs to client info",
            "title": "Presence",
            "type": "object"
          }
        },
        "required": [
          "presence"
        ],
        "title": "CentrifugoPresenceResult",
        "type": "object"
      },
      "CentrifugoPresenceStatsRequestRequest": {
        "description": "Request to get channel presence statistics.",
        "properties": {
          "channel": {
            "description": "Channel name",
            "title": "Channel",
            "type": "string"
          }
        },
        "required": [
          "channel"
        ],
        "title": "CentrifugoPresenceStatsRequest",
        "type": "object"
      },
      "CentrifugoPresenceStatsResponse": {
        "description": "Channel presence stats response.",
        "properties": {
          "error": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoError"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Error if any"
          },
          "result": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoPresenceStatsResult"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Result data"
          }
        },
        "title": "CentrifugoPresenceStatsResponse",
        "type": "object"
      },
      "CentrifugoPresenceStatsResult": {
        "description": "Presence stats result.",
        "properties": {
          "num_clients": {
            "description": "Number of connected clients",
            "title": "Num Clients",
            "type": "integer"
          },
          "num_users": {
            "description": "Number of unique users",
            "title": "Num Users",
            "type": "integer"
          }
        },
        "required": [
          "num_clients",
          "num_users"
        ],
        "title": "CentrifugoPresenceStatsResult",
        "type": "object"
      },
      "CentrifugoProcess": {
        "description": "Process information.",
        "properties": {
          "cpu": {
            "description": "CPU usage percentage",
            "title": "Cpu",
            "type": "number"
          },
          "rss": {
            "description": "Resident set size in bytes",
            "title": "Rss",
            "type": "integer"
          }
        },
        "required": [
          "cpu",
          "rss"
        ],
        "title": "CentrifugoProcess",
        "type": "object"
      },
      "CentrifugoPublication": {
        "description": "Single publication (message) in channel history.",
        "properties": {
          "data": {
            "additionalProperties": true,
            "description": "Message payload",
            "title": "Data",
            "type": "object"
          },
          "info": {
            "anyOf": [
              {
                "$ref": "#/components/schemas/CentrifugoClientInfo"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Publisher client info"
          },
          "offset": {
            "description": "Message offset in channel stream",
            "title": "Offset",
            "type": "integer"
          },
          "tags": {
            "anyOf": [
              {
                "additionalProperties": {
                  "type": "string"
                },
                "type": "object"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Optional message tags",
            "title": "Tags"
          }
        },
        "required": [
          "data",
          "offset"
        ],
        "title": "CentrifugoPublication",
        "type": "object"
      },
      "CentrifugoStreamPosition": {
        "description": "Stream position for pagination.",
        "properties": {
          "epoch": {
            "description": "Stream epoch",
            "title": "Epoch",
            "type": "string"
          },
          "offset": {
            "description": "Stream offset",
            "title": "Offset",
            "type": "integer"
          }
        },
        "required": [
          "offset",
          "epoch"
        ],
        "title": "CentrifugoStreamPosition",
        "type": "object"
      },
      "ChannelList": {
        "description": "List of channel statistics.",
        "properties": {
          "channels": {
            "description": "Channel statistics",
            "items": {
              "$ref": "#/components/schemas/ChannelStatsSerializer"
            },
            "title": "Channels",
            "type": "array"
          },
          "total_channels": {
            "description": "Total number of channels",
            "title": "Total Channels",
            "type": "integer"
          }
        },
        "required": [
          "channels",
          "total_channels"
        ],
        "title": "ChannelListSerializer",
        "type": "object"
      },
      "ChannelStatsSerializer": {
        "description": "Statistics per channel.",
        "properties": {
          "avg_acks": {
            "description": "Average ACKs received",
            "title": "Avg Acks",
            "type": "number"
          },
          "avg_duration_ms": {
            "description": "Average duration",
            "title": "Avg Duration Ms",
            "type": "number"
          },
          "channel": {
            "description": "Channel name",
            "title": "Channel",
            "type": "string"
          },
          "failed": {
            "description": "Failed publishes",
            "title": "Failed",
            "type": "integer"
          },
          "last_activity_at": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Last activity timestamp (ISO format)",
            "title": "Last Activity At"
          },
          "successful": {
            "description": "Successful publishes",
            "title": "Successful",
            "type": "integer"
          },
          "total": {
            "description": "Total publishes to this channel",
            "title": "Total",
            "type": "integer"
          }
        },
        "required": [
          "channel",
          "total",
          "successful",
          "failed",
          "avg_duration_ms",
          "avg_acks"
        ],
        "title": "ChannelStatsSerializer",
        "type": "object"
      },
      "ChartData": {
        "description": "Chart.js data structure serializer.",
        "properties": {
          "datasets": {
            "items": {
              "$ref": "#/components/schemas/ChartDataset"
            },
            "type": "array"
          },
          "labels": {
            "items": {
              "type": "string"
            },
            "type": "array"
          }
        },
        "required": [
          "datasets",
          "labels"
        ],
        "type": "object"
      },
      "ChartDataset": {
        "description": "Chart.js dataset serializer.",
        "properties": {
          "backgroundColor": {
            "type": "string"
          },
          "borderColor": {
            "type": "string"
          },
          "data": {
            "items": {
              "type": "integer"
            },
            "type": "array"
          },
          "fill": {
            "type": "boolean"
          },
          "label": {
            "type": "string"
          },
          "tension": {
            "format": "double",
            "type": "number"
          }
        },
        "required": [
          "backgroundColor",
          "borderColor",
          "data",
          "label",
          "tension"
        ],
        "type": "object"
      },
      "ChatHistory": {
        "description": "Chat history response serializer.",
        "properties": {
          "messages": {
            "items": {
              "$ref": "#/components/schemas/ChatMessage"
            },
            "type": "array"
          },
          "session_id": {
            "format": "uuid",
            "type": "string"
          },
          "total_messages": {
            "type": "integer"
          }
        },
        "required": [
          "messages",
          "session_id",
          "total_messages"
        ],
        "type": "object"
      },
      "ChatMessage": {
        "description": "Chat message response serializer.",
        "properties": {
          "content": {
            "description": "Message content",
            "type": "string"
          },
          "context_chunks": {
            "description": "IDs of chunks used for context"
          },
          "cost_usd": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "processing_time_ms": {
            "description": "Processing time in milliseconds",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "role": {
            "description": "Message sender role\n\n* `user` - User\n* `assistant` - Assistant\n* `system` - System",
            "enum": [
              "user",
              "assistant",
              "system"
            ],
            "type": "string",
            "x-spec-enum-id": "6a92eb3ff78a3708"
          },
          "tokens_used": {
            "description": "Tokens used for this message",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          }
        },
        "required": [
          "content",
          "cost_usd",
          "created_at",
          "id",
          "role"
        ],
        "type": "object"
      },
      "ChatQueryRequest": {
        "description": "Chat query request serializer.",
        "properties": {
          "include_sources": {
            "default": true,
            "description": "Include source documents in response",
            "type": "boolean"
          },
          "max_tokens": {
            "default": 1000,
            "description": "Maximum response tokens",
            "maximum": 4000,
            "minimum": 1,
            "type": "integer"
          },
          "query": {
            "description": "User query",
            "maxLength": 2000,
            "minLength": 1,
            "type": "string"
          },
          "session_id": {
            "description": "Chat session ID (creates new if not provided)",
            "format": "uuid",
            "nullable": true,
            "type": "string"
          }
        },
        "required": [
          "query"
        ],
        "type": "object"
      },
      "ChatResponse": {
        "description": "Chat response serializer.",
        "properties": {
          "content": {
            "type": "string"
          },
          "cost_usd": {
            "format": "double",
            "type": "number"
          },
          "message_id": {
            "format": "uuid",
            "type": "string"
          },
          "model_used": {
            "type": "string"
          },
          "processing_time_ms": {
            "type": "integer"
          },
          "sources": {
            "items": {
              "$ref": "#/components/schemas/ChatSource"
            },
            "nullable": true,
            "type": "array"
          },
          "tokens_used": {
            "type": "integer"
          }
        },
        "required": [
          "content",
          "cost_usd",
          "message_id",
          "model_used",
          "processing_time_ms",
          "tokens_used"
        ],
        "type": "object"
      },
      "ChatResponseRequest": {
        "description": "Chat response serializer.",
        "properties": {
          "content": {
            "minLength": 1,
            "type": "string"
          },
          "cost_usd": {
            "format": "double",
            "type": "number"
          },
          "message_id": {
            "format": "uuid",
            "type": "string"
          },
          "model_used": {
            "minLength": 1,
            "type": "string"
          },
          "processing_time_ms": {
            "type": "integer"
          },
          "sources": {
            "items": {
              "$ref": "#/components/schemas/ChatSourceRequest"
            },
            "nullable": true,
            "type": "array"
          },
          "tokens_used": {
            "type": "integer"
          }
        },
        "required": [
          "content",
          "cost_usd",
          "message_id",
          "model_used",
          "processing_time_ms",
          "tokens_used"
        ],
        "type": "object"
      },
      "ChatSession": {
        "description": "Chat session response serializer.",
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_active": {
            "description": "Whether session accepts new messages",
            "type": "boolean"
          },
          "max_context_chunks": {
            "description": "Maximum chunks to include in context",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "messages_count": {
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "model_name": {
            "description": "LLM model used for this session",
            "maxLength": 100,
            "type": "string"
          },
          "temperature": {
            "description": "Temperature setting for LLM",
            "format": "double",
            "type": "number"
          },
          "title": {
            "description": "Session title (auto-generated if empty)",
            "maxLength": 255,
            "type": "string"
          },
          "total_cost_usd": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "total_tokens_used": {
            "maximum": 2147483647,
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
          "created_at",
          "id",
          "total_cost_usd",
          "updated_at"
        ],
        "type": "object"
      },
      "ChatSessionCreateRequest": {
        "description": "Chat session creation request serializer.",
        "properties": {
          "max_context_chunks": {
            "default": 5,
            "description": "Maximum context chunks",
            "maximum": 10,
            "minimum": 1,
            "type": "integer"
          },
          "model_name": {
            "default": "openai/gpt-4o-mini",
            "description": "LLM model to use",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          },
          "temperature": {
            "default": 0.7,
            "description": "Response creativity",
            "format": "double",
            "maximum": 2.0,
            "minimum": 0.0,
            "type": "number"
          },
          "title": {
            "default": "",
            "description": "Session title",
            "maxLength": 255,
            "type": "string"
          }
        },
        "type": "object"
      },
      "ChatSessionRequest": {
        "description": "Chat session response serializer.",
        "properties": {
          "is_active": {
            "description": "Whether session accepts new messages",
            "type": "boolean"
          },
          "max_context_chunks": {
            "description": "Maximum chunks to include in context",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "messages_count": {
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "model_name": {
            "description": "LLM model used for this session",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          },
          "temperature": {
            "description": "Temperature setting for LLM",
            "format": "double",
            "type": "number"
          },
          "title": {
            "description": "Session title (auto-generated if empty)",
            "maxLength": 255,
            "type": "string"
          },
          "total_tokens_used": {
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          }
        },
        "type": "object"
      },
      "ChatSource": {
        "description": "Chat source document information serializer.",
        "properties": {
          "chunk_content": {
            "type": "string"
          },
          "document_title": {
            "type": "string"
          },
          "similarity": {
            "format": "double",
            "type": "number"
          }
        },
        "required": [
          "chunk_content",
          "document_title",
          "similarity"
        ],
        "type": "object"
      },
      "ChatSourceRequest": {
        "description": "Chat source document information serializer.",
        "properties": {
          "chunk_content": {
            "minLength": 1,
            "type": "string"
          },
          "document_title": {
            "minLength": 1,
            "type": "string"
          },
          "similarity": {
            "format": "double",
            "type": "number"
          }
        },
        "required": [
          "chunk_content",
          "document_title",
          "similarity"
        ],
        "type": "object"
      },
      "ChunkRevectorizationRequestRequest": {
        "description": "Chunk re-vectorization request serializer.",
        "properties": {
          "chunk_ids": {
            "description": "List of chunk IDs to re-vectorize",
            "items": {
              "format": "uuid",
              "type": "string"
            },
            "minItems": 1,
            "type": "array"
          },
          "force": {
            "default": false,
            "description": "Force re-vectorization even if already vectorized",
            "type": "boolean"
          }
        },
        "required": [
          "chunk_ids"
        ],
        "type": "object"
      },
      "Command": {
        "description": "Django management command serializer.",
        "properties": {
          "app": {
            "type": "string"
          },
          "help": {
            "type": "string"
          },
          "is_core": {
            "type": "boolean"
          },
          "is_custom": {
            "type": "boolean"
          },
          "name": {
            "type": "string"
          }
        },
        "required": [
          "app",
          "help",
          "is_core",
          "is_custom",
          "name"
        ],
        "type": "object"
      },
      "CommandsSummary": {
        "description": "Commands summary serializer.",
        "properties": {
          "categories": {
            "items": {
              "type": "string"
            },
            "type": "array"
          },
          "categorized": {
            "additionalProperties": {},
            "type": "object"
          },
          "commands": {
            "items": {
              "$ref": "#/components/schemas/Command"
            },
            "type": "array"
          },
          "core_commands": {
            "type": "integer"
          },
          "custom_commands": {
            "type": "integer"
          },
          "total_commands": {
            "type": "integer"
          }
        },
        "required": [
          "categories",
          "categorized",
          "commands",
          "core_commands",
          "custom_commands",
          "total_commands"
        ],
        "type": "object"
      },
      "ConnectionTokenRequestRequest": {
        "description": "Request model for connection token generation.",
        "properties": {
          "channels": {
            "description": "List of channels to authorize",
            "items": {
              "type": "string"
            },
            "title": "Channels",
            "type": "array"
          },
          "user_id": {
            "description": "User ID for the connection",
            "title": "User Id",
            "type": "string"
          }
        },
        "required": [
          "user_id"
        ],
        "title": "ConnectionTokenRequest",
        "type": "object"
      },
      "ConnectionTokenResponse": {
        "description": "Response model for connection token.",
        "properties": {
          "centrifugo_url": {
            "description": "Centrifugo WebSocket URL",
            "title": "Centrifugo Url",
            "type": "string"
          },
          "expires_at": {
            "description": "Token expiration time (ISO 8601)",
            "title": "Expires At",
            "type": "string"
          },
          "token": {
            "description": "JWT token for WebSocket connection",
            "title": "Token",
            "type": "string"
          }
        },
        "required": [
          "token",
          "centrifugo_url",
          "expires_at"
        ],
        "title": "ConnectionTokenResponse",
        "type": "object"
      },
      "Currency": {
        "description": "Currency list serializer.",
        "properties": {
          "code": {
            "description": "Currency code from provider (e.g., USDTTRC20, BTC, ETH)",
            "readOnly": true,
            "type": "string"
          },
          "decimal_places": {
            "description": "Number of decimal places for this currency",
            "readOnly": true,
            "type": "integer"
          },
          "display_name": {
            "readOnly": true,
            "type": "string"
          },
          "is_active": {
            "description": "Whether this currency is available for payments",
            "readOnly": true,
            "type": "boolean"
          },
          "min_amount_usd": {
            "description": "Minimum payment amount in USD",
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "name": {
            "description": "Full currency name (e.g., USDT (TRC20), Bitcoin)",
            "readOnly": true,
            "type": "string"
          },
          "network": {
            "description": "Network name (e.g., TRC20, ERC20, Bitcoin)",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "sort_order": {
            "description": "Sort order for currency list (lower = higher priority)",
            "readOnly": true,
            "type": "integer"
          },
          "symbol": {
            "description": "Currency symbol (e.g., \u20ae, \u20bf, \u039e)",
            "readOnly": true,
            "type": "string"
          },
          "token": {
            "description": "Token symbol (e.g., USDT, BTC, ETH)",
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "DashboardOverview": {
        "description": "Main serializer for dashboard overview endpoint.\nUses DictField to avoid allOf generation in OpenAPI.",
        "properties": {
          "quick_actions": {
            "description": "Quick action buttons",
            "items": {
              "additionalProperties": {},
              "type": "object"
            },
            "type": "array"
          },
          "recent_activity": {
            "description": "Recent activity entries",
            "items": {
              "additionalProperties": {},
              "type": "object"
            },
            "type": "array"
          },
          "stat_cards": {
            "description": "Dashboard statistics cards",
            "items": {
              "additionalProperties": {},
              "type": "object"
            },
            "type": "array"
          },
          "system_health": {
            "description": "System health status",
            "items": {
              "additionalProperties": {},
              "type": "object"
            },
            "type": "array"
          },
          "system_metrics": {
            "additionalProperties": {},
            "description": "System performance metrics",
            "type": "object"
          },
          "timestamp": {
            "description": "Data timestamp (ISO format)",
            "type": "string"
          },
          "user_statistics": {
            "additionalProperties": {},
            "description": "User statistics",
            "type": "object"
          }
        },
        "required": [
          "quick_actions",
          "recent_activity",
          "stat_cards",
          "system_health",
          "system_metrics",
          "timestamp",
          "user_statistics"
        ],
        "type": "object"
      },
      "Document": {
        "description": "Document response serializer.",
        "properties": {
          "chunks_count": {
            "readOnly": true,
            "type": "integer"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "file_size": {
            "description": "Original file size in bytes",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "file_type": {
            "description": "MIME type of original file",
            "maxLength": 100,
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "metadata": {
            "description": "Additional document metadata",
            "nullable": true
          },
          "processing_completed_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "processing_error": {
            "readOnly": true,
            "type": "string"
          },
          "processing_started_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "processing_status": {
            "readOnly": true,
            "type": "string"
          },
          "title": {
            "description": "Document title",
            "maxLength": 512,
            "type": "string"
          },
          "total_cost_usd": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "total_tokens": {
            "readOnly": true,
            "type": "integer"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "DocumentArchive": {
        "description": "Document archive serializer.",
        "properties": {
          "archive_file": {
            "description": "Uploaded archive file",
            "format": "uri",
            "readOnly": true,
            "type": "string"
          },
          "archive_type": {
            "description": "Archive format\n\n* `zip` - ZIP\n* `tar` - TAR\n* `tar.gz` - TAR GZ\n* `tar.bz2` - TAR BZ2",
            "enum": [
              "zip",
              "tar",
              "tar.gz",
              "tar.bz2"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "51253f4da98c0846"
          },
          "categories": {
            "items": {
              "$ref": "#/components/schemas/DocumentCategory"
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
            "description": "Archive description",
            "type": "string"
          },
          "file_size": {
            "description": "Archive size in bytes",
            "readOnly": true,
            "type": "integer"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_processed": {
            "description": "Check if archive processing is completed.",
            "readOnly": true,
            "type": "boolean"
          },
          "is_public": {
            "description": "Whether this archive is publicly accessible",
            "type": "boolean"
          },
          "original_filename": {
            "description": "Original uploaded filename",
            "readOnly": true,
            "type": "string"
          },
          "processed_at": {
            "description": "When processing completed",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "processed_items": {
            "description": "Successfully processed items",
            "readOnly": true,
            "type": "integer"
          },
          "processing_duration_ms": {
            "description": "Processing time in milliseconds",
            "readOnly": true,
            "type": "integer"
          },
          "processing_error": {
            "description": "Error message if processing failed",
            "readOnly": true,
            "type": "string"
          },
          "processing_progress": {
            "description": "Calculate processing progress as percentage.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "processing_status": {
            "description": "* `pending` - Pending\n* `processing` - Processing\n* `completed` - Completed\n* `failed` - Failed\n* `cancelled` - Cancelled",
            "enum": [
              "pending",
              "processing",
              "completed",
              "failed",
              "cancelled"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "9c61eae888c009aa"
          },
          "title": {
            "description": "Archive title",
            "maxLength": 512,
            "type": "string"
          },
          "total_chunks": {
            "description": "Total chunks created",
            "readOnly": true,
            "type": "integer"
          },
          "total_cost_usd": {
            "description": "Total processing cost in USD",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "total_items": {
            "description": "Total items in archive",
            "readOnly": true,
            "type": "integer"
          },
          "total_tokens": {
            "description": "Total tokens across all chunks",
            "readOnly": true,
            "type": "integer"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "vectorization_progress": {
            "description": "Calculate vectorization progress as percentage.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "vectorized_chunks": {
            "description": "Chunks with embeddings",
            "readOnly": true,
            "type": "integer"
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
        ],
        "type": "object"
      },
      "DocumentArchiveDetail": {
        "description": "Detailed archive serializer with items.",
        "properties": {
          "archive_file": {
            "description": "Uploaded archive file",
            "format": "uri",
            "readOnly": true,
            "type": "string"
          },
          "archive_type": {
            "description": "Archive format\n\n* `zip` - ZIP\n* `tar` - TAR\n* `tar.gz` - TAR GZ\n* `tar.bz2` - TAR BZ2",
            "enum": [
              "zip",
              "tar",
              "tar.gz",
              "tar.bz2"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "51253f4da98c0846"
          },
          "categories": {
            "items": {
              "$ref": "#/components/schemas/DocumentCategory"
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
            "description": "Archive description",
            "type": "string"
          },
          "file_size": {
            "description": "Archive size in bytes",
            "readOnly": true,
            "type": "integer"
          },
          "file_tree": {
            "additionalProperties": {},
            "description": "Get hierarchical file tree.",
            "readOnly": true,
            "type": "object"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_processed": {
            "description": "Check if archive processing is completed.",
            "readOnly": true,
            "type": "boolean"
          },
          "is_public": {
            "description": "Whether this archive is publicly accessible",
            "type": "boolean"
          },
          "items": {
            "items": {
              "$ref": "#/components/schemas/ArchiveItem"
            },
            "readOnly": true,
            "type": "array"
          },
          "metadata": {
            "description": "Additional archive metadata",
            "nullable": true
          },
          "original_filename": {
            "description": "Original uploaded filename",
            "readOnly": true,
            "type": "string"
          },
          "processed_at": {
            "description": "When processing completed",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "processed_items": {
            "description": "Successfully processed items",
            "readOnly": true,
            "type": "integer"
          },
          "processing_duration_ms": {
            "description": "Processing time in milliseconds",
            "readOnly": true,
            "type": "integer"
          },
          "processing_error": {
            "description": "Error message if processing failed",
            "readOnly": true,
            "type": "string"
          },
          "processing_progress": {
            "description": "Calculate processing progress as percentage.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "processing_status": {
            "description": "* `pending` - Pending\n* `processing` - Processing\n* `completed` - Completed\n* `failed` - Failed\n* `cancelled` - Cancelled",
            "enum": [
              "pending",
              "processing",
              "completed",
              "failed",
              "cancelled"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "9c61eae888c009aa"
          },
          "title": {
            "description": "Archive title",
            "maxLength": 512,
            "type": "string"
          },
          "total_chunks": {
            "description": "Total chunks created",
            "readOnly": true,
            "type": "integer"
          },
          "total_cost_usd": {
            "description": "Total processing cost in USD",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "total_items": {
            "description": "Total items in archive",
            "readOnly": true,
            "type": "integer"
          },
          "total_tokens": {
            "description": "Total tokens across all chunks",
            "readOnly": true,
            "type": "integer"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "vectorization_progress": {
            "description": "Calculate vectorization progress as percentage.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "vectorized_chunks": {
            "description": "Chunks with embeddings",
            "readOnly": true,
            "type": "integer"
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
        ],
        "type": "object"
      },
      "DocumentArchiveList": {
        "description": "Simplified archive serializer for list views.",
        "properties": {
          "archive_type": {
            "description": "Archive format\n\n* `zip` - ZIP\n* `tar` - TAR\n* `tar.gz` - TAR GZ\n* `tar.bz2` - TAR BZ2",
            "enum": [
              "zip",
              "tar",
              "tar.gz",
              "tar.bz2"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "51253f4da98c0846"
          },
          "categories": {
            "items": {
              "$ref": "#/components/schemas/DocumentCategory"
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
            "description": "Archive description",
            "readOnly": true,
            "type": "string"
          },
          "file_size": {
            "description": "Archive size in bytes",
            "readOnly": true,
            "type": "integer"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_public": {
            "description": "Whether this archive is publicly accessible",
            "readOnly": true,
            "type": "boolean"
          },
          "original_filename": {
            "description": "Original uploaded filename",
            "readOnly": true,
            "type": "string"
          },
          "processed_at": {
            "description": "When processing completed",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "processing_progress": {
            "description": "Calculate processing progress as percentage.",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "processing_status": {
            "description": "* `pending` - Pending\n* `processing` - Processing\n* `completed` - Completed\n* `failed` - Failed\n* `cancelled` - Cancelled",
            "enum": [
              "pending",
              "processing",
              "completed",
              "failed",
              "cancelled"
            ],
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "9c61eae888c009aa"
          },
          "title": {
            "description": "Archive title",
            "readOnly": true,
            "type": "string"
          },
          "total_chunks": {
            "description": "Total chunks created",
            "readOnly": true,
            "type": "integer"
          },
          "total_cost_usd": {
            "description": "Total processing cost in USD",
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "total_items": {
            "description": "Total items in archive",
            "readOnly": true,
            "type": "integer"
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
        ],
        "type": "object"
      },
      "DocumentArchiveRequest": {
        "description": "Document archive serializer.",
        "properties": {
          "description": {
            "description": "Archive description",
            "type": "string"
          },
          "is_public": {
            "description": "Whether this archive is publicly accessible",
            "type": "boolean"
          },
          "title": {
            "description": "Archive title",
            "maxLength": 512,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "title"
        ],
        "type": "object"
      },
      "DocumentCategory": {
        "description": "Document category serializer.",
        "properties": {
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "description": {
            "description": "Category description",
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "is_public": {
            "description": "Whether documents in this category are publicly accessible",
            "type": "boolean"
          },
          "name": {
            "description": "Category name",
            "maxLength": 255,
            "type": "string"
          }
        },
        "required": [
          "created_at",
          "id",
          "name"
        ],
        "type": "object"
      },
      "DocumentCategoryRequest": {
        "description": "Document category serializer.",
        "properties": {
          "description": {
            "description": "Category description",
            "type": "string"
          },
          "is_public": {
            "description": "Whether documents in this category are publicly accessible",
            "type": "boolean"
          },
          "name": {
            "description": "Category name",
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "name"
        ],
        "type": "object"
      },
      "DocumentCreateRequest": {
        "description": "Document creation request serializer.",
        "properties": {
          "content": {
            "description": "Document content",
            "maxLength": 1000000,
            "minLength": 10,
            "type": "string"
          },
          "file_type": {
            "default": "text/plain",
            "description": "MIME type",
            "minLength": 1,
            "pattern": "^[a-z]+/[a-z0-9\\-\\+\\.]+$",
            "type": "string"
          },
          "metadata": {
            "description": "Additional metadata"
          },
          "title": {
            "description": "Document title",
            "maxLength": 512,
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
      "DocumentProcessingStatus": {
        "description": "Document processing status serializer.",
        "properties": {
          "error": {
            "nullable": true,
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "type": "string"
          },
          "processing_time_seconds": {
            "format": "double",
            "nullable": true,
            "type": "number"
          },
          "progress": {},
          "status": {
            "type": "string"
          }
        },
        "required": [
          "id",
          "progress",
          "status"
        ],
        "type": "object"
      },
      "DocumentRequest": {
        "description": "Document response serializer.",
        "properties": {
          "file_size": {
            "description": "Original file size in bytes",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "file_type": {
            "description": "MIME type of original file",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          },
          "metadata": {
            "description": "Additional document metadata",
            "nullable": true
          },
          "title": {
            "description": "Document title",
            "maxLength": 512,
            "minLength": 1,
            "type": "string"
          }
        },
        "required": [
          "title"
        ],
        "type": "object"
      },
      "DocumentStats": {
        "description": "Document processing statistics serializer.",
        "properties": {
          "avg_processing_time_seconds": {
            "format": "double",
            "type": "number"
          },
          "completed_documents": {
            "type": "integer"
          },
          "processing_success_rate": {
            "format": "double",
            "type": "number"
          },
          "total_chunks": {
            "type": "integer"
          },
          "total_cost_usd": {
            "format": "double",
            "type": "number"
          },
          "total_documents": {
            "type": "integer"
          },
          "total_tokens": {
            "type": "integer"
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
      "Endpoint": {
        "description": "Serializer for single endpoint status.",
        "properties": {
          "error": {
            "description": "Error message if check failed",
            "type": "string"
          },
          "error_type": {
            "description": "Error type: database, general, etc.",
            "type": "string"
          },
          "group": {
            "description": "URL group (up to 3 depth)",
            "type": "string"
          },
          "has_parameters": {
            "default": false,
            "description": "Whether URL has parameters that were resolved with test values",
            "type": "boolean"
          },
          "is_healthy": {
            "description": "Whether endpoint is healthy",
            "nullable": true,
            "type": "boolean"
          },
          "last_checked": {
            "description": "Timestamp of last check",
            "format": "date-time",
            "nullable": true,
            "type": "string"
          },
          "namespace": {
            "description": "URL namespace",
            "type": "string"
          },
          "rate_limited": {
            "default": false,
            "description": "Whether endpoint returned 429 (rate limited)",
            "type": "boolean"
          },
          "reason": {
            "description": "Reason for warning/skip",
            "type": "string"
          },
          "required_auth": {
            "default": false,
            "description": "Whether endpoint required JWT authentication",
            "type": "boolean"
          },
          "response_time_ms": {
            "description": "Response time in milliseconds",
            "format": "double",
            "nullable": true,
            "type": "number"
          },
          "status": {
            "description": "Status: healthy, unhealthy, warning, error, skipped, pending",
            "type": "string"
          },
          "status_code": {
            "description": "HTTP status code",
            "nullable": true,
            "type": "integer"
          },
          "url": {
            "description": "Resolved URL (for parametrized URLs) or URL pattern",
            "type": "string"
          },
          "url_name": {
            "description": "Django URL name (if available)",
            "nullable": true,
            "type": "string"
          },
          "url_pattern": {
            "description": "Original URL pattern (for parametrized URLs)",
            "nullable": true,
            "type": "string"
          },
          "view": {
            "description": "View function/class name",
            "type": "string"
          }
        },
        "required": [
          "group",
          "status",
          "url"
        ],
        "type": "object"
      },
      "EndpointsStatus": {
        "description": "Serializer for overall endpoints status response.",
        "properties": {
          "endpoints": {
            "description": "List of all endpoints with their status",
            "items": {
              "$ref": "#/components/schemas/Endpoint"
            },
            "type": "array"
          },
          "errors": {
            "description": "Number of endpoints with errors",
            "type": "integer"
          },
          "healthy": {
            "description": "Number of healthy endpoints",
            "type": "integer"
          },
          "skipped": {
            "description": "Number of skipped endpoints",
            "type": "integer"
          },
          "status": {
            "description": "Overall status: healthy, degraded, or unhealthy",
            "type": "string"
          },
          "timestamp": {
            "description": "Timestamp of the check",
            "format": "date-time",
            "type": "string"
          },
          "total_endpoints": {
            "description": "Total number of endpoints checked",
            "type": "integer"
          },
          "unhealthy": {
            "description": "Number of unhealthy endpoints",
            "type": "integer"
          },
          "warnings": {
            "description": "Number of endpoints with warnings",
            "type": "integer"
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
      "HealthCheck": {
        "description": "Health check response.",
        "properties": {
          "has_api_key": {
            "description": "Whether API key is configured",
            "title": "Has Api Key",
            "type": "boolean"
          },
          "status": {
            "description": "Health status: healthy or unhealthy",
            "title": "Status",
            "type": "string"
          },
          "timestamp": {
            "description": "Current timestamp",
            "title": "Timestamp",
            "type": "string"
          },
          "wrapper_url": {
            "description": "Configured wrapper URL",
            "title": "Wrapper Url",
            "type": "string"
          }
        },
        "required": [
          "status",
          "wrapper_url",
          "has_api_key",
          "timestamp"
        ],
        "title": "HealthCheckSerializer",
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
      "ManualAckRequestRequest": {
        "description": "Request model for manual ACK sending.",
        "properties": {
          "client_id": {
            "description": "Client ID sending the ACK",
            "title": "Client Id",
            "type": "string"
          },
          "message_id": {
            "description": "Message ID to acknowledge",
            "title": "Message Id",
            "type": "string"
          }
        },
        "required": [
          "message_id",
          "client_id"
        ],
        "title": "ManualAckRequest",
        "type": "object"
      },
      "ManualAckResponse": {
        "description": "Response model for manual ACK.",
        "properties": {
          "error": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Error message if failed",
            "title": "Error"
          },
          "message_id": {
            "description": "Message ID that was acknowledged",
            "title": "Message Id",
            "type": "string"
          },
          "success": {
            "description": "Whether ACK was sent successfully",
            "title": "Success",
            "type": "boolean"
          }
        },
        "required": [
          "success",
          "message_id"
        ],
        "title": "ManualAckResponse",
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
      "OverviewStats": {
        "description": "Overview statistics for Centrifugo publishes.",
        "properties": {
          "avg_acks_received": {
            "description": "Average ACKs received",
            "title": "Avg Acks Received",
            "type": "number"
          },
          "avg_duration_ms": {
            "description": "Average duration in milliseconds",
            "title": "Avg Duration Ms",
            "type": "number"
          },
          "failed": {
            "description": "Failed publishes",
            "title": "Failed",
            "type": "integer"
          },
          "period_hours": {
            "description": "Statistics period in hours",
            "title": "Period Hours",
            "type": "integer"
          },
          "success_rate": {
            "description": "Success rate percentage",
            "title": "Success Rate",
            "type": "number"
          },
          "successful": {
            "description": "Successful publishes",
            "title": "Successful",
            "type": "integer"
          },
          "timeout": {
            "description": "Timeout publishes",
            "title": "Timeout",
            "type": "integer"
          },
          "total": {
            "description": "Total publishes in period",
            "title": "Total",
            "type": "integer"
          }
        },
        "required": [
          "total",
          "successful",
          "failed",
          "timeout",
          "success_rate",
          "avg_duration_ms",
          "avg_acks_received",
          "period_hours"
        ],
        "title": "OverviewStatsSerializer",
        "type": "object"
      },
      "PaginatedArchiveItemChunkList": {
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
              "$ref": "#/components/schemas/ArchiveItemChunk"
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
      "PaginatedArchiveItemList": {
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
              "$ref": "#/components/schemas/ArchiveItem"
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
      "PaginatedArchiveSearchResultList": {
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
              "$ref": "#/components/schemas/ArchiveSearchResult"
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
      "PaginatedChatResponseList": {
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
              "$ref": "#/components/schemas/ChatResponse"
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
      "PaginatedChatSessionList": {
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
              "$ref": "#/components/schemas/ChatSession"
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
      "PaginatedDocumentArchiveListList": {
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
              "$ref": "#/components/schemas/DocumentArchiveList"
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
      "PaginatedDocumentList": {
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
              "$ref": "#/components/schemas/Document"
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
      "PaginatedMessageList": {
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
              "$ref": "#/components/schemas/Message"
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
      "PaginatedPublicCategoryList": {
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
              "$ref": "#/components/schemas/PublicCategory"
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
      "PaginatedPublicDocumentListList": {
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
              "$ref": "#/components/schemas/PublicDocumentList"
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
      "PaginatedTicketList": {
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
              "$ref": "#/components/schemas/Ticket"
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
      "PatchedArchiveItemChunkRequest": {
        "description": "Archive item chunk serializer.",
        "properties": {
          "chunk_index": {
            "description": "Sequential chunk number within item",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "chunk_type": {
            "description": "Type of content in chunk\n\n* `text` - Text\n* `code` - Code\n* `heading` - Heading\n* `metadata` - Metadata\n* `table` - Table\n* `list` - List",
            "enum": [
              "text",
              "code",
              "heading",
              "metadata",
              "table",
              "list"
            ],
            "type": "string",
            "x-spec-enum-id": "660846bb1567d97b"
          },
          "content": {
            "description": "Chunk text content",
            "minLength": 1,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PatchedArchiveItemRequest": {
        "description": "Archive item serializer.",
        "properties": {
          "file_size": {
            "description": "Item size in bytes",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "item_name": {
            "description": "Item name",
            "maxLength": 255,
            "minLength": 1,
            "type": "string"
          },
          "item_type": {
            "description": "MIME type",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          },
          "relative_path": {
            "description": "Path within archive",
            "maxLength": 1024,
            "minLength": 1,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PatchedChatResponseRequest": {
        "description": "Chat response serializer.",
        "properties": {
          "content": {
            "minLength": 1,
            "type": "string"
          },
          "cost_usd": {
            "format": "double",
            "type": "number"
          },
          "message_id": {
            "format": "uuid",
            "type": "string"
          },
          "model_used": {
            "minLength": 1,
            "type": "string"
          },
          "processing_time_ms": {
            "type": "integer"
          },
          "sources": {
            "items": {
              "$ref": "#/components/schemas/ChatSourceRequest"
            },
            "nullable": true,
            "type": "array"
          },
          "tokens_used": {
            "type": "integer"
          }
        },
        "type": "object"
      },
      "PatchedChatSessionRequest": {
        "description": "Chat session response serializer.",
        "properties": {
          "is_active": {
            "description": "Whether session accepts new messages",
            "type": "boolean"
          },
          "max_context_chunks": {
            "description": "Maximum chunks to include in context",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "messages_count": {
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "model_name": {
            "description": "LLM model used for this session",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          },
          "temperature": {
            "description": "Temperature setting for LLM",
            "format": "double",
            "type": "number"
          },
          "title": {
            "description": "Session title (auto-generated if empty)",
            "maxLength": 255,
            "type": "string"
          },
          "total_tokens_used": {
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          }
        },
        "type": "object"
      },
      "PatchedDocumentArchiveRequest": {
        "description": "Document archive serializer.",
        "properties": {
          "description": {
            "description": "Archive description",
            "type": "string"
          },
          "is_public": {
            "description": "Whether this archive is publicly accessible",
            "type": "boolean"
          },
          "title": {
            "description": "Archive title",
            "maxLength": 512,
            "minLength": 1,
            "type": "string"
          }
        },
        "type": "object"
      },
      "PatchedDocumentRequest": {
        "description": "Document response serializer.",
        "properties": {
          "file_size": {
            "description": "Original file size in bytes",
            "maximum": 2147483647,
            "minimum": 0,
            "type": "integer"
          },
          "file_type": {
            "description": "MIME type of original file",
            "maxLength": 100,
            "minLength": 1,
            "type": "string"
          },
          "metadata": {
            "description": "Additional document metadata",
            "nullable": true
          },
          "title": {
            "description": "Document title",
            "maxLength": 512,
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
      "PaymentDetail": {
        "description": "Detailed payment information.",
        "properties": {
          "actual_amount": {
            "description": "Actual amount received in cryptocurrency",
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "readOnly": true,
            "type": "string"
          },
          "actual_amount_usd": {
            "description": "Actual amount received in USD",
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "amount_usd": {
            "description": "Payment amount in USD",
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
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
          "currency_code": {
            "readOnly": true,
            "type": "string"
          },
          "currency_name": {
            "readOnly": true,
            "type": "string"
          },
          "currency_network": {
            "readOnly": true,
            "type": "string"
          },
          "currency_token": {
            "readOnly": true,
            "type": "string"
          },
          "description": {
            "description": "Payment description",
            "readOnly": true,
            "type": "string"
          },
          "expires_at": {
            "description": "When this payment expires (typically 30 minutes)",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "explorer_link": {
            "description": "Get blockchain explorer link.",
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
          "internal_payment_id": {
            "description": "Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID)",
            "readOnly": true,
            "type": "string"
          },
          "is_completed": {
            "readOnly": true,
            "type": "boolean"
          },
          "is_expired": {
            "readOnly": true,
            "type": "boolean"
          },
          "is_failed": {
            "readOnly": true,
            "type": "boolean"
          },
          "pay_address": {
            "description": "Cryptocurrency payment address",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "pay_amount": {
            "description": "Amount to pay in cryptocurrency",
            "format": "decimal",
            "nullable": true,
            "pattern": "^-?\\d{0,12}(?:\\.\\d{0,8})?$",
            "readOnly": true,
            "type": "string"
          },
          "payment_url": {
            "description": "Payment page URL (if provided by provider)",
            "format": "uri",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "qr_code_url": {
            "description": "Get QR code URL.",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "status": {
            "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `partially_paid` - Partially Paid\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled",
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
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "a2aa9a45c3061ad0"
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
        ],
        "type": "object"
      },
      "PaymentList": {
        "description": "Payment list item (lighter than detail).",
        "properties": {
          "amount_usd": {
            "description": "Payment amount in USD",
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "completed_at": {
            "description": "When this payment was completed",
            "format": "date-time",
            "nullable": true,
            "readOnly": true,
            "type": "string"
          },
          "created_at": {
            "description": "When this record was created",
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "currency_code": {
            "readOnly": true,
            "type": "string"
          },
          "currency_token": {
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "description": "Unique identifier for this record",
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "internal_payment_id": {
            "description": "Internal payment identifier (PAY_YYYYMMDDHHMMSS_UUID)",
            "readOnly": true,
            "type": "string"
          },
          "status": {
            "description": "Current payment status\n\n* `pending` - Pending\n* `confirming` - Confirming\n* `confirmed` - Confirmed\n* `completed` - Completed\n* `partially_paid` - Partially Paid\n* `failed` - Failed\n* `expired` - Expired\n* `cancelled` - Cancelled",
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
            "readOnly": true,
            "type": "string",
            "x-spec-enum-id": "a2aa9a45c3061ad0"
          },
          "status_display": {
            "readOnly": true,
            "type": "string"
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
        ],
        "type": "object"
      },
      "PublicCategory": {
        "description": "Public category serializer.",
        "properties": {
          "description": {
            "description": "Category description",
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "name": {
            "description": "Category name",
            "maxLength": 255,
            "type": "string"
          }
        },
        "required": [
          "id",
          "name"
        ],
        "type": "object"
      },
      "PublicDocument": {
        "description": "Public document detail serializer - only essential data for clients.",
        "properties": {
          "category": {
            "allOf": [
              {
                "$ref": "#/components/schemas/PublicCategory"
              }
            ],
            "readOnly": true
          },
          "content": {
            "description": "Full document content",
            "type": "string"
          },
          "created_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          },
          "id": {
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "title": {
            "description": "Document title",
            "maxLength": 512,
            "type": "string"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "category",
          "content",
          "created_at",
          "id",
          "title",
          "updated_at"
        ],
        "type": "object"
      },
      "PublicDocumentList": {
        "description": "Public document list serializer - minimal fields for listing.",
        "properties": {
          "category": {
            "allOf": [
              {
                "$ref": "#/components/schemas/PublicCategory"
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
            "format": "uuid",
            "readOnly": true,
            "type": "string"
          },
          "title": {
            "description": "Document title",
            "maxLength": 512,
            "type": "string"
          },
          "updated_at": {
            "format": "date-time",
            "readOnly": true,
            "type": "string"
          }
        },
        "required": [
          "category",
          "created_at",
          "id",
          "title",
          "updated_at"
        ],
        "type": "object"
      },
      "PublishTestRequestRequest": {
        "description": "Request model for test message publishing.",
        "properties": {
          "ack_timeout": {
            "default": 10,
            "description": "ACK timeout in seconds",
            "maximum": 60,
            "minimum": 1,
            "title": "Ack Timeout",
            "type": "integer"
          },
          "channel": {
            "description": "Target channel name",
            "title": "Channel",
            "type": "string"
          },
          "data": {
            "additionalProperties": true,
            "description": "Message data (any JSON object)",
            "title": "Data",
            "type": "object"
          },
          "wait_for_ack": {
            "default": false,
            "description": "Wait for client acknowledgment",
            "title": "Wait For Ack",
            "type": "boolean"
          }
        },
        "required": [
          "channel",
          "data"
        ],
        "title": "PublishTestRequest",
        "type": "object"
      },
      "PublishTestResponse": {
        "description": "Response model for test message publishing.",
        "properties": {
          "acks_received": {
            "default": 0,
            "description": "Number of ACKs received",
            "title": "Acks Received",
            "type": "integer"
          },
          "channel": {
            "description": "Target channel",
            "title": "Channel",
            "type": "string"
          },
          "delivered": {
            "default": false,
            "description": "Whether message was delivered",
            "title": "Delivered",
            "type": "boolean"
          },
          "error": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "default": null,
            "description": "Error message if failed",
            "title": "Error"
          },
          "message_id": {
            "description": "Unique message ID",
            "title": "Message Id",
            "type": "string"
          },
          "success": {
            "description": "Whether publish succeeded",
            "title": "Success",
            "type": "boolean"
          }
        },
        "required": [
          "success",
          "message_id",
          "channel"
        ],
        "title": "PublishTestResponse",
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
      "QuickAction": {
        "description": "Serializer for quick action buttons.\n\nMaps to QuickAction Pydantic model.",
        "properties": {
          "category": {
            "default": "general",
            "description": "Action category",
            "type": "string"
          },
          "color": {
            "default": "primary",
            "description": "Button color theme\n\n* `primary` - primary\n* `success` - success\n* `warning` - warning\n* `danger` - danger\n* `secondary` - secondary",
            "enum": [
              "primary",
              "success",
              "warning",
              "danger",
              "secondary"
            ],
            "type": "string",
            "x-spec-enum-id": "6400710d5b71d6b0"
          },
          "description": {
            "description": "Action description",
            "type": "string"
          },
          "icon": {
            "description": "Material icon name",
            "type": "string"
          },
          "link": {
            "description": "Action URL",
            "type": "string"
          },
          "title": {
            "description": "Action title",
            "type": "string"
          }
        },
        "required": [
          "description",
          "icon",
          "link",
          "title"
        ],
        "type": "object"
      },
      "QuickHealth": {
        "description": "Serializer for quick health check response.",
        "properties": {
          "error": {
            "description": "Error message if health check failed",
            "type": "string"
          },
          "status": {
            "description": "Quick health status: ok or error",
            "type": "string"
          },
          "timestamp": {
            "description": "Timestamp of the health check",
            "format": "date-time",
            "type": "string"
          }
        },
        "required": [
          "status",
          "timestamp"
        ],
        "type": "object"
      },
      "RecentPublishes": {
        "description": "Recent publishes list.",
        "properties": {
          "count": {
            "description": "Number of publishes returned",
            "title": "Count",
            "type": "integer"
          },
          "has_more": {
            "default": false,
            "description": "Whether more results are available",
            "title": "Has More",
            "type": "boolean"
          },
          "offset": {
            "default": 0,
            "description": "Current offset for pagination",
            "title": "Offset",
            "type": "integer"
          },
          "publishes": {
            "description": "List of recent publishes",
            "items": {
              "additionalProperties": true,
              "type": "object"
            },
            "title": "Publishes",
            "type": "array"
          },
          "total_available": {
            "description": "Total publishes available",
            "title": "Total Available",
            "type": "integer"
          }
        },
        "required": [
          "publishes",
          "count",
          "total_available"
        ],
        "title": "RecentPublishesSerializer",
        "type": "object"
      },
      "RecentUser": {
        "description": "Recent user serializer.",
        "properties": {
          "date_joined": {
            "type": "string"
          },
          "email": {
            "format": "email",
            "type": "string"
          },
          "id": {
            "type": "integer"
          },
          "is_active": {
            "type": "boolean"
          },
          "is_staff": {
            "type": "boolean"
          },
          "is_superuser": {
            "type": "boolean"
          },
          "last_login": {
            "nullable": true,
            "type": "string"
          },
          "username": {
            "type": "string"
          }
        },
        "required": [
          "date_joined",
          "email",
          "id",
          "is_active",
          "is_staff",
          "is_superuser",
          "last_login",
          "username"
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
      "StatCard": {
        "description": "Serializer for dashboard statistics cards.\n\nMaps to StatCard Pydantic model.",
        "properties": {
          "change": {
            "description": "Change indicator (e.g., \u0027+12%\u0027)",
            "nullable": true,
            "type": "string"
          },
          "change_type": {
            "default": "neutral",
            "description": "Change type\n\n* `positive` - positive\n* `negative` - negative\n* `neutral` - neutral",
            "enum": [
              "positive",
              "negative",
              "neutral"
            ],
            "type": "string",
            "x-spec-enum-id": "b21c1f8e6042dbef"
          },
          "color": {
            "default": "primary",
            "description": "Card color theme",
            "type": "string"
          },
          "description": {
            "description": "Additional description",
            "nullable": true,
            "type": "string"
          },
          "icon": {
            "description": "Material icon name",
            "type": "string"
          },
          "title": {
            "description": "Card title",
            "type": "string"
          },
          "value": {
            "description": "Main value to display",
            "type": "string"
          }
        },
        "required": [
          "icon",
          "title",
          "value"
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
      "SystemHealth": {
        "description": "Serializer for overall system health status.",
        "properties": {
          "components": {
            "description": "Health status of individual components",
            "items": {
              "$ref": "#/components/schemas/SystemHealthItem"
            },
            "type": "array"
          },
          "overall_health_percentage": {
            "description": "Overall health percentage",
            "maximum": 100,
            "minimum": 0,
            "type": "integer"
          },
          "overall_status": {
            "description": "Overall system health status\n\n* `healthy` - healthy\n* `warning` - warning\n* `error` - error\n* `unknown` - unknown",
            "enum": [
              "healthy",
              "warning",
              "error",
              "unknown"
            ],
            "type": "string",
            "x-spec-enum-id": "4a4719b6db2b089e"
          },
          "timestamp": {
            "description": "Check timestamp (ISO format)",
            "type": "string"
          }
        },
        "required": [
          "components",
          "overall_health_percentage",
          "overall_status",
          "timestamp"
        ],
        "type": "object"
      },
      "SystemHealthItem": {
        "description": "Serializer for system health status items.\n\nMaps to SystemHealthItem Pydantic model.",
        "properties": {
          "component": {
            "description": "Component name",
            "type": "string"
          },
          "description": {
            "description": "Status description",
            "type": "string"
          },
          "health_percentage": {
            "description": "Health percentage (0-100)",
            "maximum": 100,
            "minimum": 0,
            "nullable": true,
            "type": "integer"
          },
          "last_check": {
            "description": "Last check time (ISO format)",
            "type": "string"
          },
          "status": {
            "description": "Health status\n\n* `healthy` - healthy\n* `warning` - warning\n* `error` - error\n* `unknown` - unknown",
            "enum": [
              "healthy",
              "warning",
              "error",
              "unknown"
            ],
            "type": "string",
            "x-spec-enum-id": "4a4719b6db2b089e"
          }
        },
        "required": [
          "component",
          "description",
          "last_check",
          "status"
        ],
        "type": "object"
      },
      "SystemMetrics": {
        "description": "Serializer for system performance metrics.",
        "properties": {
          "cpu_usage": {
            "description": "CPU usage percentage",
            "format": "double",
            "type": "number"
          },
          "disk_usage": {
            "description": "Disk usage percentage",
            "format": "double",
            "type": "number"
          },
          "memory_usage": {
            "description": "Memory usage percentage",
            "format": "double",
            "type": "number"
          },
          "network_in": {
            "description": "Network incoming bandwidth",
            "type": "string"
          },
          "network_out": {
            "description": "Network outgoing bandwidth",
            "type": "string"
          },
          "response_time": {
            "description": "Average response time",
            "type": "string"
          },
          "uptime": {
            "description": "System uptime",
            "type": "string"
          }
        },
        "required": [
          "cpu_usage",
          "disk_usage",
          "memory_usage",
          "network_in",
          "network_out",
          "response_time",
          "uptime"
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
        "description": "Transaction serializer.",
        "properties": {
          "amount_display": {
            "readOnly": true,
            "type": "string"
          },
          "amount_usd": {
            "description": "Transaction amount in USD (positive=credit, negative=debit)",
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
          },
          "balance_after": {
            "description": "User balance after this transaction",
            "format": "decimal",
            "pattern": "^-?\\d{0,8}(?:\\.\\d{0,2})?$",
            "readOnly": true,
            "type": "string"
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
          "type_display": {
            "readOnly": true,
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
          "payment_id",
          "transaction_type",
          "type_display"
        ],
        "type": "object"
      },
      "URLPattern": {
        "description": "Serializer for single URL pattern.",
        "properties": {
          "full_name": {
            "description": "Full URL name with namespace (e.g., admin:index)",
            "nullable": true,
            "type": "string"
          },
          "methods": {
            "description": "Allowed HTTP methods",
            "items": {
              "type": "string"
            },
            "type": "array"
          },
          "module": {
            "description": "View module path",
            "nullable": true,
            "type": "string"
          },
          "name": {
            "description": "URL name (if defined)",
            "nullable": true,
            "type": "string"
          },
          "namespace": {
            "description": "URL namespace",
            "nullable": true,
            "type": "string"
          },
          "pattern": {
            "description": "URL pattern (e.g., ^api/users/(?P\u003cpk\u003e[^/.]+)/$)",
            "type": "string"
          },
          "view": {
            "description": "View function/class name",
            "nullable": true,
            "type": "string"
          },
          "view_class": {
            "description": "View class name (for CBV/ViewSets)",
            "nullable": true,
            "type": "string"
          }
        },
        "required": [
          "pattern"
        ],
        "type": "object"
      },
      "URLsList": {
        "description": "Serializer for URLs list response.",
        "properties": {
          "base_url": {
            "description": "Base URL of the service",
            "type": "string"
          },
          "service": {
            "description": "Service name",
            "type": "string"
          },
          "status": {
            "description": "Status: success or error",
            "type": "string"
          },
          "total_urls": {
            "description": "Total number of registered URLs",
            "type": "integer"
          },
          "urls": {
            "description": "List of all registered URL patterns",
            "items": {
              "$ref": "#/components/schemas/URLPattern"
            },
            "type": "array"
          },
          "version": {
            "description": "Django-CFG version",
            "type": "string"
          }
        },
        "required": [
          "base_url",
          "service",
          "status",
          "total_urls",
          "urls",
          "version"
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
            "readOnly": true,
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
      "UserStatistics": {
        "description": "Serializer for user statistics.",
        "properties": {
          "active_users": {
            "description": "Active users (last 30 days)",
            "type": "integer"
          },
          "new_users": {
            "description": "New users (last 7 days)",
            "type": "integer"
          },
          "superusers": {
            "description": "Number of superusers",
            "type": "integer"
          },
          "total_users": {
            "description": "Total number of users",
            "type": "integer"
          }
        },
        "required": [
          "active_users",
          "new_users",
          "superusers",
          "total_users"
        ],
        "type": "object"
      },
      "VectorizationResult": {
        "description": "Vectorization result serializer.",
        "properties": {
          "errors": {
            "items": {
              "type": "string"
            },
            "readOnly": true,
            "type": "array"
          },
          "failed_count": {
            "readOnly": true,
            "type": "integer"
          },
          "success_rate": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "total_cost": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "total_tokens": {
            "readOnly": true,
            "type": "integer"
          },
          "vectorized_count": {
            "readOnly": true,
            "type": "integer"
          }
        },
        "required": [
          "errors",
          "failed_count",
          "success_rate",
          "total_cost",
          "total_tokens",
          "vectorized_count"
        ],
        "type": "object"
      },
      "VectorizationStatistics": {
        "description": "Vectorization statistics serializer.",
        "properties": {
          "avg_cost_per_chunk": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "avg_tokens_per_chunk": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "pending_chunks": {
            "readOnly": true,
            "type": "integer"
          },
          "total_chunks": {
            "readOnly": true,
            "type": "integer"
          },
          "total_cost": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "total_tokens": {
            "readOnly": true,
            "type": "integer"
          },
          "vectorization_rate": {
            "format": "double",
            "readOnly": true,
            "type": "number"
          },
          "vectorized_chunks": {
            "readOnly": true,
            "type": "integer"
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
        "django_cfg_accounts",
        "django_cfg_knowbase",
        "django_cfg_support",
        "django_cfg_newsletter",
        "django_cfg_leads",
        "django_cfg_agents",
        "tasks",
        "payments",
        "django_cfg_centrifugo"
      ],
      "generator": "django-client",
      "generator_version": "1.0.0",
      "group": "cfg"
    }
  },
  "openapi": "3.0.3",
  "paths": {
    "/cfg/accounts/otp/request/": {
      "post": {
        "description": "Request OTP code to email or phone.",
        "operationId": "cfg_accounts_otp_request_create",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "accounts"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/accounts/otp/verify/": {
      "post": {
        "description": "Verify OTP code and return JWT tokens.",
        "operationId": "cfg_accounts_otp_verify_create",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "accounts"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/accounts/profile/": {
      "get": {
        "description": "Retrieve the current authenticated user\u0027s profile information.",
        "operationId": "cfg_accounts_profile_retrieve",
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
            "jwtAuth": []
          }
        ],
        "summary": "Get current user profile",
        "tags": [
          "User Profile"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/accounts/profile/avatar/": {
      "post": {
        "description": "Upload avatar image for the current authenticated user. Accepts multipart/form-data with \u0027avatar\u0027 field.",
        "operationId": "cfg_accounts_profile_avatar_create",
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
            "jwtAuth": []
          }
        ],
        "summary": "Upload user avatar",
        "tags": [
          "User Profile"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/accounts/profile/partial/": {
      "patch": {
        "description": "Partially update the current authenticated user\u0027s profile information. Supports avatar upload.",
        "operationId": "cfg_accounts_profile_partial_partial_update",
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
            "jwtAuth": []
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
        "operationId": "cfg_accounts_profile_partial_update",
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
            "jwtAuth": []
          }
        ],
        "summary": "Partial update user profile",
        "tags": [
          "User Profile"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/accounts/profile/update/": {
      "patch": {
        "description": "Update the current authenticated user\u0027s profile information.",
        "operationId": "cfg_accounts_profile_update_partial_update",
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
            "jwtAuth": []
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
        "operationId": "cfg_accounts_profile_update_update",
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
            "jwtAuth": []
          }
        ],
        "summary": "Update user profile",
        "tags": [
          "User Profile"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/accounts/token/refresh/": {
      "post": {
        "description": "Refresh JWT token.",
        "operationId": "cfg_accounts_token_refresh_create",
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
    "/cfg/centrifugo/admin/api/monitor/channels/": {
      "get": {
        "description": "Get statistics per channel.",
        "operationId": "cfg_centrifugo_admin_api_monitor_channels_retrieve",
        "responses": {
          "200": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "centrifugo"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/monitor/health/": {
      "get": {
        "description": "Returns the current health status of the Centrifugo client.",
        "operationId": "cfg_centrifugo_admin_api_monitor_health_retrieve",
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
          },
          "503": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Service unavailable"
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
        "summary": "Get Centrifugo health status",
        "tags": [
          "Centrifugo Monitoring"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/monitor/overview/": {
      "get": {
        "description": "Returns overview statistics for Centrifugo publishes.",
        "operationId": "cfg_centrifugo_admin_api_monitor_overview_retrieve",
        "parameters": [
          {
            "description": "Statistics period in hours (default: 24)",
            "in": "query",
            "name": "hours",
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
                  "$ref": "#/components/schemas/OverviewStats"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid parameters"
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
        "summary": "Get overview statistics",
        "tags": [
          "Centrifugo Monitoring"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/monitor/publishes/": {
      "get": {
        "description": "Returns a list of recent Centrifugo publishes with their details.",
        "operationId": "cfg_centrifugo_admin_api_monitor_publishes_retrieve",
        "parameters": [
          {
            "description": "Filter by channel name",
            "in": "query",
            "name": "channel",
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "Number of publishes to return (default: 50, max: 200)",
            "in": "query",
            "name": "count",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Offset for pagination (default: 0)",
            "in": "query",
            "name": "offset",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Filter by status (success, failed, timeout, pending, partial)",
            "in": "query",
            "name": "status",
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
                  "$ref": "#/components/schemas/RecentPublishes"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid parameters"
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
        "summary": "Get recent publishes",
        "tags": [
          "Centrifugo Monitoring"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/monitor/timeline/": {
      "get": {
        "description": "Returns statistics grouped by channel.",
        "operationId": "cfg_centrifugo_admin_api_monitor_timeline_retrieve",
        "parameters": [
          {
            "description": "Statistics period in hours (default: 24)",
            "in": "query",
            "name": "hours",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Time interval: \u0027hour\u0027 or \u0027day\u0027 (default: hour)",
            "in": "query",
            "name": "interval",
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
                  "$ref": "#/components/schemas/ChannelList"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid parameters"
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
        "summary": "Get channel statistics",
        "tags": [
          "Centrifugo Monitoring"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/server/auth/token/": {
      "post": {
        "description": "Returns JWT token and config for WebSocket connection to Centrifugo.",
        "operationId": "cfg_centrifugo_admin_api_server_auth_token_create",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "properties": {
                    "config": {
                      "properties": {
                        "centrifugo_url": {
                          "type": "string"
                        },
                        "expires_at": {
                          "type": "string"
                        }
                      },
                      "type": "object"
                    },
                    "token": {
                      "type": "string"
                    }
                  },
                  "type": "object"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Centrifugo not configured"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get connection token for dashboard",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/server/channels/": {
      "post": {
        "description": "Returns list of active channels with optional pattern filter.",
        "operationId": "cfg_centrifugo_admin_api_server_channels_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoChannelsRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoChannelsRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoChannelsRequestRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CentrifugoChannelsResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "List active channels",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/server/history/": {
      "post": {
        "description": "Returns message history for a channel.",
        "operationId": "cfg_centrifugo_admin_api_server_history_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoHistoryRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoHistoryRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoHistoryRequestRequest"
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
                  "$ref": "#/components/schemas/CentrifugoHistoryResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get channel history",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/server/info/": {
      "post": {
        "description": "Returns server information including node count, version, and uptime.",
        "operationId": "cfg_centrifugo_admin_api_server_info_create",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CentrifugoInfoResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get Centrifugo server info",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/server/presence-stats/": {
      "post": {
        "description": "Returns quick statistics about channel presence (num_clients, num_users).",
        "operationId": "cfg_centrifugo_admin_api_server_presence_stats_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceStatsRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceStatsRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceStatsRequestRequest"
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
                  "$ref": "#/components/schemas/CentrifugoPresenceStatsResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get channel presence statistics",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/server/presence/": {
      "post": {
        "description": "Returns list of clients currently subscribed to a channel.",
        "operationId": "cfg_centrifugo_admin_api_server_presence_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceRequestRequest"
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
                  "$ref": "#/components/schemas/CentrifugoPresenceResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get channel presence",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/testing/connection-token/": {
      "post": {
        "description": "Generate JWT token for WebSocket connection to Centrifugo.",
        "operationId": "cfg_centrifugo_admin_api_testing_connection_token_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ConnectionTokenRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/ConnectionTokenRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/ConnectionTokenRequestRequest"
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
                  "$ref": "#/components/schemas/ConnectionTokenResponse"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid request"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Generate connection token",
        "tags": [
          "Centrifugo Testing"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/testing/publish-test/": {
      "post": {
        "description": "Publish test message to Centrifugo via wrapper with optional ACK tracking.",
        "operationId": "cfg_centrifugo_admin_api_testing_publish_test_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
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
                  "$ref": "#/components/schemas/PublishTestResponse"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid request"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Publish test message",
        "tags": [
          "Centrifugo Testing"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/testing/publish-with-logging/": {
      "post": {
        "description": "Publish message using CentrifugoClient with database logging. This will create CentrifugoLog records.",
        "operationId": "cfg_centrifugo_admin_api_testing_publish_with_logging_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
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
                  "$ref": "#/components/schemas/PublishTestResponse"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid request"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Publish with database logging",
        "tags": [
          "Centrifugo Testing"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/admin/api/testing/send-ack/": {
      "post": {
        "description": "Manually send ACK for a message to the wrapper. Pass message_id in request body.",
        "operationId": "cfg_centrifugo_admin_api_testing_send_ack_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ManualAckRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/ManualAckRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/ManualAckRequestRequest"
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
                  "$ref": "#/components/schemas/ManualAckResponse"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid request"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Send manual ACK",
        "tags": [
          "Centrifugo Testing"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/monitor/channels/": {
      "get": {
        "description": "Get statistics per channel.",
        "operationId": "cfg_centrifugo_monitor_channels_retrieve",
        "responses": {
          "200": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "centrifugo"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/monitor/health/": {
      "get": {
        "description": "Returns the current health status of the Centrifugo client.",
        "operationId": "cfg_centrifugo_monitor_health_retrieve",
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
          },
          "503": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Service unavailable"
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
        "summary": "Get Centrifugo health status",
        "tags": [
          "Centrifugo Monitoring"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/monitor/overview/": {
      "get": {
        "description": "Returns overview statistics for Centrifugo publishes.",
        "operationId": "cfg_centrifugo_monitor_overview_retrieve",
        "parameters": [
          {
            "description": "Statistics period in hours (default: 24)",
            "in": "query",
            "name": "hours",
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
                  "$ref": "#/components/schemas/OverviewStats"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid parameters"
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
        "summary": "Get overview statistics",
        "tags": [
          "Centrifugo Monitoring"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/monitor/publishes/": {
      "get": {
        "description": "Returns a list of recent Centrifugo publishes with their details.",
        "operationId": "cfg_centrifugo_monitor_publishes_retrieve",
        "parameters": [
          {
            "description": "Filter by channel name",
            "in": "query",
            "name": "channel",
            "schema": {
              "type": "string"
            }
          },
          {
            "description": "Number of publishes to return (default: 50, max: 200)",
            "in": "query",
            "name": "count",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Offset for pagination (default: 0)",
            "in": "query",
            "name": "offset",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Filter by status (success, failed, timeout, pending, partial)",
            "in": "query",
            "name": "status",
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
                  "$ref": "#/components/schemas/RecentPublishes"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid parameters"
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
        "summary": "Get recent publishes",
        "tags": [
          "Centrifugo Monitoring"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/monitor/timeline/": {
      "get": {
        "description": "Returns statistics grouped by channel.",
        "operationId": "cfg_centrifugo_monitor_timeline_retrieve",
        "parameters": [
          {
            "description": "Statistics period in hours (default: 24)",
            "in": "query",
            "name": "hours",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Time interval: \u0027hour\u0027 or \u0027day\u0027 (default: hour)",
            "in": "query",
            "name": "interval",
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
                  "$ref": "#/components/schemas/ChannelList"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid parameters"
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
        "summary": "Get channel statistics",
        "tags": [
          "Centrifugo Monitoring"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/server/auth/token/": {
      "post": {
        "description": "Returns JWT token and config for WebSocket connection to Centrifugo.",
        "operationId": "cfg_centrifugo_server_auth_token_create",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "properties": {
                    "config": {
                      "properties": {
                        "centrifugo_url": {
                          "type": "string"
                        },
                        "expires_at": {
                          "type": "string"
                        }
                      },
                      "type": "object"
                    },
                    "token": {
                      "type": "string"
                    }
                  },
                  "type": "object"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Centrifugo not configured"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get connection token for dashboard",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/server/channels/": {
      "post": {
        "description": "Returns list of active channels with optional pattern filter.",
        "operationId": "cfg_centrifugo_server_channels_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoChannelsRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoChannelsRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoChannelsRequestRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CentrifugoChannelsResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "List active channels",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/server/history/": {
      "post": {
        "description": "Returns message history for a channel.",
        "operationId": "cfg_centrifugo_server_history_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoHistoryRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoHistoryRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoHistoryRequestRequest"
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
                  "$ref": "#/components/schemas/CentrifugoHistoryResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get channel history",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/server/info/": {
      "post": {
        "description": "Returns server information including node count, version, and uptime.",
        "operationId": "cfg_centrifugo_server_info_create",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CentrifugoInfoResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get Centrifugo server info",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/server/presence-stats/": {
      "post": {
        "description": "Returns quick statistics about channel presence (num_clients, num_users).",
        "operationId": "cfg_centrifugo_server_presence_stats_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceStatsRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceStatsRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceStatsRequestRequest"
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
                  "$ref": "#/components/schemas/CentrifugoPresenceStatsResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get channel presence statistics",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/server/presence/": {
      "post": {
        "description": "Returns list of clients currently subscribed to a channel.",
        "operationId": "cfg_centrifugo_server_presence_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/CentrifugoPresenceRequestRequest"
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
                  "$ref": "#/components/schemas/CentrifugoPresenceResponse"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Get channel presence",
        "tags": [
          "Centrifugo Admin API"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/testing/connection-token/": {
      "post": {
        "description": "Generate JWT token for WebSocket connection to Centrifugo.",
        "operationId": "cfg_centrifugo_testing_connection_token_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ConnectionTokenRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/ConnectionTokenRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/ConnectionTokenRequestRequest"
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
                  "$ref": "#/components/schemas/ConnectionTokenResponse"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid request"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Generate connection token",
        "tags": [
          "Centrifugo Testing"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/testing/publish-test/": {
      "post": {
        "description": "Publish test message to Centrifugo via wrapper with optional ACK tracking.",
        "operationId": "cfg_centrifugo_testing_publish_test_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
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
                  "$ref": "#/components/schemas/PublishTestResponse"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid request"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Publish test message",
        "tags": [
          "Centrifugo Testing"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/testing/publish-with-logging/": {
      "post": {
        "description": "Publish message using CentrifugoClient with database logging. This will create CentrifugoLog records.",
        "operationId": "cfg_centrifugo_testing_publish_with_logging_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PublishTestRequestRequest"
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
                  "$ref": "#/components/schemas/PublishTestResponse"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid request"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Publish with database logging",
        "tags": [
          "Centrifugo Testing"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/centrifugo/testing/send-ack/": {
      "post": {
        "description": "Manually send ACK for a message to the wrapper. Pass message_id in request body.",
        "operationId": "cfg_centrifugo_testing_send_ack_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ManualAckRequestRequest"
              }
            },
            "application/x-www-form-urlencoded": {
              "schema": {
                "$ref": "#/components/schemas/ManualAckRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/ManualAckRequestRequest"
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
                  "$ref": "#/components/schemas/ManualAckResponse"
                }
              }
            },
            "description": ""
          },
          "400": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Invalid request"
                }
              }
            },
            "description": ""
          },
          "500": {
            "content": {
              "application/json": {
                "schema": {
                  "description": "Server error"
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
        "summary": "Send manual ACK",
        "tags": [
          "Centrifugo Testing"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/activity/actions/": {
      "get": {
        "description": "Retrieve quick action buttons for dashboard",
        "operationId": "cfg_dashboard_api_activity_actions_list",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/QuickAction"
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
        "summary": "Get quick actions",
        "tags": [
          "Dashboard - Activity"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/activity/recent/": {
      "get": {
        "description": "Retrieve recent system activity entries",
        "operationId": "cfg_dashboard_api_activity_recent_list",
        "parameters": [
          {
            "description": "Maximum number of entries to return",
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
                  "items": {
                    "$ref": "#/components/schemas/ActivityEntry"
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
        "summary": "Get recent activity",
        "tags": [
          "Dashboard - Activity"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/charts/activity/": {
      "get": {
        "description": "Retrieve user activity data for chart visualization",
        "operationId": "cfg_dashboard_api_charts_activity_retrieve",
        "parameters": [
          {
            "description": "Number of days to include",
            "in": "query",
            "name": "days",
            "schema": {
              "default": 7,
              "type": "integer"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ChartData"
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
        "summary": "Get user activity chart",
        "tags": [
          "Dashboard - Charts"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/charts/recent-users/": {
      "get": {
        "description": "Retrieve list of recently registered users",
        "operationId": "cfg_dashboard_api_charts_recent_users_list",
        "parameters": [
          {
            "description": "Maximum number of users to return",
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
                  "items": {
                    "$ref": "#/components/schemas/RecentUser"
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
        "summary": "Get recent users",
        "tags": [
          "Dashboard - Charts"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/charts/registrations/": {
      "get": {
        "description": "Retrieve user registration data for chart visualization",
        "operationId": "cfg_dashboard_api_charts_registrations_retrieve",
        "parameters": [
          {
            "description": "Number of days to include",
            "in": "query",
            "name": "days",
            "schema": {
              "default": 7,
              "type": "integer"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ChartData"
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
        "summary": "Get user registration chart",
        "tags": [
          "Dashboard - Charts"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/charts/tracker/": {
      "get": {
        "description": "Retrieve activity tracker data (GitHub-style contribution graph)",
        "operationId": "cfg_dashboard_api_charts_tracker_list",
        "parameters": [
          {
            "description": "Number of weeks to include",
            "in": "query",
            "name": "weeks",
            "schema": {
              "default": 52,
              "type": "integer"
            }
          }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/ActivityTrackerDay"
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
        "summary": "Get activity tracker",
        "tags": [
          "Dashboard - Charts"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/commands/": {
      "get": {
        "description": "Retrieve all available Django management commands",
        "operationId": "cfg_dashboard_api_commands_list",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/Command"
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
        "summary": "Get all commands",
        "tags": [
          "Dashboard - Commands"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/commands/summary/": {
      "get": {
        "description": "Retrieve commands summary with statistics and categorization",
        "operationId": "cfg_dashboard_api_commands_summary_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CommandsSummary"
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
        "summary": "Get commands summary",
        "tags": [
          "Dashboard - Commands"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/overview/overview/": {
      "get": {
        "description": "Retrieve complete dashboard data including stats, health, actions, and metrics",
        "operationId": "cfg_dashboard_api_overview_overview_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/DashboardOverview"
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
        "summary": "Get dashboard overview",
        "tags": [
          "Dashboard - Overview"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/statistics/apps/": {
      "get": {
        "description": "Retrieve statistics for all enabled django-cfg applications",
        "operationId": "cfg_dashboard_api_statistics_apps_list",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/AppStatistics"
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
        "summary": "Get application statistics",
        "tags": [
          "Dashboard - Statistics"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/statistics/cards/": {
      "get": {
        "description": "Retrieve dashboard statistics cards with key metrics",
        "operationId": "cfg_dashboard_api_statistics_cards_list",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/StatCard"
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
        "summary": "Get statistics cards",
        "tags": [
          "Dashboard - Statistics"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/statistics/users/": {
      "get": {
        "description": "Retrieve user-related statistics",
        "operationId": "cfg_dashboard_api_statistics_users_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UserStatistics"
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
        "summary": "Get user statistics",
        "tags": [
          "Dashboard - Statistics"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/system/health/": {
      "get": {
        "description": "Retrieve overall system health including all component checks",
        "operationId": "cfg_dashboard_api_system_health_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/SystemHealth"
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
        "summary": "Get system health status",
        "tags": [
          "Dashboard - System"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/system/metrics/": {
      "get": {
        "description": "Retrieve system performance metrics (CPU, memory, disk, etc.)",
        "operationId": "cfg_dashboard_api_system_metrics_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/SystemMetrics"
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
        "summary": "Get system metrics",
        "tags": [
          "Dashboard - System"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/zones/": {
      "get": {
        "description": "Retrieve all OpenAPI zones/groups with their configuration",
        "operationId": "cfg_dashboard_api_zones_list",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/APIZone"
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
        "summary": "Get all API zones",
        "tags": [
          "Dashboard - API Zones"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/dashboard/api/zones/summary/": {
      "get": {
        "description": "Retrieve zones summary with statistics",
        "operationId": "cfg_dashboard_api_zones_summary_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/APIZonesSummary"
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
        "summary": "Get zones summary",
        "tags": [
          "Dashboard - API Zones"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/endpoints/drf/": {
      "get": {
        "description": "Return endpoints status data.",
        "operationId": "cfg_endpoints_drf_retrieve",
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
        "security": [
          {
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "endpoints"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/endpoints/urls/": {
      "get": {
        "description": "Return all registered URLs.",
        "operationId": "cfg_endpoints_urls_retrieve",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/URLsList"
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
        "tags": [
          "endpoints"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/endpoints/urls/compact/": {
      "get": {
        "description": "Return compact URL list.",
        "operationId": "cfg_endpoints_urls_compact_retrieve",
        "responses": {
          "200": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "endpoints"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/health/drf/": {
      "get": {
        "description": "Return comprehensive health check data.",
        "operationId": "cfg_health_drf_retrieve",
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
        "security": [
          {
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "health"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/health/drf/quick/": {
      "get": {
        "description": "Return minimal health status.",
        "operationId": "cfg_health_drf_quick_retrieve",
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
        "security": [
          {
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "health"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/chat/": {
      "get": {
        "description": "Chat query endpoints.",
        "operationId": "cfg_knowbase_admin_chat_list",
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
                  "$ref": "#/components/schemas/PaginatedChatResponseList"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Chat query endpoints.",
        "operationId": "cfg_knowbase_admin_chat_create",
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
          "required": true
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/chat/query/": {
      "post": {
        "description": "Process chat query with RAG context.",
        "operationId": "cfg_knowbase_admin_chat_query_create",
        "requestBody": {
          "content": {
            "application/json": {
              "examples": {
                "SimpleQuery": {
                  "summary": "Simple Query",
                  "value": {
                    "include_sources": true,
                    "max_tokens": 1000,
                    "query": "What is machine learning?"
                  }
                }
              },
              "schema": {
                "$ref": "#/components/schemas/ChatQueryRequest"
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
          "required": true
        },
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "examples": {
                  "SimpleQuery": {
                    "summary": "Simple Query",
                    "value": {
                      "include_sources": true,
                      "max_tokens": 1000,
                      "query": "What is machine learning?"
                    }
                  }
                },
                "schema": {
                  "$ref": "#/components/schemas/ChatResponse"
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
        "summary": "Process chat query with RAG",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/chat/{id}/": {
      "delete": {
        "description": "Chat query endpoints.",
        "operationId": "cfg_knowbase_admin_chat_destroy",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
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
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Chat query endpoints.",
        "operationId": "cfg_knowbase_admin_chat_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
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
                  "$ref": "#/components/schemas/ChatResponse"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Chat query endpoints.",
        "operationId": "cfg_knowbase_admin_chat_partial_update",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
            "in": "path",
            "name": "id",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Chat query endpoints.",
        "operationId": "cfg_knowbase_admin_chat_update",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
            "in": "path",
            "name": "id",
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
          "required": true
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/chat/{id}/history/": {
      "get": {
        "description": "Get chat session history.",
        "operationId": "cfg_knowbase_admin_chat_history_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
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
                  "$ref": "#/components/schemas/ChatHistory"
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
        "summary": "Get chat history",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/documents/": {
      "get": {
        "description": "List user documents with filtering and pagination.",
        "operationId": "cfg_knowbase_admin_documents_list",
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
          },
          {
            "description": "Filter by processing status",
            "in": "query",
            "name": "status",
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
                  "$ref": "#/components/schemas/PaginatedDocumentList"
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
        "summary": "List user documents",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Upload and process a new knowledge document",
        "operationId": "cfg_knowbase_admin_documents_create",
        "requestBody": {
          "content": {
            "application/json": {
              "examples": {
                "TextDocument": {
                  "summary": "Text Document",
                  "value": {
                    "content": "# API Guide\n\nThis guide explains...",
                    "file_type": "text/markdown",
                    "title": "API Documentation"
                  }
                }
              },
              "schema": {
                "$ref": "#/components/schemas/DocumentCreateRequest"
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
          "required": true
        },
        "responses": {
          "201": {
            "content": {
              "application/json": {
                "examples": {
                  "TextDocument": {
                    "summary": "Text Document",
                    "value": {
                      "content": "# API Guide\n\nThis guide explains...",
                      "file_type": "text/markdown",
                      "title": "API Documentation"
                    }
                  }
                },
                "schema": {
                  "$ref": "#/components/schemas/Document"
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Upload new document",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/documents/stats/": {
      "get": {
        "description": "Get user\u0027s document processing statistics.",
        "operationId": "cfg_knowbase_admin_documents_stats_retrieve",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Get processing statistics",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/documents/{id}/": {
      "delete": {
        "description": "Delete document and all associated chunks.",
        "operationId": "cfg_knowbase_admin_documents_destroy",
        "parameters": [
          {
            "description": "A UUID string identifying this document.",
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
          "204": {
            "description": "Document deleted successfully"
          },
          "404": {
            "description": "Document not found"
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Delete document",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Get document by ID.",
        "operationId": "cfg_knowbase_admin_documents_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this document.",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Get document details",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Document management endpoints - Admin only.",
        "operationId": "cfg_knowbase_admin_documents_partial_update",
        "parameters": [
          {
            "description": "A UUID string identifying this document.",
            "in": "path",
            "name": "id",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Document management endpoints - Admin only.",
        "operationId": "cfg_knowbase_admin_documents_update",
        "parameters": [
          {
            "description": "A UUID string identifying this document.",
            "in": "path",
            "name": "id",
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
          "required": true
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/documents/{id}/reprocess/": {
      "post": {
        "description": "Trigger reprocessing of document chunks and embeddings",
        "operationId": "cfg_knowbase_admin_documents_reprocess_create",
        "parameters": [
          {
            "description": "A UUID string identifying this document.",
            "in": "path",
            "name": "id",
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
          "required": true
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Reprocess document",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/documents/{id}/status/": {
      "get": {
        "description": "Get document processing status.",
        "operationId": "cfg_knowbase_admin_documents_status_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this document.",
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
                  "$ref": "#/components/schemas/DocumentProcessingStatus"
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
        "summary": "Get document processing status",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/sessions/": {
      "get": {
        "description": "List user chat sessions with filtering.",
        "operationId": "cfg_knowbase_admin_sessions_list",
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
                  "$ref": "#/components/schemas/PaginatedChatSessionList"
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
        "summary": "List user chat sessions",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Create new chat session.",
        "operationId": "cfg_knowbase_admin_sessions_create",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Create new chat session",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/sessions/{id}/": {
      "delete": {
        "description": "Chat session management endpoints.",
        "operationId": "cfg_knowbase_admin_sessions_destroy",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
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
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Chat session management endpoints.",
        "operationId": "cfg_knowbase_admin_sessions_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
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
                  "$ref": "#/components/schemas/ChatSession"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Chat session management endpoints.",
        "operationId": "cfg_knowbase_admin_sessions_partial_update",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
            "in": "path",
            "name": "id",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Chat session management endpoints.",
        "operationId": "cfg_knowbase_admin_sessions_update",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
            "in": "path",
            "name": "id",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/sessions/{id}/activate/": {
      "post": {
        "description": "Activate chat session.",
        "operationId": "cfg_knowbase_admin_sessions_activate_create",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
            "in": "path",
            "name": "id",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Activate chat session",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/admin/sessions/{id}/archive/": {
      "post": {
        "description": "Archive (deactivate) chat session.",
        "operationId": "cfg_knowbase_admin_sessions_archive_create",
        "parameters": [
          {
            "description": "A UUID string identifying this chat session.",
            "in": "path",
            "name": "id",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Archive chat session",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/categories/": {
      "get": {
        "description": "Get list of all public categories",
        "operationId": "cfg_knowbase_categories_list",
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
                  "$ref": "#/components/schemas/PaginatedPublicCategoryList"
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
        "summary": "List public categories",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/categories/{id}/": {
      "get": {
        "description": "Get category details by ID (public access)",
        "operationId": "cfg_knowbase_categories_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this Document Category.",
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
        "security": [
          {
            "jwtAuth": []
          },
          {}
        ],
        "summary": "Get public category details",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/documents/": {
      "get": {
        "description": "Get list of all completed and publicly accessible documents",
        "operationId": "cfg_knowbase_documents_list",
        "parameters": [
          {
            "description": "Filter by category name",
            "in": "query",
            "name": "category",
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
            "description": "Search in title and content",
            "in": "query",
            "name": "search",
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
                  "$ref": "#/components/schemas/PaginatedPublicDocumentListList"
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
        "summary": "List public documents",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/documents/{id}/": {
      "get": {
        "description": "Get document details by ID (public access)",
        "operationId": "cfg_knowbase_documents_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this document.",
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
        "security": [
          {
            "jwtAuth": []
          },
          {}
        ],
        "summary": "Get public document details",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/archives/": {
      "get": {
        "description": "Document archive management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_archives_list",
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
                  "$ref": "#/components/schemas/PaginatedDocumentArchiveListList"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Upload archive file and process it synchronously",
        "operationId": "cfg_knowbase_system_archives_create",
        "requestBody": {
          "content": {
            "multipart/form-data": {
              "schema": {
                "properties": {
                  "category_ids": {
                    "items": {
                      "type": "string"
                    },
                    "type": "array"
                  },
                  "description": {
                    "type": "string"
                  },
                  "file": {
                    "format": "binary",
                    "type": "string"
                  },
                  "is_public": {
                    "type": "boolean"
                  },
                  "process_immediately": {
                    "type": "boolean"
                  },
                  "title": {
                    "type": "string"
                  }
                },
                "type": "object"
              }
            }
          }
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Upload and process archive",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/archives/revectorize/": {
      "post": {
        "description": "Re-vectorize specific chunks",
        "operationId": "cfg_knowbase_system_archives_revectorize_create",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ChunkRevectorizationRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/ChunkRevectorizationRequestRequest"
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
                  "$ref": "#/components/schemas/VectorizationResult"
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
        "summary": "Re-vectorize chunks",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/archives/statistics/": {
      "get": {
        "description": "Get processing and vectorization statistics",
        "operationId": "cfg_knowbase_system_archives_statistics_retrieve",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Get archive statistics",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/archives/vectorization_stats/": {
      "get": {
        "description": "Get vectorization statistics for archives",
        "operationId": "cfg_knowbase_system_archives_vectorization_stats_retrieve",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Get vectorization statistics",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/archives/{id}/": {
      "delete": {
        "description": "Document archive management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_archives_destroy",
        "parameters": [
          {
            "description": "A UUID string identifying this Document Archive.",
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
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Document archive management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_archives_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this Document Archive.",
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
                  "$ref": "#/components/schemas/DocumentArchiveDetail"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Document archive management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_archives_partial_update",
        "parameters": [
          {
            "description": "A UUID string identifying this Document Archive.",
            "in": "path",
            "name": "id",
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
                "$ref": "#/components/schemas/PatchedDocumentArchiveRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/PatchedDocumentArchiveRequest"
              }
            }
          }
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Document archive management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_archives_update",
        "parameters": [
          {
            "description": "A UUID string identifying this Document Archive.",
            "in": "path",
            "name": "id",
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
                "$ref": "#/components/schemas/DocumentArchiveRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/DocumentArchiveRequest"
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
                  "$ref": "#/components/schemas/DocumentArchive"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/archives/{id}/file_tree/": {
      "get": {
        "description": "Get hierarchical file tree structure",
        "operationId": "cfg_knowbase_system_archives_file_tree_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this Document Archive.",
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
                  "type": "object"
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
        "summary": "Get archive file tree",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/archives/{id}/items/": {
      "get": {
        "description": "Get all items in the archive",
        "operationId": "cfg_knowbase_system_archives_items_list",
        "parameters": [
          {
            "description": "A UUID string identifying this Document Archive.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "format": "uuid",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Get archive items",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/archives/{id}/search/": {
      "post": {
        "description": "Semantic search within archive chunks",
        "operationId": "cfg_knowbase_system_archives_search_create",
        "parameters": [
          {
            "description": "A UUID string identifying this Document Archive.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "format": "uuid",
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
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ArchiveSearchRequestRequest"
              }
            },
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/ArchiveSearchRequestRequest"
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
                  "$ref": "#/components/schemas/PaginatedArchiveSearchResultList"
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
        "summary": "Search archive chunks",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/chunks/": {
      "get": {
        "description": "Archive item chunk management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_chunks_list",
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
                  "$ref": "#/components/schemas/PaginatedArchiveItemChunkList"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Archive item chunk management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_chunks_create",
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
          "required": true
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/chunks/{id}/": {
      "delete": {
        "description": "Archive item chunk management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_chunks_destroy",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item Chunk.",
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
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Archive item chunk management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_chunks_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item Chunk.",
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
                  "$ref": "#/components/schemas/ArchiveItemChunkDetail"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Archive item chunk management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_chunks_partial_update",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item Chunk.",
            "in": "path",
            "name": "id",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Archive item chunk management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_chunks_update",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item Chunk.",
            "in": "path",
            "name": "id",
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
          "required": true
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/chunks/{id}/context/": {
      "get": {
        "description": "Get full context metadata for chunk",
        "operationId": "cfg_knowbase_system_chunks_context_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item Chunk.",
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
                  "$ref": "#/components/schemas/ArchiveItemChunkDetail"
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
        "summary": "Get chunk context",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/chunks/{id}/vectorize/": {
      "post": {
        "description": "Generate embedding for specific chunk",
        "operationId": "cfg_knowbase_system_chunks_vectorize_create",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item Chunk.",
            "in": "path",
            "name": "id",
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
          "required": true
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Vectorize chunk",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/items/": {
      "get": {
        "description": "Archive item management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_items_list",
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
                  "$ref": "#/components/schemas/PaginatedArchiveItemList"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Archive item management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_items_create",
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
          "required": true
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/items/{id}/": {
      "delete": {
        "description": "Archive item management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_items_destroy",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item.",
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
          "204": {
            "description": "No response body"
          }
        },
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "Archive item management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_items_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item.",
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
                  "$ref": "#/components/schemas/ArchiveItemDetail"
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
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "Archive item management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_items_partial_update",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item.",
            "in": "path",
            "name": "id",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Archive item management endpoints - Admin only.",
        "operationId": "cfg_knowbase_system_items_update",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item.",
            "in": "path",
            "name": "id",
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
          "required": true
        },
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/items/{id}/chunks/": {
      "get": {
        "description": "Get all chunks for this item",
        "operationId": "cfg_knowbase_system_items_chunks_list",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item.",
            "in": "path",
            "name": "id",
            "required": true,
            "schema": {
              "format": "uuid",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Get item chunks",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/knowbase/system/items/{id}/content/": {
      "get": {
        "description": "Get full content of archive item",
        "operationId": "cfg_knowbase_system_items_content_retrieve",
        "parameters": [
          {
            "description": "A UUID string identifying this Archive Item.",
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
                  "$ref": "#/components/schemas/ArchiveItemDetail"
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
        "summary": "Get item content",
        "tags": [
          "knowbase"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/leads/": {
      "get": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "cfg_leads_list",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "leads"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "cfg_leads_create",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "leads"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/leads/submit/": {
      "post": {
        "description": "Submit a new lead from frontend contact form with automatic Telegram notifications.",
        "operationId": "cfg_leads_submit_create",
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
            "jwtAuth": []
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
    "/cfg/leads/{id}/": {
      "delete": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "cfg_leads_destroy",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "leads"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "cfg_leads_retrieve",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "leads"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "cfg_leads_partial_update",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "leads"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "ViewSet for Lead model.\n\nProvides only submission functionality for leads from frontend forms.",
        "operationId": "cfg_leads_update",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "leads"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/newsletter/bulk/": {
      "post": {
        "description": "Send bulk emails to multiple recipients using base email template.",
        "operationId": "cfg_newsletter_bulk_create",
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
            "jwtAuth": []
          }
        ],
        "summary": "Send Bulk Email",
        "tags": [
          "Bulk Email"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/newsletter/campaigns/": {
      "get": {
        "description": "Get a list of all newsletter campaigns.",
        "operationId": "cfg_newsletter_campaigns_list",
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
            "jwtAuth": []
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
        "operationId": "cfg_newsletter_campaigns_create",
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
            "jwtAuth": []
          }
        ],
        "summary": "Create Newsletter Campaign",
        "tags": [
          "Campaigns"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/newsletter/campaigns/send/": {
      "post": {
        "description": "Send a newsletter campaign to all subscribers.",
        "operationId": "cfg_newsletter_campaigns_send_create",
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
            "jwtAuth": []
          }
        ],
        "summary": "Send Newsletter Campaign",
        "tags": [
          "Campaigns"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/newsletter/campaigns/{id}/": {
      "delete": {
        "description": "Delete a newsletter campaign.",
        "operationId": "cfg_newsletter_campaigns_destroy",
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
            "jwtAuth": []
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
        "operationId": "cfg_newsletter_campaigns_retrieve",
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
            "jwtAuth": []
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
        "operationId": "cfg_newsletter_campaigns_partial_update",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "newsletter"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "Update a newsletter campaign.",
        "operationId": "cfg_newsletter_campaigns_update",
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
            "jwtAuth": []
          }
        ],
        "summary": "Update Campaign",
        "tags": [
          "Campaigns"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/newsletter/logs/": {
      "get": {
        "description": "Get a list of email sending logs.",
        "operationId": "cfg_newsletter_logs_list",
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
            "jwtAuth": []
          }
        ],
        "summary": "List Email Logs",
        "tags": [
          "Logs"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/newsletter/newsletters/": {
      "get": {
        "description": "Get a list of all active newsletters available for subscription.",
        "operationId": "cfg_newsletter_newsletters_list",
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
            "jwtAuth": []
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
    "/cfg/newsletter/newsletters/{id}/": {
      "get": {
        "description": "Retrieve details of a specific newsletter.",
        "operationId": "cfg_newsletter_newsletters_retrieve",
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
            "jwtAuth": []
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
    "/cfg/newsletter/subscribe/": {
      "post": {
        "description": "Subscribe an email address to a newsletter.",
        "operationId": "cfg_newsletter_subscribe_create",
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
            "jwtAuth": []
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
    "/cfg/newsletter/subscriptions/": {
      "get": {
        "description": "Get a list of current user\u0027s active newsletter subscriptions.",
        "operationId": "cfg_newsletter_subscriptions_list",
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
            "jwtAuth": []
          }
        ],
        "summary": "List User Subscriptions",
        "tags": [
          "Subscriptions"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/newsletter/test/": {
      "post": {
        "description": "Send a test email to verify mailer configuration.",
        "operationId": "cfg_newsletter_test_create",
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
            "jwtAuth": []
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
    "/cfg/newsletter/unsubscribe/": {
      "patch": {
        "description": "Handle newsletter unsubscriptions.",
        "operationId": "cfg_newsletter_unsubscribe_partial_update",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "newsletter"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "Unsubscribe from a newsletter using subscription ID.",
        "operationId": "cfg_newsletter_unsubscribe_create",
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
            "jwtAuth": []
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
        "operationId": "cfg_newsletter_unsubscribe_update",
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
            "jwtAuth": []
          },
          {}
        ],
        "tags": [
          "newsletter"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/payments/balance/": {
      "get": {
        "description": "Get current user balance and transaction statistics",
        "operationId": "cfg_payments_balance_retrieve",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "summary": "Get user balance",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/payments/currencies/": {
      "get": {
        "description": "Returns list of available currencies with token+network info",
        "operationId": "cfg_payments_currencies_list",
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": {
                  "items": {
                    "$ref": "#/components/schemas/Currency"
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
            "jwtAuth": []
          }
        ],
        "summary": "Get available currencies",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/payments/payments/": {
      "get": {
        "description": "ViewSet for payment operations.\n\nEndpoints:\n- GET /payments/ - List user\u0027s payments\n- GET /payments/{id}/ - Get payment details\n- POST /payments/create/ - Create new payment\n- GET /payments/{id}/status/ - Check payment status\n- POST /payments/{id}/confirm/ - Confirm payment",
        "operationId": "cfg_payments_payments_list",
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
                  "$ref": "#/components/schemas/PaginatedPaymentListList"
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
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/payments/payments/create/": {
      "post": {
        "description": "POST /api/v1/payments/create/\n\nCreate new payment.\n\nRequest body:\n{\n    \"amount_usd\": \"100.00\",\n    \"currency_code\": \"USDTTRC20\",\n    \"description\": \"Optional description\"\n}",
        "operationId": "cfg_payments_payments_create_create",
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
        "security": [
          {
            "jwtAuth": []
          }
        ],
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/payments/payments/{id}/": {
      "get": {
        "description": "ViewSet for payment operations.\n\nEndpoints:\n- GET /payments/ - List user\u0027s payments\n- GET /payments/{id}/ - Get payment details\n- POST /payments/create/ - Create new payment\n- GET /payments/{id}/status/ - Check payment status\n- POST /payments/{id}/confirm/ - Confirm payment",
        "operationId": "cfg_payments_payments_retrieve",
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
                  "$ref": "#/components/schemas/PaymentDetail"
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
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/payments/payments/{id}/confirm/": {
      "post": {
        "description": "POST /api/v1/payments/{id}/confirm/\n\nConfirm payment (user clicked \"I have paid\").\nChecks status with provider and creates transaction if completed.",
        "operationId": "cfg_payments_payments_confirm_create",
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
                  "$ref": "#/components/schemas/PaymentList"
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
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/payments/payments/{id}/status/": {
      "get": {
        "description": "GET /api/v1/payments/{id}/status/?refresh=true\n\nCheck payment status (with optional refresh from provider).\n\nQuery params:\n- refresh: boolean (default: false) - Force refresh from provider",
        "operationId": "cfg_payments_payments_status_retrieve",
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
                  "$ref": "#/components/schemas/PaymentList"
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
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/payments/transactions/": {
      "get": {
        "description": "Get user transactions with pagination and filtering",
        "operationId": "cfg_payments_transactions_list",
        "parameters": [
          {
            "description": "Number of transactions to return (max 100)",
            "in": "query",
            "name": "limit",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Offset for pagination",
            "in": "query",
            "name": "offset",
            "schema": {
              "type": "integer"
            }
          },
          {
            "description": "Filter by transaction type (deposit/withdrawal)",
            "in": "query",
            "name": "type",
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
                  "items": {
                    "$ref": "#/components/schemas/Transaction"
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
            "jwtAuth": []
          }
        ],
        "summary": "Get user transactions",
        "tags": [
          "payments"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/support/tickets/": {
      "get": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "cfg_support_tickets_list",
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
                  "$ref": "#/components/schemas/PaginatedTicketList"
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
        "tags": [
          "support"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "cfg_support_tickets_create",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/support/tickets/{ticket_uuid}/messages/": {
      "get": {
        "description": "ViewSet for managing support messages.",
        "operationId": "cfg_support_tickets_messages_list",
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
          },
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
                  "$ref": "#/components/schemas/PaginatedMessageList"
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
        "tags": [
          "support"
        ],
        "x-async-capable": false
      },
      "post": {
        "description": "ViewSet for managing support messages.",
        "operationId": "cfg_support_tickets_messages_create",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/support/tickets/{ticket_uuid}/messages/{uuid}/": {
      "delete": {
        "description": "ViewSet for managing support messages.",
        "operationId": "cfg_support_tickets_messages_destroy",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "ViewSet for managing support messages.",
        "operationId": "cfg_support_tickets_messages_retrieve",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "ViewSet for managing support messages.",
        "operationId": "cfg_support_tickets_messages_partial_update",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "ViewSet for managing support messages.",
        "operationId": "cfg_support_tickets_messages_update",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/support/tickets/{uuid}/": {
      "delete": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "cfg_support_tickets_destroy",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      },
      "get": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "cfg_support_tickets_retrieve",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      },
      "patch": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "cfg_support_tickets_partial_update",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      },
      "put": {
        "description": "ViewSet for managing support tickets.",
        "operationId": "cfg_support_tickets_update",
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
            "jwtAuth": []
          }
        ],
        "tags": [
          "support"
        ],
        "x-async-capable": false
      }
    },
    "/cfg/tasks/api/clear-queues/": {
      "post": {
        "description": "Clear all tasks from all Dramatiq queues.",
        "operationId": "cfg_tasks_api_clear_queues_create",
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
    "/cfg/tasks/api/clear/": {
      "post": {
        "description": "Clear all test data from Redis.",
        "operationId": "cfg_tasks_api_clear_create",
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
    "/cfg/tasks/api/purge-failed/": {
      "post": {
        "description": "Purge all failed tasks from queues.",
        "operationId": "cfg_tasks_api_purge_failed_create",
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
    "/cfg/tasks/api/queues/manage/": {
      "post": {
        "description": "Manage queue operations (clear, purge, etc.).",
        "operationId": "cfg_tasks_api_queues_manage_create",
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
    "/cfg/tasks/api/queues/status/": {
      "get": {
        "description": "Get current status of all queues.",
        "operationId": "cfg_tasks_api_queues_status_retrieve",
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
    "/cfg/tasks/api/simulate/": {
      "post": {
        "description": "Simulate test data for dashboard testing.",
        "operationId": "cfg_tasks_api_simulate_create",
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
    "/cfg/tasks/api/tasks/list/": {
      "get": {
        "description": "Get paginated task list with filtering.",
        "operationId": "cfg_tasks_api_tasks_list_retrieve",
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
    "/cfg/tasks/api/tasks/stats/": {
      "get": {
        "description": "Get task execution statistics.",
        "operationId": "cfg_tasks_api_tasks_stats_retrieve",
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
    "/cfg/tasks/api/workers/list/": {
      "get": {
        "description": "Get detailed list of workers.",
        "operationId": "cfg_tasks_api_workers_list_retrieve",
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
    "/cfg/tasks/api/workers/manage/": {
      "post": {
        "description": "Manage worker operations.",
        "operationId": "cfg_tasks_api_workers_manage_create",
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