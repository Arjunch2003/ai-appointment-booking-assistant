"""
Database models for the AI Booking Assistant
"""

from datetime import datetime
from typing import Optional

class Customer:
    """Customer model"""
    def __init__(self, customer_id: Optional[int], name: str, email: str, phone: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }


class Booking:
    """Booking model"""
    def __init__(
        self, 
        id: Optional[int], 
        customer_id: int,
        service_type: str,
        date: str,
        time: str,
        status: str = 'Pending',
        created_at: Optional[str] = None
    ):
        self.id = id
        self.customer_id = customer_id
        self.service_type = service_type
        self.date = date
        self.time = time
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'service_type': self.service_type,
            'date': self.date,
            'time': self.time,
            'status': self.status,
            'created_at': self.created_at
        }
