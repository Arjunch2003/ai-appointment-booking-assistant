"""
Database handler for SQLite operations
"""

import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime
from .models import Customer, Booking
import os


class Database:
    """SQLite database handler for the booking system"""
    
    def __init__(self, db_path: str = "bookings.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Create bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                service_type TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT CHECK(status IN ('Pending', 'Confirmed', 'Cancelled', 'Completed')) DEFAULT 'Pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_customer(self, name: str, email: str, phone: str) -> Optional[int]:
        """Add a new customer or return existing customer_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if customer exists
            cursor.execute('SELECT customer_id FROM customers WHERE email = ?', (email,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            
            # Insert new customer
            cursor.execute(
                'INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)',
                (name, email, phone)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Email already exists
            cursor.execute('SELECT customer_id FROM customers WHERE email = ?', (email,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def add_booking(self, customer_id: int, service_type: str, date: str, time: str) -> Optional[int]:
        """Add a new booking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            created_at = datetime.now().isoformat()
            cursor.execute(
                '''INSERT INTO bookings (customer_id, service_type, date, time, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (customer_id, service_type, date, time, 'Pending', created_at)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding booking: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_bookings(self) -> List[dict]:
        """Get all bookings with customer details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                b.id, b.customer_id, b.service_type, b.date, b.time, b.status, b.created_at,
                c.name, c.email, c.phone
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            ORDER BY b.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        bookings = []
        for row in rows:
            bookings.append({
                'id': row[0],
                'customer_id': row[1],
                'service_type': row[2],
                'date': row[3],
                'time': row[4],
                'status': row[5],
                'created_at': row[6],
                'customer_name': row[7],
                'customer_email': row[8],
                'customer_phone': row[9]
            })
        
        return bookings
    
    def get_booking_by_id(self, booking_id: int) -> Optional[dict]:
        """Get a specific booking by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                b.id, b.customer_id, b.service_type, b.date, b.time, b.status, b.created_at,
                c.name, c.email, c.phone
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE b.id = ?
        ''', (booking_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'customer_id': row[1],
                'service_type': row[2],
                'date': row[3],
                'time': row[4],
                'status': row[5],
                'created_at': row[6],
                'customer_name': row[7],
                'customer_email': row[8],
                'customer_phone': row[9]
            }
        return None
    
    def search_bookings(self, query: str) -> List[dict]:
        """Search bookings by name, email, or date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        cursor.execute('''
            SELECT 
                b.id, b.customer_id, b.service_type, b.date, b.time, b.status, b.created_at,
                c.name, c.email, c.phone
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE c.name LIKE ? OR c.email LIKE ? OR b.date LIKE ?
            ORDER BY b.created_at DESC
        ''', (search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        conn.close()
        
        bookings = []
        for row in rows:
            bookings.append({
                'id': row[0],
                'customer_id': row[1],
                'service_type': row[2],
                'date': row[3],
                'time': row[4],
                'status': row[5],
                'created_at': row[6],
                'customer_name': row[7],
                'customer_email': row[8],
                'customer_phone': row[9]
            })
        
        return bookings
    def update_booking_status(self, booking_id: int, status: str) -> bool:
        """Update the status of a booking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'UPDATE bookings SET status = ? WHERE id = ?',
                (status, booking_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating booking status: {e}")
            return False
        finally:
            conn.close()

    def get_all_customers(self) -> List[dict]:
        """Get all customers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM customers')
            rows = cursor.fetchall()
            return [
                {'customer_id': r[0], 'name': r[1], 'email': r[2], 'phone': r[3]}
                for r in rows
            ]
        finally:
            conn.close()
