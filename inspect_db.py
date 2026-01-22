import sqlite3
import os

db_path = "bookings.db"

if not os.path.exists(db_path):
    print("Database file not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Table Info: bookings ---")
    try:
        cursor.execute("PRAGMA table_info(bookings)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
            
        print("\n--- Table Info: customers ---")
        cursor.execute("PRAGMA table_info(customers)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
            
    except Exception as e:
        print(f"Error reading schema: {e}")
    finally:
        conn.close()
