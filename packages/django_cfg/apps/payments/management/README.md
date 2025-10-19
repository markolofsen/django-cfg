# Payment Management Commands

Interactive CLI commands for managing payments in Payments v2.0.

## Commands Overview

### 1. `sync_currencies` - Sync currencies from NowPayments

Fetch available cryptocurrencies from NowPayments API and update local database.

**Usage:**

```bash
# Interactive mode (with confirmation)
python manage.py sync_currencies

# Skip confirmation
python manage.py sync_currencies --skip-confirmation

# Dry run (preview changes without saving)
python manage.py sync_currencies --dry-run

# Deactivate currencies not in provider response
python manage.py sync_currencies --deactivate-missing
```

**Features:**
- ✅ Fetches all available currencies from NowPayments
- ✅ Creates new currencies in database
- ✅ Updates existing currencies
- ✅ Shows summary by network (Bitcoin, Ethereum, TRC20, etc.)
- ✅ Dry run mode for testing
- ✅ Rich formatted output with colors

**Example:**

```bash
$ python manage.py sync_currencies

🔄 Currency Sync from NowPayments

Fetching currencies from NowPayments...
✓ Fetched 150 currencies

┌─ Fetched Currencies Summary ─┐
│ Network          │ Count     │
├──────────────────┼───────────┤
│ TRC20            │      35   │
│ ERC20            │      28   │
│ BEP20            │      20   │
│ Native           │      15   │
│ ...              │      ...  │
├──────────────────┼───────────┤
│ TOTAL            │     150   │
└──────────────────┴───────────┘

Proceed with currency sync? Yes

✓ Created: 150 new currencies
↻ Updated: 0 existing currencies
```

---

### 2. `create_payment` - Create payment interactively

Interactive wizard to create a payment using questionary.

**Usage:**

```bash
# Interactive mode (full wizard)
python manage.py create_payment

# With pre-filled parameters
python manage.py create_payment --user-id 1 --amount 100.00 --currency USDTTRC20

# Quick payment
python manage.py create_payment \
  --user-id 1 \
  --amount 50.00 \
  --currency BTCBTC \
  --description "Test payment from CLI"
```

**Interactive Flow:**

1. **Select User** - Choose from existing users or create new
2. **Select Currency** - Choose from active cryptocurrencies
3. **Enter Amount** - Amount in USD (validated)
4. **Enter Description** - Optional payment description
5. **Confirm** - Review summary and confirm
6. **Result** - Payment details with QR code and wallet address

**Features:**
- ✅ Interactive questionary wizard
- ✅ Input validation (amount, email, etc.)
- ✅ User creation on-the-fly
- ✅ Rich formatted output
- ✅ QR code generation
- ✅ Option to open QR code in browser

**Example:**

```bash
$ python manage.py create_payment

💰 Payment Creation Wizard

? Select user for payment:
  › alice (alice@example.com) - ID: 1
    bob (bob@example.com) - ID: 2
    ➕ Create new user

? Select payment currency:
  › USDT (TRC20) - TRC20
    USDT (ERC20) - ERC20
    Bitcoin - Native
    Ethereum - Native

? Enter amount in USD: 100.00

? Payment description (optional): Payment for services

┌─ Payment Summary ─────────────┐
│ Field        │ Value          │
├──────────────┼────────────────┤
│ User         │ alice          │
│ Amount USD   │ $100.00        │
│ Currency     │ USDT (TRC20)   │
│ Network      │ TRC20          │
└──────────────┴────────────────┘

? Create this payment? Yes

Creating payment...

✓ Payment created successfully!

┌─ Payment Details ──────────────────────┐
│ Payment ID: a1b2c3d4-...               │
│ Provider Payment ID: 123456789         │
│                                        │
│ Amount: $100.00 USD                    │
│ Pay Amount: 100.50000000 USDT         │
│ Currency: USDT (TRC20)                │
│                                        │
│ Status: pending                        │
│ Wallet Address: TXqR8Bmj8KmwEBL...    │
│                                        │
│ QR Code URL:                           │
│ https://api.qrserver.com/v1/...       │
└────────────────────────────────────────┘

📝 Next steps:
1. Send crypto to the wallet address above
2. Check payment status with: python manage.py check_payment_status <payment_id>
3. View in admin: /admin/payments_v2/payment/

? Open QR code in browser? No
```

---

### 3. `check_payment_status` - Check payment status

Check payment status interactively or by payment ID.

**Usage:**

```bash
# Interactive mode (select from list)
python manage.py check_payment_status

# By payment ID
python manage.py check_payment_status a1b2c3d4-e5f6-7890-abcd-1234567890ab

# Force refresh from provider
python manage.py check_payment_status <payment_id> --refresh

# List recent payments
python manage.py check_payment_status --list
```

