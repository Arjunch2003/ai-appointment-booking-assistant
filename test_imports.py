"""
Simple test of imports
"""

print("Testing imports...")

try:
    print("1. Importing streamlit...")
    import streamlit as st
    print("   ✅ streamlit OK")
except Exception as e:
    print(f"   ❌ streamlit FAILED: {e}")

try:
    print("2. Importing config...")
    from app.config import APP_NAME
    print(f"   ✅ config OK - App name: {APP_NAME}")
except Exception as e:
    print(f"   ❌ config FAILED: {e}")

try:
    print("3. Importing database...")
    from db.database import Database
    print("   ✅ database OK")
except Exception as e:
    print(f"   ❌ database FAILED: {e}")

try:
    print("4. Importing booking_flow...")
    from app.booking_flow import BookingFlow
    print("   ✅ booking_flow OK")
except Exception as e:
    print(f"   ❌ booking_flow FAILED: {e}")

try:
    print("5. Importing tools...")
    from app.tools import BookingTool, EmailTool
    print("   ✅ tools OK")
except Exception as e:
    print(f"   ❌ tools FAILED: {e}")

try:
    print("6. Importing rag_pipeline...")
    from app.rag_pipeline import RAGPipeline
    print("   ✅ rag_pipeline OK")
except Exception as e:
    print(f"   ❌ rag_pipeline FAILED: {e}")

try:
    print("7. Importing chat_logic...")
    from app.chat_logic import ChatLogic
    print("   ✅ chat_logic OK")
except Exception as e:
    print(f"   ❌ chat_logic FAILED: {e}")

try:
    print("8. Importing admin_dashboard...")
    from app.admin_dashboard import render_admin_dashboard
    print("   ✅ admin_dashboard OK")
except Exception as e:
    print(f"   ❌ admin_dashboard FAILED: {e}")

print("\n" + "="*50)
print("Testing RAG Pipeline initialization...")
print("="*50)

try:
    from app.rag_pipeline import RAGPipeline
    rag = RAGPipeline()
    print("RAGPipeline instance created")
    result = rag.initialize()
    print(f"RAG initialization result: {result}")
except Exception as e:
    print(f"❌ RAG initialization FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\nAll import tests complete!")
