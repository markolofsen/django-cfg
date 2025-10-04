# 🚀 Django CFG Twilio Integration - Complete Setup Guide

## 📋 Overview

Django CFG Twilio provides seamless integration for:
- 📱 **WhatsApp OTP** via Twilio Verify API
- 📱 **SMS OTP** via Twilio Verify API  
- 📧 **Email OTP** via SendGrid
- 🔧 **Testing Suite** with management commands
- 📧 **HTML Email Templates** with customization

## 🛠️ Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install django-cfg[twilio]
# or
poetry add django-cfg[twilio]
```

### 2. Configure Twilio Services

#### A. Create Twilio Verify Service
1. Go to [Twilio Console > Verify > Services](https://console.twilio.com/us1/develop/verify/services)
2. Click **Create new Service**
3. Name: `YourApp OTP Service`
4. **Enable channels**: WhatsApp ✅, SMS ✅
5. Copy the **Service SID** (starts with `VA...`)

#### B. Get SendGrid API Key (Optional)
1. Go to [SendGrid Console > API Keys](https://app.sendgrid.com/settings/api_keys)
2. Create new API key with **Mail Send** permissions
3. Copy the API key (starts with `SG.`)

### 3. Update Configuration Files

#### `config.dev.yaml`
```yaml
twilio:
  account_sid: "AC_YOUR_ACCOUNT_SID"
  auth_token: "YOUR_AUTH_TOKEN"
  whatsapp_from: "+14155238886"  # Twilio sandbox
  sms_from: "+YOUR_SMS_NUMBER"
  sendgrid_api_key: "SG.YOUR_SENDGRID_API_KEY"
  verify_service_sid: "VA_YOUR_VERIFY_SERVICE_SID"
```

#### `config.py`
```python
from django_cfg.modules.django_twilio.models import SendGridConfig, TwilioVerifyConfig, TwilioChannelType

class YourProjectConfig(DjangoConfig):
    # Admin emails for testing
    admin_emails: List[str] = ["admin@yourdomain.com"]
    
    # Twilio configuration
    twilio: Optional[TwilioConfig] = TwilioConfig(
        account_sid=env.twilio.account_sid,
        auth_token=SecretStr(env.twilio.auth_token),
        
        # Verify API for OTP
        verify=TwilioVerifyConfig(
            service_sid=env.twilio.verify_service_sid,
            service_name=env.app.name,
            default_channel=TwilioChannelType.WHATSAPP,
            fallback_channels=[TwilioChannelType.SMS],
            code_length=6,
            ttl_seconds=600,  # 10 minutes
            max_attempts=5,
        ) if env.twilio.verify_service_sid else None,
        
        # SendGrid for email
        sendgrid=SendGridConfig(
            api_key=SecretStr(env.twilio.sendgrid_api_key),
            from_email="noreply@yourdomain.com",
            from_name=env.app.name,
            default_subject=f"Your {env.app.name} verification code",
        ) if env.twilio.sendgrid_api_key else None,
    ) if env.twilio.account_sid and env.twilio.auth_token else None
```

## 🧪 Testing Everything

### Quick Test Command
```bash
# Test all services
python manage.py test_twilio --mode=all

# Test OTP only
python manage.py test_twilio --mode=test-otp --phone="+1234567890"

# Interactive mode
python manage.py test_twilio --interactive

# Check configuration
python manage.py test_twilio --mode=setup
```

### Expected Output
```
🚀 Django CFG Twilio Test Suite
==================================================
📧 Using admin email from config: admin@yourdomain.com

🔧 Configuration Check
------------------------------
✅ Admin emails configured
✅ Twilio configuration found
✅ Verify API configured
✅ SendGrid configured
✅ Email configuration found

🔐 Testing OTP Functionality
------------------------------
📱 Testing WhatsApp OTP to +1234567890...
✅ OTP sent via WhatsApp to ***7890

📧 Testing Email OTP to admin@yourdomain.com...
✅ Email OTP sent (code: 123456)

🎉 All tests completed!
```

## 🔌 API Usage

### Basic OTP Request
```python
from django_cfg.modules.django_twilio import send_whatsapp_otp, verify_otp

