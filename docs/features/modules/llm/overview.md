---
title: LLM Integration Overview
description: Django-CFG overview feature guide. Production-ready llm integration overview with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview & Philosophy
sidebar_position: 1
keywords:
  - django-cfg overview
  - django overview
  - overview django-cfg
---

# LLM Integration Module

Django-CFG includes a **comprehensive LLM integration module** that provides multi-provider support, intelligent caching, cost tracking, and seamless Django integration.

## Overview

The Django LLM module provides:
- **Multi-provider support** (OpenAI, OpenRouter)
- **Automatic cost calculation** and tracking
- **Intelligent caching** with TTL
- **Type-safe configuration** with Pydantic 2
- **Token counting** and usage analytics
- **JSON extraction** utilities
- **Translation services** with caching

## Quick Start

### Enable LLM Module

```python
# config.py
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    # LLM API keys
    openai_api_key: str = env.openai_api_key  # From YAML config
    openrouter_api_key: str = "<from-yaml-config>"  # Set via environment/config.yaml
    
    # Optional: Custom cache directory
    llm_cache_dir: str = "cache/llm"
    llm_cache_ttl: int = 3600  # 1 hour
```

### Basic Usage

```python
from django_cfg.modules.django_llm.llm.client import LLMClient

# Initialize with API keys
client = LLMClient(
    apikey_openrouter="sk-or-v1-...",
    apikey_openai="sk-proj-...",
    cache_dir=Path("cache/llm"),
    cache_ttl=3600,
    max_cache_size=1000
)

# Chat completion
response = client.chat_completion(
    messages=[
        {"role": "user", "content": "Explain quantum computing"}
    ],
    model="openai/gpt-4o-mini"
)

print(response['content'])
```

## LLM Client

### Chat Completions

```python
from django_cfg.modules.django_llm.llm.client import LLMClient

client = LLMClient()

# Basic chat completion
response = client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ],
    model="openai/gpt-4o-mini",
    temperature=0.7,
    max_tokens=500
)

# Streaming response
for chunk in client.chat_completion_stream(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="openai/gpt-4o-mini"
):
    print(chunk, end='', flush=True)

# With function calling
functions = [
    {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }
]

response = client.chat_completion(
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    model="openai/gpt-4o-mini",
    functions=functions,
    function_call="auto"
)
```

### Embeddings

```python
# Generate embeddings
embedding = client.generate_embedding(
    text="Sample text for embedding",
    model="text-embedding-ada-002"
)

# Batch embeddings
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = client.generate_embeddings_batch(
    texts=texts,
    model="text-embedding-ada-002"
)

# Similarity search
def find_similar_documents(query_text, document_embeddings):
    query_embedding = client.generate_embedding(query_text)
    
    similarities = []
    for doc_id, doc_embedding in document_embeddings.items():
        similarity = cosine_similarity(query_embedding, doc_embedding)
        similarities.append((doc_id, similarity))
    
    return sorted(similarities, key=lambda x: x[1], reverse=True)
```

## 💰 Cost Tracking

### Automatic Cost Calculation

```python
from django_cfg.modules.django_llm.llm.costs import calculate_chat_cost

# Calculate cost for chat completion
cost = calculate_chat_cost(
    model="openai/gpt-4o-mini",
    input_tokens=100,
    output_tokens=50,
    models_cache=models_cache
)

print(f"Cost: ${cost:.4f}")

# Estimate cost before API call
from django_cfg.modules.django_llm.llm.tokenizer import count_tokens

messages = [
    {"role": "user", "content": "What is artificial intelligence?"}
]

input_tokens = count_tokens(messages, model="gpt-4o-mini")
estimated_cost = calculate_chat_cost(
    model="openai/gpt-4o-mini",
    input_tokens=input_tokens,
    output_tokens=100  # Estimated
)

print(f"Estimated cost: ${estimated_cost:.4f}")
```

### Cost Monitoring

```python
class CostTracker:
    def __init__(self):
        self.total_cost = 0
        self.usage_log = []
    
    def track_usage(self, model, input_tokens, output_tokens, cost):
        self.total_cost += cost
        self.usage_log.append({
            'timestamp': datetime.now(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost
        })
    
    def get_daily_usage(self, date=None):
        if date is None:
            date = datetime.now().date()
        
        daily_usage = [
            entry for entry in self.usage_log
            if entry['timestamp'].date() == date
        ]
        
        return {
            'total_cost': sum(entry['cost'] for entry in daily_usage),
            'total_tokens': sum(
                entry['input_tokens'] + entry['output_tokens'] 
                for entry in daily_usage
            ),
            'requests': len(daily_usage)
        }
```

## 🧠 Intelligent Caching

### Cache Configuration

```python
from django_cfg.modules.django_llm.llm.cache import LLMCache

# Custom cache settings
cache = LLMCache(
    cache_dir=Path("cache/llm"),
    ttl=3600,  # 1 hour
    max_size=1000  # Max 1000 cached responses
)

# Cache management
cache_info = cache.get_cache_info()
print(f"Cache size: {cache_info['size']}")
print(f"Hit rate: {cache_info['hit_rate']:.2%}")

# Clear cache
cache.clear_cache()

# Cache specific to model
cache.clear_cache(model="gpt-4o-mini")
```

