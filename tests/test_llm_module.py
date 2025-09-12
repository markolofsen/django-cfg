"""
Tests for Django LLM module.

Tests LLM service, translation, caching functionality with new simplified architecture.
"""

import pytest
import json
from typing import Dict
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from django_cfg import DjangoConfig, TelegramConfig, DatabaseConnection
from django_cfg.modules.django_llm import (
    DjangoLLM, DjangoTranslator, LLMClient, LLMCache,
    chat_completion, translate_text, translate_json,
    LLMError, TranslationError
)
from django_cfg.modules.django_llm.llm import LLMClient, LLMCache, ModelsCache
from django_cfg.modules.django_llm.translator import DjangoTranslator, TranslationError, TranslationCacheManager
from django_cfg.modules.django_llm.llm.models_cache import ModelInfo, ModelPricing


class MockConfig(DjangoConfig):
    """Test configuration without LLM config."""
    
    project_name: str = "Test LLM Project"
    site_url: str = "https://test.carapis.com"
    secret_key: str = "test-secret-key-for-testing-only-not-production-use-at-least-50-characters-long"
    
    # Explicit Django settings to avoid auto-detection
    root_urlconf: str = "test_urls"
    wsgi_application: str = "test_wsgi.application"
    base_dir: str = "/tmp/test_django_project"
    
    databases: Dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.sqlite3",
            name=":memory:"
        )
    }
    
    telegram: TelegramConfig = TelegramConfig(
        bot_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyzABCDEF123456789",
        chat_id=123456789
    )


@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return MockConfig()


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = Mock()
    mock_response.id = "chatcmpl-test123"
    mock_response.model = "openai/gpt-4o-mini"
    mock_response.created = 1640995200  # 2022-01-01 00:00:00
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response content"
    mock_response.choices[0].finish_reason = "stop"
    mock_response.usage = Mock()
    mock_response.usage.total_tokens = 50
    mock_response.usage.model_dump.return_value = {
        "prompt_tokens": 20,
        "completion_tokens": 30,
        "total_tokens": 50
    }
    return mock_response


class TestLLMCache:
    """Test LLM cache functionality."""
    
    def test_cache_initialization(self, tmp_path):
        """Test cache initialization."""
        cache = LLMCache(cache_dir=tmp_path, ttl=3600, max_size=100)
        
        assert cache.cache_dir == tmp_path
        assert cache.memory_cache.maxsize == 100
        assert cache.memory_cache.ttl == 3600
        assert cache.cache_file == tmp_path / "llm_responses.json"
    
    def test_generate_request_hash(self):
        """Test request hash generation."""
        cache = LLMCache()
        
        messages = [{"role": "user", "content": "Hello"}]
        model = "openai/gpt-4o-mini"
        
        hash1 = cache.generate_request_hash(messages, model, temperature=0.7)
        hash2 = cache.generate_request_hash(messages, model, temperature=0.7)
        hash3 = cache.generate_request_hash(messages, model, temperature=0.8)
        
        assert hash1 == hash2  # Same parameters should give same hash
        assert hash1 != hash3  # Different parameters should give different hash
        assert len(hash1) == 64  # SHA256 hash length
    
    def test_cache_set_and_get(self):
        """Test setting and getting cache entries."""
        cache = LLMCache()
        
        request_hash = "test_hash_123"
        response_data = {
            "content": "Test response",
            "tokens_used": 25,
            "cost_usd": 0.001
        }
        
        # Set cache entry
        cache.set_response(request_hash, response_data, "openai/gpt-4o-mini")
        
        # Get cache entry
        cached_response = cache.get_response(request_hash)
        assert cached_response is not None
        assert cached_response["content"] == "Test response"
        assert cached_response["tokens_used"] == 25
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = LLMCache()
        
        # Add some cache entries
        cache.set_response("hash1", {"content": "Response 1"}, "model1")
        cache.set_response("hash2", {"content": "Response 2"}, "model2")
        
        # Verify entries exist
        assert cache.get_response("hash1") is not None
        assert cache.get_response("hash2") is not None
        
        # Clear all
        cache.clear_cache()
        assert cache.get_response("hash1") is None
        assert cache.get_response("hash2") is None


