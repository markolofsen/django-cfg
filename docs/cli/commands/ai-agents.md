---
title: AI Agents Commands
description: Django-CFG CLI ai agents commands. Command-line interface for ai agents commands with examples, options, and production workflows.
sidebar_label: AI Agents
sidebar_position: 3
keywords:
  - django-cfg ai agents
  - django-cfg command ai agents
  - cli ai agents
---

# AI Agents Commands

Commands for managing AI agents, orchestrator, and workflow automation.

## Agent Creation

### `create_agent`

Create new agent definitions or load pre-built templates.

```bash
python manage.py create_agent NAME INSTRUCTIONS [OPTIONS]
```

**Arguments:**
- `NAME` - Agent name (unique identifier)
- `INSTRUCTIONS` - Agent instructions/system prompt

**Options:**
- `--deps-type TEXT` - Dependencies type (default: DjangoDeps)
- `--output-type TEXT` - Output type (default: ProcessResult)
- `--model TEXT` - LLM model to use (default: openai:gpt-4o-mini)
- `--category TEXT` - Agent category
- `--timeout INTEGER` - Execution timeout in seconds (default: 300)
- `--max-retries INTEGER` - Maximum retry attempts (default: 3)
- `--public` - Make agent public (accessible to all users)
- `--no-cache` - Disable caching for this agent
- `--creator TEXT` - Username of agent creator
- `--description TEXT` - Agent description
- `--tags TEXT [TEXT...]` - Agent tags (space-separated)

---

## Creating Custom Agents

### Basic Content Analyzer

```bash
python manage.py create_agent "content_analyzer" \
  "Analyze content for sentiment, topics, keywords, and quality metrics. \
   Provide detailed analysis including readability scores and recommendations." \
  --category content \
  --description "Comprehensive content analysis agent"
```

### Business Rules Agent

```bash
python manage.py create_agent "business_rules" \
  "Apply business rules, validate decisions, and ensure compliance with policies. \
   Check all input against defined business logic and return validation results." \
  --category business \
  --public \
  --model openai:gpt-4o \
  --timeout 600
```

### Data Processor

```bash
python manage.py create_agent "data_processor" \
  "Process, clean, and transform data according to specifications. \
   Handle data validation, normalization, and enrichment tasks." \
  --category data \
  --tags processing etl automation \
  --description "Handles data transformation workflows" \
  --max-retries 5
```

### Customer Support Agent

```bash
python manage.py create_agent "support_agent" \
  "Respond to customer inquiries with helpful, accurate information. \
   Use friendly tone, provide step-by-step guidance, and escalate when needed." \
  --category support \
  --public \
  --model openai:gpt-4o \
  --description "24/7 customer support automation"
```

### Code Review Agent

```bash
python manage.py create_agent "code_reviewer" \
  "Review code for quality, security, and best practices. \
   Identify bugs, suggest improvements, and check coding standards." \
  --category development \
  --tags code-quality security review \
  --model openai:gpt-4o \
  --timeout 900
```

---

## Template Management

### List Available Templates

```bash
python manage.py create_agent --list
```

**Output:**
```
📋 Available Agent Templates:
========================================

CONTENT:
  • content_analyzer: Analyze content sentiment, topics, and quality
  • content_generator: Generate high-quality content based on requirements
  • content_validator: Validate content quality and compliance

DATA:
  • data_processor: Process and transform data
  • data_validator: Validate data quality and integrity

BUSINESS:
  • business_rules: Apply business rules and logic
  • decision_maker: Make decisions based on criteria
```

### Load Specific Templates

```bash
# Load single template
python manage.py create_agent --load content_analyzer

# Load multiple templates
python manage.py create_agent --load content_analyzer data_processor business_rules
```

### Load All Templates

```bash
python manage.py create_agent --load-all
```

**Available Templates:**

#### Content Templates
- **content_analyzer** - Analyze content sentiment, topics, and quality
- **content_generator** - Generate high-quality content based on requirements
- **content_validator** - Validate content quality and compliance

#### Data Templates
- **data_processor** - Process and transform data
- **data_validator** - Validate data quality and integrity

#### Business Templates
- **business_rules** - Apply business rules and logic
- **decision_maker** - Make decisions based on criteria

---

## Orchestrator Management

### `orchestrator_status`

Display Django Orchestrator status and statistics.

```bash
python manage.py orchestrator_status [OPTIONS]
```

**Options:**
- `--detailed` - Show detailed statistics
- `--agents` - Show agent-specific statistics
- `--recent INTEGER` - Show statistics for recent hours (default: 24)

---

## Status Commands

### Basic Status

```bash
python manage.py orchestrator_status
```

**Output:**
```
🤖 Django Orchestrator Status
==================================================

📋 Registry Status:
  Runtime Agents: 5
  Available Patterns: 12
  Loaded Agents: content_analyzer, data_processor, business_rules

📊 Database Statistics:
  Agent Definitions: 15 (12 active)
  Recent Executions (24h): 234 agents, 45 workflows
  Overall Success Rate: 94.5%
```

### Detailed Statistics

```bash
python manage.py orchestrator_status --detailed
```

**Additional output:**
```
📈 Detailed Statistics:
  Execution Status (last 24h):
    Completed: 221
    Running: 8
    Failed: 5
  Average Execution Time: 4.32s
  Total Tokens Used: 1,245,890
  Total Cost: $2.4567
```

### Agent-Specific Stats

```bash
python manage.py orchestrator_status --agents
```

