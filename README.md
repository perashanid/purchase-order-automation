# Intelligent Purchase Order & Supplier Escalation System

Automates purchase order creation when inventory drops below threshold and escalates to backup suppliers when primary suppliers don't respond.

## 🎯 Features

- **Automatic PO Generation**: Creates professional POs when stock falls below threshold
- **Smart Quantity Calculation**: Orders deficit + 20% safety buffer
- **Business Day Calculation**: Accurately calculates delivery dates (skips weekends)
- **Supplier Escalation**: Auto-escalates to backup supplier after 24h no-response
- **Email Automation**: Sends formatted POs and urgent escalation emails
- **Status Tracking**: Updates inventory dashboard with PO status
- **Multi-Platform**: Integrates with Shopify, Google Sheets, Airtable, and more

## 📋 How It Works

### Task 1: Generate Purchase Order

When inventory drops below reorder threshold:

1. **Calculate Order Quantity**
   - Formula: `(reorder_threshold - current_stock) + 20% safety buffer`
   - Example: Threshold 100, Current 45 → Order 66 units

2. **Generate PO Number**
   - Format: `PO-YYYYMMDD-XXXX`
   - Example: `PO-20260727-3847`

3. **Calculate Delivery Date**
   - 7 business days from today (skips weekends)
   - Example: Ordered Monday → Delivered next Wednesday

4. **Create Professional PO**
   - Formatted email with all details
   - Sent to primary supplier

### Task 2: Escalation (If No Response in 24h)

If supplier doesn't confirm within 24 hours:

1. **Generate Urgent Email** to backup supplier
2. **Update PO Status** to "Escalated"
3. **Notify Operations Team** via Slack/email
4. **Request 12-Hour Confirmation** from backup supplier

## 🚀 Quick Start

### Installation

```bash
cd purchase-order-automation
pip install -r requirements.txt
```

### Basic Usage

```python
from po_generator import create_purchase_order

# Generate a purchase order
po_json = create_purchase_order(
    product_name="Industrial Ball Bearings 6202-2RS",
    sku="BB-6202-2RS",
    current_stock=45,
    reorder_threshold=100,
    supplier_name="Acme Bearings Inc.",
    supplier_email="orders@acmebearings.com",
    supplier_phone="+1-555-0123"
)

print(po_json)
```

**Output:**
```json
{
  "po_number": "PO-20260727-3847",
  "product": "Industrial Ball Bearings 6202-2RS",
  "sku": "BB-6202-2RS",
  "quantity": 66,
  "current_stock": 45,
  "reorder_threshold": 100,
  "requested_delivery": "2026-08-07",
  "supplier": {
    "name": "Acme Bearings Inc.",
    "email": "orders@acmebearings.com",
    "phone": "+1-555-0123"
  },
  "created_at": "2026-07-27T18:30:00.000000",
  "status": "draft"
}
```

### Run Webhook Server

```bash
python webhook_handler.py
```

Server starts on `http://localhost:5001`

### Test Endpoints

#### 1. Check Inventory & Generate PO

```bash
curl -X POST http://localhost:5001/webhook/inventory-check \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Industrial Ball Bearings",
    "sku": "BB-6202-2RS",
    "current_stock": 45,
    "reorder_threshold": 100,
    "supplier": {
      "name": "Acme Bearings Inc.",
      "email": "orders@acmebearings.com",
      "phone": "+1-555-0123"
    },
    "backup_supplier": {
      "name": "Reliable Parts Co.",
      "email": "urgent@reliableparts.com",
      "phone": "+1-555-9999"
    }
  }'
```

#### 2. Escalate to Backup Supplier

```bash
curl -X POST http://localhost:5001/webhook/escalate-po \
  -H "Content-Type: application/json" \
  -d '{
    "po_data": {
      "po_number": "PO-20260727-3847",
      "product": "Industrial Ball Bearings",
      "sku": "BB-6202-2RS",
      "quantity": 66,
      "current_stock": 45,
      "reorder_threshold": 100,
      "requested_delivery": "2026-08-07",
      "supplier": {
        "name": "Acme Bearings Inc.",
        "email": "orders@acmebearings.com"
      },
      "created_at": "2026-07-27T18:30:00"
    },
    "backup_supplier": {
      "name": "Reliable Parts Co.",
      "email": "urgent@reliableparts.com"
    },
    "primary_supplier_name": "Acme Bearings Inc."
  }'
```

