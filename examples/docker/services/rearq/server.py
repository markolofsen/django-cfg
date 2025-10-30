"""
ReArq Server Wrapper
====================
Wrapper module to initialize Tortoise ORM for rearq Web UI server.

This module patches the rearq server app to add proper Tortoise initialization.
"""

import os
from tortoise import Tortoise
from rearq.server.app import app

# Import the rearq instance from main
from main import rearq, DB_URL

# Set rearq instance to app
app.set_rearq(rearq)


# Add Tortoise initialization to FastAPI startup
@app.on_event("startup")
async def init_tortoise():
    """
    Initialize Tortoise ORM for rearq Web UI.
    This creates the database schema if it doesn't exist.
    """
    print("═══════════════════════════════════════════════════════════════════")
    print("Initializing Tortoise ORM for rearq Web UI...")
    print(f"Database: {DB_URL}")

    await Tortoise.init(
        db_url=DB_URL,
        modules={"rearq": ["rearq.server.models"]},
    )
    await Tortoise.generate_schemas()

    print("✓ Tortoise ORM initialized successfully!")
    print("═══════════════════════════════════════════════════════════════════")


@app.on_event("shutdown")
async def close_tortoise():
    """
    Close Tortoise ORM connections on shutdown.
    """
    print("Closing Tortoise ORM connections...")
    await Tortoise.close_connections()
    await rearq.close()
