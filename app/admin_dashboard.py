""" Admin Dashboard - View and manage bookings """
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import db.database
from app.config import DB_PATH, ADMIN_USERNAME, ADMIN_PASSWORD

def check_login():
    """Login form for admin access"""
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if not st.session_state.admin_logged_in:
        st.subheader("🔐 Admin Authentication")
        with st.form("login_form"):
            username = st.text_input("Username", key="admin_user")
            password = st.text_input("Password", type="password", key="admin_pass")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        return False
    return True

def filter_bookings(bookings, search_query, status_filter, date_filter=None):
    """Filter bookings based on search criteria"""
    if not search_query and not date_filter and (status_filter == "All" or status_filter is None):
        return bookings
    
    filtered = bookings
    
    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        filtered = [b for b in filtered if (
            search_lower in b['customer_name'].lower() or
            search_lower in b['customer_email'].lower() or
            search_lower in b['customer_phone'].lower()
        )]
    
    # Apply status filter
    if status_filter and status_filter != "All":
        filtered = [b for b in filtered if b['status'] == status_filter]
    
    # Apply date filter
    if date_filter:
        filtered = [b for b in filtered if b['date'] == date_filter]
    
    return filtered

def render_admin_dashboard():
    """Render the admin dashboard"""
    if not check_login():
        return
    
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("🏥 Amrita Hospital Admin Panel")
    with col2:
        if st.button("Logout", key="logout_btn"):
            st.session_state.admin_logged_in = False
            st.rerun()
    
    st.markdown("---")
    
    # Initialize database
    import importlib
    importlib.reload(db.database)
    db_conn = db.database.Database(str(DB_PATH))
    
    # Create tabs
    tab_bookings, tab_customers = st.tabs(["📋 Appointments", "👥 Patients"])
    
    with tab_bookings:
        # Stats section
        bookings = db_conn.get_all_bookings()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Appointments", len(bookings))
        with col2:
            pending = len([b for b in bookings if b['status'] == 'Pending'])
            st.metric("⏳ Pending", pending)
        with col3:
            confirmed = len([b for b in bookings if b['status'] == 'Confirmed'])
            st.metric("✅ Confirmed", confirmed)
        with col4:
            unique_patients = len(set(b['customer_email'] for b in bookings))
            st.metric("👥 Unique Patients", unique_patients)
        
        st.markdown("---")
        
        # Search and filter section
        st.subheader("🔍 Search & Filter")
        search_col1, search_col2, search_col3, search_col4 = st.columns([3, 2, 2, 1])
        
        with search_col1:
            search_query = st.text_input(
                "Search",
                placeholder="Name, email, or phone",
                key="search_input",
                label_visibility="collapsed"
            )
        
        with search_col2:
            status_filter = st.selectbox(
                "Status",
                options=["All", "Pending", "Confirmed", "Cancelled", "Completed"],
                key="status_filter",
                label_visibility="collapsed"
            )
        
        with search_col3:
            date_filter = st.date_input(
                "Date",
                value=None,
                key="date_filter",
                label_visibility="collapsed"
            )
        
        with search_col4:
            if st.button("🔄 Reset", key="reset_filters", use_container_width=True):
                st.session_state.search_input = ""
                st.session_state.date_filter = None
                st.session_state.status_filter = "All"
                st.rerun()
        
        # Apply filters
        date_filter_str = date_filter.strftime("%Y-%m-%d") if date_filter else None
        filtered_bookings = filter_bookings(bookings, search_query, status_filter, date_filter_str)
        
        st.markdown("---")
        
        # Bookings table with Inline Editing
        st.subheader("📋 Appointment Schedule")
        
        if filtered_bookings:
            st.caption(f"Showing {len(filtered_bookings)} of {len(bookings)} appointments")
            
            df_data = []
            for b in filtered_bookings:
                df_data.append({
                    'ID': b['id'],
                    'Patient': b['customer_name'],
                    'Email': b['customer_email'],
                    'Specialty': b['service_type'],
                    'Date': b['date'],
                    'Time': b['time'],
                    'Status': b['status'],
                    'Phone': b['customer_phone']
                })
            
            df = pd.DataFrame(df_data)
            
            edited_df = st.data_editor(
                df,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        help="Update appointment status",
                        width="medium",
                        options=[
                            "Pending",
                            "Confirmed",
                            "Cancelled",
                            "Completed",
                        ],
                        required=True,
                    ),
                    "ID": st.column_config.NumberColumn(width="small"),
                    "Patient": st.column_config.TextColumn(width="medium"),
                    "Email": st.column_config.TextColumn(width="medium"),
                    "Specialty": st.column_config.TextColumn(width="medium"),
                    "Date": st.column_config.TextColumn(width="small"),
                    "Time": st.column_config.TextColumn(width="small"),
                    "Phone": st.column_config.TextColumn(width="medium"),
                },
                disabled=["ID", "Patient", "Email", "Specialty", "Date", "Time", "Phone"],
                hide_index=True,
                use_container_width=True,
                key="bookings_editor"
            )
            
            # Detect and handle changes
            if not df.equals(edited_df):
                for index, row in edited_df.iterrows():
                    original_status = df.iloc[index]['Status']
                    current_status = row['Status']
                    
                    if current_status != original_status:
                        booking_id = row['ID']
                        if db_conn.update_booking_status(booking_id, current_status):
                            st.toast(f"✅ Updated Appointment #{booking_id} to {current_status}")
                            import time
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"Failed to update status for #{booking_id}")
        else:
            st.info("No appointments found matching your search criteria.")
    
    with tab_customers:
        st.subheader("👥 Patient Database")
        
        # Search bar for patients
        patient_search = st.text_input(
            "Search patients by name or email",
            placeholder="e.g., Jane Smith or jane@example.com",
            key="patient_search"
        )
        
        patients = db_conn.get_all_customers()
        
        if patients:
            # Filter patients
            if patient_search:
                search_lower = patient_search.lower()
                patients = [p for p in patients if (
                    search_lower in p.get('name', '').lower() or
                    search_lower in p.get('email', '').lower()
                )]
            
            if patients:
                df_patients = pd.DataFrame(patients)
                st.caption(f"Found {len(patients)} patient(s)")
                st.dataframe(df_patients, use_container_width=True, hide_index=True)
            else:
                st.info("No patients found matching your search.")
        else:
            st.info("No patients found in database.")
    
    # Footer
    st.markdown("---")
    st.caption(f"System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    render_admin_dashboard()