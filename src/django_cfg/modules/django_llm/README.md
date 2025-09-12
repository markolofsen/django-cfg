# Django LLM Module

🚀 **Auto-configuring LLM and translation service for django-cfg**

A comprehensive LLM and translation module that integrates seamlessly with DjangoConfig, featuring multiple providers, intelligent caching, and beautiful YAML export functionality.

## ✨ Features

- **🤖 Universal LLM Client**: Support for OpenRouter, OpenAI, and other providers
- **📁 YAML Caching**: Beautiful, human-readable cache files with comments
- **⚡ TTL Memory Cache**: Fast in-memory caching with automatic expiration
- **🌍 Smart Translation**: Automatic language detection with CJK support
- **🔧 Auto-Configuration**: Seamless integration with DjangoConfig
- **📊 Token Counting**: Accurate token counting with tiktoken integration
- **🎨 Pretty Export**: Export cache to formatted YAML with descriptions
- **🔔 Telegram Integration**: Send LLM alerts via Telegram

## 🚀 Quick Start

### Basic LLM Usage

```python
from django_cfg.modules.django_llm import DjangoLLM

# Initialize service (auto-configured)
llm = DjangoLLM()

# Chat completion
messages = [
    {"role": "user", "content": "What is the capital of France?"}
]
response = llm.chat_completion(messages)
print(response['content'])

# Generate text
text = llm.generate_text("Write a short poem about cars")
print(text)

# Generate JSON
json_data = llm.generate_json("Create a JSON object with car information")
print(json_data)
```

### Translation Services

```python
from django_cfg.modules.django_llm import DjangoTranslator

# Initialize translator (auto-configured)
translator = DjangoTranslator()

# Translate text
translated = translator.translate(
    text="안녕하세요",
    source_language="ko",
    target_language="en"
)
print(translated)  # "Hello"

# Translate JSON with CJK detection
data = {
    "title": "Car for sale",
    "description": "这是一辆很好的车",
    "features": ["GPS", "空调系统", "Leather seats"]
}

translated_data = translator.translate_json(
    data=data,
    target_language="en",
    source_language="zh"
)
print(translated_data)
```

### Convenience Functions

```python
from django_cfg.modules.django_llm import chat_completion, translate_text, translate_json

# Quick chat completion
response = chat_completion([
    {"role": "user", "content": "Hello, how are you?"}
])

# Quick translation
text = translate_text("Bonjour le monde", target_language="en", source_language="fr")

# Quick JSON translation
data = translate_json({"greeting": "Hola mundo"}, target_language="en")
```

## 📁 YAML Caching

The module uses beautiful YAML files for caching with automatic comments:

```yaml
# LLM Responses Cache - Django CFG
# Generated: 2024-01-15 14:30:25 UTC
# Total responses: 15
# TTL: 24 hours
# Auto-generated - do not edit manually

cache_info:
  version: '1.0'
  format: 'YAML'
  description: 'LLM responses cache for Django CFG'
  last_updated: '2024-01-15 14:30:25 UTC'
  total_responses: 15
  ttl_hours: 24

# Cached Responses
responses:
  # Model: openai/gpt-4o-mini, Cached: 2024-01-15T14:30:25.123456
  # Preview: Hello! I'm doing well, thank you for asking...
  a1b2c3d4e5f6:
    id: chatcmpl-8abc123
    model: openai/gpt-4o-mini
    content: "Hello! I'm doing well, thank you for asking."
    tokens_used: 25
    cost_usd: 0.000375
    processing_time: 1.2
    cached_at: '2024-01-15T14:30:25.123456'
```

## 🔧 Configuration

### DjangoConfig Integration

```python
from django_cfg import DjangoConfig
from django_cfg.models.services import LLMConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Project"
    
    # LLM configuration
    llm: LLMConfig = LLMConfig(
        provider="openrouter",  # or "openai"
        api_key="${OPENROUTER_API_KEY}",
        default_model="openai/gpt-4o-mini",
        default_temperature=0.7,
        cache_dir="/path/to/cache"  # optional
    )
    
    # Telegram integration (optional)
    telegram: TelegramConfig = TelegramConfig(
        bot_token="your_bot_token",
        chat_id="your_chat_id"
    )

config = MyConfig()
```

