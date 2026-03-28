import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.database import get_all_bookings, get_booking_stats, update_booking_status

def admin_page():
    st.markdown("""
    <div style='padding: 2rem 0 1rem 0;'>
        <h1 style='font-family: Cormorant Garamond, serif; font-size: 2.8rem; font-weight: 300; color: #2C2C2C; margin: 0;'>Admin Dashboard</h1>
        <p style='color: #8A7F7A; font-size: 0.9rem; margin-top: 0.5rem;'>View and manage all bookings</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    stats = get_booking_stats()
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in [
        (c1, "Total Bookings", stats["total"]),
        (c2, "Confirmed",      stats["confirmed"]),
        (c3, "Customers",      stats["customers"]),
        (c4, "Today",          stats["today"]),
    ]:
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='number'>{val}</div>
                <div class='label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # Filters
    with st.expander("🔍 Filter Bookings", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            search_name  = st.text_input("Search by name")
        with fc2:
            search_email = st.text_input("Search by email")
        with fc3:
            search_date  = st.text_input("Filter by date (YYYY-MM-DD)")

    rows = get_all_bookings()
    columns = ["Booking ID", "Name", "Email", "Phone", "Service", "Date", "Time", "Status", "Created At"]
    df = pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)

    # Apply filters
    if search_name:
        df = df[df["Name"].str.contains(search_name, case=False, na=False)]
    if search_email:
        df = df[df["Email"].str.contains(search_email, case=False, na=False)]
    if search_date:
        df = df[df["Date"] == search_date]

    if df.empty:
        st.info("No bookings found.")
    else:
        st.markdown(f"**{len(df)} booking(s) found**")

        # Status colour
        def highlight_status(val):
            colors = {"confirmed": "#D4EDDA", "cancelled": "#F8D7DA", "pending": "#FFF3CD"}
            return f"background-color: {colors.get(val, 'white')};"

        styled = df.style.applymap(highlight_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # Export
        csv = df.to_csv(index=False)
        st.download_button("⬇ Export CSV", csv, "bookings.csv", "text/csv", use_container_width=False)

        st.markdown("---")
        st.markdown("**Update Booking Status**")
        uc1, uc2, uc3 = st.columns([2, 2, 1])
        with uc1:
            booking_id_input = st.text_input("Booking ID (e.g. GLW-ABC123)")
        with uc2:
            new_status = st.selectbox("New Status", ["confirmed", "cancelled", "pending"])
        with uc3:
            st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)
            if st.button("Update", use_container_width=True):
                if booking_id_input:
                    update_booking_status(booking_id_input.strip(), new_status)
                    st.success(f"Updated {booking_id_input} → {new_status}")
                    st.rerun()
                else:
                    st.warning("Enter a Booking ID.")
