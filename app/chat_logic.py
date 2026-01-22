"""
Chat logic - handles intent detection and conversation flow
"""

from typing import Optional, Dict, List
from langchain_groq import ChatGroq
from app import config
from app.booking_flow import BookingFlow
from app.rag_pipeline import RAGPipeline
from app.tools import BookingTool, EmailTool


class ChatLogic:
    """Manages chat conversation and intent detection"""
    
    def __init__(self):
        self.llm = None
        if config.GROQ_API_KEY:
            self.llm = ChatGroq(
                groq_api_key=config.GROQ_API_KEY,
                model_name=config.LLM_MODEL,
                temperature=0.7
            )
        
        self.booking_flow = BookingFlow()
        self.rag_pipeline = RAGPipeline()
        self.booking_tool = BookingTool()
        self.email_tool = EmailTool()
        
        self.conversation_history = []
        self.current_mode = None  # 'booking' or 'general'
        self.awaiting_confirmation = False
    
    def initialize_rag(self):
        """Initialize RAG pipeline"""
        return self.rag_pipeline.initialize()
    
    def detect_intent(self, message: str) -> str:
        """
        Detect user intent - SIMPLE KEYWORD MATCHING ONLY
        """
        message_lower = message.lower().strip()
        
        # PRIORITY 1: Explicit cancellation
        if any(phrase in message_lower for phrase in ['cancel booking', 'stop booking', 'cancel appointment', 'stop appointment']):
            return 'cancel'
        if message_lower in ['cancel', 'stop', 'exit', 'quit']:
            return 'cancel'
        
        # PRIORITY 2: Confirmation when awaiting
        if self.awaiting_confirmation:
            if any(k in message_lower for k in ['yes', 'confirm', 'correct', 'right', 'ok', 'okay', 'sure']):
                return 'confirm'
        
        # PRIORITY 3: EXACT booking keywords ONLY
        # Must contain one of these exact words
        booking_keywords = ['book', 'schedule', 'appointment', 'reserve', 'reservation']
        
        # Check if ANY booking keyword is present
        for keyword in booking_keywords:
            if keyword in message_lower:
                return 'booking'
        
        # PRIORITY 4: Everything else is GENERAL
        return 'general'
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            'role': role,
            'content': content
        })
        
        # Keep only last config.MAX_CONVERSATION_HISTORY messages
        if len(self.conversation_history) > config.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-config.MAX_CONVERSATION_HISTORY:]
    
    def handle_general_query(self, message: str) -> str:
        """Handle general questions using RAG"""
        try:
            # Try RAG first if documents are loaded
            if self.rag_pipeline.documents_loaded:
                answer = self.rag_pipeline.query(message)
                return answer
            else:
                # Fallback to general LLM response
                return self.generate_general_response(message)
        except Exception as e:
            return f"I'm having trouble processing your question. Error: {str(e)}"
    
    def generate_general_response(self, message: str) -> str:
        """Generate general response using LLM"""
        try:
            if not self.llm:
                return "❌ I'm not properly configured. Please check that GROQ_API_KEY is set in the .env file."
            
            # Create conversation context
            messages = [
                {
                    "role": "system",
                    "content": f"""You are an AI Medical Appointment Assistant for {config.APP_NAME}.

IMPORTANT: You ONLY handle HOSPITAL APPOINTMENTS and medical inquiries. 
- Do NOT suggest booking flights, hotels, cars, vacations, or any non-medical services
- Do NOT ask what type of booking they want
- If they want to book something, assume it's a MEDICAL APPOINTMENT

Your role:
1. Answer questions about hospital services, doctors, and medical specialties
2. Help patients schedule medical appointments
3. Provide professional, empathetic medical assistance

Available specialties: {', '.join(config.BOOKING_TYPES)}

If someone says they want to "book" or "make an appointment", tell them to say "I want to book an appointment" to start the booking process.

If someone asks about symptoms or medical conditions, provide helpful information and suggest they book an appointment if needed."""
                }
            ]
            
            # Add recent history
            messages.extend(self.conversation_history[-5:] if self.conversation_history else [])
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Generate response
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error generating general response: {error_msg}")
            
            # Provide helpful error messages
            if "api" in error_msg.lower() or "key" in error_msg.lower():
                return "❌ API error. Please check your GROQ_API_KEY in the .env file."
            elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
                return "⏱️ Rate limit reached. Please wait a moment and try again."
            elif "timeout" in error_msg.lower():
                return "⏱️ Request timed out. Please try again."
            else:
                return f"❌ I'm having trouble generating a response. Error: {error_msg}\n\nPlease try again or rephrase your question."
    
    def _extract_booking_info_with_llm(self, message: str, focused_field: str = None) -> Dict:
        """Use LLM to extract booking information from natural language"""
        try:
            current_state = self.booking_flow.current_booking
            
            # Current date for relative date parsing
            from datetime import datetime
            today = datetime.now()
            today_str = today.strftime('%Y-%m-%d (%A)')
            
            # Recent context
            recent_context = self.conversation_history[-5:] if self.conversation_history else []
            
            focus_instruction = ""
            if focused_field:
                focus_instruction = f"FOCUS: The user was specifically asked for their '{focused_field}'. Prioritize extracting this information from the message."

            prompt = f"""
            You are a booking assistant for "{config.APP_NAME}".
            Extract booking details from the user's message.
            Today's Date: {today_str}
            
            Recent context: {recent_context}
            Current state: {current_state}
            User message: "{message}"
            {focus_instruction}
            
            Allowed booking types: {config.BOOKING_TYPES}
            
            Return ONLY a valid JSON object. 
            
            FORMAT RULES:
            - date: Convert ALL dates (e.g., "next Monday", "25-01-2026") to YYYY-MM-DD. 
            - time: Convert ALL times (e.g., "2 PM", "14:30") to 24-hour HH:MM format.
            - phone: Ensure it's 10 digits.
            
            Do NOT include a key if the information is missing or if the user is just saying hi/intent.
            Do NOT hallucinate values.
            
            Available keys:
            - name: string (real persons name)
            - email: string (verified format)
            - phone: string (10 digits)
            - service_type: string (must match allowed specialties exactly)
            - date: string (YYYY-MM-DD)
            - time: string (HH:MM)
            
            Example input: "book for next Monday at 2 PM" -> Output: {"date": "YYYY-MM-DD", "time": "14:00"}
            
            IMPORTANT: If the user response looks like a name (e.g., "John Doe", "Sarah") or they were asked for a name, extract it as "name".
            """
            
            response = self.llm.invoke([{"role": "user", "content": prompt}])
            
            import json
            import re
            
            # Find JSON in response
            match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {}
        except Exception as e:
            print(f"LLM Extraction failed: {e}")
            return {}

    def handle_booking_flow(self, message: str) -> str:
        """Handle booking conversation flow dynamically with LLM"""
        try:
            # Determine what we are looking for (the first missing field)
            missing_before_update = self.booking_flow.get_missing_fields()
            focused_field = missing_before_update[0] if missing_before_update else None

            # 1. Update from message using both Regex (reliability) and LLM (flexibility)
            regex_updated = self.booking_flow.update_from_message(message)
            llm_extracted = self._extract_booking_info_with_llm(message, focused_field=focused_field)
            
            # Merge LLM info into booking state if regex missed them
            for key, val in llm_extracted.items():
                if key not in self.booking_flow.current_booking:
                    self.booking_flow.current_booking[key] = val
                    
            # Fallback: If we needed a Name and didn't get one, and the message is short, assume it's the name
            missing = self.booking_flow.get_missing_fields()
            if missing and missing[0] == 'name' and 'name' not in self.booking_flow.current_booking:
                # Heuristic: If message is reasonably short (<= 7 words) and not a command, treat as name
                # This covers "John", "John Doe", "My name is John Doe", "It is John"
                words = message.split()
                if len(words) <= 7 and message.lower() not in ['cancel', 'stop', 'exit', 'no']:
                    # Clean up common prefixes if simple extraction needed
                    clean_name = message
                    for prefix in ['my name is', 'i am', 'this is', 'it is', 'name is']:
                        if clean_name.lower().startswith(prefix):
                            clean_name = clean_name[len(prefix):].strip()
                    
                    if clean_name.strip():
                        self.booking_flow.current_booking['name'] = clean_name.strip()
            
            # 2. Check completeness
            if self.booking_flow.is_complete():
                valid, error_msg = self.booking_flow.validate_fields()
                if not valid:
                    return f"❌ {error_msg}. Could you please correct that?"
                
                self.awaiting_confirmation = True
                return self.booking_flow.get_summary()
            
            # Get the next question directly from BookingFlow (fixed questions)
            next_question = self.booking_flow.get_next_question()
            if next_question:
                return next_question
            
            return "How can I help you finalize this booking?"
            
        except Exception as e:
            # Fallback to robotic mode if LLM fails
            return self.booking_flow.get_next_question() or f"Error in booking flow: {str(e)}"
    
    def confirm_booking(self) -> str:
        """Confirm and save booking"""
        try:
            # Save to database
            result = self.booking_tool.save_booking(self.booking_flow.current_booking)
            
            if not result['success']:
                return f"❌ Sorry, there was an error saving your booking: {result.get('error')}"
            
            booking_id = result['booking_id']
            
            # Send email confirmation
            email_result = self.email_tool.send_confirmation_email(
                to_email=self.booking_flow.current_booking['email'],
                booking_id=booking_id,
                name=self.booking_flow.current_booking['name'],
                booking_type=self.booking_flow.current_booking['service_type'],
                date=self.booking_flow.current_booking['date'],
                time=self.booking_flow.current_booking['time']
            )
            
            # Store info before reset
            user_email = self.booking_flow.current_booking.get('email', 'your email')
            
            # Reset booking state
            self.booking_flow.reset()
            self.awaiting_confirmation = False
            self.current_mode = None
            
            # Create confirmation message
            confirmation_msg = f"""
✅ **Booking Confirmed!**

Your booking has been successfully saved with ID: **#{booking_id}**

📧 {email_result.get('message', 'A confirmation email has been sent to ' + user_email)}.

You can view your booking in the Admin Dashboard.

Is there anything else I can help you with?
            """
            
            if not email_result['success']:
                confirmation_msg += f"\n\n⚠️ Note: {email_result.get('message', 'Email could not be sent')}"
            
            return confirmation_msg.strip()
            
        except Exception as e:
            return f"❌ Error confirming booking: {str(e)}"
    
    def cancel_booking(self) -> str:
        """Cancel current booking"""
        self.booking_flow.reset()
        self.awaiting_confirmation = False
        self.current_mode = None
        
        # Clear conversation history to prevent LLM from picking up old name/info
        # when a new booking starts. This fixes the "name not asked" issue.
        self.conversation_history = []
        
        return "Booking cancelled. Would you like to start over or ask something else?"
    
    def process_message(self, message: str) -> str:
        """
        Main method to process user message
        
        Args:
            message: User message
            
        Returns:
            Bot response
        """
        # Add user message to history
        self.add_to_history('user', message)
        
        # Detect intent
        intent = self.detect_intent(message)
        
        # Handle based on intent with priority to active booking flow
        # Priority 1: Explicit cancellation
        if intent == 'cancel':
            response = self.cancel_booking()
        # Priority 2: Confirmation when awaiting
        elif intent == 'confirm' and self.awaiting_confirmation:
            response = self.confirm_booking()
        # Priority 3: Active booking flow (continue if already in progress)
        elif self.current_mode == 'booking' or len(self.booking_flow.current_booking) > 0:
            # We're in an active booking flow, continue it
            self.current_mode = 'booking'
            response = self.handle_booking_flow(message)
        # Priority 4: New booking intent
        elif intent == 'booking':
            self.current_mode = 'booking'
            response = self.handle_booking_flow(message)
        # Priority 5: General query
        else:
            response = self.handle_general_query(message)
        
        # Add bot response to history
        self.add_to_history('assistant', response)
        
        return response
