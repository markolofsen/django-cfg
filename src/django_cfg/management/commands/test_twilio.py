"""
Test Twilio Command

Tests Twilio messaging functionality using django_cfg configuration.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to test Twilio functionality."""
    help = "Test Twilio messaging functionality"

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            type=str,
            help="Phone number to send test message to",
            default="+6281339646301"
        )
        parser.add_argument(
            "--message",
            type=str,
            help="Message to send",
            default="Test message from Django CFG Twilio"
        )
        parser.add_argument(
            "--whatsapp",
            action="store_true",
            help="Send WhatsApp message (default: SMS)"
        )
        parser.add_argument(
            "--content-sid",
            type=str,
            help="Content template SID for WhatsApp (optional)"
        )

    def handle(self, *args, **options):
        to_number = options["to"]
        message = options["message"]
        is_whatsapp = options["whatsapp"]
        content_sid = options.get("content_sid")

        self.stdout.write("🚀 Testing Twilio messaging service")

        try:
            from django_cfg.modules.django_twilio import SimpleTwilioService
            twilio_service = SimpleTwilioService()
            
            if is_whatsapp:
                self.stdout.write(f"\n📱 Sending WhatsApp message to {to_number}...")
                
                if content_sid:
                    # Send with template
                    result = twilio_service.send_whatsapp_message(
                        to=to_number,
                        body="",  # Not used with templates
                        content_sid=content_sid,
                        content_variables={"1": "12/1", "2": "3pm"}
                    )
                    self.stdout.write(self.style.SUCCESS("✅ WhatsApp template message sent!"))
                else:
                    # Send regular message
                    result = twilio_service.send_whatsapp_message(
                        to=to_number,
                        body=message
                    )
                    self.stdout.write(self.style.SUCCESS("✅ WhatsApp message sent!"))
            else:
                self.stdout.write(f"\n📱 Sending SMS to {to_number}...")
                result = twilio_service.send_sms_message(
                    to=to_number,
                    body=message
                )
                self.stdout.write(self.style.SUCCESS("✅ SMS message sent!"))

            # Show result details
            self.stdout.write(f"\n📊 Message Details:")
            self.stdout.write(f"  SID: {result['sid']}")
            self.stdout.write(f"  Status: {result['status']}")
            self.stdout.write(f"  To: {result['to']}")
            self.stdout.write(f"  From: {result['from']}")
            self.stdout.write(f"  Created: {result['date_created']}")
            
            if result.get('price'):
                self.stdout.write(f"  Price: {result['price']} {result['price_unit']}")

            self.stdout.write(self.style.SUCCESS("\n✅ Twilio test completed successfully!"))

        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Twilio dependencies not installed: {e}"))
            self.stdout.write("💡 Install with: pip install twilio")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Failed to send message: {e}"))
            self.stdout.write("\n💡 Troubleshooting:")
            self.stdout.write("  1. Check your Twilio credentials in config.dev.yaml")
            self.stdout.write("  2. Ensure account_sid starts with 'AC' and is 34 characters")
            self.stdout.write("  3. Verify auth_token is 32 characters")
            self.stdout.write("  4. For WhatsApp: use sandbox number +14155238886")
            self.stdout.write("  5. For SMS: ensure your number is verified")
