"""
Simple LLM JSON translation command.
"""

import json
from django.core.management.base import BaseCommand, CommandError
from django_cfg.modules.django_llm import DjangoTranslator, LLMClient
from api.environment import env


class Command(BaseCommand):
    help = 'Translate JSON content using LLM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            type=str,
            help='JSON string to translate'
        )
        parser.add_argument(
            '--target-lang',
            type=str,
            default='ru',
            help='Target language (default: ru)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show preview without translating'
        )

    def handle(self, *args, **options):
        """Main handler."""
        try:
            # Check API keys from config and env
            openrouter_key = env.api_keys.openrouter_api_key
            openai_key = env.api_keys.openai_api_key
            
            if not openrouter_key and not openai_key:
                raise CommandError(
                    "❌ No API keys found! Set OPENROUTER_API_KEY or OPENAI_API_KEY environment variables"
                )
            
            self.stdout.write(f"🔑 API Keys: OpenRouter={'✅' if openrouter_key else '❌'} OpenAI={'✅' if openai_key else '❌'}")

            # Get JSON data
            if options.get('json'):
                try:
                    data = json.loads(options['json'])
                    self.stdout.write("📄 Using provided JSON")
                except json.JSONDecodeError as e:
                    raise CommandError(f"Invalid JSON: {e}")
            else:
                data = self.get_sample_json()
                self.stdout.write("📄 Using sample JSON")

            target_lang = options['target_lang']
            self.stdout.write(f"🎯 Target language: {target_lang}")

            if options['dry_run']:
                self.stdout.write(self.style.WARNING('🔍 DRY RUN'))
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return

            # Translate
            self.stdout.write("🤖 Starting translation...")
            
            # Create LLM client with API keys from config
            api_key = openrouter_key or openai_key
            provider = "openrouter" if openrouter_key else "openai"
            
            client = LLMClient(
                provider=provider,
                api_key=api_key
            )
            
            # Create translator with the client
            translator = DjangoTranslator(client=client)
            
            translated = translator.translate_json(
                data=data,
                target_language=target_lang,
                source_language='auto',
                model="openai/gpt-4o-mini",
                temperature=0.1
            )
            
            self.stdout.write(self.style.SUCCESS('✨ Translation result:'))
            print(json.dumps(translated, ensure_ascii=False, indent=2))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            raise CommandError(str(e))

    def get_sample_json(self):
        """Complex sample JSON for testing nested structures, arrays, mixed types."""
        return {
            "title": "Django CFG Sample Project",
            "version": "1.0.0",
            "description": "A powerful configuration management system for Django",
            "url": "https://github.com/example/django-cfg",
            "email": "support@example.com",
            "enabled": True,
            "count": 42,
            "price": 29.99,
            "empty_string": "",
            "null_value": None,
            "features": [
                "Type-safe configuration",
                "Environment-based settings", 
                "LLM integration",
                "Translation services"
            ],
            "navigation": {
                "home": "Home",
                "blog": "Blog", 
                "products": "Products",
                "about": "About Us",
                "contact": {
                    "title": "Contact Us",
                    "subtitle": "Get in touch with our team",
                    "phone": "+1-555-0123",
                    "address": "123 Main St, City, Country"
                }
            },
            "messages": {
                "success": "Operation completed successfully!",
                "error": "An error occurred. Please try again.",
                "loading": "Loading, please wait...",
                "validation": {
                    "required": "This field is required",
                    "email": "Please enter a valid email address",
                    "min_length": "Minimum length is 3 characters"
                }
            },
            "products": [
                {
                    "id": "prod_001",
                    "name": "Basic Plan",
                    "description": "Perfect for small teams",
                    "price": 9.99,
                    "currency": "USD",
                    "features": [
                        "Up to 5 users",
                        "Basic support",
                        "Standard features"
                    ],
                    "metadata": {
                        "category": "subscription",
                        "popular": False,
                        "trial_days": 14
                    }
                },
                {
                    "id": "prod_002", 
                    "name": "Pro Plan",
                    "description": "Best for growing businesses",
                    "price": 29.99,
                    "currency": "USD",
                    "features": [
                        "Unlimited users",
                        "Priority support", 
                        "Advanced features",
                        "Custom integrations"
                    ],
                    "metadata": {
                        "category": "subscription",
                        "popular": True,
                        "trial_days": 30
                    }
                }
            ],
            "config": {
                "debug": False,
                "max_retries": 3,
                "timeout": 30.0,
                "allowed_hosts": ["example.com", "www.example.com"],
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "django_cfg_db",
                    "ssl": True
                },
                "cache": {
                    "backend": "redis",
                    "location": "redis://localhost:6379/1",
                    "timeout": 300
                }
            },
            "localization": {
                "default_language": "en",
                "supported_languages": ["en", "es", "fr", "de", "ru"],
                "date_format": "YYYY-MM-DD",
                "currency_symbol": "$",
                "timezone": "UTC"
            }
        }