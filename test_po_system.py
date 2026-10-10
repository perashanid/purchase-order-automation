"""
Test script for Purchase Order automation system
"""

from po_generator import POGenerator, create_purchase_order, create_escalation
import json


def test_basic_po_generation():
    """Test basic PO generation."""
    print("=" * 80)
    print("TEST 1: Basic Purchase Order Generation")
    print("=" * 80)
    
    po_json = create_purchase_order(
        product_name="Industrial Ball Bearings 6202-2RS",
        sku="BB-6202-2RS",
        current_stock=45,
        reorder_threshold=100,
        supplier_name="Acme Bearings Inc.",
        supplier_email="orders@acmebearings.com",
        supplier_phone="+1-555-0123"
    )
    
    po_data = json.loads(po_json)
    
    print(f"\n✅ PO Generated Successfully")
    print(f"PO Number: {po_data['po_number']}")
    print(f"Product: {po_data['product']}")
    print(f"SKU: {po_data['sku']}")
    print(f"Quantity: {po_data['quantity']} units")
    print(f"Current Stock: {po_data['current_stock']}")
    print(f"Reorder Threshold: {po_data['reorder_threshold']}")
    print(f"Delivery Date: {po_data['requested_delivery']}")
    print(f"Supplier: {po_data['supplier']['name']}")
    
    # Verify quantity calculation
    expected_deficit = po_data['reorder_threshold'] - po_data['current_stock']
    expected_quantity = expected_deficit + int(expected_deficit * 0.20)
    
    print(f"\n📊 Quantity Calculation:")
    print(f"Deficit: {expected_deficit} units")
    print(f"Safety Buffer (20%): {int(expected_deficit * 0.20)} units")
    print(f"Total Order: {po_data['quantity']} units")
    print(f"Calculation Valid: {'✅' if po_data['quantity'] == expected_quantity else '❌'}")
    
    return po_data


def test_email_formatting():
    """Test email formatting."""
    print("\n\n" + "=" * 80)
    print("TEST 2: Email Formatting")
    print("=" * 80)
    
    po_data = json.loads(create_purchase_order(
        product_name="Hydraulic Pump Model HP-500",
        sku="HP-500-STD",
        current_stock=15,
        reorder_threshold=50,
        supplier_name="Hydraulics Direct Ltd.",
        supplier_email="sales@hydraulicsdirect.com",
        supplier_phone="+44-20-1234-5678"
    ))
    
    generator = POGenerator()
    email = generator.format_po_email(po_data)
    
    print("\n📧 Generated Email:\n")
    print(email)
    
    return email


def test_escalation():
    """Test escalation email generation."""
    print("\n\n" + "=" * 80)
    print("TEST 3: Escalation Email Generation")
    print("=" * 80)
    
    # First create a PO
    po_json = create_purchase_order(
        product_name="Premium Motor Oil 10W-40",
        sku="OIL-10W40-5L",
        current_stock=20,
        reorder_threshold=100,
        supplier_name="Oil Supplies Co.",
        supplier_email="orders@oilsupplies.com"
    )
    
    po_data = json.loads(po_json)
    print(f"\n📋 Original PO: {po_data['po_number']}")
    print(f"Primary Supplier: {po_data['supplier']['name']}")
    
    # Generate escalation
    escalation_json = create_escalation(
        po_json=po_json,
        backup_supplier_name="Reliable Lubricants Inc.",
        backup_supplier_email="urgent@reliablelubricants.com",
        primary_supplier_name="Oil Supplies Co."
    )
    
    escalation_data = json.loads(escalation_json)
    
    print(f"\n⚠️ Escalation Created")
    print(f"Escalated PO: {escalation_data['escalated_po_number']}")
    print(f"Backup Supplier: {escalation_data['supplier_name']}")
    print(f"Urgency: {escalation_data['urgency']}")
    print(f"Response Deadline: {escalation_data['response_deadline_hours']} hours")
    
    print("\n📧 Escalation Email:\n")
    print(escalation_data['body'])
    
    return escalation_data