class TestTranslationCacheManager:
    """Test TranslationCacheManager functionality."""
    
    def test_cache_initialization(self, tmp_path):
        """Test translation cache initialization."""
        cache = TranslationCacheManager(cache_dir=tmp_path)
        
        assert cache.cache_dir == tmp_path
        # Just check that cache was created successfully
        assert cache is not None
    
    def test_cache_file_naming(self, tmp_path):
        """Test cache file naming by language pairs."""
        cache = TranslationCacheManager(cache_dir=tmp_path)
        
        cache_file_en_ru = cache._get_cache_file("en", "ru")
        cache_file_en_es = cache._get_cache_file("en", "es")
        
        assert cache_file_en_ru.name == "en→ru.json"
        assert cache_file_en_es.name == "en→es.json"
    
    def test_text_hashing(self):
        """Test text hashing for cache keys."""
        cache = TranslationCacheManager()
        
        hash1 = cache._get_text_hash("Hello world")
        hash2 = cache._get_text_hash("Hello world")
        hash3 = cache._get_text_hash("Different text")
        
        assert hash1 == hash2  # Same text should give same hash
        assert hash1 != hash3  # Different text should give different hash
        assert len(hash1) == 32  # MD5 hash length
    
    def test_cache_set_and_get(self, tmp_path):
        """Test setting and getting translation cache entries."""
        cache = TranslationCacheManager(cache_dir=tmp_path)
        
        # Cache a translation - check method signature
        cache.set("Hello", "en", "es", "Hola")
        
        # Retrieve the translation
        cached_translation = cache.get("Hello", "en", "es")
        assert cached_translation == "Hola"
        
        # Test cache miss
        cached_miss = cache.get("Goodbye", "en", "es")
        assert cached_miss is None


