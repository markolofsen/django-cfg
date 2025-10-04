"""
Example usage of Django LLM module.

Demonstrates LLM and translation functionality with django-cfg integration.
"""

import asyncio
import json
from pathlib import Path
from django_cfg import DjangoConfig, LLMConfig, TelegramConfig, DjangoLLM, DjangoTranslator

class ExampleConfig(DjangoConfig):
    """Example configuration with LLM support."""
    
    project_name: str = "LLM Example Project"
    
    # LLM configuration
    llm: LLMConfig = LLMConfig(
        provider="openrouter",
        api_key="${OPENROUTER_API_KEY}",
        default_model="openai/gpt-4o-mini",
        default_temperature=0.7,
        enable_translation=True,
        cost_tracking=True,
        usage_alerts=True
    )
    
    # Optional: Telegram for alerts
    telegram: TelegramConfig = TelegramConfig(
        bot_token="${TELEGRAM_BOT_TOKEN}",
        chat_id="${TELEGRAM_CHAT_ID}"
    )


async def example_llm_usage():
    """Example LLM usage."""
    print("🤖 Testing Django LLM Module...")
    print("=" * 50)
    
    # Import after config is set
    from django_cfg.modules.django_llm import DjangoLLM, chat_completion
    
    # Initialize LLM service
    llm = DjangoLLM()
    
    if not llm.is_configured:
        print("❌ LLM service is not configured. Please set OPENROUTER_API_KEY.")
        return
    
    print("✅ LLM service is configured")
    
    # Test chat completion
    print("\n💬 Chat Completion:")
    messages = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    try:
        response = llm.chat_completion(messages)
        print(f"✅ Response: {response.get('content', 'No content')}")
        print(f"📊 Tokens used: {response.get('tokens_used', 0)}")
        print(f"💰 Cost: ${response.get('cost_usd', 0):.6f}")
    except Exception as e:
        print(f"❌ Chat completion failed: {e}")
    
    # Test text generation
    print("\n📝 Text Generation:")
    try:
        text = llm.generate_text("Write a haiku about programming")
        print(f"✅ Generated text:\n{text}")
    except Exception as e:
        print(f"❌ Text generation failed: {e}")
    
    # Test JSON generation
    print("\n📋 JSON Generation:")
    try:
        json_data = llm.generate_json(
            "Create a JSON object with information about a car: make, model, year, price"
        )
        print(f"✅ Generated JSON:")
        print(json.dumps(json_data, indent=2))
    except Exception as e:
        print(f"❌ JSON generation failed: {e}")
    
    # Test convenience function
    print("\n🚀 Convenience Function:")
    try:
        response = chat_completion([
            {"role": "user", "content": "Hello, how are you?"}
        ])
        print(f"✅ Convenience response: {response.get('content', 'No content')}")
    except Exception as e:
        print(f"❌ Convenience function failed: {e}")
    
    # Get statistics
    print("\n📊 Statistics:")
    stats = llm.get_stats()
    print(f"Total requests: {stats.get('total_requests', 0)}")
    print(f"Successful requests: {stats.get('successful_requests', 0)}")
    print(f"Cache hits: {stats.get('cache_hits', 0)}")
    print(f"Total cost: ${stats.get('total_cost_usd', 0):.6f}")


