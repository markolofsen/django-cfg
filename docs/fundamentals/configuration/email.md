---
title: Email Models
description: EmailConfig model for SMTP, SendGrid, and Console email backends
sidebar_label: Email Models
sidebar_position: 6
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Email Models

:::tip[Automatic Backend Selection]
Django-CFG provides **type-safe email configuration** with automatic backend selection - Console for development, SMTP/SendGrid for production.
:::

Django-CFG provides `EmailConfig` model for type-safe email configuration with support for SMTP, SendGrid, and Console backends.

## EmailConfig

Type-safe email service configuration.

### Complete Model

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal

class EmailConfig(BaseModel):
    """
    Email service configuration for SMTP, SendGrid, or console backend.
    """

    backend: Literal["console", "smtp", "sendgrid"] = Field(
        default="console",
        description="Email backend type"
    )
    host: str = Field(
        default="localhost",
        description="SMTP server hostname"
    )
    port: int = Field(
        default=587,
        description="SMTP server port",
        ge=1,
        le=65535
    )
    username: Optional[str] = Field(
        default=None,
        description="SMTP username"
    )
    password: Optional[str] = Field(
        default=None,
        description="SMTP password"
    )
    use_tls: bool = Field(
        default=True,
        description="Use TLS encryption"
    )
    use_ssl: bool = Field(
        default=False,
        description="Use SSL encryption"
    )
    default_from: str = Field(
        default="noreply@example.com",
        description="Default FROM email address"
    )
    timeout: int = Field(
        default=30,
        description="Email send timeout in seconds",
        ge=1
    )

    @field_validator('backend')
    @classmethod
    def validate_backend(cls, v):
        """Validate email backend"""
        if v not in ['console', 'smtp', 'sendgrid']:
            raise ValueError("Backend must be 'console', 'smtp', or 'sendgrid'")
        return v

    def to_django_config(self) -> dict:
        """Convert to Django email settings"""
        if self.backend == "console":
            return {
                'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend'
            }
        elif self.backend == "sendgrid":
            return {
                'EMAIL_BACKEND': 'sendgrid_backend.SendgridBackend',
                'SENDGRID_API_KEY': self.password,
                'EMAIL_HOST_USER': self.username,
                'DEFAULT_FROM_EMAIL': self.default_from,
            }
        else:  # smtp
            return {
                'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                'EMAIL_HOST': self.host,
                'EMAIL_PORT': self.port,
                'EMAIL_HOST_USER': self.username,
                'EMAIL_HOST_PASSWORD': self.password,
                'EMAIL_USE_TLS': self.use_tls,
                'EMAIL_USE_SSL': self.use_ssl,
                'DEFAULT_FROM_EMAIL': self.default_from,
                'EMAIL_TIMEOUT': self.timeout,
            }
```

## Usage Examples

<Tabs>
  <TabItem value="console" label="Console (Development)" default>

```python
from django_cfg import DjangoConfig
from django_cfg.models import EmailConfig

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = True

    email: EmailConfig = EmailConfig(
        backend="console"  # Prints emails to console
    )
```

**Generated Django settings:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Usage:**
```python
from django.core.mail import send_mail

send_mail(
    'Subject',
    'Message body',
    'from@example.com',
    ['to@example.com'],
)
# Email printed to console instead of sent
```

:::note[Console Backend Use Case]
Console backend is ideal for:
- **Development** - See email content without sending
- **Testing** - Verify email content in unit tests
- **Debugging** - Inspect email formatting

**Not suitable for:**
- ❌ Production environments
- ❌ Actual email delivery
- ❌ User notifications
:::

  </TabItem>
  <TabItem value="smtp" label="SMTP (Production)">

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.gmail.com",
        port=587,
        username="your-email@gmail.com",
        password="your-app-password",
        use_tls=True,
        default_from="noreply@myapp.com",
        timeout=30
    )
```

