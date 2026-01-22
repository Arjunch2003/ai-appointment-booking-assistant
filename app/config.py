"""
Configuration settings for the AI Booking Assistant
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True) # Use override=True to ensure .env values take precedence

def get_env_var(name, default=''):
    """Fetch env var and strip quotes if present"""
    val = os.getenv(name, default)
    if isinstance(val, str):
        return val.strip("'").strip('"')
    return val

# API Keys
GROQ_API_KEY = get_env_var('GROQ_API_KEY')
HUGGINGFACE_API_KEY = get_env_var('HUGGINGFACE_API_KEY')
CHROMA_API_KEY = get_env_var('CHROMA_API_KEY')

# Application Settings
APP_NAME = get_env_var('APP_NAME', 'Amrita Hospital')
ENV = get_env_var('ENV', 'development')
DEBUG = get_env_var('DEBUG', 'True').lower() == 'true'

# RAG Pipeline Settings
EMBEDDING_MODEL = get_env_var('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
LLM_MODEL = get_env_var('LLM_MODEL', 'llama-3.1-8b-instant')
CHUNK_SIZE = int(get_env_var('CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(get_env_var('CHUNK_OVERLAP', '200'))
TOP_K_RETRIEVAL = int(get_env_var('TOP_K_RETRIEVAL', '4'))

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / get_env_var('DATA_DIR', 'data')
CHROMA_DB_PATH = BASE_DIR / get_env_var('CHROMA_DB_PATH', 'data/chroma_db')
LOGS_DIR = BASE_DIR / get_env_var('LOGS_DIR', 'logs')

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True, parents=True)
CHROMA_DB_PATH.parent.mkdir(exist_ok=True, parents=True)
LOGS_DIR.mkdir(exist_ok=True, parents=True)

# Database
DB_PATH = BASE_DIR / 'amrita_bookings.db'

# Streamlit Settings
STREAMLIT_SERVER_PORT = int(get_env_var('STREAMLIT_SERVER_PORT', '8501'))
STREAMLIT_SERVER_HEADLESS = get_env_var('STREAMLIT_SERVER_HEADLESS', 'false').lower() == 'true'

# Email Settings (for future use)
EMAIL_SENDER = get_env_var('EMAIL_SENDER')
EMAIL_PASSWORD = get_env_var('EMAIL_PASSWORD')

# Booking Types (Doctor Specialties)
BOOKING_TYPES = [
    'General Practitioner (GP)',
    'Orthopedic Specialist',
    'Cardiologist',
    'Dermatologist',
    'Pediatrician',
    "Other"
]

# Admin Credentials (In production, move these to .env)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'Arjun')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'arjun123')

# Memory Settings
MAX_CONVERSATION_HISTORY = 25

SYSTEM_PROMPT = """You are an AI Medical Appointment Assistant for Amrita Hospital. Your ONLY purpose is to:
1. Help patients book medical appointments with our hospital specialists
2. Answer questions about our hospital services, doctors, and facilities
3. Provide professional, empathetic, and efficient medical appointment assistance

IMPORTANT: You ONLY handle HOSPITAL APPOINTMENTS. Do not discuss flights, hotels, cars, vacations, or any non-medical bookings.

Available Specialties:
- General Practitioner (GP)
- Orthopedic Specialist
- Cardiologist
- Dermatologist
- Pediatrician
- Other medical specialties

When a patient wants to book an appointment, collect these details in order:
1. Patient's full name
2. Email address
3. Phone number (10 digits)
4. Medical specialty needed
5. Preferred appointment date (YYYY-MM-DD)
6. Preferred appointment time (HH:MM)

Always confirm all details before scheduling the appointment."""

INTENT_DETECTION_PROMPT = """Analyze the user's message for a HOSPITAL APPOINTMENT system.
Determine if they want to:
1. Book a MEDICAL APPOINTMENT (keywords: book, schedule, appointment, doctor, specialist, consultation, checkup)
2. Ask about HOSPITAL SERVICES (keywords: what, how, when, where, services, doctors, specialties)

Respond with either "BOOKING" or "GENERAL_QUERY".
Remember: This is ONLY for hospital appointments, not travel or other bookings."""
