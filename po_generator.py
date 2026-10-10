"""
Purchase Order Generator and Escalation Handler
Automates PO creation and supplier follow-ups
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, Optional


class POGenerator:
    def __init__(self):
        self.business_days_to_delivery = 7
        self.safety_buffer_percentage = 0.20
    
    def generate_po(
        self,
        product_name: str,
        sku: str,
        current_stock: int,
        reorder_threshold: int,
        supplier_name: str,
        supplier_email: str,
        supplier_phone: Optional[str] = None
    ) -> Dict:
        """
        Generate a complete purchase order.
        
        Args:
            product_name: Name of the product
            sku: Stock Keeping Unit identifier
            current_stock: Current inventory level
            reorder_threshold: Minimum stock level before reorder
            supplier_name: Primary supplier company name
            supplier_email: Supplier email address
            supplier_phone: Optional supplier phone number
            
        Returns:
            Dictionary containing complete PO details
        """
        # Calculate quantity to order
        quantity = self._calculate_order_quantity(current_stock, reorder_threshold)
        
        # Generate PO number
        po_number = self._generate_po_number()
        
        # Calculate delivery date (7 business days)
        requested_delivery = self._calculate_delivery_date()
        
        # Create PO data
        po_data = {
            "po_number": po_number,
            "product": product_name,
            "sku": sku,
            "quantity": quantity,
            "current_stock": current_stock,
            "reorder_threshold": reorder_threshold,
            "requested_delivery": requested_delivery,
            "supplier": {
                "name": supplier_name,
                "email": supplier_email,
                "phone": supplier_phone
            },
            "created_at": datetime.now().isoformat(),
            "status": "draft"
        }
        
        return po_data
    
    def _calculate_order_quantity(self, current_stock: int, reorder_threshold: int) -> int:
        """
        Calculate quantity to reorder with safety buffer.
        Formula: (reorder_threshold - current_stock) + 20% safety buffer
        """
        deficit = max(0, reorder_threshold - current_stock)
        safety_buffer = int(deficit * self.safety_buffer_percentage)
        total_quantity = deficit + safety_buffer
        
        # Minimum order quantity
        return max(total_quantity, 1)
    
    def _generate_po_number(self) -> str:
        """Generate PO number in format: PO-YYYYMMDD-XXXX"""
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = str(random.randint(1000, 9999))
        return f"PO-{date_part}-{random_part}"
    
    def _calculate_delivery_date(self, business_days: int = 7) -> str:
        """Calculate delivery date X business days from today."""
        current_date = datetime.now()
        days_added = 0
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            # Skip weekends (5 = Saturday, 6 = Sunday)
            if current_date.weekday() < 5:
                days_added += 1
        
        return current_date.strftime("%Y-%m-%d")
    
    def format_po_email(self, po_data: Dict) -> str:
        """
        Format PO data into a professional email body.
        
        Args:
            po_data: Purchase order dictionary
            
        Returns:
            Formatted email body string
        """
        email_body = f"""Dear {po_data['supplier']['name']},

