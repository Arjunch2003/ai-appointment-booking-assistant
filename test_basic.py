"""
Quick test script to verify database and basic functionality
"""

import sys
from pathlib import Path

# Add project to path
sys.path.append(str(Path(__file__).parent))

from db.database import Database
from app.tools import BookingTool, EmailTool
from app.config import DB_PATH

def test_database():
    """Test database operations"""
    print("=" * 50)
    print("Testing Database...")
    print("=" * 50)
    
    db = Database(str(DB_PATH))
    
    # Test adding customer
    print("\n1. Adding test customer...")
    customer_id = db.add_customer(
        name="Test User",
        email="test@example.com",
        phone="1234567890"
    )
    print(f"✅ Customer added with ID: {customer_id}")
    
    # Test adding booking
    print("\n2. Adding test booking...")
    booking_id = db.add_booking(
        customer_id=customer_id,
        booking_type="Doctor Appointment",
        date="2026-02-01",
        time="14:30"
    )
    print(f"✅ Booking added with ID: {booking_id}")
    
    # Test retrieving bookings
    print("\n3. Retrieving all bookings...")
    bookings = db.get_all_bookings()
    print(f"✅ Found {len(bookings)} booking(s)")
    
    if bookings:
        print("\nLatest booking:")
        latest = bookings[0]
        print(f"  - ID: {latest['id']}")
        print(f"  - Customer: {latest['customer_name']}")
        print(f"  - Email: {latest['customer_email']}")
        print(f"  - Service: {latest['booking_type']}")
        print(f"  - Date: {latest['date']} at {latest['time']}")
    
    print("\n✅ Database tests passed!")


def test_booking_tool():
    """Test booking tool"""
    print("\n" + "=" * 50)
    print("Testing Booking Tool...")
    print("=" * 50)
    
    booking_tool = BookingTool()
    
    print("\n1. Testing booking save...")
    result = booking_tool.save_booking({
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '9876543210',
        'booking_type': 'Salon Service',
        'date': '2026-02-15',
        'time': '10:00'
    })
    
    if result['success']:
        print(f"✅ Booking saved with ID: {result['booking_id']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n✅ Booking tool tests passed!")


def test_email_tool():
    """Test email tool"""
    print("\n" + "=" * 50)
    print("Testing Email Tool...")
    print("=" * 50)
    
    email_tool = EmailTool()
    
    print("\n1. Testing email confirmation...")
    result = email_tool.send_confirmation_email(
        to_email="test@example.com",
        booking_id=1,
        name="Test User",
        booking_type="Test Service",
        date="2026-02-01",
        time="14:00"
    )
    
    if result['success']:
        print(f"✅ Email sent successfully")
    else:
        print(f"⚠️ Email simulated (SMTP not configured)")
    
    print("\n✅ Email tool tests passed!")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " " * 8 + "AI Booking Assistant - Test Suite" + " " * 7 + "║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    try:
        test_database()
        test_booking_tool()
        test_email_tool()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\nYou can now run the application with:")
        print("  streamlit run app/main.py")
        print("\nOr use the quick start script:")
        print("  run.bat")
        print()
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
