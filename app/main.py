"""
Main Streamlit application for AI Booking Assistant
"""

import streamlit as st
import sys
import importlib
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import app.config
import app.chat_logic
import app.admin_dashboard
import app.rag_pipeline
import app.tools
import db.database

from app.config import APP_NAME, BOOKING_TYPES
from app.chat_logic import ChatLogic
from app.admin_dashboard import render_admin_dashboard

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS Design System
st.markdown("""
<style>
    /* Dark blue-black background for the entire app to meet dashboard requirement */
    .stApp {
        background-color: #0d1117; /* GitHub Dark mode like background */
    }
    
    /* Global Sidebar Style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
        color: #c9d1d9;
        border-right: 1px solid #30363d;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    /* High-Contrast Chat Bubbles */
    .stChatMessage {
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        line-height: 1.6 !important;
    }
    
    /* Assistant: Slate Blue background with White text */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    /* User: Depth Gray with slightly different border */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-right: 4px solid #94a3b8 !important;
    }

    /* Professional Button Styling */
    .stButton>button {
        background-color: #2563eb;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #3b82f6 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
    }
    
    /* Tab Navigation Improvements */
    .stTabs [data-baseweb="tab-list"] {
        padding: 6px !important;
        background-color: #161b22 !important;
        border-radius: 10px !important;
        border-bottom: 1px solid #30363d !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600 !important;
        color: #8b949e !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        border-bottom-color: #2563eb !important;
    }

    /* Ensure text in Admin Dashboard is readable */
    h1, h2, h3, p, span, li, label {
        color: #e6edf3 !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #8b949e !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_logic' not in st.session_state:
        try:
            st.session_state.chat_logic = ChatLogic()
            st.session_state.chat_logic.initialize_rag()
        except Exception as e:
            st.error(f"Error initializing chat: {e}")
            # Create minimal chat logic even if RAG fails
            st.session_state.chat_logic = ChatLogic()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"""👋 **Welcome to {APP_NAME}!**

I'm your AI Medical Appointment Assistant. I can help you with:

🏥 **Book Medical Appointments**
- Schedule appointments with our specialists
- Choose from: GP, Cardiologist, Orthopedic, Dermatologist, Pediatrician

📚 **Answer Medical Questions**
- Information about our hospital services
- Details about our doctors and specialties
- General medical inquiries

📄 **Knowledge Base**
- Upload medical documents (PDFs) for reference
- Ask questions about uploaded materials

**Ready to help! How can I assist you today?**

💡 *To book an appointment, just say "I want to book an appointment" or "Schedule a doctor visit"*
"""
            }
        ]
    
    if 'rag_initialized' not in st.session_state:
        st.session_state.rag_initialized = False


def render_sidebar():
    """Render sidebar with PDF upload and info"""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        st.markdown("---")
        
        # PDF Upload section
        st.subheader("📄 Upload Documents")
        st.caption("Upload PDFs to enable RAG-based question answering")
        
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            key='pdf_uploader'
        )
        
        if uploaded_files:
            if st.button("🚀 Process PDFs", use_container_width=True):
                with st.spinner("Processing PDFs..."):
                    result = st.session_state.chat_logic.rag_pipeline.process_pdfs(uploaded_files)
                    
                    if result['success']:
                        st.success(f"✅ Processed {result['num_files']} files, created {result['num_chunks']} chunks!")
                        st.session_state.rag_initialized = True
                    else:
                        st.error(f"❌ Error: {result['error']}")
        
        if st.session_state.rag_initialized:
            if st.button("🗑️ Forget PDF Database", use_container_width=True, type="secondary"):
                if st.session_state.chat_logic.rag_pipeline.clear_database():
                    st.session_state.rag_initialized = False
                    st.success("PDF Database cleared!")
                    st.rerun()
                else:
                    st.error("Failed to clear PDF Database")
        
        st.markdown("---")
        
        # Admin / System Controls
        st.subheader("🛠️ System Controls")
        if st.button("🔄 Reset & Reload Config", use_container_width=True):
            # Reload configuration and modules
            importlib.reload(app.config)
            importlib.reload(db.database)
            importlib.reload(app.tools)
            importlib.reload(app.rag_pipeline)
            importlib.reload(app.chat_logic)
            importlib.reload(app.admin_dashboard)
            
            # Clear all session state to force re-initialization
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            st.success("Config reloaded! Initializing...")
            st.rerun()
        
        st.caption("Click above if you changed .env or want to refresh the models.")
        
        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.messages = st.session_state.messages[:1] # Keep only welcome message
            if 'chat_logic' in st.session_state:
                st.session_state.chat_logic.conversation_history = []
            st.rerun()
            
        st.markdown("---")
        
        # Information section
        st.subheader("ℹ️ Information")
        
        with st.expander("🏥 Medical Specialties"):
            st.markdown("**Available for Appointment:**")
            for booking_type in BOOKING_TYPES:
                st.markdown(f"• {booking_type}")
        
        with st.expander("📖 How to Book an Appointment"):
            st.markdown("""
**Step-by-step:**
1. Say "I want to book an appointment"
2. Provide patient details:
   - Patient's full name
   - Email address
   - Phone number (10 digits)
   - Medical specialty needed
   - Preferred date (YYYY-MM-DD)
   - Preferred time (HH:MM)
3. Review the appointment summary
4. Confirm with "Yes"
5. Receive confirmation email!

**Example:**
- "I need to see a cardiologist"
- "Book appointment for John Doe"
- "Schedule a checkup"
            """)
        
        with st.expander("🤖 Features"):
            st.markdown("""
- **Medical Appointments**: Book with hospital specialists
- **RAG Q&A**: Upload medical PDFs and ask questions
- **Smart Booking**: Natural conversation flow
- **Auto-extract**: Detects info from your messages
- **Email Alerts**: Appointment confirmation emails
- **Admin Panel**: View all appointments
- **Secure**: Patient data protected
            """)
        
        st.markdown("---")
        
        # Status indicators
        st.subheader("📊 Status")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.rag_initialized:
                st.success("RAG ✅")
            else:
                st.warning("RAG ⏳")
        
        with col2:
            if st.session_state.chat_logic.llm:
                st.success("LLM ✅")
            else:
                st.error("LLM ❌")


def render_chat_interface():
    """Render chat interface"""
    st.title("🏥 Amrita Hospital AI Assistant")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chat_logic.process_message(prompt)
                st.markdown(response)
        
        # Add assistant message to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Keep only last 25 messages + welcome message if needed
        # but let's just keep last 25 total for simplicity
        if len(st.session_state.messages) > 25:
            st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-24:]
        
        # Rerun to update chat
        st.rerun()


def main():
    """Main application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Create tabs
    tab1, tab2 = st.tabs(["💬 Chat", "📊 Admin Dashboard"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_admin_dashboard()


if __name__ == "__main__":
    main()