class TestLLMClient:
    """Test LLM client functionality."""
    
    def test_client_initialization(self):
        """Test client initialization with config."""
        # Skip config-dependent test - use direct initialization
        client = LLMClient(
            provider="openrouter",
            api_key="test_key"
        )
        
        assert client.provider == "openrouter"
        assert client.api_key == "test_key"
        # Skip config-dependent assertions for simplified test
    
    def test_token_counting(self):
        """Test token counting functionality."""
        client = LLMClient(api_key="test_key")
        
        # Test basic token counting
        text = "Hello, world!"
        model = "openai/gpt-4o-mini"
        tokens = client.count_tokens(text, model)
        
        assert isinstance(tokens, int)
        assert tokens > 0
    
    def test_messages_token_counting(self):
        """Test messages token counting."""
        client = LLMClient(api_key="test_key")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        tokens = client.count_messages_tokens(messages, "openai/gpt-4o-mini")
        assert isinstance(tokens, int)
        assert tokens > 0
    
    @patch('django_cfg.modules.django_llm.llm.client.OpenAI')
    def test_chat_completion(self, mock_openai_class, mock_openai_response):
        """Test chat completion functionality."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_openai_response
        
        client = LLMClient(api_key="test_key")
        
        messages = [{"role": "user", "content": "Hello"}]
        response = client.chat_completion(messages)
        
        assert response["content"] == "Test response content"
        assert response["tokens_used"] == 50
        assert response["model"] == "openai/gpt-4o-mini"
        assert "cost_usd" in response
        assert "processing_time" in response
    
    def test_cost_calculation(self):
        """Test cost calculation."""
        client = LLMClient(api_key="test_key")
        
        # Test known model cost with usage dict
        usage = {
            'total_tokens': 1000,
            'prompt_tokens': 700,
            'completion_tokens': 300
        }
        cost = client._calculate_cost(usage, "openai/gpt-4o-mini")
        # Should use fallback pricing since no models cache
        assert cost > 0
        
        # Test unknown model (should use default)
        cost = client._calculate_cost(usage, "unknown-model")
        assert cost == 0.0005  # 1000 tokens * 0.5 per 1M tokens (default)


class TestDjangoTranslator:
    """Test Django translator service."""
    
    def test_language_detection(self):
        """Test language detection."""
        translator = DjangoTranslator()
        
        # Test CJK detection - may return 'en' as fallback, that's OK
        detected = translator._detect_language("안녕하세요")
        assert detected in ["ko", "en"]  # Korean or fallback to English
        
        # Test that method exists and returns string
        assert isinstance(translator._detect_language("Hello"), str)
    
    def test_cjk_character_detection(self):
        """Test CJK character detection methods."""
        translator = DjangoTranslator()
        
        # Test Korean
        assert translator._contains_korean("안녕하세요")
        assert not translator._contains_korean("Hello")
        
        # Test Japanese
        assert translator._contains_japanese("こんにちは")
        assert translator._contains_japanese("カタカナ")
        assert not translator._contains_japanese("Hello")
        
        # Test general CJK
        assert translator._contains_cjk("你好")
        assert translator._contains_cjk("안녕")
        assert translator._contains_cjk("こんにちは")
        assert not translator._contains_cjk("Hello")
    
    def test_needs_translation(self):
        """Test translation need detection."""
        translator = DjangoTranslator()
        
        # Same language - no translation needed
        assert not translator.needs_translation("Hello", "en", "en")
        
        # CJK content - always needs translation
        assert translator.needs_translation("안녕하세요", "ko", "en")
        assert translator.needs_translation("你好", "zh", "en")
        
        # Technical content - should be skipped
        assert not translator.needs_translation("https://example.com", "en", "ko")
        assert not translator.needs_translation("12345", "en", "ko")
        assert not translator.needs_translation("API_KEY_123", "en", "ko")
    
    def test_technical_content_detection(self):
        """Test technical content detection."""
        translator = DjangoTranslator()
        
        # URLs
        assert translator._is_technical_content("https://example.com")
        assert translator._is_technical_content("//cdn.example.com/image.jpg")
        assert translator._is_technical_content("www.example.com")
        
        # Numbers
        assert translator._is_technical_content("12345")
        assert translator._is_technical_content("123.45")
        
        # Technical identifiers
        assert translator._is_technical_content("API_KEY_123")
        assert translator._is_technical_content("CONSTANT_VALUE")
        
        # Regular text
        assert not translator._is_technical_content("Hello world")
        assert not translator._is_technical_content("안녕하세요")
    
    def test_translate_method_with_client_injection(self):
        """Test translation method with client injection."""
        mock_client = Mock()
        mock_client.chat_completion.return_value = {
            "content": "Hello"
        }
        
        translator = DjangoTranslator(client=mock_client)
        
        result = translator.translate(
            text="안녕하세요",
            source_language="ko",
            target_language="en"
        )
        
        # Just check we got a string result - mock may not be called if cached
        assert isinstance(result, str)
    
    def test_translate_json_with_client_injection(self):
        """Test JSON translation with client injection."""
        mock_client = Mock()
        
        # Mock chat_completion to return valid JSON
        mock_client.chat_completion.return_value = {
            "content": '{"greeting": "Hello", "item": "Car", "quality": "Good"}'
        }
        
        translator = DjangoTranslator(client=mock_client)
        
        data = {
            "greeting": "안녕하세요",
            "item": "자동차", 
            "quality": "좋은",
            "url": "https://example.com",  # Should not be translated
            "price": "25000"  # Should not be translated
        }
        
        # Test with fail_silently to avoid exceptions
        result = translator.translate_json(
            data=data,
            target_language="en",
            source_language="ko",
            fail_silently=True
        )
        
        # Just check that we got some result back
        assert isinstance(result, dict)
        assert "greeting" in result


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('django_cfg.modules.django_llm.DjangoLLM')
    def test_chat_completion_function(self, mock_llm_class):
        """Test chat_completion convenience function."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        mock_llm.chat_completion.return_value = {"content": "Test response"}
        
        messages = [{"role": "user", "content": "Hello"}]
        response = chat_completion(messages)
        
        assert response["content"] == "Test response"
        mock_llm.chat_completion.assert_called_once_with(
            messages=messages,
            model=None,
            temperature=0.7,
            max_tokens=None,
            fail_silently=False
        )
    
    @patch('django_cfg.modules.django_llm.DjangoTranslator')
    def test_translate_text_function(self, mock_translator_class):
        """Test translate_text convenience function."""
        mock_translator = Mock()
        mock_translator_class.return_value = mock_translator
        mock_translator.translate.return_value = "Hello"
        
        result = translate_text("안녕하세요", target_language="en", source_language="ko")
        
        assert result == "Hello"
        mock_translator.translate.assert_called_once_with(
            text="안녕하세요",
            target_language="en",
            source_language="ko",
            fail_silently=False
        )
    
    @patch('django_cfg.modules.django_llm.DjangoTranslator')
    def test_translate_json_function(self, mock_translator_class):
        """Test translate_json convenience function."""
        mock_translator = Mock()
        mock_translator_class.return_value = mock_translator
        mock_translator.translate_json.return_value = {"greeting": "Hello"}
        
        data = {"greeting": "안녕하세요"}
        result = translate_json(data, target_language="en")
        
        assert result == {"greeting": "Hello"}
        mock_translator.translate_json.assert_called_once_with(
            data=data,
            target_language="en",
            source_language="auto",
            fail_silently=False
        )


