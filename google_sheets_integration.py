"""
Google Sheets Integration for PO Automation
Reads inventory from Google Sheets and updates PO status
"""

import json
from typing import List, Dict
from po_generator import create_purchase_order, create_escalation

# Note: Install google-auth and google-api-python-client for production use
# pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client


class GoogleSheetsIntegration:
    """
    Integration with Google Sheets for inventory and PO management.
    
    Sheet Structure:
    - Sheet 1 "Inventory": Product tracking
    - Sheet 2 "Purchase Orders": PO records
    - Sheet 3 "Suppliers": Supplier database
    """
    
    def __init__(self, spreadsheet_id: str = None):
        """Initialize with Google Sheets credentials."""
        self.spreadsheet_id = spreadsheet_id
        # In production, initialize Google Sheets API client here
        
    def check_inventory_levels(self) -> List[Dict]:
        """
        Check all products and return those needing reorder.
        
        Returns:
            List of products with stock below threshold
        """
        # This is a simulation - in production, fetch from Google Sheets API
        low_stock_items = []
        
        # Example: Read from Sheets
        # service = build('sheets', 'v4', credentials=creds)
        # sheet = service.spreadsheets()
        # result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range='Inventory!A2:Z').execute()
        # values = result.get('values', [])
        
        # Simulated data
        inventory_data = [
            {
                "product_name": "Industrial Ball Bearings 6202-2RS",
                "sku": "BB-6202-2RS",
                "current_stock": 45,
                "reorder_threshold": 100,
                "row_number": 2
            },
            {
                "product_name": "Hydraulic Pump Model HP-500",
                "sku": "HP-500-STD",
                "current_stock": 15,
                "reorder_threshold": 50,
                "row_number": 3
            }
        ]
        
        for item in inventory_data:
            if item['current_stock'] < item['reorder_threshold']:
                low_stock_items.append(item)
        
        return low_stock_items
    
    def get_supplier_info(self, sku: str) -> Dict:
        """
        Get supplier information for a product.
        
        Args:
            sku: Product SKU
            
        Returns:
            Dictionary with primary and backup supplier info
        """
        # Simulated supplier lookup
        suppliers = {
            "BB-6202-2RS": {
                "primary": {
                    "name": "Acme Bearings Inc.",
                    "email": "orders@acmebearings.com",
                    "phone": "+1-555-0123"
                },
                "backup": {
                    "name": "Reliable Parts Co.",
                    "email": "urgent@reliableparts.com",
                    "phone": "+1-555-9999"
                }
            },
            "HP-500-STD": {
                "primary": {
                    "name": "Hydraulics Direct Ltd.",
                    "email": "sales@hydraulicsdirect.com",
                    "phone": "+44-20-1234-5678"
                },
                "backup": {
                    "name": "Global Pumps Inc.",
                    "email": "orders@globalpumps.com",
                    "phone": "+1-555-7777"
                }
            }
        }
        
        return suppliers.get(sku, {
            "primary": {"name": "Unknown", "email": "unknown@example.com"},
            "backup": {"name": "Unknown", "email": "unknown@example.com"}
        })
    
    def create_po_record(self, po_data: Dict) -> bool:
        """
        Add PO record to Google Sheets.
        
        Args:
            po_data: Purchase order data
            
        Returns:
            Success status
        """
        # In production, append row to "Purchase Orders" sheet
        # row = [
        #     po_data['po_number'],
        #     po_data['product'],
        #     po_data['sku'],
        #     po_data['quantity'],
        #     po_data['supplier']['name'],
        #     'Pending',
        #     po_data['created_at'],
        #     po_data['requested_delivery']
        # ]
        # service.spreadsheets().values().append(
        #     spreadsheetId=self.spreadsheet_id,
        #     range='Purchase Orders!A:H',
        #     valueInputOption='RAW',
        #     body={'values': [row]}
        # ).execute()
        
        print(f"✅ PO Record Created: {po_data['po_number']}")
        return True
    
    def update_po_status(self, po_number: str, status: str, notes: str = "") -> bool:
        """
        Update PO status in Google Sheets.
        
        Args:
            po_number: PO number to update
            status: New status (Pending/Confirmed/Escalated)
            notes: Optional notes
            
        Returns:
            Success status
        """
        # In production, find and update the row
        print(f"✅ Updated PO {po_number} → Status: {status}")
        if notes:
            print(f"   Notes: {notes}")
        return True
    
    def update_inventory_status(self, sku: str, po_number: str, expected_delivery: str) -> bool:
        """
        Update inventory sheet with PO information.
        
        Args:
            sku: Product SKU
            po_number: Associated PO number
            expected_delivery: Expected delivery date
            
        Returns:
            Success status
        """
        print(f"✅ Updated Inventory for SKU {sku}")
        print(f"   PO: {po_number}, Expected: {expected_delivery}")
        return True