## 🔧 Automation Setup

### Option 1: Make.com (Recommended)

**Blueprint:** See `automation_blueprint.json` for complete configuration

**Quick Setup:**

1. **Create New Scenario**
   - Import modules from blueprint

2. **Configure Trigger**
   - **Google Sheets**: Watch rows where Current Stock < Reorder Threshold
   - **Shopify**: Watch inventory levels
   - **Schedule**: Every 4-6 hours

3. **Add HTTP Module**
   - POST to your webhook endpoint
   - Map inventory data from trigger

4. **Add Router**
   - Path A: If `needs_reorder = true` → Continue
   - Path B: If `needs_reorder = false` → Stop

5. **Create PO Record**
   - Google Sheets: Add row to "Purchase Orders" sheet
   - Map all PO fields from webhook response

6. **Send Email**
   - Gmail/Outlook module
   - To: `{{email.to}}`
   - Subject: `{{email.subject}}`
   - Body: `{{email.body}}`

7. **Add Delay**
   - Tools → Sleep: 24 hours

8. **Check Response** (Router)
   - **Path A** (Confirmed):
     - Gmail: Search for reply from supplier
     - Update Sheet: Status = "Confirmed"
     - Slack: Send success notification
   
   - **Path B** (No Response):
     - HTTP: POST to `/webhook/escalate-po`
     - Gmail: Send escalation email
     - Slack: Alert ops team
     - Update Sheet: Status = "Escalated"

### Option 2: Zapier

**Requirements:** Professional plan for multi-step Zaps

1. **Trigger**: Google Sheets - New/Updated Row (filter: stock < threshold)
2. **Action**: Webhooks - POST to inventory-check endpoint
3. **Action**: Google Sheets - Create row in Purchase Orders
4. **Action**: Gmail - Send email to primary supplier
5. **Action**: Delay - Wait 24 hours
6. **Action**: Paths (conditional logic)
   - Path A: If supplier replied → Update status
   - Path B: If no reply → Escalate
7. **Action**: Webhooks - POST to escalate-po endpoint
8. **Action**: Gmail - Send escalation email
9. **Action**: Slack - Send notification

### Option 3: Shopify Integration

**Using Shopify Inventory Webhooks:**

```json
{
  "topic": "inventory_levels/update",
  "address": "https://your-server.com/webhook/inventory-check",
  "format": "json"
}
```

Configure in: Shopify Admin → Settings → Notifications → Webhooks

## 📊 Dashboard Setup

### Google Sheets Structure

**Sheet 1: Inventory**
| Product Name | SKU | Current Stock | Reorder Threshold | Last PO | Status | Last Checked |
|--------------|-----|---------------|-------------------|---------|--------|--------------|
| Ball Bearings| BB-6202 | 45 | 100 | PO-20260727-3847 | Pending | 2026-07-27 18:30 |

**Sheet 2: Purchase Orders**
| PO Number | Product | SKU | Quantity | Supplier | Status | Created | Confirmed | Escalated |
|-----------|---------|-----|----------|----------|--------|---------|-----------|-----------|
| PO-20260727-3847 | Ball Bearings | BB-6202 | 66 | Acme Inc. | Pending | 2026-07-27 18:30 | | |

**Sheet 3: Supplier Database**
| Product | Primary Supplier | Email | Phone | Backup Supplier | Email | Phone |
|---------|------------------|-------|-------|-----------------|-------|-------|
| Ball Bearings | Acme Inc. | orders@acme.com | +1-555-0123 | Reliable Parts | urgent@reliable.com | +1-555-9999 |

## 🔔 Notification Templates

### Slack Notification (Success)
```
✅ PO Confirmed

PO Number: PO-20260727-3847
Product: Industrial Ball Bearings
Supplier: Acme Bearings Inc.
Quantity: 66 units
Expected Delivery: 2026-08-07

Status: Confirmed by primary supplier
```

### Slack Notification (Escalation)
```
⚠️ PO ESCALATION REQUIRED

PO Number: PO-20260727-3847
Product: Industrial Ball Bearings
Current Stock: 45 units (Threshold: 100)

Primary Supplier: Acme Bearings Inc. (NO RESPONSE after 24h)
Escalated To: Reliable Parts Co.

Action Required: Monitor backup supplier response (12h deadline)
@ops-team
```