async def example_translation_usage():
    """Example translation usage."""
    print("\n🌐 Testing Django Translation Module...")
    print("=" * 50)
    
    
    # Initialize translator
    translator = DjangoTranslator()
    
    if not translator.is_configured:
        print("❌ Translation service is not configured. Please set OPENROUTER_API_KEY.")
        return
    
    print("✅ Translation service is configured")
    
    # Test simple translation
    print("\n🔤 Simple Translation:")
    try:
        translated = translator.translate(
            text="안녕하세요, 세계!",
            source_language="ko",
            target_language="en"
        )
        print(f"✅ Korean to English: {translated}")
    except Exception as e:
        print(f"❌ Translation failed: {e}")
    
    # Test CJK translation
    print("\n🈳 CJK Translation:")
    cjk_texts = [
        ("这是一辆很好的汽车", "zh", "Chinese"),
        ("これは良い車です", "ja", "Japanese"),
        ("이것은 좋은 차입니다", "ko", "Korean")
    ]
    
    for text, lang, lang_name in cjk_texts:
        try:
            translated = translator.translate(
                text=text,
                source_language=lang,
                target_language="en"
            )
            print(f"✅ {lang_name}: {text} → {translated}")
        except Exception as e:
            print(f"❌ {lang_name} translation failed: {e}")
    
    # Test JSON translation
    print("\n📄 JSON Translation:")
    car_data = {
        "title": "자동차 판매",  # Korean
        "description": "这是一辆很好的车",  # Chinese
        "features": ["GPS", "エアコン", "가죽 시트"],  # Mixed: English, Japanese, Korean
        "url": "https://example.com/car.jpg",  # Should be skipped
        "price": "$25,000",  # Should be skipped
        "id": "CAR_12345"  # Should be skipped
    }
    
    try:
        translated_data = translator.translate_json(
            data=car_data,
            target_language="en",
            source_language="auto"
        )
        print("✅ Translated JSON:")
        print(json.dumps(translated_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ JSON translation failed: {e}")
    
    # Test convenience functions
    print("\n🚀 Convenience Functions:")
    try:
        # Quick text translation
        quick_text = translate_text("Bonjour le monde", target_language="en", source_language="fr")
        print(f"✅ Quick translation: {quick_text}")
        
        # Quick JSON translation
        quick_json = translate_json(
            {"greeting": "Hola mundo", "url": "https://example.com"},
            target_language="en"
        )
        print(f"✅ Quick JSON: {quick_json}")
    except Exception as e:
        print(f"❌ Convenience functions failed: {e}")
    
    # Get translation statistics
    print("\n📊 Translation Statistics:")
    stats = translator.get_stats()
    print(f"Total translations: {stats.get('total_translations', 0)}")
    print(f"Cache hits: {stats.get('cache_hits', 0)}")
    print(f"Cache misses: {stats.get('cache_misses', 0)}")
    print(f"Language pairs: {stats.get('language_pairs', {})}")
    print(f"Total cost: ${stats.get('total_cost_usd', 0):.6f}")


async def example_cache_management():
    """Example cache management."""
    print("\n💾 Testing Cache Management...")
    print("=" * 50)
    
    from django_cfg.modules.django_llm import DjangoLLM
    
    llm = DjangoLLM()
    
    if not llm.is_configured:
        print("❌ LLM service is not configured.")
        return
    
    # Get cache information
    print("📋 Cache Information:")
    config_info = llm.get_config_info()
    cache_info = config_info.get('cache_info', {})
    
    print(f"Cache directory: {config_info.get('cache_directory')}")
    print(f"Memory cache size: {cache_info.get('memory_cache', {}).get('size', 0)}")
    print(f"File cache exists: {cache_info.get('file_cache', {}).get('exists', False)}")
    
    # Test cache export
    print("\n📤 Cache Export:")
    try:
        yaml_content = llm.cache.export_cache_yaml()
        print("✅ Cache exported to YAML:")
        print(yaml_content[:500] + "..." if len(yaml_content) > 500 else yaml_content)
        
        # Save to file
        export_file = Path("llm_cache_export.yaml")
        llm.cache.export_cache_yaml(export_file)
        print(f"✅ Cache saved to: {export_file}")
        
    except Exception as e:
        print(f"❌ Cache export failed: {e}")


async def example_alerts():
    """Example alert functionality."""
    print("\n🔔 Testing Alert Functionality...")
    print("=" * 50)
    
    
    # Test LLM alerts
    print("🤖 Sending LLM Alert:")
    try:
        DjangoLLM.send_llm_alert(
            "Test LLM alert from django-cfg",
            context={
                "module": "django_llm",
                "status": "testing",
                "timestamp": "2024-01-15 14:30:25"
            }
        )
        print("✅ LLM alert sent (check Telegram)")
    except Exception as e:
        print(f"❌ LLM alert failed: {e}")
    
    # Test translation alerts
    print("\n🌐 Sending Translation Alert:")
    try:
        DjangoTranslator.send_translation_alert(
            "Test translation alert from django-cfg",
            context={
                "texts_processed": 5,
                "languages": "ko->en, zh->en, ja->en",
                "cost_usd": 0.025
            }
        )
        print("✅ Translation alert sent (check Telegram)")
    except Exception as e:
        print(f"❌ Translation alert failed: {e}")


async def example_models_cache():
    """Example of using models cache for dynamic pricing."""
    print("\n📊 Models Cache Example")
    print("-" * 30)
    
    try:
        # Initialize LLM service
        llm_service = DjangoLLM()
        
        if not llm_service.is_configured:
            print("⚠️  LLM service not configured, skipping models cache example")
            return
        
        client = llm_service.client
        
        if not client.models_cache:
            print("⚠️  Models cache not available for this provider")
            return
        
        print("🔄 Fetching models from OpenRouter API...")
        models = await client.fetch_models()
        print(f"✅ Fetched {len(models)} models")
        
        # Get models summary
        summary = client.get_models_summary()
        print(f"📈 Total models: {summary.get('total_models', 0)}")
        print(f"📈 Available models: {summary.get('available_models', 0)}")
        print(f"📈 Free models: {summary.get('free_models_count', 0)}")
        print(f"📈 Budget models: {summary.get('budget_models_count', 0)}")
        
        # Show some free models
        free_models = client.get_free_models()
        if free_models:
            print(f"\n🆓 Free models ({len(free_models)}):")
            for model in free_models[:3]:  # Show first 3
                print(f"  • {model.name} ({model.provider})")
        
        # Show budget models
        budget_models = client.get_budget_models(max_price=1.0)
        if budget_models:
            print(f"\n💰 Budget models ≤$1.0/1M tokens ({len(budget_models)}):")
            for model in budget_models[:3]:  # Show first 3
                print(f"  • {model.name}: ${model.pricing.prompt_price}/1M prompt tokens")
        
        # Search for coding models
        coding_models = client.search_models("code")
        if coding_models:
            print(f"\n💻 Coding models ({len(coding_models)}):")
            for model in coding_models[:3]:  # Show first 3
                print(f"  • {model.name}: ${model.pricing.prompt_price}/1M tokens")
        
        # Test dynamic cost estimation
        model_id = "openai/gpt-4o-mini"
        cost = client.estimate_cost(model_id, 1000, 500)
        print(f"\n💵 Dynamic cost estimate for {model_id}:")
        print(f"   Input: 1000 tokens, Output: 500 tokens")
        print(f"   Total cost: ${cost:.6f}")
        
        # Show model details
        model_info = client.get_model_info(model_id)
        if model_info:
            print(f"\n📋 Model details for {model_id}:")
            print(f"   Name: {model_info.name}")
            print(f"   Provider: {model_info.provider}")
            print(f"   Context: {model_info.context_length:,} tokens")
            print(f"   Prompt price: ${model_info.pricing.prompt_price}/1M tokens")
            print(f"   Completion price: ${model_info.pricing.completion_price}/1M tokens")
        
        # Cache information
        cache_info = client.get_models_cache_info()
        print(f"\n🗄️  Cache info:")
        print(f"   Models cached: {cache_info.get('models_count', 0)}")
        print(f"   Last updated: {cache_info.get('last_fetch', 'Never')}")
        print(f"   Cache file: {cache_info.get('cache_file_exists', False)}")
        
    except Exception as e:
        print(f"❌ Models cache example failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main example function."""
    print("🚀 Django LLM Module Examples")
    print("=" * 50)
    
    # Set up configuration
    config = ExampleConfig()
    
    # Run examples
    await example_llm_usage()
    await example_translation_usage()
    await example_cache_management()
    await example_models_cache()
    await example_alerts()
    
    print("\n🎉 All examples completed!")
    print("\nNext steps:")
    print("1. Check the generated cache files")
    print("2. Review the YAML exports")
    print("3. Monitor Telegram for alerts")
    print("4. Integrate into your Django project")


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
