#!/usr/bin/env python3
"""
Generate TypeScript and Python clients for Unrealon WebSocket RPC.

Auto-generates type-safe clients with environment detection.
"""

import sys
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from django_ipc.codegen.cli import generate_clients
from django_ipc.server.message_router import MessageRouter
from config import rpc_config
from src.handlers import WorkspaceHandler, SessionHandler, NotificationHandler
from loguru import logger


def copy_to_frontend(typescript_dir: Path):
    """
    Copy generated TypeScript client to frontend project.

    Args:
        typescript_dir: Path to generated TypeScript client directory
    """
    # Define target directory (relative to this file)
    # This file: /projects/websocket/src/generate_client.py
    # Target:    /projects/frontend/apps/demo/src/rpc/generated/
    projects_root = Path(__file__).parent.parent.parent  # /projects/
    frontend_target = projects_root / "frontend" / "apps" / "demo" / "src" / "rpc" / "generated"

    # Create target directory if it doesn't exist
    frontend_target.mkdir(parents=True, exist_ok=True)

    logger.info(f"📋 Copying TypeScript client to frontend project...")
    logger.info(f"   Source: {typescript_dir}")
    logger.info(f"   Target: {frontend_target}")

    # Files to copy
    files_to_copy = ["client.ts", "types.ts", "logger.ts", "index.ts"]

    copied_files = []
    for filename in files_to_copy:
        source_file = typescript_dir / filename
        target_file = frontend_target / filename

        if source_file.exists():
            shutil.copy2(source_file, target_file)
            copied_files.append(filename)
            logger.info(f"   ✅ {filename}")
        else:
            logger.warning(f"   ⚠️  {filename} not found")

    if copied_files:
        logger.info(f"✅ Copied {len(copied_files)} files to frontend project")
        logger.info(f"   {frontend_target}")
    else:
        logger.warning("⚠️  No files were copied")


def main():
    """Generate RPC clients."""
    logger.info("🔧 Generating RPC clients for Unrealon WebSocket Server")

    # Create mock ConnectionManager for code generation
    # We don't need a real connection manager, just the router to discover methods
    from django_ipc.server.connection_manager import ConnectionManager

    # Use a dummy redis_url for code generation (won't actually connect)
    mock_connection_manager = ConnectionManager(redis_url="redis://localhost:6379/0")

    # Create message router with mock connection manager
    router = MessageRouter(connection_manager=mock_connection_manager)

    # Instantiate handlers with mock connection manager
    workspace_handler = WorkspaceHandler(mock_connection_manager)
    session_handler = SessionHandler(mock_connection_manager)
    notification_handler = NotificationHandler(mock_connection_manager)

    # Register handlers (this will auto-discover RPC methods)
    workspace_handler.register(router)
    session_handler.register(router)
    notification_handler.register(router)

    # Log discovered methods
    handlers_info = router.list_handlers()
    logger.info("📦 Registered RPC methods:")
    for method in sorted(handlers_info.get("methods", [])):
        logger.info(f"  - {method}")

    # Output directory
    output_dir = Path(__file__).parent.parent / "clients"
    output_dir.mkdir(exist_ok=True)

    logger.info(f"📁 Output directory: {output_dir}")

    # Generate clients
    logger.info("🚀 Generating clients...")

    generate_clients(
        router=router,
        output_dir=output_dir,
        config=rpc_config,
        typescript=True,
        python=True,
    )

    logger.info("✅ Client generation complete!")
    logger.info("")
    logger.info("📦 TypeScript Client:")
    logger.info(f"   {output_dir}/typescript/")
    logger.info("   - Run: cd clients/typescript && npm install && npm run build")
    logger.info("")
    logger.info("📦 Python Client:")
    logger.info(f"   {output_dir}/python/")
    logger.info("   - Run: cd clients/python && pip install -e .")
    logger.info("")
    logger.info("📖 See README.md in each directory for usage examples")
    logger.info("")

    # Copy TypeScript client to frontend project
    typescript_dir = output_dir / "typescript"
    copy_to_frontend(typescript_dir)


if __name__ == "__main__":
    main()
