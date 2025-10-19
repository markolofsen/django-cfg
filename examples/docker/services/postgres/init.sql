-- PostgreSQL Initialization Script
-- Django-CFG Sample Project

-- Enable UUID extension for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for full-text search and similarity queries
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable pgvector for vector embeddings (Knowbase AI features)
-- Used for: document similarity, semantic search, RAG functionality
CREATE EXTENSION IF NOT EXISTS vector;

-- Set default timezone to UTC
SET timezone = 'UTC';