**Generated Django settings:**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'noreply@myapp.com'
EMAIL_TIMEOUT = 30
```

:::warning[SMTP Credentials Security]
**Never hardcode SMTP credentials:**
- Use environment variables for username/password
- Use app-specific passwords (not account passwords)
- Enable TLS encryption (`use_tls=True`)
- Store credentials in secure secrets manager
:::

  </TabItem>
  <TabItem value="sendgrid" label="SendGrid (Production)">

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    email: EmailConfig = EmailConfig(
        backend="sendgrid",
        username="apikey",
        password="SG.your-sendgrid-api-key",
        default_from="noreply@myapp.com"
    )
```

**Generated Django settings:**
```python
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'SG.your-sendgrid-api-key'
EMAIL_HOST_USER = 'apikey'
DEFAULT_FROM_EMAIL = 'noreply@myapp.com'
```

:::info[SendGrid Benefits]
SendGrid provides:
- ✅ **High deliverability** - Dedicated IP addresses
- ✅ **Analytics** - Email open/click tracking
- ✅ **Templates** - Transactional email templates
- ✅ **Scalability** - Send millions of emails
- ✅ **No SMTP management** - API-based delivery

**Requirements:**
- Install `sendgrid-django` package
- Verify sender domain in SendGrid dashboard
- Use API key (not SMTP credentials)
:::

  </TabItem>
</Tabs>

## Provider-Specific Examples

<Tabs>
  <TabItem value="gmail" label="Gmail SMTP" default>

```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.gmail.com",
        port=587,
        username="your-email@gmail.com",
        password="your-app-password",  # Generate at https://myaccount.google.com/apppasswords
        use_tls=True,
        default_from="your-email@gmail.com"
    )
```

:::warning[Gmail Requirements]
**Before using Gmail SMTP:**
1. ✅ Enable 2-Factor Authentication in Gmail
2. ✅ Generate App Password at https://myaccount.google.com/apppasswords
3. ✅ Use App Password (not regular password)
4. ✅ Verify FROM address matches Gmail account

**Common Issues:**
- ❌ "Username and Password not accepted" - Use App Password
- ❌ Daily sending limit: 500 emails/day for free accounts
- ❌ Rate limits apply - consider dedicated SMTP for production
:::

  </TabItem>
  <TabItem value="ses" label="AWS SES">

```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="email-smtp.us-east-1.amazonaws.com",
        port=587,
        username="YOUR_SES_SMTP_USERNAME",
        password="YOUR_SES_SMTP_PASSWORD",
        use_tls=True,
        default_from="verified@yourdomain.com"  # Must be verified in SES
    )
```

:::info[AWS SES Configuration]
**Setup Steps:**
1. Verify sender email/domain in AWS SES console
2. Create SMTP credentials (IAM → SES SMTP credentials)
3. Request production access (sandbox mode limited to verified emails)
4. Configure SPF/DKIM records for better deliverability

**Benefits:**
- ✅ High deliverability and reputation
- ✅ Pay-as-you-go pricing ($0.10 per 1000 emails)
- ✅ Integrated with AWS ecosystem
- ✅ Detailed sending statistics
:::

  </TabItem>
  <TabItem value="mailgun" label="Mailgun SMTP">

```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.mailgun.org",
        port=587,
        username="postmaster@yourdomain.mailgun.org",
        password="your-mailgun-smtp-password",
        use_tls=True,
        default_from="noreply@yourdomain.com"
    )
```

:::note[Mailgun Setup]
**Configuration:**
- Use sandbox domain for testing
- Add custom domain for production
- Verify domain with DNS records
- Get SMTP credentials from Mailgun dashboard

**Free Tier:**
- 5,000 emails/month free
- Email validation API included
- Analytics and tracking
:::

  </TabItem>
  <TabItem value="office365" label="Office 365">

```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.office365.com",
        port=587,
        username="your-email@yourdomain.com",
        password="your-password",
        use_tls=True,
        default_from="your-email@yourdomain.com"
    )
```

:::warning[Office 365 Notes]
**Requirements:**
- Valid Office 365 subscription
- FROM address must match authenticated user
- Modern authentication may require app password