### Environment Variables

```bash
# Required
export OPENROUTER_API_KEY="your_openrouter_key"
# or
export OPENAI_API_KEY="your_openai_key"

# Optional
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

## 🌍 Translation Features

### CJK Language Support

The translator has enhanced support for Chinese, Japanese, and Korean:

```python
translator = DjangoTranslator()

# Chinese
chinese_text = translator.translate("这是一辆汽车", target_language="en")
print(chinese_text)  # "This is a car"

# Korean
korean_text = translator.translate("안녕하세요", target_language="en")
print(korean_text)  # "Hello"

# Japanese
japanese_text = translator.translate("こんにちは", target_language="en")
print(japanese_text)  # "Hello"

# Mixed content with automatic detection
mixed_data = {
    "title": "Car Sale",
    "description": "这辆车很好 - 현대 자동차",
    "price": "$25,000"
}
translated = translator.translate_json(mixed_data, target_language="en")
```

### Smart Content Detection

The translator automatically skips technical content:

```python
data = {
    "title": "汽车销售",  # Will be translated
    "url": "https://example.com/car.jpg",  # Will be skipped
    "id": "CAR_12345",  # Will be skipped
    "price": "25000",  # Will be skipped
    "description": "这是一辆很好的车"  # Will be translated
}

result = translator.translate_json(data, target_language="en")
# Only title and description are translated
```

## 📊 Advanced Features

### Token Counting and Cost Estimation

```python
llm = DjangoLLM()

# Count tokens
text = "Hello, how are you today?"
tokens = llm.count_tokens(text, model="openai/gpt-4o-mini")
print(f"Tokens: {tokens}")

# Estimate cost
cost = llm.estimate_cost(
    input_tokens=100,
    output_tokens=50,
    model="openai/gpt-4o-mini"
)
print(f"Estimated cost: ${cost:.6f}")

# Get usage statistics
stats = llm.get_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Total cost: ${stats['total_cost_usd']:.4f}")
```

### Cache Management

```python
llm = DjangoLLM()

# Get cache information
cache_info = llm.get_config_info()
print(f"Cache directory: {cache_info['cache_directory']}")
print(f"Memory cache size: {cache_info['cache_info']['memory_cache']['size']}")

# Export cache to YAML
yaml_content = llm.cache.export_cache_yaml()
print(yaml_content)

# Save to file
from pathlib import Path
output_file = Path('llm_cache_export.yaml')
llm.cache.export_cache_yaml(output_file)

# Clear cache
llm.clear_cache()
```

### Translation Statistics

```python
translator = DjangoTranslator()

# Get translation statistics
stats = translator.get_stats()
print(f"Total translations: {stats['total_translations']}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Language pairs: {stats['language_pairs']}")
print(f"Total cost: ${stats['total_cost_usd']:.4f}")

# Get configuration info
config_info = translator.get_config_info()
print(f"Supported languages: {config_info['supported_languages']}")
```

## 🎨 Export and Monitoring

### YAML Cache Export

```python
llm = DjangoLLM()

# Export cache with detailed information
yaml_content = llm.cache.export_cache_yaml()

# The export includes:
# - Cache metadata and statistics
# - Response previews and model information
# - Formatted YAML with comments
# - Token usage and cost information

# Save to custom location
from pathlib import Path
export_path = Path('/path/to/exports/llm_cache.yaml')
llm.cache.export_cache_yaml(export_path)
```

### Telegram Alerts

```python
from django_cfg.modules.django_llm import DjangoLLM, DjangoTranslator

# Send LLM alerts
DjangoLLM.send_llm_alert(
    "High token usage detected!",
    context={
        "tokens_used": 50000,
        "cost_usd": 0.75,
        "model": "openai/gpt-4o"
    }
)

# Send translation alerts
DjangoTranslator.send_translation_alert(
    "Translation batch completed",
    context={
        "texts_translated": 100,
        "languages": "ko->en",
        "cost_usd": 0.25
    }
)
```

## 🧪 Testing

### Basic Testing

```python
import pytest
from django_cfg.modules.django_llm import DjangoLLM, DjangoTranslator