### Cache Strategies

```python
# Cache with custom key
def cached_completion(prompt, model="gpt-4o-mini", use_cache=True):
    if use_cache:
        cache_key = f"{model}:{hash(prompt)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
    
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model
    )
    
    if use_cache:
        cache.set(cache_key, response, ttl=3600)
    
    return response

# Conditional caching based on cost
def smart_cached_completion(prompt, model="gpt-4o-mini"):
    # Estimate cost
    input_tokens = count_tokens([{"role": "user", "content": prompt}], model)
    estimated_cost = calculate_chat_cost(model, input_tokens, 100)
    
    # Use cache for expensive requests
    use_cache = estimated_cost > 0.01  # Cache if cost > $0.01
    
    return cached_completion(prompt, model, use_cache)
```

## Token Management

### Token Counting

```python
from django_cfg.modules.django_llm.llm.tokenizer import count_tokens, estimate_tokens

# Count tokens in messages
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is machine learning?"}
]

token_count = count_tokens(messages, model="gpt-4o-mini")
print(f"Token count: {token_count}")

# Estimate tokens for text
text = "This is a sample text for token estimation."
estimated = estimate_tokens(text)
print(f"Estimated tokens: {estimated}")

# Token budget management
def manage_token_budget(messages, max_tokens=4000, model="gpt-4o-mini"):
    current_tokens = count_tokens(messages, model)
    
    if current_tokens > max_tokens:
        # Truncate older messages
        while current_tokens > max_tokens and len(messages) > 1:
            messages.pop(1)  # Keep system message, remove oldest user/assistant
            current_tokens = count_tokens(messages, model)
    
    return messages
```

### Usage Analytics

```python
class TokenAnalytics:
    def __init__(self):
        self.usage_stats = {}
    
    def track_usage(self, model, input_tokens, output_tokens, cost):
        if model not in self.usage_stats:
            self.usage_stats[model] = {
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_cost': 0,
                'request_count': 0
            }
        
        stats = self.usage_stats[model]
        stats['total_input_tokens'] += input_tokens
        stats['total_output_tokens'] += output_tokens
        stats['total_cost'] += cost
        stats['request_count'] += 1
    
    def get_model_efficiency(self, model):
        if model not in self.usage_stats:
            return None
        
        stats = self.usage_stats[model]
        total_tokens = stats['total_input_tokens'] + stats['total_output_tokens']
        
        return {
            'cost_per_token': stats['total_cost'] / total_tokens if total_tokens > 0 else 0,
            'avg_tokens_per_request': total_tokens / stats['request_count'],
            'avg_cost_per_request': stats['total_cost'] / stats['request_count']
        }
```

## JSON Extraction

### Structured Data Extraction

```python
from django_cfg.modules.django_llm.llm.extractor import JSONExtractor

extractor = JSONExtractor(client)

# Extract structured data
text = """
John Doe is a 30-year-old software engineer living in San Francisco.
He works at TechCorp and earns $120,000 per year.
"""

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "profession": {"type": "string"},
        "location": {"type": "string"},
        "company": {"type": "string"},
        "salary": {"type": "integer"}
    }
}

result = extractor.extract_json(
    text=text,
    schema=schema,
    model="openai/gpt-4o-mini"
)

print(result)
# Output: {
#   "name": "John Doe",
#   "age": 30,
#   "profession": "software engineer",
#   "location": "San Francisco",
#   "company": "TechCorp",
#   "salary": 120000
# }
```

### Batch Extraction

```python
# Extract from multiple texts
texts = [
    "Alice Smith, 25, designer at CreativeCo",
    "Bob Johnson, 35, manager at BusinessInc",
    "Carol Brown, 28, developer at StartupXYZ"
]

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "role": {"type": "string"},
        "company": {"type": "string"}
    }
}

results = extractor.extract_json_batch(
    texts=texts,
    schema=schema,
    model="openai/gpt-4o-mini"
)

for result in results:
    print(f"{result['name']}: {result['role']} at {result['company']}")
```

## 🌍 Translation Services

### Multi-language Translation

```python
from django_cfg.modules.django_llm.translator import Translator

translator = Translator(client)

# Basic translation
result = translator.translate(
    text="Hello, how are you?",
    target_language="Spanish",
    model="openai/gpt-4o-mini"
)

print(result['translated_text'])
# Output: "Hola, ¿cómo estás?"

# Batch translation
texts = [
    "Good morning",
    "Thank you",
    "Goodbye"
]

results = translator.translate_batch(
    texts=texts,
    target_language="French",
    model="openai/gpt-4o-mini"
)

for original, translated in zip(texts, results):
    print(f"{original} -> {translated['translated_text']}")
```

### Translation with Context

```python
# Translation with context for better accuracy
result = translator.translate(
    text="The bank is closed",
    target_language="Spanish",
    context="Financial institution",
    model="openai/gpt-4o-mini"
)

# vs without context (might translate as river bank)
result_no_context = translator.translate(
    text="The bank is closed",
    target_language="Spanish",
    model="openai/gpt-4o-mini"
)
```

