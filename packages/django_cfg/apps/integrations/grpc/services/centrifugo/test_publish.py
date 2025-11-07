"""
Test script to verify Centrifugo event publishing.

Run this to test that events are being published to Centrifugo channels.

Usage:
    # From Django shell:
    >>> from django_cfg.apps.integrations.grpc.services.centrifugo.test_publish import run_test
    >>> await run_test()

    # Or from async context:
    >>> import asyncio
    >>> from django_cfg.apps.integrations.grpc.services.centrifugo.test_publish import run_test
    >>> asyncio.run(run_test())
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def run_test(verbose: bool = True):
    """
    Run complete Centrifugo integration test.

    Tests:
    1. Centrifugo client initialization
    2. Interceptor simulation (RPC metadata)
    3. Mixin demo (message data)

    Args:
        verbose: Show detailed output

    Returns:
        dict: Test results with success/failure counts
    """
    if verbose:
        # Set logging to DEBUG to see all details
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    logger.info("=" * 70)
    logger.info("🧪 CENTRIFUGO INTEGRATION TEST")
    logger.info("=" * 70)

    results = {
        'client_init': False,
        'interceptor_test': 0,
        'mixin_test': {},
        'total_published': 0,
        'errors': [],
    }

    # Test 1: Client initialization
    logger.info("\n📍 Step 1: Testing Centrifugo client initialization")
    logger.info("-" * 70)
    try:
        from django_cfg.apps.integrations.centrifugo import get_centrifugo_client

        client = get_centrifugo_client()
        logger.info(f"✅ Client initialized: {client.wrapper_url}")
        results['client_init'] = True
    except Exception as e:
        logger.error(f"❌ Client initialization failed: {e}")
        results['errors'].append(f"Client init: {str(e)}")
        return results

    # Test 2: Test interceptor simulation (raw publish)
    logger.info("\n📍 Step 2: Testing Interceptor-style publishing (RPC metadata)")
    logger.info("-" * 70)
    try:
        from django_cfg.apps.integrations.grpc.services.centrifugo.demo import send_demo_event

        # Send 3 test events
        for i in range(1, 4):
            success = await send_demo_event(
                channel=f"grpc#demo#TestMethod#meta",
                metadata={
                    'test_number': i,
                    'test_type': 'interceptor_simulation',
                }
            )
            if success:
                results['interceptor_test'] += 1
                results['total_published'] += 1
                logger.info(f"  ✅ Event {i}/3 published to grpc#demo#TestMethod#meta")
            else:
                logger.warning(f"  ⚠️ Event {i}/3 failed")

            await asyncio.sleep(0.5)

    except Exception as e:
        logger.error(f"❌ Interceptor test failed: {e}")
        results['errors'].append(f"Interceptor: {str(e)}")

    # Test 3: Test mixin (DemoBridgeService)
    logger.info("\n📍 Step 3: Testing Mixin-style publishing (message data)")
    logger.info("-" * 70)
    try:
        from django_cfg.apps.integrations.grpc.services.centrifugo.demo import test_demo_service

        stats = await test_demo_service(service_id='test-integration', count=3)
        results['mixin_test'] = stats
        results['total_published'] += sum(stats.values())

        logger.info(f"  📊 Mixin test results: {stats}")

    except Exception as e:
        logger.error(f"❌ Mixin test failed: {e}")
        results['errors'].append(f"Mixin: {str(e)}")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Client initialized: {'✅ Yes' if results['client_init'] else '❌ No'}")
    logger.info(f"Interceptor events: {results['interceptor_test']}/3")
    logger.info(f"Mixin events: {results['mixin_test']}")
    logger.info(f"Total published: {results['total_published']}")

    if results['errors']:
        logger.error(f"\n❌ Errors encountered:")
        for error in results['errors']:
            logger.error(f"  - {error}")
    else:
        logger.info(f"\n✅ All tests passed successfully!")

    logger.info("=" * 70)

    return results


async def check_centrifugo_config():
    """
    Check Centrifugo configuration.

    Returns:
        dict: Configuration details
    """
    logger.info("🔍 Checking Centrifugo configuration...")

    try:
        from django_cfg.apps.integrations.centrifugo.services.config_helper import get_centrifugo_config

        config = get_centrifugo_config()

        if not config:
            logger.error("❌ Centrifugo not configured in django-cfg")
            return {
                'enabled': False,
                'error': 'Not configured',
            }

        logger.info(f"✅ Centrifugo enabled: {config.enabled}")
        logger.info(f"   Wrapper URL: {config.wrapper_url}")
        logger.info(f"   Log all calls: {config.log_all_calls}")
        logger.info(f"   Log only ACK: {config.log_only_with_ack}")

        return {
            'enabled': config.enabled,
            'wrapper_url': config.wrapper_url,
            'log_all_calls': config.log_all_calls,
            'log_only_with_ack': config.log_only_with_ack,
        }

    except Exception as e:
        logger.error(f"❌ Failed to get config: {e}")
        return {
            'enabled': False,
            'error': str(e),
        }


async def test_simple_publish():
    """
    Simple test - publish one event and check logs.

    Returns:
        bool: True if successful
    """
    logger.info("🧪 Simple publish test...")

    try:
        from django_cfg.apps.integrations.centrifugo import get_centrifugo_client
        from datetime import datetime, timezone as tz

        client = get_centrifugo_client()

        test_data = {
            'message': 'Hello from test_publish.py',
            'timestamp': datetime.now(tz.utc).isoformat(),
            'test': True,
        }

        logger.info(f"📤 Publishing to channel: test#demo#simple")

        result = await client.publish(
            channel='test#demo#simple',
            data=test_data
        )

        logger.info(f"✅ Publish result: {result}")
        logger.info(f"   Message ID: {result.message_id}")
        logger.info(f"   Published: {result.published}")

        return result.published

    except Exception as e:
        logger.error(f"❌ Publish failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    # For standalone execution
    print("Running Centrifugo integration test...")
    print("=" * 70)
    results = asyncio.run(run_test(verbose=True))
    print("\nTest completed.")
    print(f"Total events published: {results['total_published']}")


__all__ = [
    'run_test',
    'check_centrifugo_config',
    'test_simple_publish',
]
