"""
Webhook types for the Universal Payment System v2.0.

Pydantic models for webhook validation and processing.
"""

from decimal import Decimal
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, timedelta


class WebhookData(BaseModel):
    """Base webhook data structure."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    provider: str = Field(description="Provider name")
    payment_id: str = Field(description="Payment ID")
    status: str = Field(description="Payment status")
    timestamp: datetime = Field(description="Webhook timestamp")
    signature: Optional[str] = Field(None, description="Webhook signature")
    raw_payload: Dict[str, Any] = Field(description="Raw webhook payload")


class NowPaymentsWebhook(BaseModel):
    """
    NowPayments webhook structure.
    
    Based on NowPayments IPN (Instant Payment Notification) format.
    """
    model_config = ConfigDict(validate_assignment=True, extra="allow")
    
    # Required fields from NowPayments
    payment_id: str = Field(description="NowPayments payment ID")
    payment_status: Literal[
        'waiting', 'confirming', 'confirmed', 'sending', 'partially_paid', 
        'finished', 'failed', 'refunded', 'expired'
    ] = Field(description="Payment status")
    pay_address: str = Field(description="Payment address")
    price_amount: Decimal = Field(description="Original price amount")
    price_currency: str = Field(description="Original price currency (USD)")
    pay_amount: Decimal = Field(description="Amount to pay in crypto")
    pay_currency: str = Field(description="Cryptocurrency code")
    order_id: Optional[str] = Field(None, description="Order ID")
    order_description: Optional[str] = Field(None, description="Order description")
    
    # Optional fields
    actually_paid: Optional[Decimal] = Field(None, description="Actually paid amount")
    outcome_amount: Optional[Decimal] = Field(None, description="Outcome amount")
    outcome_currency: Optional[str] = Field(None, description="Outcome currency")
    
    # Network information
    network: Optional[str] = Field(None, description="Blockchain network")
    txn_id: Optional[str] = Field(None, description="Transaction ID")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    
    # Additional data
    purchase_id: Optional[str] = Field(None, description="Purchase ID")
    smart_contract: Optional[str] = Field(None, description="Smart contract address")
    burning_percent: Optional[str] = Field(None, description="Burning percentage")
    
    @field_validator('payment_status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate payment status."""
        valid_statuses = [
            'waiting', 'confirming', 'confirmed', 'sending', 'partially_paid',
            'finished', 'failed', 'refunded', 'expired'
        ]
        if v not in valid_statuses:
            raise ValueError(f"Invalid payment status: {v}")
        return v
    
    @field_validator('price_currency')
    @classmethod
    def validate_price_currency(cls, v: str) -> str:
        """Validate price currency is USD."""
        if v.upper() != 'USD':
            raise ValueError("Price currency must be USD")
        return v.upper()
    
    def to_universal_status(self) -> str:
        """Convert NowPayments status to universal payment status."""
        status_mapping = {
            'waiting': 'pending',
            'confirming': 'confirming',
            'confirmed': 'confirmed',
            'sending': 'processing',
            'partially_paid': 'partial',
            'finished': 'completed',
            'failed': 'failed',
            'refunded': 'refunded',
            'expired': 'expired'
        }
        return status_mapping.get(self.payment_status, 'unknown')
    
    def is_final_status(self) -> bool:
        """Check if payment status is final."""
        final_statuses = ['finished', 'failed', 'refunded', 'expired']
        return self.payment_status in final_statuses
    
    def is_successful(self) -> bool:
        """Check if payment is successful."""
        return self.payment_status == 'finished'


class WebhookProcessingResult(BaseModel):
    """Result of webhook processing."""
    model_config = ConfigDict(validate_assignment=True)
    
    success: bool = Field(description="Processing success")
    webhook_id: Optional[str] = Field(None, description="Webhook ID")
    payment_id: Optional[str] = Field(None, description="Related payment ID")
    provider: str = Field(description="Provider name")
    status_before: Optional[str] = Field(None, description="Status before processing")
    status_after: Optional[str] = Field(None, description="Status after processing")
    actions_taken: list[str] = Field(default_factory=list, description="Actions performed")
    balance_updated: bool = Field(default=False, description="Whether balance was updated")
    notifications_sent: list[str] = Field(default_factory=list, description="Notifications sent")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    processed: bool = Field(default=False, description="Whether webhook was processed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")


class WebhookValidationResult(BaseModel):
    """Result of webhook validation."""
    model_config = ConfigDict(validate_assignment=True)
    
    is_valid: bool = Field(description="Validation result")
    provider: str = Field(description="Provider name")
    signature_valid: Optional[bool] = Field(None, description="Signature validation result")
    payload_valid: bool = Field(description="Payload validation result")
    error_message: Optional[str] = Field(None, description="Validation error message")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="Parsed webhook data")


class WebhookSignature(BaseModel):
    """Webhook signature validation data."""
    model_config = ConfigDict(validate_assignment=True)
    
    provider: str = Field(description="Provider name")
    signature: str = Field(description="Webhook signature")
    payload: str = Field(description="Raw payload string")
    secret_key: str = Field(description="Secret key for validation")
    algorithm: str = Field(default="sha512", description="Signature algorithm")
    
    def validate_signature(self) -> bool:
        """Validate webhook signature."""
        import hmac
        import hashlib
        
        if self.algorithm == "sha512":
            expected = hmac.new(
                self.secret_key.encode('utf-8'),
                self.payload.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
        elif self.algorithm == "sha256":
            expected = hmac.new(
                self.secret_key.encode('utf-8'),
                self.payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
        return hmac.compare_digest(expected, self.signature)


class WebhookRetry(BaseModel):
    """Webhook retry configuration."""
    model_config = ConfigDict(validate_assignment=True)
    
    webhook_id: str = Field(description="Webhook ID")
    attempt_number: int = Field(description="Retry attempt number")
    max_attempts: int = Field(default=3, description="Maximum retry attempts")
    delay_seconds: int = Field(default=60, description="Delay between retries")
    last_error: Optional[str] = Field(None, description="Last error message")
    next_retry_at: Optional[datetime] = Field(None, description="Next retry timestamp")
    
    def should_retry(self) -> bool:
        """Check if webhook should be retried."""
        return self.attempt_number < self.max_attempts
    
    def calculate_next_retry(self) -> datetime:
        """Calculate next retry timestamp with exponential backoff."""
        import math
        
        # Exponential backoff: delay * (2 ^ attempt_number)
        delay = self.delay_seconds * (2 ** self.attempt_number)
        # Cap at 1 hour
        delay = min(delay, 3600)
        
        return datetime.utcnow() + timedelta(seconds=delay)


class WebhookEvent(BaseModel):
    """Webhook event for logging and monitoring."""
    model_config = ConfigDict(validate_assignment=True)
    
    event_id: str = Field(description="Event ID")
    webhook_id: str = Field(description="Webhook ID")
    provider: str = Field(description="Provider name")
    event_type: Literal['received', 'validated', 'processed', 'failed', 'retried'] = Field(
        description="Event type"
    )
    payment_id: Optional[str] = Field(None, description="Related payment ID")
    status: Optional[str] = Field(None, description="Payment status")
    message: Optional[str] = Field(None, description="Event message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    ip_address: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    
    def to_log_entry(self) -> Dict[str, Any]:
        """Convert to structured log entry."""
        return {
            'event_id': self.event_id,
            'webhook_id': self.webhook_id,
            'provider': self.provider,
            'event_type': self.event_type,
            'payment_id': self.payment_id,
            'status': self.status,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'metadata': self.metadata
        }
