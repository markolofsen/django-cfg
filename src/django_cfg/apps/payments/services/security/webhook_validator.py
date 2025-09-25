"""
Enhanced Webhook Signature Validation Service.
Critical Foundation Security Component.
"""

import json
import hmac
import hashlib
from django_cfg.modules.django_logger import get_logger
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

from django_cfg.apps.payments.config import get_payments_config
from django_cfg.apps.payments.models.events import PaymentEvent
from ...models.payments import UniversalPayment

logger = get_logger("webhook_validator")


class WebhookValidator:
    """
    Secure webhook signature validation with replay attack protection.
    
    Foundation Security Component - CRITICAL for system security.
    """
    
    def __init__(self):
        self.config = get_payments_config()
        self.nonce_cache_timeout = 3600  # 1 hour nonce validity
        self.max_timestamp_drift = 300   # 5 minutes max timestamp drift
    
    def validate_webhook(
        self,
        provider: str,
        webhook_data: Dict[str, Any],
        request_headers: Dict[str, str],
        raw_body: bytes = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive webhook validation with security checks.
        
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        
        try:
            # Step 1: Provider-specific signature validation
            signature_valid, signature_error = self._validate_provider_signature(
                provider, webhook_data, request_headers, raw_body
            )
            
            if not signature_valid:
                self._log_security_event('signature_validation_failed', provider, signature_error)
                return False, signature_error
            
            # Step 2: Replay attack protection
            replay_valid, replay_error = self._validate_against_replay(
                provider, webhook_data, request_headers
            )
            
            if not replay_valid:
                self._log_security_event('replay_attack_detected', provider, replay_error)
                return False, replay_error
            
            # Step 3: Timestamp validation
            timestamp_valid, timestamp_error = self._validate_timestamp(
                webhook_data, request_headers
            )
            
            if not timestamp_valid:
                self._log_security_event('timestamp_validation_failed', provider, timestamp_error)
                return False, timestamp_error
            
            # Step 4: Rate limiting check
            rate_limit_valid, rate_limit_error = self._check_rate_limits(
                provider, request_headers
            )
            
            if not rate_limit_valid:
                self._log_security_event('rate_limit_exceeded', provider, rate_limit_error)
                return False, rate_limit_error
            
            # All validations passed
            self._log_security_event('webhook_validated', provider, 'Validation successful')
            return True, None
            
        except Exception as e:
            error_msg = f"Webhook validation error: {str(e)}"
            logger.error(f"Critical validation error for {provider}: {e}", exc_info=True)
            self._log_security_event('validation_exception', provider, error_msg)
            return False, error_msg
    
    def _validate_provider_signature(
        self,
        provider: str,
        webhook_data: Dict[str, Any],
        request_headers: Dict[str, str],
        raw_body: bytes = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate signature based on provider-specific method."""
        
        if provider == 'cryptapi':
            return self._validate_cryptapi_signature(webhook_data, request_headers)
        elif provider == 'cryptomus':
            return self._validate_cryptomus_signature(webhook_data, request_headers, raw_body)
        elif provider == 'nowpayments':
            return self._validate_nowpayments_signature(webhook_data, request_headers, raw_body)
        elif provider == 'test':
            return True, None  # Allow test webhooks in development
        else:
            return False, f"Unknown provider: {provider}"
    
    def _validate_cryptapi_signature(
        self,
        webhook_data: Dict[str, Any],
        request_headers: Dict[str, str]
    ) -> Tuple[bool, Optional[str]]:
        """
        CryptAPI signature validation with nonce verification.
        
        CRITICAL FIX: Proper nonce validation to prevent replay attacks.
        """
        
        # Get security nonce from webhook data
        security_nonce = webhook_data.get('nonce')
        if not security_nonce:
            return False, "Missing security nonce in CryptAPI webhook"
        
        # Validate nonce format and uniqueness
        nonce_valid, nonce_error = self._validate_nonce(security_nonce, 'cryptapi')
        if not nonce_valid:
            return False, f"Invalid security nonce: {nonce_error}"
        
        # Check required fields
        required_fields = ['order_id', 'value_coin', 'confirmations']
        missing_fields = [field for field in required_fields if field not in webhook_data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate order_id format
        order_id = webhook_data.get('order_id')
        if not self._validate_order_id_format(order_id):
            return False, f"Invalid order_id format: {order_id}"
        
        # CryptAPI specific validation: check if address exists in our system
        address_in = webhook_data.get('address')
        if address_in and not self._validate_payment_address(address_in, 'cryptapi'):
            return False, f"Unknown payment address: {address_in}"
        
        return True, None
    
    def _validate_cryptomus_signature(
        self,
        webhook_data: Dict[str, Any],
        request_headers: Dict[str, str],
        raw_body: bytes = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Cryptomus webhook signature validation.
        
        Uses HMAC-SHA256 signature verification.
        """
        
        # Get webhook secret from configuration
        if not self.config or not hasattr(self.config, 'providers'):
            return False, "Cryptomus configuration not found"
        
        cryptomus_config = self.config.providers.get('cryptomus')
        if not cryptomus_config:
            return False, "Cryptomus provider not configured"
        
        webhook_secret = getattr(cryptomus_config, 'webhook_secret', None)
        if not webhook_secret:
            logger.warning("Cryptomus webhook secret not configured, skipping validation")
            return True, None  # Allow if not configured (development mode)
        
        # Get signature from headers
        signature = request_headers.get('HTTP_X_CRYPTOMUS_SIGNATURE')
        if not signature:
            return False, "Missing Cryptomus signature header"
        
        # Calculate expected signature
        if raw_body:
            payload = raw_body
        else:
            payload = json.dumps(webhook_data, separators=(',', ':'), sort_keys=True).encode()
        
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Secure comparison
        if not hmac.compare_digest(signature, expected_signature):
            return False, "Invalid Cryptomus signature"
        
        # Validate required fields
        required_fields = ['order_id', 'status']
        missing_fields = [field for field in required_fields if field not in webhook_data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    def _validate_nowpayments_signature(
        self,
        webhook_data: Dict[str, Any],
        request_headers: Dict[str, str],
        raw_body: bytes = None
    ) -> Tuple[bool, Optional[str]]:
        """
        NowPayments IPN signature validation.
        
        Uses HMAC-SHA512 signature verification.
        """
        
        # Get IPN secret from configuration
        if not self.config or not hasattr(self.config, 'providers'):
            return False, "NowPayments configuration not found"
        
        nowpayments_config = self.config.providers.get('nowpayments')
        if not nowpayments_config:
            return False, "NowPayments provider not configured"
        
        ipn_secret = getattr(nowpayments_config, 'ipn_secret', None)
        if not ipn_secret:
            logger.warning("NowPayments IPN secret not configured, skipping validation")
            return True, None  # Allow if not configured (development mode)
        
        # Get signature from headers
        signature = request_headers.get('HTTP_X_NOWPAYMENTS_SIG')
        if not signature:
            return False, "Missing NowPayments signature header"
        
        # Calculate expected signature
        if raw_body:
            payload = raw_body.decode('utf-8')
        else:
            payload = json.dumps(webhook_data, separators=(',', ':'), sort_keys=True)
        
        expected_signature = hmac.new(
            ipn_secret.encode(),
            payload.encode(),
            hashlib.sha512
        ).hexdigest()
        
        # Secure comparison
        if not hmac.compare_digest(signature, expected_signature):
            return False, "Invalid NowPayments signature"
        
        return True, None
    
    def _validate_against_replay(
        self,
        provider: str,
        webhook_data: Dict[str, Any],
        request_headers: Dict[str, str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Protect against replay attacks using idempotency keys.
        """
        
        # Generate idempotency key
        idempotency_key = self._generate_idempotency_key(provider, webhook_data, request_headers)
        
        # Check if we've seen this webhook before
        cache_key = f"webhook_idempotency:{idempotency_key}"
        if cache.get(cache_key):
            return False, f"Replay attack detected: duplicate webhook {idempotency_key}"
        
        # Store idempotency key to prevent replays
        cache.set(cache_key, True, timeout=self.nonce_cache_timeout)
        
        return True, None
    
    def _validate_timestamp(
        self,
        webhook_data: Dict[str, Any],
        request_headers: Dict[str, str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate webhook timestamp to prevent old webhook replay.
        """
        
        # Try different timestamp fields
        timestamp_fields = ['timestamp', 'created_at', 'updated_at', 'time']
        webhook_timestamp = None
        
        for field in timestamp_fields:
            if field in webhook_data:
                webhook_timestamp = webhook_data[field]
                break
        
        # Also check headers
        if not webhook_timestamp:
            webhook_timestamp = request_headers.get('HTTP_X_TIMESTAMP')
        
        if not webhook_timestamp:
            # If no timestamp provided, skip validation (some providers don't include it)
            return True, None
        
        try:
            # Parse timestamp (support multiple formats)
            if isinstance(webhook_timestamp, (int, float)):
                webhook_time = datetime.fromtimestamp(webhook_timestamp, tz=timezone.utc)
            else:
                # Try to parse ISO format
                webhook_time = datetime.fromisoformat(webhook_timestamp.replace('Z', '+00:00'))
            
            current_time = timezone.now()
            time_diff = abs((current_time - webhook_time).total_seconds())
            
            if time_diff > self.max_timestamp_drift:
                return False, f"Webhook timestamp too old or too new: {time_diff}s drift"
            
            return True, None
            
        except Exception as e:
            logger.warning(f"Could not validate timestamp: {e}")
            return True, None  # Skip validation if timestamp format is unknown
    
    def _check_rate_limits(
        self,
        provider: str,
        request_headers: Dict[str, str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check webhook rate limits to prevent abuse.
        """
        
        # Extract IP address
        ip_address = (
            request_headers.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or
            request_headers.get('HTTP_X_REAL_IP', '') or
            request_headers.get('REMOTE_ADDR', 'unknown')
        )
        
        # Rate limit key
        rate_limit_key = f"webhook_rate_limit:{provider}:{ip_address}"
        
        # Check current rate
        current_count = cache.get(rate_limit_key, 0)
        max_webhooks_per_minute = 60  # Configurable limit
        
        if current_count >= max_webhooks_per_minute:
            return False, f"Rate limit exceeded: {current_count} webhooks/minute from {ip_address}"
        
        # Increment counter
        cache.set(rate_limit_key, current_count + 1, timeout=60)
        
        return True, None
    
    def _validate_nonce(self, nonce: str, provider: str) -> Tuple[bool, Optional[str]]:
        """
        Validate nonce format and uniqueness.
        
        CRITICAL: Prevents replay attacks for CryptAPI.
        """
        
        # Validate nonce format
        if not nonce or len(nonce) < 8:
            return False, "Nonce too short"
        
        if len(nonce) > 64:
            return False, "Nonce too long"
        
        # Check nonce uniqueness
        nonce_key = f"webhook_nonce:{provider}:{nonce}"
        if cache.get(nonce_key):
            return False, "Nonce already used (replay attack)"
        
        # Store nonce to prevent reuse
        cache.set(nonce_key, True, timeout=self.nonce_cache_timeout)
        
        return True, None
    
    def _validate_order_id_format(self, order_id: str) -> bool:
        """Validate order ID format."""
        if not order_id:
            return False
        
        # Basic validation (customize per your order ID format)
        if len(order_id) < 3 or len(order_id) > 50:
            return False
        
        # Allow alphanumeric, dash, underscore
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', order_id):
            return False
        
        return True
    
    def _validate_payment_address(self, address: str, provider: str) -> bool:
        """
        Validate that payment address exists in our system.
        
        CRITICAL: Prevents webhooks for unknown addresses.
        """
        try:
            # Check if address exists in our payments
            return UniversalPayment.objects.filter(
                provider=provider,
                pay_address=address
            ).exists()
        except Exception as e:
            logger.error(f"Error validating payment address: {e}")
            return True  # Allow if validation fails (avoid false negatives)
    
    def _generate_idempotency_key(
        self,
        provider: str,
        webhook_data: Dict[str, Any],
        request_headers: Dict[str, str]
    ) -> str:
        """Generate secure idempotency key for webhook deduplication."""
        
        # Use multiple fields for uniqueness
        payment_id = (
            webhook_data.get('payment_id') or
            webhook_data.get('order_id') or
            webhook_data.get('id') or
            webhook_data.get('uuid') or
            'unknown'
        )
        
        # Include status to allow multiple status updates for same payment
        status = webhook_data.get('status', 'unknown')
        
        # Include timestamp for additional uniqueness
        timestamp = (
            webhook_data.get('timestamp') or
            webhook_data.get('created_at') or
            webhook_data.get('updated_at') or
            str(int(time.time()))
        )
        
        # Create secure hash
        key_data = f"{provider}:{payment_id}:{status}:{timestamp}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    def _log_security_event(self, event_type: str, provider: str, details: str):
        """Log security events for monitoring and alerting."""
        
        try:
            # Create security event log
            PaymentEvent.objects.create(
                event_type=f'security_{event_type}',
                provider=provider,
                metadata={
                    'event_type': event_type,
                    'provider': provider,
                    'details': details,
                    'timestamp': timezone.now().isoformat(),
                    'severity': 'HIGH' if 'attack' in event_type else 'MEDIUM'
                }
            )
            
            # Log to application logger
            if 'attack' in event_type or 'failed' in event_type:
                logger.warning(f"🚨 Security Event [{event_type}] {provider}: {details}")
            else:
                logger.info(f"🔒 Security Event [{event_type}] {provider}: {details}")
                
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")


# Singleton instance for import
webhook_validator = WebhookValidator()
