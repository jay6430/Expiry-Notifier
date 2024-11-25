import streamlit as st
import pandas as pd
from pymongo import MongoClient, errors
from datetime import datetime, timedelta
from PIL import Image
import numpy as np
import cv2
from pyzbar.pyzbar import decode

# MongoDB setup gRXKF2x1S0GjL4zg
MONGO_URI = "mongodb+srv://kadamjay100:gRXKF2x1S0GjL4zg@cluster0.288bi.mongodb.net/myDatabase?retryWrites=true&w=majority&appName=Cluster0"
# Replace with your actual MongoDB connection string
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["expiry_notifier"]
    collection = db["products"]
    client.server_info()  # Test connection
except errors.ServerSelectionTimeoutError as e:
    st.error(f"Could not connect to MongoDB: {e}")
    st.stop()

# MongoDB helper functions
def load_database():
    """Load all records from MongoDB."""
    try:
        records = list(collection.find({}, {"_id": 1, "EAN_No": 1, "product_name": 1, "expiry_date": 1, "timestamp": 1}))
        for record in records:
            record["_id"] = str(record["_id"])  # Convert ObjectId to string
        return records
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return []

def add_record(data):
    """Insert a new record into MongoDB."""
    try:
        collection.insert_one(data)
    except Exception as e:
        st.error(f"Error adding record: {e}")

def update_record(record_id, updated_data):
    """Update a specific record in MongoDB."""
    try:
        collection.update_one({"_id": record_id}, {"$set": updated_data})
    except Exception as e:
        st.error(f"Error updating record: {e}")

def delete_record(record_id):
    """Delete a specific record from MongoDB."""
    try:
        collection.delete_one({"_id": record_id})
    except Exception as e:
        st.error(f"Error deleting record: {e}")

def delete_all_records():
    """Delete all records from MongoDB."""
    try:
        collection.delete_many({})
    except Exception as e:
        st.error(f"Error deleting all records: {e}")

def scan_barcode(image):
    """Scan barcode from an image."""
    barcodes = decode(image)
    for barcode in barcodes:
        return barcode.data.decode("utf-8")
    return None

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Add Product"

# Sidebar navigation
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
        camera_image = st.camera_input("Scan a barcode using your camera")
        scanned_ean = None
        if camera_image:
            image = Image.open(camera_image)
            open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            scanned_ean = scan_barcode(open_cv_image)
            if scanned_ean:
                st.success(f"Scanned EAN: {scanned_ean}")
            else:
                st.error("EAN not detected, enter it manually.")
        
        ean_no = st.text_input("Product EAN Number", value=scanned_ean if scanned_ean else "")
        product_name = st.text_input("Product Name")
        expiry_date = st.date_input("Expiry Date")
        submit = st.form_submit_button("Add Product")

        if submit:
            if ean_no and product_name:
                new_entry = {
                    "EAN_No": ean_no,
                    "product_name": product_name,
                    "expiry_date": pd.to_datetime(expiry_date),
                    "timestamp": datetime.now(),
                }
                add_record(new_entry)
                st.success("Product added successfully!")
            else:
                st.error("Please fill in all fields.")

elif st.session_state.page == "View Database":
    st.title("Product Database")
    data = load_database()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)

        st.subheader("Edit or Delete Records")
        record_id = st.selectbox("Select Record to Edit/Delete", options=[r["_id"] for r in data])

        if st.button("Delete Record"):
            delete_record(record_id)
            st.success("Record deleted successfully!")
            st.query_params(page="view")  # Trigger app rerun

        if st.checkbox("Delete All Records"):
            if st.button("Confirm Deletion"):
                delete_all_records()
                st.success("All records deleted successfully!")
                st.query_params(page="view")  # Trigger app rerun

        st.subheader("Edit Selected Record")
        selected_record = next((r for r in data if r["_id"] == record_id), None)
        if selected_record:
            new_ean_no = st.text_input("Product EAN Number", value=selected_record["EAN_No"])
            new_product_name = st.text_input("Product Name", value=selected_record["product_name"])
            new_expiry_date = st.date_input("Expiry Date", value=pd.to_datetime(selected_record["expiry_date"]))

            if st.button("Update Record"):
                update_record(record_id, {
                    "EAN_No": new_ean_no,
                    "product_name": new_product_name,
                    "expiry_date": pd.to_datetime(new_expiry_date),
                })
                st.success("Record updated successfully!")
                st.query_params(page="view")  # Trigger app rerun

    else:
        st.info("No records found.")
