"""
Proof of Concept test for RPC codegen.

Demonstrates:
1. Creating a simple RPC server with handlers
2. Discovering methods from router
3. Generating TypeScript types from Pydantic models
"""

from pydantic import BaseModel, Field
from django_ipc.server.message_router import MessageRouter
from django_ipc.server.connection_manager import ConnectionManager, ActiveConnection

# Import codegen modules
from .discovery import discover_rpc_methods_from_router, get_method_summary, extract_all_models
from .utils.type_converter import generate_typescript_types


# ==== Define Example Pydantic Models ====

class SendEmailParams(BaseModel):
    """Parameters for sending email."""

    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    cc: list[str] = Field(default_factory=list, description="CC recipients")


class SendEmailResult(BaseModel):
    """Result of sending email."""

    success: bool = Field(description="Whether email was sent successfully")
    message_id: str = Field(description="Message ID from email provider")
    delivered_at: str = Field(description="ISO timestamp of delivery")


class NotificationParams(BaseModel):
    """Parameters for sending notification."""

    user_id: str = Field(description="User ID to notify")
    message: str = Field(description="Notification message")
    priority: int = Field(default=1, description="Priority level (1-5)")


class NotificationResult(BaseModel):
    """Result of sending notification."""

    sent: bool
    notification_id: str


# ==== Create Example RPC Server ====

def create_example_rpc_server():
    """Create example RPC server with handlers."""

    # Create router (ConnectionManager needs redis_url)
    connection_manager = ConnectionManager(redis_url="redis://localhost:6379/2")
    router = MessageRouter(connection_manager)

    # Register handlers

    @router.register("send_email")
    async def handle_send_email(conn: ActiveConnection, params: SendEmailParams) -> SendEmailResult:
        """
        Send email via SMTP.

        Validates email address and sends message through configured SMTP server.
        """
        # Simulated implementation
        return SendEmailResult(
            success=True,
            message_id=f"msg-{params.to}",
            delivered_at="2025-10-03T12:00:00Z",
        )

    @router.register("send_notification")
    async def handle_notification(conn: ActiveConnection, params: NotificationParams) -> NotificationResult:
        """Send real-time notification to user."""
        return NotificationResult(
            sent=True,
            notification_id=f"notif-{params.user_id}",
        )

    return router


# ==== POC Test ====

def run_poc_test():
    """Run proof of concept test."""

    print("=" * 80)
    print("🚀 django_ipc Codegen POC Test")
    print("=" * 80)
    print()

    # 1. Create RPC server
    print("1️⃣  Creating example RPC server...")
    router = create_example_rpc_server()
    print(f"   ✅ Created router with {len(router._handlers)} handlers")
    print()

    # 2. Discover methods
    print("2️⃣  Discovering RPC methods...")
    methods = discover_rpc_methods_from_router(router)
    print(get_method_summary(methods))
    print()

    # 3. Extract models
    print("3️⃣  Extracting Pydantic models...")
    models = extract_all_models(methods)
    print(f"   Found {len(models)} unique models:")
    for model in models:
        print(f"     • {model.__name__}")
    print()

    # 4. Generate TypeScript types
    print("4️⃣  Generating TypeScript types...")
    ts_types = generate_typescript_types(models)
    print("   Generated TypeScript:")
    print()
    print("   " + "-" * 76)
    for line in ts_types.split("\n"):
        print(f"   {line}")
    print("   " + "-" * 76)
    print()

    # 5. Show what client would look like
    print("5️⃣  Example generated TypeScript client (preview):")
    print()
    print("   " + "-" * 76)
    client_preview = """
   // Auto-generated RPC client
   export class RPCClient extends WebSocketClient {

     /**
      * Send email via SMTP.
      * Validates email address and sends message through configured SMTP server.
      */
     async sendEmail(params: SendEmailParams): Promise<SendEmailResult> {
       return this.call('send_email', params);
     }

     /**
      * Send real-time notification to user.
      */
     async sendNotification(params: NotificationParams): Promise<NotificationResult> {
       return this.call('send_notification', params);
     }
   }
    """
    print(client_preview)
    print("   " + "-" * 76)
    print()

    print("=" * 80)
    print("✅ POC Test Completed Successfully!")
    print("=" * 80)
    print()
    print("📝 Next Steps:")
    print("   1. Create Jinja2 templates for client generation")
    print("   2. Implement CLI: python -m django_ipc codegen")
    print("   3. Add Python client generation")
    print("   4. Add React Context integration")
    print()


if __name__ == "__main__":
    run_poc_test()
