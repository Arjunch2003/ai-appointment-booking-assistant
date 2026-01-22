"""
Tools for RAG, booking persistence, and email functionality
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import db.database
from app import config


class BookingTool:
    """Tool for persisting bookings to the database"""
    
    def __init__(self):
        self.db = db.database.Database(str(config.DB_PATH))
    
    def save_booking(self, booking_data: Dict) -> Dict:
        """
        Save booking to database
        
        Args:
            booking_data: Dictionary with keys: name, email, phone, service_type, date, time
            
        Returns:
            Dictionary with success status and booking_id
        """
        try:
            # Add customer (or get existing)
            customer_id = self.db.add_customer(
                name=booking_data['name'],
                email=booking_data['email'],
                phone=booking_data['phone']
            )
            
            if not customer_id:
                return {'success': False, 'error': 'Failed to create customer'}
            
            # Add booking
            booking_id = self.db.add_booking(
                customer_id=customer_id,
                service_type=booking_data['service_type'],
                date=booking_data['date'],
                time=booking_data['time']
            )
            
            if booking_id:
                return {
                    'success': True,
                    'booking_id': booking_id,
                    'customer_id': customer_id
                }
            else:
                return {'success': False, 'error': 'Failed to create booking'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}


class EmailTool:
    """Tool for sending email confirmations"""
    
    def __init__(self, sender_email: str = None, sender_password: str = None):
        self.sender_email = sender_email or config.EMAIL_SENDER
        self.sender_password = sender_password or config.EMAIL_PASSWORD
    
    def send_confirmation_email(
        self, 
        to_email: str, 
        booking_id: int,
        name: str,
        booking_type: str,
        date: str,
        time: str
    ) -> Dict:
        """
        Send booking confirmation email
        
        Args:
            to_email: Recipient email address
            booking_id: Booking ID
            name: Customer name
            booking_type: Type of booking
            date: Booking date
            time: Booking time
            
        Returns:
            Dictionary with success status
        """
        # For now, simulate email sending (will implement actual SMTP later)
        try:
            # Create email content
            subject = f"Booking Confirmation - #{booking_id}"
            body = f"""
Dear {name},

Your medical appointment has been scheduled and is currently Pending confirmation from our staff.

Appointment Details:
- Appointment ID: #{booking_id}
- Specialty: {booking_type}
- Date: {date}
- Time: {time}

Thank you for trusting our clinic!

Best regards,
{config.APP_NAME}
            """
            
            # For development, log the email
            print(f"\n{'='*50}")
            print(f"📧 EMAIL LOG: SENDING TO {to_email}")
            print(f"SUBJECT: {subject}")
            print(f"{'='*50}\n")
            
            # Send actual SMTP email if credentials exist
            if self.sender_email and self.sender_password:
                success = self._send_smtp_email(to_email, subject, body)
                if not success:
                    return {
                        'success': False,
                        'message': 'Failed to send actual email. Check your SMTP settings and app password.',
                        'to': to_email
                    }
                return {
                    'success': True,
                    'message': 'Email sent successfully via SMTP',
                    'to': to_email
                }
            else:
                return {
                    'success': True,
                    'message': 'Booking saved. (Add EMAIL_SENDER and EMAIL_PASSWORD to .env to send real emails)',
                    'to': to_email
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Email could not be sent, but booking was saved.'
            }
    
    def _send_smtp_email(self, to_email: str, subject: str, body: str):
        """Send email using SMTP (Gmail)"""
        try:
            if not self.sender_email or not self.sender_password:
                print("⚠️ SMTP Error: Credentials not provided")
                return False

            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to Gmail SMTP server
            print(f"🔄 Attempting SMTP connection to smtp.gmail.com:587 for {to_email}...")
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
            print("  ✅ TCP Connection established")
            
            server.set_debuglevel(1) # Enable SMTP debug trace in terminal
            
            print("🔄 Starting TLS...")
            server.starttls()
            print("  ✅ TLS encryption established")
            
            print(f"🔄 Logging in as {self.sender_email}...")
            server.login(self.sender_email, self.sender_password)
            print("  ✅ SMTP Login successful")
            
            print(f"🔄 Sending message to {to_email}...")
            server.send_message(msg)
            print("  ✅ Message sent")
            
            server.quit()
            print(f"✅ SMTP session closed successfully")
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Error: Authentication failed for {self.sender_email}. Details: {e}")
            return False
        except Exception as e:
            print(f"❌ SMTP Error: An unexpected error occurred: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False


class RAGTool:
    """Tool for RAG-based question answering"""
    
    def __init__(self, vector_store=None):
        self.vector_store = vector_store
    
    def query(self, question: str) -> str:
        """
        Query the RAG system
        
        Args:
            question: User question
            
        Returns:
            Answer from RAG system
        """
        if not self.vector_store:
            return "No knowledge base loaded. Please upload PDF documents first."
        
        try:
            # This will be implemented in rag_pipeline.py
            # For now, return a placeholder
            return "RAG functionality will be implemented with PDF upload."
        except Exception as e:
            return f"Error querying knowledge base: {str(e)}"