def test_llm_chat_completion():
    llm = DjangoLLM()
    
    if llm.is_configured:
        messages = [{"role": "user", "content": "Hello"}]
        response = llm.chat_completion(messages)
        
        assert 'content' in response
        assert response['content']
        assert 'tokens_used' in response

def test_translation():
    translator = DjangoTranslator()
    
    if translator.is_configured:
        result = translator.translate(
            text="Hello world",
            source_language="en",
            target_language="es"
        )
        
        assert result
        assert result != "Hello world"  # Should be translated

def test_json_translation():
    translator = DjangoTranslator()
    
    data = {
        "greeting": "Hello",
        "url": "https://example.com",
        "number": "123"
    }
    
    result = translator.translate_json(
        data=data,
        source_language="en",
        target_language="es"
    )
    
    # Only greeting should be translated
    assert result["url"] == data["url"]  # URL unchanged
    assert result["number"] == data["number"]  # Number unchanged
```

## 📦 Dependencies

### Production Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.8"
pydantic = "^2.4.0"
pyyaml = "^6.0"
cachetools = "^5.3.0"
openai = "^1.3.0"  # optional
tiktoken = "^0.5.0"  # optional
```

### Optional Dependencies

- `openai`: For OpenAI API integration
- `tiktoken`: For accurate token counting
- `fast-langdetect`: For enhanced language detection

## 🔍 Error Handling

### Common Scenarios

```python
from django_cfg.modules.django_llm import DjangoLLM, LLMError, TranslationError

try:
    llm = DjangoLLM()
    response = llm.chat_completion([
        {"role": "user", "content": "Hello"}
    ])
except LLMError as e:
    print(f"LLM error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

# Graceful error handling
llm = DjangoLLM()
response = llm.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    fail_silently=True
)
# Returns empty dict on error when fail_silently=True
```

## 🎯 Use Cases

### E-commerce Translation

```python
translator = DjangoTranslator()

# Translate product data
product_data = {
    "name": "스마트폰",
    "description": "최신 기술이 적용된 스마트폰입니다",
    "features": ["5G", "카메라", "배터리"],
    "price": "$599",
    "sku": "PHONE_001"
}

translated_product = translator.translate_json(
    data=product_data,
    source_language="ko",
    target_language="en"
)
```

### Content Generation

```python
llm = DjangoLLM()

# Generate product descriptions
prompt = "Write a compelling product description for a luxury car"
description = llm.generate_text(prompt, temperature=0.8)

# Generate structured data
prompt = "Create a JSON object with car specifications"
car_specs = llm.generate_json(prompt)
```

### Multilingual Support

```python
translator = DjangoTranslator()

# Support multiple languages
languages = ["es", "fr", "de", "it", "pt"]
content = {"title": "Welcome", "message": "Hello world"}

translations = {}
for lang in languages:
    translations[lang] = translator.translate_json(
        data=content,
        source_language="en",
        target_language=lang
    )
```

## 🔗 Integration with Django CFG

The module automatically integrates with other django-cfg services:

- **📧 Email Service**: Send LLM reports via email
- **📱 Telegram Service**: Send notifications to Telegram
- **📊 Logger Service**: Structured logging with configuration
- **⚙️ Configuration**: Auto-discovery of DjangoConfig settings

## 📈 Performance

- **Memory Cache**: Sub-millisecond lookups for cached responses
- **File Cache**: ~10ms for file-based cache hits  
- **API Calls**: ~200-2000ms for fresh data from LLM providers
- **Token Counting**: ~1ms with tiktoken for accurate counting
- **YAML Export**: ~50ms for 100+ cached responses with formatting

## 🛠️ Development

### Project Structure

```
django_llm/
├── __init__.py          # Public API exports
├── service.py           # Main DjangoLLM service
├── translator.py        # Translation service
├── client.py            # Universal LLM client
├── cache.py             # YAML caching system
└── README.md           # This file
```

### Contributing

1. Follow django-cfg module patterns
2. Use YAML for configuration files
3. Include comprehensive error handling
4. Add tests for new features
5. Update documentation

---

**Made with ❤️ for the Django CFG ecosystem**

*Intelligent LLM and translation services with beautiful caching and seamless Django integration.*
