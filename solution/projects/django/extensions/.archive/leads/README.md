# 🎯 Django CFG Leads App

Universal lead management system for collecting and managing potential customers from all websites.

## 🎯 Features

- **Universal Lead Collection** - Single model for leads from all sites
- **Contact Form API** - REST API endpoint for frontend forms
- **Lead Status Tracking** - Full lifecycle management (New → Contacted → Qualified → Converted/Rejected)
- **Multiple Contact Types** - Email, WhatsApp, Telegram, Phone, Other
- **Automatic Notifications** - Telegram alerts for new leads
- **Rich Metadata** - IP address, User Agent, site URL tracking
- **Admin Interface** - Full management with Unfold theme

## 🏗️ Architecture

### Models
- `Lead` - Universal lead model with full contact information and metadata

### API Endpoints (DRF)
```
POST   /leads/submit/          - Submit new lead from frontend form
GET    /leads/                 - List leads (admin only)
GET    /leads/{id}/            - Lead details (admin only)
PUT    /leads/{id}/            - Update lead (admin only)
DELETE /leads/{id}/            - Delete lead (admin only)
```

## 🚀 Usage

### Frontend Form Integration
```javascript
// Submit lead form
const submitLead = async (formData) => {
    const response = await fetch('/cfg/leads/leads/submit/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: formData.name,
            email: formData.email,
            company: formData.company,
            company_site: formData.companyWebsite,
            contact_type: 'email',
            contact_value: formData.email,
            subject: formData.subject,
            message: formData.message,
            site_url: window.location.origin
        })
    });
    
    const result = await response.json();
    return result;
};
```

### API Example
```python
# Submit lead
POST /cfg/leads/leads/submit/
{
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Tech Corp",
    "company_site": "https://techcorp.com",
    "contact_type": "email",
    "contact_value": "john@example.com",
    "subject": "Partnership Inquiry",
    "message": "I'm interested in discussing a potential partnership.",
    "site_url": "https://mysite.com/contact"
}

# Response
{
    "success": true,
    "message": "Lead submitted successfully",
    "lead_id": 123
}
```

## 🔧 Integration

The app is automatically integrated into Django CFG:
- URLs: `/leads/` (included in main URL config)
- Admin: Available in Django admin with Unfold theme
- Signals: Auto-send Telegram notifications for new leads
- Permissions: Public API for form submission, admin-only for management

## 📊 Lead Lifecycle

1. **New** - Initial submission from frontend form
2. **Contacted** - Sales team has reached out
3. **Qualified** - Lead meets criteria and shows interest
4. **Converted** - Lead became a customer
5. **Rejected** - Lead doesn't meet criteria or not interested

## 🔔 Notifications

Automatic Telegram notifications include:
- Lead name, email, company
- Contact preferences
- Message preview
- Site source URL
- Timestamp and metadata

## 📝 Notes

- All leads are collected in a single universal model
- Automatic metadata collection (IP, User Agent, timestamp)
- Integration with Django CFG Telegram notifications
- KISS principle - simple, focused functionality
- Follows Django CFG patterns and conventions
