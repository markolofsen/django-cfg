"""
Crypto gRPC Integration.

Modern gRPC service for cryptocurrency operations with Centrifugo WebSocket bridge.

Features:
- Unary RPC for CRUD operations (coins, wallets, portfolio)
- Server-side streaming for real-time price updates
- Centrifugo bridge for WebSocket publishing
- Production-ready error handling and logging

Structure:
- services/ - gRPC service implementation
- proto/ - Protocol Buffer definitions and converters
- handlers/ - Business logic handlers
- channels/ - Centrifugo channel configuration
- tests/ - Integration tests
- examples/ - Usage examples

Auto-discovered by django-cfg when GRPCConfig.enabled_apps includes "crypto"
"""

__all__ = []