## 🧪 Testing

Run the example script:

```bash
python po_generator.py
```

This will:
1. Generate a sample PO
2. Display formatted email
3. Create an escalation example
4. Show all JSON outputs

## 📈 Advanced Features

### Custom Order Quantities

Modify safety buffer percentage:

```python
generator = POGenerator()
generator.safety_buffer_percentage = 0.30  # 30% buffer instead of 20%
```

### Custom Delivery Timeframes

```python
# Urgent orders - 3 business days
urgent_delivery = generator._calculate_delivery_date(business_days=3)

# Standard orders - 7 business days (default)
standard_delivery = generator._calculate_delivery_date(business_days=7)

# Bulk orders - 14 business days
bulk_delivery = generator._calculate_delivery_date(business_days=14)
```

### Email Customization

Edit the email templates in `po_generator.py`:

```python
def format_po_email(self, po_data: Dict) -> str:
    # Customize email format here
    # Add company logo, terms & conditions, etc.
    pass
```

## 🔐 Security Best Practices

1. **API Authentication**
   - Add API key validation to webhooks
   - Use HTTPS only

2. **Supplier Verification**
   - Verify email domains
   - Whitelist approved suppliers

3. **PO Approval Workflow**
   - Add approval step for high-value orders
   - Require manager sign-off over certain amounts

4. **Data Protection**
   - Don't log sensitive pricing data
   - Encrypt supplier contact information

## 🐛 Troubleshooting

### PO Not Generated

**Check:**
- Is `current_stock < reorder_threshold`?
- Are all required fields provided?
- Check webhook endpoint logs

### Wrong Delivery Date

**Issue:** Delivery date calculation includes weekends

**Fix:** Verify `_calculate_delivery_date()` logic
```python
# Should skip weekends (Saturday=5, Sunday=6)
if current_date.weekday() < 5:
    days_added += 1
```

### Escalation Not Triggered

**Check:**
- Did 24-hour delay complete?
- Is email reply detection working?
- Check inbox search query syntax

### Email Not Sent

**Check:**
- SMTP credentials configured?
- Supplier email address valid?
- Email provider rate limits?

## 🚀 Deployment

### Deploy to Heroku

```bash
# Create app
heroku create po-automation

# Deploy
git push heroku main

# Set environment variables
heroku config:set FLASK_ENV=production

# View logs
heroku logs --tail
```

### Deploy to AWS Lambda

1. Package application:
```bash
pip install -r requirements.txt -t ./package
cd package
zip -r ../deployment.zip .
cd ..
zip -g deployment.zip *.py
```

2. Create Lambda function
3. Set up API Gateway trigger
4. Configure environment variables

## 📞 Integration Examples

### Shopify

```javascript
// Shopify webhook payload
{
  "inventory_item_id": 12345,
  "available": 45,
  "location_id": 67890
}
```

Map to webhook format in Make.com/Zapier

### WooCommerce

Use WooCommerce REST API:
```
GET /wp-json/wc/v3/products?low_stock=true
```

### QuickBooks

Sync PO to QuickBooks using their API for accounting

## 📚 Resources

- [Make.com Documentation](https://www.make.com/en/help)
- [Zapier Delay Documentation](https://zapier.com/apps/delay/integrations)
- [Shopify Inventory Webhooks](https://shopify.dev/api/admin-rest/webhooks)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)

## 🔄 Future Enhancements

- [ ] Multi-currency support
- [ ] Automatic price negotiation
- [ ] Supplier performance tracking
- [ ] Predictive reorder based on trends
- [ ] SMS alerts for critical escalations
- [ ] Mobile app for PO approval
- [ ] Integration with ERP systems (SAP, Oracle)

## 📄 License

MIT License - Free to use and modify

## 💡 Tips

1. **Test thoroughly** before going live
2. **Start with email only** (no auto-creation) to verify logic
3. **Monitor for first few days** to catch edge cases
4. **Keep backup supplier list updated**
5. **Set up alerts** for all escalations
6. **Review PO history monthly** to optimize thresholds

---

**Need Help?** Check the troubleshooting section or review the automation blueprint for detailed flow diagrams.