def test_edge_cases():
    """Test edge cases."""
    print("\n\n" + "=" * 80)
    print("TEST 4: Edge Cases")
    print("=" * 80)
    
    # Test 1: Stock exactly at threshold (should still order)
    print("\n📌 Case 1: Stock exactly at threshold")
    po1 = json.loads(create_purchase_order(
        product_name="Widget A",
        sku="WDG-A",
        current_stock=100,
        reorder_threshold=100,
        supplier_name="Supplier X",
        supplier_email="x@supplier.com"
    ))
    print(f"Current: {po1['current_stock']}, Threshold: {po1['reorder_threshold']}")
    print(f"Order Quantity: {po1['quantity']} units")
    print(f"Expected: 0 (at threshold) → Result: {'✅ Correct' if po1['quantity'] == 0 else '⚠️ Still orders'}")
    
    # Test 2: Stock well below threshold
    print("\n📌 Case 2: Critical low stock")
    po2 = json.loads(create_purchase_order(
        product_name="Widget B",
        sku="WDG-B",
        current_stock=5,
        reorder_threshold=100,
        supplier_name="Supplier Y",
        supplier_email="y@supplier.com"
    ))
    print(f"Current: {po2['current_stock']}, Threshold: {po2['reorder_threshold']}")
    print(f"Order Quantity: {po2['quantity']} units")
    deficit = po2['reorder_threshold'] - po2['current_stock']
    expected = deficit + int(deficit * 0.20)
    print(f"Expected: {expected} → Result: {'✅ Correct' if po2['quantity'] == expected else '❌ Wrong'}")
    
    # Test 3: Very small deficit
    print("\n📌 Case 3: Small deficit")
    po3 = json.loads(create_purchase_order(
        product_name="Widget C",
        sku="WDG-C",
        current_stock=98,
        reorder_threshold=100,
        supplier_name="Supplier Z",
        supplier_email="z@supplier.com"
    ))
    print(f"Current: {po3['current_stock']}, Threshold: {po3['reorder_threshold']}")
    print(f"Order Quantity: {po3['quantity']} units")
    print(f"Result: {'✅ Orders minimum amount' if po3['quantity'] >= 1 else '❌ No order'}")


def test_business_day_calculation():
    """Test business day delivery date calculation."""
    print("\n\n" + "=" * 80)
    print("TEST 5: Business Day Calculation")
    print("=" * 80)
    
    from datetime import datetime
    
    generator = POGenerator()
    
    # Test different business day ranges
    for days in [3, 5, 7, 10, 14]:
        delivery_date = generator._calculate_delivery_date(business_days=days)
        delivery_dt = datetime.strptime(delivery_date, "%Y-%m-%d")
        print(f"\n{days} business days → {delivery_date} ({delivery_dt.strftime('%A')})")
        print(f"Weekend check: {'✅ Not weekend' if delivery_dt.weekday() < 5 else '⚠️ Weekend!'}")


def test_po_number_uniqueness():
    """Test PO number generation uniqueness."""
    print("\n\n" + "=" * 80)
    print("TEST 6: PO Number Uniqueness")
    print("=" * 80)
    
    generator = POGenerator()
    po_numbers = set()
    
    # Generate 10 PO numbers
    for i in range(10):
        po_num = generator._generate_po_number()
        po_numbers.add(po_num)
        print(f"PO #{i+1}: {po_num}")
    
    print(f"\n✅ Generated {len(po_numbers)} unique PO numbers out of 10")
    print(f"Uniqueness: {'✅ PASS' if len(po_numbers) == 10 else '⚠️ Duplicates found'}")


def run_all_tests():
    """Run all tests."""
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PURCHASE ORDER SYSTEM TESTS" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Run tests
        test_basic_po_generation()
        test_email_formatting()
        test_escalation()
        test_edge_cases()
        test_business_day_calculation()
        test_po_number_uniqueness()
        
        print("\n\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