**Features:**
- ✅ Interactive payment selection
- ✅ Direct payment ID lookup
- ✅ Force refresh from provider API
- ✅ List recent payments
- ✅ Shows transaction history
- ✅ Blockchain confirmations
- ✅ Status emoji indicators
- ✅ Rich formatted output

**Example:**

```bash
$ python manage.py check_payment_status --list

💳 Payment Status Checker

┌─ Recent Payments ────────────────────────────────────────┐
│ ID       │ Internal ID        │ User   │ Amount   │ ... │
├──────────┼────────────────────┼────────┼──────────┼─────┤
│ a1b2c3d4 │ PM_20231014_123... │ alice  │ $100.00  │ ... │
│ e5f67890 │ PM_20231014_456... │ bob    │ $50.00   │ ... │
└──────────┴────────────────────┴────────┴──────────┴─────┘

$ python manage.py check_payment_status a1b2c3d4-... --refresh

💳 Payment Status Checker

✓ Found payment: PM_20231014_123456
⚡ Force refreshing from provider API...

Checking status for payment PM_20231014_123456...

✓ Status checked successfully!

┌─ Payment Status ───────────────────────┐
│ Payment ID: a1b2c3d4-...               │
│ Internal ID: PM_20231014_123456        │
│ Provider Payment ID: 123456789         │
│                                        │
│ Amount: $100.00 USD                    │
│ Pay Amount: 100.50000000 USDT         │
│ Currency: USDTTRC20                   │
│                                        │
│ Status: ✅ COMPLETED                   │
│ Is Completed: ✅ Yes                   │
│                                        │
│ Wallet Address: TXqR8Bmj8KmwEBL...    │
│ Transaction Hash: 0xabc123...          │
└────────────────────────────────────────┘

🔗 Blockchain Confirmations: 12

💰 Balance Transactions:
┌────────────┬─────────┬─────────┬─────────────┬──────────┐
│ ID         │ Type    │ Amount  │ Balance     │ Created  │
├────────────┼─────────┼─────────┼─────────────┼──────────┤
│ tx_123...  │ deposit │ $100.00 │ $100.00     │ 14:35    │
└────────────┴─────────┴─────────┴─────────────┴──────────┘

📝 Next steps:
✅ Payment completed successfully!
   User balance has been updated
```

---

## Payment Flow Example

Complete workflow from sync to payment creation and checking:

```bash
# Step 1: Sync currencies from provider
python manage.py sync_currencies --skip-confirmation

# Step 2: Create a payment
python manage.py create_payment \
  --user-id 1 \
  --amount 100.00 \
  --currency USDTTRC20 \
  --description "Test payment"

# Step 3: Check payment status (after user sends crypto)
python manage.py check_payment_status <payment_id> --refresh

# Step 4: List all payments
python manage.py check_payment_status --list
```

---

## Requirements

These commands require:

- ✅ **questionary** - Interactive CLI prompts
- ✅ **rich** - Beautiful terminal output
- ✅ **httpx** - HTTP client for NowPayments API
- ✅ **pydantic** - Data validation

Install with:

```bash
poetry add questionary rich httpx pydantic
```

---

## Configuration

Commands use NowPayments configuration from `django_cfg`:

```yaml
# config.dev.yaml or config.prod.yaml
payments:
  enabled: true
  nowpayments:
    api_key: "your_api_key_here"
    sandbox: true  # false for production
    timeout: 30
```

Or via environment variables:

```bash
export NOWPAYMENTS_API_KEY="your_api_key"
export NOWPAYMENTS_SANDBOX="true"
```

---

## Tips

### For Development

```bash
# Use dry-run to preview changes
python manage.py sync_currencies --dry-run

# Create test payments with small amounts
python manage.py create_payment --amount 1.00
```

### For Production

```bash
# Always use --skip-confirmation in scripts/cron
python manage.py sync_currencies --skip-confirmation --deactivate-missing

# Force refresh to get latest status
python manage.py check_payment_status <id> --refresh
```

### Automation

```bash
# Sync currencies daily
0 0 * * * cd /path/to/project && python manage.py sync_currencies --skip-confirmation

# Check pending payments every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py check_pending_payments
```

---

## Troubleshooting

### "No currencies found"

Run sync_currencies first:

```bash
python manage.py sync_currencies
```

### "NowPayments configuration not found"

Check your config file has payments.nowpayments section with api_key.

### "Currency X is not available"

Currency is not active. Check admin or run sync_currencies again.

---

## Related Documentation

- [Payments v2.0 Documentation](../README.md)
- [Testing Guide](../tests/TESTING.md)
- [API Documentation](../api/README.md)
- [NowPayments API Docs](https://documenter.getpostman.com/view/7907941/S1a32n38)
