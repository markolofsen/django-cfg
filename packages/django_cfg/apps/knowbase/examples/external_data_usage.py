"""
Примеры использования нового ExternalDataManager.

Этот файл показывает, как легко интегрировать внешние данные в knowbase
после рефакторинга.
"""

from django.contrib.auth import get_user_model

from django_cfg.apps.knowbase.utils.external_data_manager import (
    ExternalDataManager,
    quick_search,
)

User = get_user_model()


def example_add_django_model():
    """Пример добавления Django модели как внешнего источника данных."""

    # Получаем пользователя
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return

    # Создаем менеджер
    manager = ExternalDataManager(user)

    # Добавляем модель Vehicle (если она существует)
    try:
        from apps.vehicles_data.models import Vehicle

        external_data = manager.add_django_model(
            model_class=Vehicle,
            title="Vehicle Database",
            fields=['brand__name', 'model', 'year', 'description'],
            description="All vehicles from the database",
            search_fields=['brand__name', 'model'],
            chunk_size=800,
            overlap_size=150,
            auto_vectorize=True
        )

        print(f"✅ Added Vehicle model as external data: {external_data.id}")
        print(f"   Status: {external_data.status}")
        print(f"   Total chunks: {external_data.total_chunks}")

    except ImportError:
        print("⚠️ Vehicle model not found, using example data instead")

        # Добавляем произвольные данные
        external_data = manager.add_custom_data(
            title="Sample Car Data",
            identifier="sample_cars",
            content="""
            Toyota Camry 2023: Reliable sedan with excellent fuel economy
            Honda Civic 2023: Compact car perfect for city driving
            BMW X5 2023: Luxury SUV with advanced features
            Tesla Model 3 2023: Electric vehicle with autopilot
            """,
            description="Sample car data for testing",
            tags=['cars', 'vehicles', 'sample']
        )

        print(f"✅ Added sample car data: {external_data.id}")


def example_search_external_data():
    """Пример поиска по внешним данным."""

    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return

    manager = ExternalDataManager(user)

    # Поиск по запросу
    results = manager.search(
        query="reliable car with good fuel economy",
        limit=3,
        threshold=0.6
    )

    print(f"🔍 Search results ({len(results)} found):")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['source_title']} (similarity: {result['similarity']:.3f})")
        print(f"     Content: {result['content'][:100]}...")
        print()


def example_get_statistics():
    """Пример получения статистики."""

    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return

    manager = ExternalDataManager(user)
    stats = manager.get_statistics()

    print("📊 External Data Statistics:")
    print(f"   Total sources: {stats.total_sources}")
    print(f"   Active sources: {stats.active_sources}")
    print(f"   Processed sources: {stats.processed_sources}")
    print(f"   Failed sources: {stats.failed_sources}")
    print(f"   Total chunks: {stats.total_chunks}")
    print(f"   Total tokens: {stats.total_tokens}")
    print(f"   Total cost: ${stats.total_cost:.4f}")
    print(f"   Source types: {stats.source_type_counts}")


def example_health_check():
    """Пример проверки здоровья системы."""

    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return

    manager = ExternalDataManager(user)
    health = manager.health_check()

    print("🏥 System Health Check:")
    print(f"   Status: {health.status}")
    print(f"   Healthy: {'✅' if health.healthy else '❌'}")
    print(f"   Database: {'✅' if health.database_healthy else '❌'}")
    print(f"   Embedding Service: {'✅' if health.embedding_service_healthy else '❌'}")
    print(f"   Processing: {'✅' if health.processing_healthy else '❌'}")
    print(f"   Response time: {health.response_time_ms:.2f}ms")
    print(f"   Active sources: {health.active_sources}")
    print(f"   Pending processing: {health.pending_processing}")
    print(f"   Failed processing: {health.failed_processing}")

    if health.issues:
        print(f"   Issues: {health.issues}")
    if health.warnings:
        print(f"   Warnings: {health.warnings}")


def example_quick_functions():
    """Пример использования быстрых функций."""

    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return

    # Быстрый поиск
    results = quick_search(
        user=user,
        query="electric vehicle",
        limit=2
    )

    print(f"⚡ Quick search results: {len(results)} found")
    for result in results:
        print(f"   - {result['source_title']}: {result['similarity']:.3f}")


def run_all_examples():
    """Запустить все примеры."""

    print("🚀 Running External Data Manager Examples")
    print("=" * 50)

    try:
        print("\n1. Adding Django Model:")
        example_add_django_model()

        print("\n2. Searching External Data:")
        example_search_external_data()

        print("\n3. Getting Statistics:")
        example_get_statistics()

        print("\n4. Health Check:")
        example_health_check()

        print("\n5. Quick Functions:")
        example_quick_functions()

        print("\n✅ All examples completed successfully!")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