**Additional output:**
```
🤖 Agent Statistics:
  Most Used Agents (last 24h):
    content_analyzer: 89 executions
    data_processor: 67 executions
    business_rules: 45 executions

  Agents by Category:
    Content: 3
    Data: 2
    Business: 2

  Runtime Agent Metrics:
    content_analyzer: 89 runs, 96.7% success, 85.2% cache hit
    data_processor: 67 runs, 94.0% success, 72.3% cache hit
```

### Custom Time Range

```bash
# Show statistics for last 48 hours
python manage.py orchestrator_status --agents --recent 48

# Show statistics for last week
python manage.py orchestrator_status --detailed --recent 168
```

---

## Agent Configuration

### Model Selection

Django-CFG supports multiple LLM providers:

```bash
# OpenAI models
--model openai:gpt-4o
--model openai:gpt-4o-mini
--model openai:gpt-4-turbo

# OpenRouter models
--model openrouter:anthropic/claude-3.5-sonnet
--model openrouter:google/gemini-pro-1.5
--model openrouter:meta-llama/llama-3.1-70b
```

### Dependencies Configuration

Available dependency types:

```bash
# Django dependencies (default)
--deps-type DjangoDeps

# Content processing dependencies
--deps-type ContentDeps

# Data processing dependencies
--deps-type DataProcessingDeps

# Business logic dependencies
--deps-type BusinessLogicDeps

# Custom dependencies
--deps-type CustomDeps
```

### Output Types

Configure agent output format:

```bash
# Process result (default)
--output-type ProcessResult

# Analysis result
--output-type AnalysisResult

# Validation result
--output-type ValidationResult

# Custom result type
--output-type CustomResult
```

---

## Best Practices

### 1. Use Descriptive Names

```bash
# ✅ GOOD - Clear, descriptive name
python manage.py create_agent "email_spam_detector" \
  "Detect spam in emails using content analysis"

# ❌ BAD - Vague name
python manage.py create_agent "agent1" "Do stuff"
```

### 2. Provide Detailed Instructions

```bash
# ✅ GOOD - Detailed, specific instructions
python manage.py create_agent "support_ticket_classifier" \
  "Classify support tickets into categories: technical, billing, feature_request, bug. \
   Analyze ticket content, urgency, and context. \
   Return category, confidence score, and suggested priority." \
  --category support

# ❌ BAD - Vague instructions
python manage.py create_agent "classifier" "Classify things"
```

### 3. Set Appropriate Timeouts

```bash
# Quick tasks
--timeout 60      # 1 minute for simple classification

# Normal tasks
--timeout 300     # 5 minutes (default) for most tasks

# Complex tasks
--timeout 900     # 15 minutes for document processing
--timeout 1800    # 30 minutes for batch operations
```

### 4. Use Tags for Organization

```bash
python manage.py create_agent "email_processor" \
  "Process and route incoming emails" \
  --tags email automation processing routing \
  --category communication
```

### 5. Make Public Only When Appropriate

```bash
# Public agent - accessible to all users
python manage.py create_agent "content_formatter" \
  "Format content according to style guidelines" \
  --public

# Private agent - specific to creator/admins
python manage.py create_agent "internal_audit" \
  "Audit internal processes and compliance" \
  --category compliance
```

### 6. Enable Caching for Repetitive Tasks

```bash
# Enable caching (default)
python manage.py create_agent "faq_responder" \
  "Respond to frequently asked questions"

# Disable caching for dynamic content
python manage.py create_agent "market_analyzer" \
  "Analyze current market conditions" \
  --no-cache
```

---

## Workflow Examples

### Setup Content Processing Pipeline

```bash
# 1. Load content templates
python manage.py create_agent --load content_analyzer content_validator

# 2. Create custom content generator
python manage.py create_agent "blog_writer" \
  "Generate engaging blog posts on given topics" \
  --category content --public --model openai:gpt-4o

# 3. Check orchestrator status
python manage.py orchestrator_status --agents
```

### Setup Customer Support Automation

```bash
# 1. Create ticket classifier
python manage.py create_agent "ticket_classifier" \
  "Classify support tickets by urgency and category" \
  --category support --public

# 2. Create response generator
python manage.py create_agent "response_generator" \
  "Generate helpful responses to customer inquiries" \
  --category support --public --model openai:gpt-4o

# 3. Create escalation detector
python manage.py create_agent "escalation_detector" \
  "Detect when tickets need human escalation" \
  --category support --timeout 120
```

### Setup Data Processing Pipeline

```bash
# 1. Load data templates
python manage.py create_agent --load data_processor data_validator

# 2. Create data enrichment agent
python manage.py create_agent "data_enricher" \
  "Enrich data with additional information" \
  --category data --tags enrichment automation

# 3. Monitor processing
python manage.py orchestrator_status --detailed --recent 1
```

---

## Monitoring & Debugging

### Check Agent Execution

```bash
# Real-time status during execution
watch -n 5 'python manage.py orchestrator_status'
```

### Monitor Token Usage

```bash
# Check token consumption
python manage.py orchestrator_status --detailed
```

### Review Agent Performance

```bash
# Analyze performance metrics
python manage.py orchestrator_status --agents --recent 168
```

---

## Related Documentation

- **[Quick Reference](./quick-reference)** - Fast command lookup
- **[AI Agents Guide](/ai-agents/introduction)** - Complete AI agents documentation
- **[Core Commands](./core-commands)** - Project setup commands

---

**AI Agents automate complex workflows!** 🤖
