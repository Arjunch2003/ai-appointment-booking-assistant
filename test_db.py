from db.database import Database
from app.config import DB_PATH
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

db = Database(str(DB_PATH))
print(f"Methods in Database: {[m for m in dir(db) if not m.startswith('_')]}")
if hasattr(db, 'get_all_customers'):
    print("Found get_all_customers")
    try:
        customers = db.get_all_customers()
        print(f"Success! Found {len(customers)} customers.")
    except Exception as e:
        print(f"Error calling get_all_customers: {e}")
else:
    print("MISSING get_all_customers!")