We would like to place the following purchase order:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PURCHASE ORDER: {po_data['po_number']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Product Name:        {po_data['product']}
SKU:                 {po_data['sku']}
Quantity:            {po_data['quantity']} units

Requested Delivery:  {po_data['requested_delivery']}
Current Stock:       {po_data['current_stock']} units
Reorder Threshold:   {po_data['reorder_threshold']} units

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please confirm receipt of this purchase order and provide:
1. Confirmation of quantity availability
2. Estimated delivery date
3. Updated pricing (if applicable)
4. Invoice or proforma invoice

We kindly request confirmation within 24 hours to ensure timely delivery.

If you have any questions, please contact us immediately.

Best regards,
Procurement Team

---
This is an automated purchase order. PO created: {datetime.fromisoformat(po_data['created_at']).strftime("%Y-%m-%d %H:%M")}
"""
        return email_body
    
    def generate_escalation_email(
        self,
        po_data: Dict,
        backup_supplier_name: str,
        backup_supplier_email: str,
        primary_supplier_name: str
    ) -> Dict:
        """
        Generate escalation email to backup supplier when primary doesn't respond.
        
        Args:
            po_data: Original purchase order data
            backup_supplier_name: Backup supplier company name
            backup_supplier_email: Backup supplier email
            primary_supplier_name: Name of non-responsive primary supplier
            
        Returns:
            Dictionary with escalation email details
        """
        # Update PO number for backup supplier
        escalated_po_number = po_data['po_number'].replace('PO-', 'PO-ESC-')
        
        # Adjust delivery date (urgent - 5 business days)
        urgent_delivery = self._calculate_delivery_date(business_days=5)
        
        email_subject = f"URGENT: Backup Purchase Order {escalated_po_number}"
        
        email_body = f"""Dear {backup_supplier_name},

⚠️ URGENT REQUEST - Confirmation Required Within 12 Hours ⚠️

We are reaching out to you as our backup supplier for an urgent purchase order. Our primary supplier ({primary_supplier_name}) has not responded to our original request within the expected timeframe.

We need your immediate assistance with the following order:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESCALATED PURCHASE ORDER: {escalated_po_number}
Original PO: {po_data['po_number']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Product Name:        {po_data['product']}
SKU:                 {po_data['sku']}
Quantity Needed:     {po_data['quantity']} units

URGENT Delivery:     {urgent_delivery} (EXPEDITED)
Original Request:    {po_data['requested_delivery']}

Reason for Urgency:  Current stock ({po_data['current_stock']} units) is below reorder threshold ({po_data['reorder_threshold']} units)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMMEDIATE ACTION REQUIRED:
Please confirm within 12 hours:
✓ Can you fulfill this quantity?
✓ Can you meet the expedited delivery date?
✓ Current pricing per unit
✓ Any additional expedite fees

If you cannot fulfill this order, please inform us immediately so we can seek alternative suppliers.

This is a high-priority order affecting our operations. Your prompt response is greatly appreciated.

Best regards,
Procurement Team

---
Escalation sent: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Primary supplier non-responsive since: {datetime.fromisoformat(po_data['created_at']).strftime("%Y-%m-%d %H:%M")}
"""
        
        return {
            "escalated_po_number": escalated_po_number,
            "subject": email_subject,
            "body": email_body,
            "to": backup_supplier_email,
            "supplier_name": backup_supplier_name,
            "urgency": "HIGH",
            "response_deadline_hours": 12,
            "original_po": po_data['po_number']
        }


def create_purchase_order(
    product_name: str,
    sku: str,
    current_stock: int,
    reorder_threshold: int,
    supplier_name: str,
    supplier_email: str,
    supplier_phone: Optional[str] = None
) -> str:
    """
    Main function to create a purchase order and return JSON.
    
    Returns:
        JSON string with PO details
    """
    generator = POGenerator()
    po_data = generator.generate_po(
        product_name=product_name,
        sku=sku,
        current_stock=current_stock,
        reorder_threshold=reorder_threshold,
        supplier_name=supplier_name,
        supplier_email=supplier_email,
        supplier_phone=supplier_phone
    )
    
    return json.dumps(po_data, indent=2)


def create_escalation(
    po_json: str,
    backup_supplier_name: str,
    backup_supplier_email: str,
    primary_supplier_name: str
) -> str:
    """
    Create escalation email for backup supplier.
    
    Args:
        po_json: JSON string of original PO data
        backup_supplier_name: Backup supplier name
        backup_supplier_email: Backup supplier email
        primary_supplier_name: Primary supplier that didn't respond
        
    Returns:
        JSON string with escalation email details
    """
    po_data = json.loads(po_json)
    generator = POGenerator()
    
    escalation = generator.generate_escalation_email(
        po_data=po_data,
        backup_supplier_name=backup_supplier_name,
        backup_supplier_email=backup_supplier_email,
        primary_supplier_name=primary_supplier_name
    )
    
    return json.dumps(escalation, indent=2)


if __name__ == "__main__":
    # Example usage
    print("=== TASK 1: Generate Purchase Order ===\n")
    
    po = create_purchase_order(
        product_name="Industrial Ball Bearings 6202-2RS",
        sku="BB-6202-2RS",
        current_stock=45,
        reorder_threshold=100,
        supplier_name="Acme Bearings Inc.",
        supplier_email="orders@acmebearings.com",
        supplier_phone="+1-555-0123"
    )
    
    po_data = json.loads(po)
    print(po)
    
    # Generate email format
    print("\n\n=== Email to Primary Supplier ===\n")
    generator = POGenerator()
    email = generator.format_po_email(po_data)
    print(email)
    
    # Example escalation
    print("\n\n=== TASK 2: Generate Escalation Email ===\n")
    
    escalation = create_escalation(
        po_json=po,
        backup_supplier_name="Reliable Parts Co.",
        backup_supplier_email="urgent@reliableparts.com",
        primary_supplier_name="Acme Bearings Inc."
    )
    
    print(escalation)
    
    escalation_data = json.loads(escalation)
    print("\n\n=== Escalation Email Body ===\n")
    print(escalation_data['body'])