**Limitations:**
- 30 messages/minute rate limit
- 10,000 recipients/day limit
- Not recommended for bulk sending
:::

  </TabItem>
</Tabs>

## SSL vs TLS

### TLS (Port 587) - Recommended

```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.example.com",
        port=587,
        use_tls=True,   # ✅ TLS encryption
        use_ssl=False,
        username="user",
        password="pass"
    )
```

**Advantages:**
- Standard port for STARTTLS
- More compatible
- Recommended by most providers

### SSL (Port 465)

```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.example.com",
        port=465,
        use_tls=False,
        use_ssl=True,   # ✅ SSL encryption
        username="user",
        password="pass"
    )
```

**Advantages:**
- Older standard
- Some providers require it

## Environment-Specific Configuration

### Using Properties

```python
import os

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"

    @property
    def email(self) -> EmailConfig:
        if self._environment == "production":
            return EmailConfig(
                backend="sendgrid",
                username="apikey",
                password=os.getenv('SENDGRID_API_KEY'),
                default_from="noreply@myapp.com"
            )
        elif self._environment == "staging":
            return EmailConfig(
                backend="smtp",
                host="smtp.gmail.com",
                port=587,
                username=os.getenv('SMTP_USER'),
                password=os.getenv('SMTP_PASSWORD'),
                use_tls=True,
                default_from="staging@myapp.com"
            )
        else:  # development
            return EmailConfig(
                backend="console"
            )
```

### Using YAML

```yaml
# config.production.yaml
email:
  backend: "sendgrid"
  username: "apikey"
  password: "${SENDGRID_API_KEY}"
  default_from: "noreply@myapp.com"

# config.development.yaml
email:
  backend: "console"
```

## Advanced Usage

### Custom Timeout

```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.example.com",
        port=587,
        username="user",
        password="pass",
        use_tls=True,
        timeout=60  # 60 seconds timeout for slow connections
    )
```

### Multiple FROM Addresses

```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.gmail.com",
        port=587,
        username="your-email@gmail.com",
        password="your-app-password",
        use_tls=True,
        default_from="noreply@myapp.com"  # Default FROM
    )
```

**Usage:**
```python
from django.core.mail import send_mail

# Use default FROM
send_mail('Subject', 'Body', None, ['to@example.com'])

# Override FROM
send_mail('Subject', 'Body', 'support@myapp.com', ['to@example.com'])
```

## Testing

### Send Test Email

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email from Django-CFG',
    'noreply@myapp.com',
    ['test@example.com'],
    fail_silently=False,
)
```

### Test Configuration

```python
# tests/test_email.py
from django.core.mail import send_mail
from django.test import TestCase, override_settings

class EmailTestCase(TestCase):
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_email(self):
        send_mail('Subject', 'Body', 'from@example.com', ['to@example.com'])

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].subject, 'Subject')
```

## Security Best Practices

:::danger[Email Security Critical]
Email credentials are **high-value targets** for attackers. Compromised email access can lead to:
- ❌ Spam/phishing sent from your domain
- ❌ Reputation damage and blacklisting
- ❌ Account takeovers via password resets
- ❌ Data breaches through email access

**Always follow ALL security practices below.**
:::

<Tabs>
  <TabItem value="env-vars" label="Environment Variables" default>

### 1. Use Environment Variables

:::warning[Never Hardcode Credentials]
Hardcoded email credentials can be:
- Leaked through version control (git history)
- Exposed in error messages and logs
- Found via code search tools
- Stolen if server is compromised
:::

**❌ Bad:**
```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        username="user@example.com",  # ❌ EXPOSED
        password="actual-password-123",  # ❌ LEAKED
    )
```

**✅ Good:**
```python
import os

class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host=os.getenv('EMAIL_HOST'),
        port=int(os.getenv('EMAIL_PORT', '587')),
        username=os.getenv('EMAIL_USER'),
        password=os.getenv('EMAIL_PASSWORD'),
        use_tls=True,
        default_from=os.getenv('DEFAULT_FROM_EMAIL')
    )
