"""
Webhook Handler for Purchase Order Automation
Receives inventory data and generates POs
"""

from flask import Flask, request, jsonify
from po_generator import POGenerator, create_purchase_order, create_escalation
import json
from datetime import datetime

app = Flask(__name__)


@app.route('/webhook/inventory-check', methods=['POST'])
def handle_inventory_check():
    """
    Webhook endpoint to check inventory and generate PO if needed.
    
    Expected JSON payload:
    {
        "product_name": "Product Name",
        "sku": "SKU-123",
        "current_stock": 45,
        "reorder_threshold": 100,
        "supplier": {
            "name": "Supplier Inc.",
            "email": "orders@supplier.com",
            "phone": "+1-555-0123"
        },
        "backup_supplier": {
            "name": "Backup Supplier Co.",
            "email": "orders@backup.com",
            "phone": "+1-555-9999"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_name', 'sku', 'current_stock', 'reorder_threshold', 'supplier']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        current_stock = int(data['current_stock'])
        reorder_threshold = int(data['reorder_threshold'])
        
        # Check if reorder is needed
        needs_reorder = current_stock < reorder_threshold
        
        if not needs_reorder:
            return jsonify({
                "needs_reorder": False,
                "message": f"Stock level ({current_stock}) is above threshold ({reorder_threshold})",
                "current_stock": current_stock,
                "reorder_threshold": reorder_threshold
            }), 200
        
        # Generate purchase order
        po_json = create_purchase_order(
            product_name=data['product_name'],
            sku=data['sku'],
            current_stock=current_stock,
            reorder_threshold=reorder_threshold,
            supplier_name=data['supplier']['name'],
            supplier_email=data['supplier']['email'],
            supplier_phone=data['supplier'].get('phone')
        )
        
        po_data = json.loads(po_json)
        
        # Generate email body
        generator = POGenerator()
        email_body = generator.format_po_email(po_data)
        
        response = {
            "needs_reorder": True,
            "po_created": True,
            "po_data": po_data,
            "email": {
                "to": data['supplier']['email'],
                "subject": f"Purchase Order {po_data['po_number']} - {data['product_name']}",
                "body": email_body
            },
            "backup_supplier": data.get('backup_supplier'),
            "processed_at": datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Processing failed: {str(e)}"
        }), 500


@app.route('/webhook/escalate-po', methods=['POST'])
def handle_po_escalation():
    """
    Webhook endpoint to escalate PO to backup supplier.
    
    Expected JSON payload:
    {
        "po_data": { ... original PO data ... },
        "backup_supplier": {
            "name": "Backup Supplier Co.",
            "email": "orders@backup.com"
        },
        "primary_supplier_name": "Primary Supplier Inc."
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'po_data' not in data or 'backup_supplier' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Generate escalation
        escalation_json = create_escalation(
            po_json=json.dumps(data['po_data']),
            backup_supplier_name=data['backup_supplier']['name'],
            backup_supplier_email=data['backup_supplier']['email'],
            primary_supplier_name=data.get('primary_supplier_name', 'Primary Supplier')
        )
        
        escalation_data = json.loads(escalation_json)
        
        response = {
            "escalation_created": True,
            "escalation_data": escalation_data,
            "email": {
                "to": escalation_data['to'],
                "subject": escalation_data['subject'],
                "body": escalation_data['body']
            },
            "urgency": escalation_data['urgency'],
            "response_deadline_hours": escalation_data['response_deadline_hours'],
            "processed_at": datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Escalation failed: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "PO Automation"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