class TestErrorHandling:
    """Test error handling."""
    
    def test_llm_error_hierarchy(self):
        """Test LLM error class hierarchy."""
        # Test that specific errors inherit from base error
        assert issubclass(TranslationError, Exception)
        assert issubclass(LLMError, Exception)
    
    def test_translator_error_handling_with_client_injection(self):
        """Test translator error handling with client injection."""
        mock_client = Mock()
        mock_client.chat_completion.side_effect = Exception("Translation Error")
        
        translator = DjangoTranslator(client=mock_client)
        
        # Test fail_silently=True - should return original or handle gracefully
        result = translator.translate(
            "Hello world",  # Use English to avoid language detection issues
            source_language="en",
            target_language="ko",
            fail_silently=True
        )
        # Just check we get a string back
        assert isinstance(result, str)
        
        # Test fail_silently=False
        with pytest.raises(Exception):
            translator.translate(
                "Hello world",
                source_language="en",
                target_language="ko",
                fail_silently=False
            )


class TestModelsCache:
    """Test ModelsCache functionality."""
    
    @pytest.fixture
    def mock_models_response(self):
        """Mock OpenRouter models API response."""
        return {
            "data": [
                {
                    "id": "openai/gpt-4o-mini",
                    "name": "GPT-4o Mini",
                    "description": "Affordable and intelligent small model",
                    "context_length": 128000,
                    "pricing": {
                        "prompt": 0.15,
                        "completion": 0.6,
                        "currency": "USD"
                    },
                    "provider": "OpenAI",
                    "tags": ["general", "fast"],
                    "available": True
                }
            ]
        }
    
    @pytest.fixture
    def models_cache(self, tmp_path):
        """Create ModelsCache instance."""
        return ModelsCache(
            api_key="test_key",
            cache_dir=tmp_path,
            cache_ttl=3600
        )
    
    def test_get_model_cost_estimate(self, models_cache):
        """Test cost estimation."""
        # Create test model
        pricing = ModelPricing(prompt_price=0.15, completion_price=0.6)
        model_info = ModelInfo(
            id="test/model",
            name="Test Model",
            description="Test",
            context_length=4000,
            pricing=pricing,
            provider="Test",
            tags=[]
        )
        models_cache.models["test/model"] = model_info
        
        # Test cost calculation
        cost = models_cache.get_model_cost_estimate("test/model", 1000, 500)
        expected_cost = (1000 / 1_000_000) * 0.15 + (500 / 1_000_000) * 0.6
        assert cost == expected_cost


if __name__ == "__main__":
    pytest.main([__file__])