def automated_inventory_check(spreadsheet_id: str = None):
    """
    Main automation function - checks inventory and creates POs as needed.
    
    This function would be called by Make.com/Zapier on a schedule.
    
    Args:
        spreadsheet_id: Google Sheets ID
        
    Returns:
        Summary of actions taken
    """
    print("=" * 80)
    print("AUTOMATED INVENTORY CHECK")
    print("=" * 80)
    
    integration = GoogleSheetsIntegration(spreadsheet_id)
    
    # Step 1: Check inventory levels
    print("\n📊 Checking inventory levels...")
    low_stock_items = integration.check_inventory_levels()
    
    if not low_stock_items:
        print("✅ All inventory levels are adequate. No action needed.")
        return {"status": "success", "pos_created": 0}
    
    print(f"⚠️ Found {len(low_stock_items)} items below reorder threshold\n")
    
    # Step 2: Create POs for low stock items
    pos_created = []
    
    for item in low_stock_items:
        print(f"\n{'─' * 80}")
        print(f"Processing: {item['product_name']}")
        print(f"Current Stock: {item['current_stock']} | Threshold: {item['reorder_threshold']}")
        
        # Get supplier info
        suppliers = integration.get_supplier_info(item['sku'])
        
        # Generate PO
        po_json = create_purchase_order(
            product_name=item['product_name'],
            sku=item['sku'],
            current_stock=item['current_stock'],
            reorder_threshold=item['reorder_threshold'],
            supplier_name=suppliers['primary']['name'],
            supplier_email=suppliers['primary']['email'],
            supplier_phone=suppliers['primary'].get('phone')
        )
        
        po_data = json.loads(po_json)
        
        print(f"✅ Generated PO: {po_data['po_number']}")
        print(f"   Quantity: {po_data['quantity']} units")
        print(f"   Supplier: {po_data['supplier']['name']}")
        print(f"   Delivery: {po_data['requested_delivery']}")
        
        # Save to sheets
        integration.create_po_record(po_data)
        integration.update_inventory_status(
            sku=item['sku'],
            po_number=po_data['po_number'],
            expected_delivery=po_data['requested_delivery']
        )
        
        pos_created.append(po_data)
    
    print(f"\n{'=' * 80}")
    print(f"✅ COMPLETED: Created {len(pos_created)} purchase orders")
    print(f"{'=' * 80}")
    
    return {
        "status": "success",
        "pos_created": len(pos_created),
        "purchase_orders": pos_created
    }


# Example: Setup instructions for Google Sheets API
GOOGLE_SHEETS_SETUP = """
GOOGLE SHEETS API SETUP INSTRUCTIONS
=====================================

1. Enable Google Sheets API:
   - Go to https://console.cloud.google.com/
   - Create a new project (or select existing)
   - Enable "Google Sheets API"
   
2. Create Service Account:
   - Navigate to "Credentials"
   - Create Service Account
   - Download JSON key file
   - Save as 'credentials.json' in project folder

3. Share Your Sheet:
   - Open your Google Sheet
   - Click "Share"
   - Add service account email (found in credentials.json)
   - Grant "Editor" permission

4. Install Required Packages:
   pip install google-auth google-auth-oauthlib google-api-python-client

5. Get Your Spreadsheet ID:
   - From URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
   - Copy the SPREADSHEET_ID part

6. Initialize in Code:
   ```python
   from google.oauth2 import service_account
   from googleapiclient.discovery import build
   
   SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
   credentials = service_account.Credentials.from_service_account_file(
       'credentials.json', scopes=SCOPES
   )
   service = build('sheets', 'v4', credentials=credentials)
   ```

SHEET STRUCTURE:
================

Sheet 1: "Inventory"
Columns: Product Name | SKU | Current Stock | Reorder Threshold | Last PO | Status | Last Checked

Sheet 2: "Purchase Orders"
Columns: PO Number | Product | SKU | Quantity | Supplier | Status | Created | Confirmed | Escalated

Sheet 3: "Suppliers"
Columns: SKU | Primary Name | Primary Email | Primary Phone | Backup Name | Backup Email | Backup Phone

AUTOMATION WITH MAKE.COM:
=========================

1. Trigger: Schedule (every 4-6 hours)
2. Action: Google Sheets - Search Rows
   - Range: Inventory!A2:Z
   - Condition: Current Stock < Reorder Threshold
3. Action: HTTP Request - POST to webhook
4. Action: Google Sheets - Add Row (Purchase Orders)
5. Action: Gmail - Send Email to Supplier
6. Action: Google Sheets - Update Row (Inventory status)
"""


if __name__ == "__main__":
    print(GOOGLE_SHEETS_SETUP)
    print("\n\n")
    
    # Run automated check simulation
    result = automated_inventory_check()
    
    print("\n\nResult Summary:")
    print(json.dumps(result, indent=2))
