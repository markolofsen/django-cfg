# Newsletter Manager

Custom manager for the `Newsletter` model with email newsletter sending functionality.

## Description

`NewsletterManager` provides convenient methods for working with newsletters, including:

- Getting newsletters by status
- Starting background sending
- Newsletter statistics
- Error handling

## Usage

### Basic Methods

```python
from mailer.managers.newsletter_manager import NewsletterManager
from mailer.models import Newsletter

# Create manager
manager = NewsletterManager()

# Get newsletters by status
draft_newsletters = manager.get_draft_newsletters()
sending_newsletters = manager.get_sending_newsletters()
sent_newsletters = manager.get_sent_newsletters()
failed_newsletters = manager.get_failed_newsletters()

# Statistics
stats = manager.get_newsletter_stats()
print(f"Total: {stats['total']}")
print(f"Drafts: {stats['draft']}")
print(f"Sending: {stats['sending']}")
print(f"Sent: {stats['sent']}")
print(f"Failed: {stats['failed']}")
```

### Sending Newsletter

```python
# Get newsletter
newsletter = Newsletter.objects.get(id=1)

# Start sending (only for DRAFT status)
if newsletter.status == Newsletter.NewsletterStatus.DRAFT:
    success = manager.start_sending(newsletter)
    if success:
        print("Sending started in background")
    else:
        print("Failed to start sending")
```

### Direct Model Usage

```python
# Newsletter has built-in start_sending method
newsletter = Newsletter.objects.get(id=1)
success = newsletter.start_sending()
```

### Error Handling

```python
# Mark newsletter as failed
manager.mark_as_failed(newsletter, "SMTP server error")
```

## Newsletter Statuses

- `DRAFT` - Draft (default)
- `SENDING` - Currently sending
- `SENT` - Sent successfully
- `FAILED` - Failed to send

## Background Sending

When calling `start_sending()`:

1. Newsletter status is checked (must be DRAFT)
2. Status changes to SENDING
3. Background thread starts
4. Emails are sent sequentially to all active users
5. Status changes to SENT when complete

## Logging

All operations are logged with `[Newsletter Thread]` prefix:

```
[Newsletter Thread] Starting sequential send for newsletter 'Test' to 5 users.
[Newsletter Thread] Progress for 'Test': 50/100 processed (45 sent, 5 failed).
[Newsletter Thread] Finished sending newsletter 'Test'. Total sent: 95, Total failed: 5.
```

## Testing

Run tests:

```bash
# From Django project root
python manage.py test mailer.tests

# Or via script
python src/mailer/tests/run_tests.py
```

## Admin Integration

Django Admin actions added:

- "Start Sending This Newsletter" - for individual newsletter
- "Send selected newsletters" - for bulk sending

## Dependencies

- `threading` - for background sending
- `EmailService` - for email sending
- `CustomUser` - user model