# Send WhatsApp OTP
success, message = send_whatsapp_otp("+1234567890")

# Verify OTP
is_valid, message = verify_otp("+1234567890", "123456")
```

### Email OTP
```python
from django_cfg.modules.django_twilio import send_otp_email

# Send email OTP
success, message, otp_code = send_otp_email("user@example.com")
```

### REST API Endpoints
```bash
# Request OTP
curl -X POST http://localhost:8000/api/accounts/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "+1234567890", "channel": "phone"}'

# Verify OTP
curl -X POST http://localhost:8000/api/accounts/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"identifier": "+1234567890", "otp": "123456", "channel": "phone"}'
```

## 📧 Email Templates

### Template Structure
```
django_cfg/modules/django_twilio/templates/
├── email_otp_template.html      # Main HTML template
├── email_otp_test_data.json     # Test data
└── email_otp_rendered.html      # Generated preview
```

### Template Variables
- `{{app_name}}` - Your app name
- `{{user_name}}` - User's name
- `{{otp_code}}` - 6-digit OTP code
- `{{otp_link}}` - Verification link
- `{{expires_minutes}}` - Expiry time

### Generate Templates
```bash
python manage.py test_twilio --mode=generate-templates
```

## 🚨 Troubleshooting

### Common Issues

#### 1. WhatsApp Not Working
```
❌ Error: Unable to create record: Delivery channel disabled: WHATSAPP
```
**Solution**: Enable WhatsApp channel in [Twilio Console > Verify > Services](https://console.twilio.com/us1/develop/verify/services)

#### 2. SMS to International Numbers
```
❌ Error: Message cannot be sent with current 'To' and 'From' parameters
```
**Solution**: Use Verify API (automatic) or upgrade Twilio account for international SMS

#### 3. SendGrid Not Working
```
❌ Error: SendGrid configuration not found
```
**Solution**: Add `sendgrid_api_key` to your YAML config and enable in `config.py`

#### 4. Email Not Sending
```
❌ Error: Email backend not configured
```
**Solution**: Check email configuration in `config.py` and ensure SMTP settings are correct

### Debug Mode
```python
# Enable detailed logging
twilio: TwilioConfig = TwilioConfig(
    debug_logging=True,  # Shows all API requests/responses
    test_mode=True,      # Uses test credentials
)
```

## 📱 Production Checklist

### Before Going Live:

#### Twilio Setup
- [ ] **Account verified** and upgraded from trial
- [ ] **Phone numbers verified** for SMS
- [ ] **WhatsApp Business approved** (if using production WhatsApp)
- [ ] **Verify Service** created and channels enabled
- [ ] **Webhook URLs** configured (optional)

#### SendGrid Setup  
- [ ] **Domain authentication** completed
- [ ] **Sender identity** verified
- [ ] **API key** with proper permissions
- [ ] **Email templates** tested and approved

#### Security
- [ ] **Environment variables** for sensitive data
- [ ] **Rate limiting** configured
- [ ] **Admin emails** updated for production
- [ ] **Error monitoring** setup (Sentry, etc.)

#### Testing
- [ ] **All OTP channels** tested with real numbers
- [ ] **Email delivery** tested with real addresses  
- [ ] **Error handling** tested with invalid inputs
- [ ] **Load testing** completed for expected volume

## 🔗 Useful Links

- [Twilio Console](https://console.twilio.com/)
- [Twilio Verify API Docs](https://www.twilio.com/docs/verify/api)
- [SendGrid Console](https://app.sendgrid.com/)
- [Django CFG Documentation](https://github.com/your-repo/django-cfg)

## 💡 Pro Tips

1. **Use Verify API** for professional OTP instead of custom solutions
2. **Enable both WhatsApp and SMS** for better delivery rates
3. **Test with real numbers** in different countries
4. **Monitor delivery rates** in Twilio Console
5. **Use admin_emails** for easy testing configuration
6. **Keep templates simple** for better email client compatibility

---

🎉 **You're all set!** Your Django CFG Twilio integration is ready for production use.

For support, check the troubleshooting section or create an issue on GitHub.
