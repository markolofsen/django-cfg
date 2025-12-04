"""
Demo Service for Testing Centrifugo Integration.

This module provides a complete working example of Centrifugo integration:

1. ObservabilityInterceptor - Automatic RPC metadata publishing (built-in)
2. CentrifugoBridgeMixin - Service-level message data publishing

Note:
    CentrifugoInterceptor has been merged into ObservabilityInterceptor
    to fix the bidirectional streaming StopAsyncIteration bug.

Usage:
    # Send single demo event
    >>> await send_demo_event()

    # Test mixin-based publishing
    >>> await test_demo_service()

    # Test complete chain (interceptor + mixin)
    >>> await test_complete_integration()
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timezone as tz

from google.protobuf.struct_pb2 import Struct
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .bridge import CentrifugoBridgeMixin
from .config import ChannelConfig, CentrifugoChannels
from ...utils.streaming_logger import setup_streaming_logger

# Setup logger with Rich support
logger = setup_streaming_logger(
    name='centrifugo_demo',
    level=logging.DEBUG,
    console_level=logging.INFO
)

# Rich console for beautiful output
console = Console()


# ========================================================================
# Demo Channel Configuration (Pydantic)
# ========================================================================

class DemoChannels(CentrifugoChannels):
    """
    Demo channel configuration for testing CentrifugoBridgeMixin.

    This shows how to define channel mappings using Pydantic v2 models.
    """

    # High-frequency updates (rate limited)
    heartbeat: ChannelConfig = ChannelConfig(
        template='demo#{service_id}#heartbeat',
        rate_limit=0.5,  # Max once per 0.5 seconds
        metadata={'priority': 'low', 'demo': True}
    )

    # Status changes (critical, always published)
    status: ChannelConfig = ChannelConfig(
        template='demo#{service_id}#status',
        critical=True,  # Bypass rate limiting
        metadata={'priority': 'high', 'demo': True}
    )

    # Test execution reports
    execution: ChannelConfig = ChannelConfig(
        template='demo#{service_id}#executions',
        rate_limit=1.0,
        metadata={'priority': 'medium', 'demo': True}
    )

    # Error events (critical)
    error: ChannelConfig = ChannelConfig(
        template='demo#{service_id}#errors',
        critical=True,
        metadata={'priority': 'critical', 'demo': True}
    )


# ========================================================================
# Demo Service with CentrifugoBridgeMixin
# ========================================================================

class DemoBridgeService(CentrifugoBridgeMixin):
    """
    Demo service using CentrifugoBridgeMixin for Centrifugo publishing.

    This demonstrates:
    - Pydantic configuration
    - Automatic field detection
    - Rate limiting
    - Critical event bypass
    - Template-based channel naming

    Example:
        >>> service = DemoBridgeService()
        >>> message = create_mock_message('heartbeat', cpu=45.2)
        >>> await service.publish_demo(message, service_id='demo-123')
    """

    # Configure Centrifugo channels using Pydantic
    centrifugo_channels = DemoChannels()

    def __init__(self):
        """Initialize demo service with Centrifugo bridge."""
        super().__init__()
        logger.info("DemoBridgeService initialized with Centrifugo bridge")

    async def publish_demo(
        self,
        message: Struct,
        service_id: str,
        **extra_context: Any
    ) -> bool:
        """
        Publish demo message to Centrifugo.

        Args:
            message: Protobuf Struct message with test data
            service_id: Service identifier for channel routing
            **extra_context: Additional template variables

        Returns:
            True if published successfully
        """
        context = {'service_id': service_id, **extra_context}
        return await self._notify_centrifugo(message, **context)


# ========================================================================
# Mock Protobuf Message Generation
# ========================================================================

def create_mock_message(message_type: str, **fields: Any) -> Struct:
    """
    Create a mock protobuf Struct message for testing.

    Uses google.protobuf.struct_pb2.Struct to simulate protobuf messages
    without requiring compiled .proto files.

    Args:
        message_type: Type of message (heartbeat, status, execution, error)
        **fields: Additional fields to include in the message

    Returns:
        Protobuf Struct message with HasField() support

    Example:
        >>> msg = create_mock_message('heartbeat', cpu=45.2, memory=60.1)
        >>> msg.HasField('heartbeat')
        True
    """
    message = Struct()

    # Create nested structure for the message type
    field_data = message.fields[message_type]

    # Add timestamp by default
    field_data.struct_value.fields['timestamp'].string_value = (
        datetime.now(tz.utc).isoformat()
    )

    # Add custom fields
    for key, value in fields.items():
        if isinstance(value, bool):
            field_data.struct_value.fields[key].bool_value = value
        elif isinstance(value, (int, float)):
            field_data.struct_value.fields[key].number_value = float(value)
        elif isinstance(value, str):
            field_data.struct_value.fields[key].string_value = value
        elif value is None:
            field_data.struct_value.fields[key].null_value = 0
        else:
            field_data.struct_value.fields[key].string_value = str(value)

    return message


def generate_mock_heartbeat(**overrides: Any) -> Struct:
    """Generate mock heartbeat message."""
    defaults = {
        'status': 'RUNNING',
        'cpu_usage': 45.2,
        'memory_usage': 60.1,
        'open_positions': 3,
        'daily_pnl': 1250.50,
    }
    defaults.update(overrides)
    return create_mock_message('heartbeat', **defaults)


def generate_mock_status(**overrides: Any) -> Struct:
    """Generate mock status update message."""
    defaults = {
        'old_status': 'STOPPED',
        'new_status': 'RUNNING',
        'reason': 'Demo test event',
    }
    defaults.update(overrides)
    return create_mock_message('status', **defaults)


def generate_mock_execution(**overrides: Any) -> Struct:
    """Generate mock execution report message."""
    defaults = {
        'execution_id': f'exec-{datetime.now().microsecond}',
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'quantity': 0.01,
        'price': 50000.0,
        'status': 'FILLED',
    }
    defaults.update(overrides)
    return create_mock_message('execution', **defaults)


def generate_mock_error(**overrides: Any) -> Struct:
    """Generate mock error report message."""
    defaults = {
        'error_code': 'DEMO_ERROR',
        'message': 'This is a test error',
        'severity': 'WARNING',
    }
    defaults.update(overrides)
    return create_mock_message('error', **defaults)


# ========================================================================
# Testing Functions
# ========================================================================

async def send_demo_event(
    channel: str = "grpc#demo#TestMethod#meta",
    metadata: Optional[Dict[str, Any]] = None,
    quiet: bool = False,
) -> bool:
    """
    Send a raw demo event to Centrifugo (interceptor simulation).

    This simulates what CentrifugoInterceptor publishes automatically.

    Args:
        channel: Centrifugo channel name
        metadata: Additional metadata to include
        quiet: Suppress log messages

    Returns:
        True if published successfully

    Example:
        >>> await send_demo_event()
        ✅ Demo event published to: grpc#demo#TestMethod#meta
    """
    try:
        from django_cfg.apps.integrations.centrifugo.services import get_centrifugo_publisher

        publisher = get_centrifugo_publisher()

        # Use high-level publishing service
        await publisher.publish_demo_event(
            channel=channel,
            metadata={
                "method": "/demo.DemoService/TestMethod",
                "service": "demo.DemoService",
                "method_name": "TestMethod",
                "peer": "demo-client",
                "duration_ms": 123.45,
                "status": "OK",
                "message": "Raw interceptor-style event from demo.py",
                **(metadata or {}),
            },
        )

        if not quiet:
            logger.info(f"✅ Demo event published to: {channel}")

        return True

    except Exception as e:
        if not quiet:
            logger.error(f"❌ Failed to send demo event: {e}")
        return False


async def test_demo_service(
    service_id: str = "demo-service-123",
    count: int = 3,
) -> Dict[str, int]:
    """
    Test DemoBridgeService with mock messages (mixin testing).

    This tests the CentrifugoBridgeMixin functionality with various
    message types and rate limiting.

    Args:
        service_id: Service identifier for channels
        count: Number of test messages per type

    Returns:
        Dict with publish statistics

    Example:
        >>> stats = await test_demo_service(count=5)
        >>> print(stats)
        {'heartbeat': 3, 'status': 5, 'execution': 3, 'error': 5}
    """
    logger.info(f"🧪 Testing DemoBridgeService with service_id={service_id}")

    service = DemoBridgeService()

    stats = {
        'heartbeat': 0,
        'status': 0,
        'execution': 0,
        'error': 0,
    }

    # Test different message types
    for i in range(1, count + 1):
        logger.info(f"--- Test iteration {i}/{count} ---")

        # Test heartbeat (rate limited)
        heartbeat = generate_mock_heartbeat(
            cpu_usage=40.0 + i * 5,
            memory_usage=50.0 + i * 3,
        )
        if await service.publish_demo(heartbeat, service_id=service_id):
            stats['heartbeat'] += 1
            logger.info(f"  ✅ Heartbeat {i} published")
        else:
            logger.info(f"  ⏱️ Heartbeat {i} rate limited")

        # Test status (critical, always published)
        status = generate_mock_status(
            new_status=f"TEST_STATE_{i}"
        )
        if await service.publish_demo(status, service_id=service_id):
            stats['status'] += 1
            logger.info(f"  ✅ Status {i} published (critical)")

        # Test execution (rate limited)
        execution = generate_mock_execution(
            price=50000.0 + i * 100,
        )
        if await service.publish_demo(execution, service_id=service_id):
            stats['execution'] += 1
            logger.info(f"  ✅ Execution {i} published")
        else:
            logger.info(f"  ⏱️ Execution {i} rate limited")

        # Test error (critical, always published)
        error = generate_mock_error(
            error_code=f"TEST_ERROR_{i}"
        )
        if await service.publish_demo(error, service_id=service_id):
            stats['error'] += 1
            logger.info(f"  ✅ Error {i} published (critical)")

        # Small delay between iterations
        if i < count:
            await asyncio.sleep(0.6)  # Slightly longer than heartbeat rate limit

    logger.info(f"📊 Test complete: {stats}")
    return stats


async def test_interceptor_simulation(count: int = 3) -> int:
    """
    Test interceptor-style event publishing.

    Args:
        count: Number of events to send

    Returns:
        Number of successfully published events
    """
    logger.info(f"🔬 Testing CentrifugoInterceptor simulation ({count} events)")

    success_count = 0

    for i in range(1, count + 1):
        result = await send_demo_event(
            metadata={
                "sequence_number": i,
                "total_events": count,
            },
            quiet=True,
        )

        if result:
            success_count += 1
            logger.info(f"✅ Interceptor event {i}/{count} published")
        else:
            logger.warning(f"⚠️ Interceptor event {i}/{count} failed")

        if i < count:
            await asyncio.sleep(0.5)

    logger.info(f"📊 Interceptor test: {success_count}/{count} successful")
    return success_count


async def test_complete_integration(
    service_id: str = "demo-integration-test",
    mixin_count: int = 3,
    interceptor_count: int = 3,
) -> Dict[str, Any]:
    """
    Test complete integration: both interceptor and mixin.

    This demonstrates how CentrifugoInterceptor and CentrifugoBridgeMixin
    work together to provide complete event visibility.

    Args:
        service_id: Service identifier for mixin tests
        mixin_count: Number of mixin test messages
        interceptor_count: Number of interceptor test events

    Returns:
        Complete test results

    Example:
        >>> results = await test_complete_integration()
        >>> print(results)
        {
            'interceptor': {'published': 3, 'total': 3},
            'mixin': {'heartbeat': 2, 'status': 3, ...},
            'total_published': 15,
        }
    """
    # Rich header
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Centrifugo Integration Test[/bold cyan]\n"
        "[dim]Testing CentrifugoInterceptor + CentrifugoBridgeMixin[/dim]",
        border_style="cyan"
    ))

    results = {
        'interceptor': {'published': 0, 'total': interceptor_count},
        'mixin': {},
        'total_published': 0,
    }

    # Test 1: Interceptor (RPC metadata)
    console.print("\n[bold blue]📍 Phase 1: CentrifugoInterceptor (RPC metadata)[/bold blue]")
    console.rule(style="blue")
    interceptor_success = await test_interceptor_simulation(count=interceptor_count)
    results['interceptor']['published'] = interceptor_success
    results['total_published'] += interceptor_success

    # Small delay between phases
    await asyncio.sleep(1.0)

    # Test 2: Mixin (Message data)
    console.print("\n[bold green]📍 Phase 2: CentrifugoBridgeMixin (message data)[/bold green]")
    console.rule(style="green")
    mixin_stats = await test_demo_service(service_id=service_id, count=mixin_count)
    results['mixin'] = mixin_stats
    results['total_published'] += sum(mixin_stats.values())

    # Summary table
    console.print()
    console.rule("[bold]Test Summary[/bold]", style="yellow")

    summary_table = Table(title="📊 Integration Test Results", show_header=True, header_style="bold magenta")
    summary_table.add_column("Component", style="cyan", width=20)
    summary_table.add_column("Published", style="green", justify="right")
    summary_table.add_column("Total", style="blue", justify="right")
    summary_table.add_column("Success Rate", style="yellow", justify="right")

    # Interceptor row
    interceptor_rate = (results['interceptor']['published'] / results['interceptor']['total'] * 100) if results['interceptor']['total'] > 0 else 0
    summary_table.add_row(
        "Interceptor",
        str(results['interceptor']['published']),
        str(results['interceptor']['total']),
        f"{interceptor_rate:.1f}%"
    )

    # Mixin rows
    for msg_type, count in results['mixin'].items():
        rate = (count / mixin_count * 100) if mixin_count > 0 else 0
        summary_table.add_row(
            f"Mixin ({msg_type})",
            str(count),
            str(mixin_count),
            f"{rate:.1f}%"
        )

    # Total row
    total_expected = results['interceptor']['total'] + (mixin_count * len(results['mixin']))
    total_rate = (results['total_published'] / total_expected * 100) if total_expected > 0 else 0
    summary_table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{results['total_published']}[/bold]",
        f"[bold]{total_expected}[/bold]",
        f"[bold]{total_rate:.1f}%[/bold]",
        style="bold yellow"
    )

    console.print(summary_table)

    # Status message
    if results['total_published'] == total_expected:
        console.print("\n[bold green]✅ All tests passed successfully![/bold green]")
    elif results['total_published'] > 0:
        console.print(f"\n[bold yellow]⚠️ Partial success: {results['total_published']}/{total_expected} events published[/bold yellow]")
    else:
        console.print("\n[bold red]❌ All tests failed![/bold red]")

    console.print()

    return results


async def start_demo_publisher(
    interval: float = 5.0,
    duration: Optional[float] = None,
    service_id: str = "demo-continuous",
) -> None:
    """
    Start continuous demo event publisher using mixin.

    Publishes rotating message types until stopped or duration expires.

    Args:
        interval: Seconds between events
        duration: Total duration in seconds (None = run forever)
        service_id: Service ID for channel routing

    Example:
        >>> # Run for 30 seconds
        >>> await start_demo_publisher(interval=5.0, duration=30.0)

        >>> # Run forever (until Ctrl+C)
        >>> await start_demo_publisher(interval=10.0)
    """
    logger.info(
        f"🚀 Starting demo publisher "
        f"(interval={interval}s, duration={duration or 'infinite'})"
    )

    service = DemoBridgeService()
    start_time = asyncio.get_event_loop().time()
    event_count = 0

    # Message generators
    generators = {
        'heartbeat': generate_mock_heartbeat,
        'status': generate_mock_status,
        'execution': generate_mock_execution,
        'error': generate_mock_error,
    }

    message_types = list(generators.keys())

    try:
        while True:
            event_count += 1

            # Rotate through message types
            message_type = message_types[(event_count - 1) % len(message_types)]

            # Generate message
            message = generators[message_type]()

            # Publish
            await service.publish_demo(
                message,
                service_id=service_id,
                event_count=event_count,
            )

            logger.info(
                f"📤 Event {event_count}: {message_type} → "
                f"demo#{service_id}#{message_type}"
            )

            # Check duration
            if duration:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= duration:
                    logger.info(
                        f"⏱️ Duration reached ({duration}s), "
                        f"published {event_count} events"
                    )
                    break

            await asyncio.sleep(interval)

    except asyncio.CancelledError:
        logger.info(f"🛑 Demo publisher stopped (published {event_count} events)")
        raise

    except Exception as e:
        logger.error(f"❌ Demo publisher error: {e}")
        raise


__all__ = [
    # Classes
    "DemoChannels",
    "DemoBridgeService",

    # Mock message generation
    "create_mock_message",
    "generate_mock_heartbeat",
    "generate_mock_status",
    "generate_mock_execution",
    "generate_mock_error",

    # Testing functions
    "send_demo_event",
    "test_demo_service",
    "test_interceptor_simulation",
    "test_complete_integration",
    "start_demo_publisher",
]