## Real-World Applications

### Content Generation

```python
class ContentGenerator:
    def __init__(self):
        self.client = LLMClient()
    
    def generate_product_description(self, product_name, features, target_audience):
        prompt = f"""
        Generate a compelling product description for {product_name}.
        
        Features: {', '.join(features)}
        Target Audience: {target_audience}
        
        Make it engaging and highlight the key benefits.
        """
        
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-4o-mini",
            temperature=0.7
        )
        
        return response['content']
    
    def generate_blog_post(self, topic, keywords, word_count=800):
        prompt = f"""
        Write a {word_count}-word blog post about {topic}.
        Include these keywords naturally: {', '.join(keywords)}
        
        Structure:
        1. Engaging introduction
        2. Main content with subheadings
        3. Conclusion with call-to-action
        """
        
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-4o-mini",
            temperature=0.8
        )
        
        return response['content']
```

### Data Analysis

```python
class DataAnalyzer:
    def __init__(self):
        self.client = LLMClient()
        self.extractor = JSONExtractor(self.client)
    
    def analyze_customer_feedback(self, feedback_text):
        schema = {
            "type": "object",
            "properties": {
                "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "key_topics": {"type": "array", "items": {"type": "string"}},
                "action_items": {"type": "array", "items": {"type": "string"}},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]}
            }
        }
        
        return self.extractor.extract_json(
            text=feedback_text,
            schema=schema,
            model="openai/gpt-4o-mini"
        )
    
    def summarize_data_trends(self, data_description):
        prompt = f"""
        Analyze the following data and provide insights:
        {data_description}
        
        Provide:
        1. Key trends
        2. Notable patterns
        3. Recommendations
        4. Potential concerns
        """
        
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-4o-mini"
        )
        
        return response['content']
```

### Customer Support

```python
class AICustomerSupport:
    def __init__(self):
        self.client = LLMClient()
    
    def generate_response(self, customer_message, context=None):
        system_prompt = """
        You are a helpful customer support agent. Be polite, professional, 
        and provide accurate information. If you don't know something, 
        say so and offer to escalate to a human agent.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({
                "role": "system", 
                "content": f"Context: {context}"
            })
        
        messages.append({
            "role": "user", 
            "content": customer_message
        })
        
        response = self.client.chat_completion(
            messages=messages,
            model="openai/gpt-4o-mini",
            temperature=0.3  # Lower temperature for consistent responses
        )
        
        return response['content']
    
    def classify_ticket(self, ticket_content):
        schema = {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string", 
                    "enum": ["billing", "technical", "account", "general"]
                },
                "urgency": {
                    "type": "string", 
                    "enum": ["low", "medium", "high", "critical"]
                },
                "requires_human": {"type": "boolean"},
                "suggested_response": {"type": "string"}
            }
        }
        
        return self.extractor.extract_json(
            text=ticket_content,
            schema=schema,
            model="openai/gpt-4o-mini"
        )
```

## Performance Monitoring

### Client Information

```python
# Get comprehensive client info
client_info = client.get_client_info()

print(f"Cache directory: {client_info['cache_directory']}")
print(f"Cache size: {client_info['cache_info']['size']}")
print(f"API keys configured: {client_info['api_keys']}")
print(f"Available models: {len(client_info['available_models'])}")
```

### Usage Monitoring

```python
class LLMMonitor:
    def __init__(self):
        self.usage_log = []
    
    def log_request(self, model, input_tokens, output_tokens, cost, response_time):
        self.usage_log.append({
            'timestamp': datetime.now(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'response_time': response_time
        })
    
    def get_usage_report(self, days=7):
        cutoff = datetime.now() - timedelta(days=days)
        recent_usage = [
            entry for entry in self.usage_log 
            if entry['timestamp'] > cutoff
        ]
        
        if not recent_usage:
            return {}
        
        total_cost = sum(entry['cost'] for entry in recent_usage)
        total_tokens = sum(
            entry['input_tokens'] + entry['output_tokens'] 
            for entry in recent_usage
        )
        avg_response_time = sum(
            entry['response_time'] for entry in recent_usage
        ) / len(recent_usage)
        
        return {
            'total_requests': len(recent_usage),
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'avg_response_time': avg_response_time,
            'cost_per_token': total_cost / total_tokens if total_tokens > 0 else 0
        }
```

## Related Documentation

- [**Module System Overview**](./overview) - Django-CFG modules
- [**AI Agents**](/ai-agents/introduction) - AI agent integration
- [**Knowledge Base**](/features/built-in-apps/ai-knowledge/knowbase-setup) - Knowledge base with LLM
- [**Configuration Guide**](/fundamentals/configuration) - Module configuration

The LLM module provides comprehensive AI integration for your Django applications! 🤖

TAGS: llm, ai, openai, chat-completion, embeddings, cost-tracking, caching
DEPENDS_ON: [configuration, caching, api-keys]
USED_BY: [agents, knowbase, content-generation, customer-support]
