import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize or load the database
DB_FILE = "product_database.csv"

def load_database():
    try:
        db = pd.read_csv(DB_FILE)
        db["expiry_date"] = pd.to_datetime(db["expiry_date"])
        db["timestamp"] = pd.to_datetime(db["timestamp"])
        return db
    except FileNotFoundError:
        return pd.DataFrame(columns=["EAN_No", "product_name", "expiry_date", "timestamp"])

def save_database(data):
    data.to_csv(DB_FILE, index=False)

# Load data
database = load_database()

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Add Product"

# Sidebar navigation with tiles
st.sidebar.markdown("<h2 style='text-align: center;'>Navigation</h2>", unsafe_allow_html=True)
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("➕ Add Product"):
        st.session_state.page = "Add Product"
with col2:
    if st.button("📋 View Database"):
        st.session_state.page = "View Database"

# Main App Logic
if st.session_state.page == "Add Product":
    st.title("Add New Product")
    with st.form("add_product_form", clear_on_submit=True):
        ean_no = st.text_input("Product EAN Number", placeholder="Enter EAN Number")
        product_name = st.text_input("Product Name", placeholder="Enter Product Name")
        expiry_date = st.date_input("Expiry Date")
        submit = st.form_submit_button("Add Product")
        
        if submit:
            if ean_no and product_name:
                timestamp = datetime.now()
                new_entry = pd.DataFrame({
                    "EAN_No": [ean_no],
                    "product_name": [product_name],
                    "expiry_date": [pd.to_datetime(expiry_date)],
                    "timestamp": [timestamp]
                })
                database = pd.concat([database, new_entry], ignore_index=True)
                save_database(database)
                st.success("Product added successfully!")
            else:
                st.error("Please fill in all fields.")

elif st.session_state.page == "View Database":
    st.title("Product Database")
    
    # Display options for sorting
    sort_expiring = st.checkbox("Sort by Soonest Expiry", key="sort_checkbox")
    
    if sort_expiring:
        # Sort by expiry date
        sorted_db = database.sort_values(by="expiry_date", ascending=True)
        st.dataframe(sorted_db)
    else:
        # Display in original order
        st.dataframe(database)

    # Notification for expiring products
    st.subheader("Expiring Soon")
    current_date = datetime.now()
    expiring_soon = database[
        (database["expiry_date"] >= current_date) &
        (database["expiry_date"] <= current_date + timedelta(days=5))
    ]
    
    if not expiring_soon.empty:
        for _, row in expiring_soon.iterrows():
            st.warning(f"Product '{row['product_name']}' (EAN: {row['EAN_No']}) is expiring on {row['expiry_date'].date()}!")
    else:
        st.info("No products are expiring soon.")
