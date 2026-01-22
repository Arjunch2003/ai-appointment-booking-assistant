"""
Booking flow logic - handles slot filling and confirmation
"""

from typing import Dict, Optional, Tuple
import re
from datetime import datetime
from app import config


class BookingFlow:
    """Manages the booking conversation flow"""
    
    def __init__(self):
        self.required_fields = ['name', 'email', 'phone', 'service_type', 'date', 'time']
        self.current_booking = {}
        self.confirmed = False
    
    def reset(self):
        """Reset booking state"""
        self.current_booking = {}
        self.confirmed = False
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        # Simple pattern for phone numbers
        phone_pattern = r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        matches = re.findall(phone_pattern, text)
        if matches:
            # Clean phone number
            phone = re.sub(r'[-.\s]', '', matches[0])
            return phone
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from text (YYYY-MM-DD or DD-MM-YYYY format)"""
        # Look for YYYY-MM-DD format
        date_pattern_1 = r'\b\d{4}-\d{2}-\d{2}\b'
        matches_1 = re.findall(date_pattern_1, text)
        if matches_1:
            try:
                datetime.strptime(matches_1[0], '%Y-%m-%d')
                return matches_1[0]
            except ValueError:
                pass
        
        # Look for DD-MM-YYYY format
        date_pattern_2 = r'\b\d{2}-\d{2}-\d{4}\b'
        matches_2 = re.findall(date_pattern_2, text)
        if matches_2:
            try:
                d = datetime.strptime(matches_2[0], '%d-%m-%Y')
                return d.strftime('%Y-%m-%d')
            except ValueError:
                pass
        return None
    
    def extract_time(self, text: str) -> Optional[str]:
        """Extract time from text (HH:MM 24h or HH:MM AM/PM)"""
        # Look for HH:MM (24h)
        time_pattern_24 = r'\b([01]?[0-9]|2[0-3]):([0-5][0-9])\b'
        
        # Look for 12h format (e.g., 2:30 PM, 11am)
        time_pattern_12 = r'\b(1[0-2]|0?[1-9])(?::([0-5][0-9]))?\s*([AaPp][Mm])\b'
        
        # Try 12h first (more specific)
        match_12 = re.search(time_pattern_12, text)
        if match_12:
            hour = match_12.group(1)
            minute = match_12.group(2) or "00"
            period = match_12.group(3).lower()
            try:
                t_str = f"{hour}:{minute} {period}"
                # Handle cases like "2pm" missing minutes
                t_obj = datetime.strptime(t_str, "%I:%M %p")
                return t_obj.strftime("%H:%M")
            except ValueError:
                pass

        # Try 24h format
        match_24 = re.search(time_pattern_24, text)
        if match_24:
            hour, minute = match_24.groups()
            return f"{hour.zfill(2)}:{minute}"
            
        return None
    
    def extract_service_type(self, text: str) -> Optional[str]:
        """Extract specialty/service type from text"""
        text_lower = text.lower()
        
        # 1. Check exact canonical match first
        for b_type in config.BOOKING_TYPES:
            if b_type.lower() in text_lower:
                return b_type
        
        # 2. Check keyword mappings
        mappings = {
            'gp': 'General Practitioner (GP)',
            'general practitioner': 'General Practitioner (GP)',
            'general doctor': 'General Practitioner (GP)',
            'ortho': 'Orthopedic Specialist',
            'bone': 'Orthopedic Specialist',
            'cardio': 'Cardiologist',
            'heart': 'Cardiologist',
            'derma': 'Dermatologist',
            'skin': 'Dermatologist',
            'pedia': 'Pediatrician',
            'child': 'Pediatrician',
            'kid': 'Pediatrician'
        }
        
        for keyword, canonical in mappings.items():
            if keyword in text_lower:
                return canonical
                
        return None
    
    def update_from_message(self, message: str) -> Dict:
        """
        Extract and update booking details from user message
        
        Returns:
            Dictionary with updated fields
        """
        updated = {}
        
        # Extract email
        email = self.extract_email(message)
        if email:
            self.current_booking['email'] = email
            updated['email'] = email
        
        # Extract phone
        phone = self.extract_phone(message)
        if phone:
            self.current_booking['phone'] = phone
            updated['phone'] = phone
        
        # Extract date
        date = self.extract_date(message)
        if date:
            self.current_booking['date'] = date
            updated['date'] = date
        
        # Extract time
        time = self.extract_time(message)
        if time:
            self.current_booking['time'] = time
            updated['time'] = time
        
        # Extract service type
        service_type = self.extract_service_type(message)
        if service_type:
            self.current_booking['service_type'] = service_type
            updated['service_type'] = service_type
        
        # Extract name
        # Removing the heuristic to prevent capturing 'I want to book' as a name.
        # The LLM in ChatLogic will now handle natural name extraction.
        pass
        
        return updated
    
    def get_missing_fields(self) -> list:
        """Get list of missing required fields"""
        return [field for field in self.required_fields if field not in self.current_booking]
    
    def get_next_question(self) -> Optional[str]:
        """Get the next question to ask based on missing fields"""
        missing = self.get_missing_fields()
        
        if not missing:
            return None
        
        field = missing[0]
        
        questions = {
            'name': "What's the patient's full name?",
            'email': "What's your email address?",
            'phone': "What's your phone number? (10 digits)",
            'service_type': f"Which specialist do you need to see? Options: {', '.join(config.BOOKING_TYPES)}",
            'date': "What's your preferred date? (YYYY-MM-DD)",
            'time': "What time would you prefer? (HH:MM)"
        }
        
        return questions.get(field, f"Please provide your {field}")
    
    def is_complete(self) -> bool:
        """Check if all required fields are collected"""
        return len(self.get_missing_fields()) == 0
    
    def get_summary(self) -> str:
        """Get a summary of the booking for confirmation"""
        if not self.is_complete():
            return "Booking information is incomplete."
        
        summary = f"""
### 🏥 Appointment Summary

👤 **Patient:** {self.current_booking.get('name')}
📧 **Email:** {self.current_booking.get('email')}
📱 **Phone:** {self.current_booking.get('phone')}
🎯 **Specialty:** {self.current_booking.get('service_type')}
📅 **Date:** {self.current_booking.get('date')}
⏰ **Time:** {self.current_booking.get('time')}

**Is this information correct?** 
Reply with **"Yes"** to confirm and save your booking (we'll also send you an email confirmation).
Reply with **"No"** or **"Cancel"** to start over.
        """
        return summary.strip()
    
    def validate_fields(self) -> Tuple[bool, str]:
        """Validate all booking fields"""
        # Validate email
        email = self.current_booking.get('email')
        if email and not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
            return False, "Invalid email format"
        
        # Validate phone
        phone = self.current_booking.get('phone')
        if phone and not re.match(r'^\d{10}$', phone):
            return False, "Phone number must be 10 digits"
        
        # Validate date
        date = self.current_booking.get('date')
        if date:
            try:
                booking_date = datetime.strptime(date, '%Y-%m-%d')
                if booking_date < datetime.now():
                    return False, "Booking date cannot be in the past"
            except ValueError:
                return False, "Invalid date format. Please use YYYY-MM-DD"
        
        # Validate time
        time = self.current_booking.get('time')
        if time:
            try:
                datetime.strptime(time, '%H:%M')
            except ValueError:
                return False, "Invalid time format. Please use HH:MM"
        
        return True, "All fields valid"