```

  </TabItem>
  <TabItem value="tls" label="TLS/SSL Encryption">

### 2. Enable TLS/SSL

:::danger[Unencrypted Email]
Without TLS/SSL encryption:
- Passwords transmitted in **plain text**
- Email content readable by network sniffers
- Man-in-the-middle attacks possible
- Compliance violations (GDPR, HIPAA)
:::

**❌ Bad:**
```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.example.com",
        port=25,  # ❌ Unencrypted port
        use_tls=False,  # ❌ No encryption
        use_ssl=False,  # ❌ No encryption
    )
```

**✅ Good:**
```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.example.com",
        port=587,
        use_tls=True,  # ✅ Encryption enabled
        username="user",
        password="pass"
    )
```

  </TabItem>
  <TabItem value="app-passwords" label="App Passwords">

### 3. Use App Passwords

:::warning[Gmail App Passwords Required]
Gmail **blocks** regular passwords for SMTP since May 2022. You must:
1. Enable 2-Factor Authentication
2. Generate App Password (16-character code)
3. Use App Password for SMTP (not account password)

Regular passwords will fail with "Username and Password not accepted" error.
:::

**✅ Gmail with App Password:**
```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.gmail.com",
        port=587,
        username="your-email@gmail.com",
        password="abcd efgh ijkl mnop",  # ✅ 16-char App Password
        use_tls=True
    )
```

  </TabItem>
  <TabItem value="domain" label="Domain Verification">

### 4. Validate FROM Address

:::info[Domain Reputation]
Using verified domains improves:
- ✅ **Deliverability** - Lower spam scores
- ✅ **Trust** - SPF/DKIM authentication
- ✅ **Reputation** - Sender reputation tracking

**Unverified domains:**
- ❌ High spam scores
- ❌ Emails blocked by providers
- ❌ No SPF/DKIM authentication
:::

**✅ Good:**
```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.example.com",
        port=587,
        username="user",
        password="pass",
        use_tls=True,
        default_from="noreply@verified-domain.com"  # ✅ Verified domain
    )
```

  </TabItem>
</Tabs>

## Troubleshooting

### Authentication Failed (Gmail)

**Error:**
```
SMTPAuthenticationError: Username and Password not accepted
```

**Solution:**
- Enable 2FA in Gmail
- Generate App Password at https://myaccount.google.com/apppasswords
- Use App Password instead of regular password

### Connection Timeout

**Error:**
```
socket.timeout: timed out
```

**Solution:**
```python
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.example.com",
        port=587,
        timeout=60,  # Increase timeout
        username="user",
        password="pass"
    )
```

### TLS/SSL Errors

**Error:**
```
ssl.SSLError: [SSL: WRONG_VERSION_NUMBER]
```

**Solution:**
```python
# Try port 465 with SSL instead of 587 with TLS
class MyConfig(DjangoConfig):
    email: EmailConfig = EmailConfig(
        backend="smtp",
        host="smtp.example.com",
        port=465,
        use_tls=False,
        use_ssl=True,  # Use SSL instead of TLS
        username="user",
        password="pass"
    )
```

### SendGrid Errors

**Error:**
```
HTTP Error 403: Forbidden
```

**Solution:**
- Verify API key is correct
- Check SendGrid account is active
- Verify FROM address is verified in SendGrid

## Validation

EmailConfig validates:

- **Backend** - Must be 'console', 'smtp', or 'sendgrid'
- **Port** - Must be 1-65535
- **Timeout** - Must be ≥ 1 second

**Example validation error:**

```python
# ❌ Invalid backend
EmailConfig(
    backend="invalid"  # Validation error
)

# ❌ Invalid port
EmailConfig(
    backend="smtp",
    port=99999  # Validation error
)
```

## See Also

- [**DjangoConfig**](./django-settings) - Base configuration class
- [**Configuration Overview**](./) - Configuration system overview
