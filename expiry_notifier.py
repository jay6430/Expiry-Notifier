import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
import numpy as np



import subprocess
import sys

def install_package(package_name):
    """Helper function to run system commands to install a package."""
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", package_name], check=True)
        print(f"Successfully installed {package_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}. Error: {e}")
        sys.exit(1)  # Exit the script if installation fails

# OpenCV import and dependency handling
try:
    import cv2
except ImportError as e:
    print(f"Error importing OpenCV: {e}")
    print("Attempting to install the required package 'libgl1-mesa-glx'...")
    install_package("libgl1-mesa-glx")
    # Retry the import
    try:
        import cv2
        print("Successfully imported OpenCV after installing dependencies.")
    except ImportError:
        print("Failed to import OpenCV even after installing dependencies. Exiting.")
        sys.exit(1)

# Pyzbar import and dependency handling
try:
    from pyzbar.pyzbar import decode
except ImportError as e:
    print(f"Error importing pyzbar: {e}")
    print("Attempting to install the required package 'libzbar0'...")
    install_package("libzbar0")
    # Retry the import
    try:
        from pyzbar.pyzbar import decode
        print("Successfully imported pyzbar after installing dependencies.")
    except ImportError:
        print("Failed to import pyzbar even after installing dependencies. Exiting.")
        sys.exit(1)



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

def scan_barcode(image):
    """Decodes barcodes from an uploaded image."""
    decoded_objects = decode(image)
    if decoded_objects:
        # Return the first detected barcode's data
        return decoded_objects[0].data.decode('utf-8')
    return None

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
    
    # Start form context
    with st.form("add_product_form", clear_on_submit=True):
        # Camera input for mobile or desktop
        camera_image = st.camera_input(
            "Scan a barcode using your mobile or laptop camera (choose back camera on mobile)"
        )

        # Initialize EAN number
        scanned_ean = None

        if camera_image:
            # Process the captured image
            image = Image.open(camera_image)
            open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            scanned_ean = scan_barcode(open_cv_image)
            if scanned_ean:
                st.success(f"Scanned EAN: {scanned_ean}")
            else:
                st.error("No valid barcode detected. Please try again.")
        
        # EAN Input Field
        ean_no = st.text_input("Product EAN Number", value=scanned_ean if scanned_ean else "", placeholder="Enter or edit EAN Number manually")
        product_name = st.text_input("Product Name", placeholder="Enter Product Name")
        expiry_date = st.date_input("Expiry Date")
        
        # Submit button inside form context
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
