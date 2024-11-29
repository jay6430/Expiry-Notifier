import streamlit as st
import pandas as pd
from pymongo import MongoClient, errors
from datetime import datetime
import streamlit.components.v1 as components

# MongoDB setup
MONGO_URI = "mongodb+srv://kadamjay100:gRXKF2x1S0GjL4zg@cluster0.288bi.mongodb.net/myDatabase?retryWrites=true&w=majority&appName=Cluster0"
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

# Initialize session state
if "scanned_ean" not in st.session_state:
    st.session_state.scanned_ean = ""

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
if "page" not in st.session_state:
    st.session_state.page = "Add Product"

if st.session_state.page == "Add Product":
    st.title("U2RZ - Article Submission")

    # JavaScript QR Code Scanner with improved styling and behavior
    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html5-qrcode/2.3.8/html5-qrcode.min.js"></script>
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #333; color: #f5f5f5;">
            <h1>Scan EAN Barcode</h1>
            <div style="display: flex; justify-content: center; margin-top: 20px;">
                <!-- Reader container with styled border -->
                <div id="reader" style="
                    width: 500px; 
                    height: 450px;
                    border: 5px solid white; 
                    border-radius: 10px; 
                    position: relative; 
                    background: black;">
                </div>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <h4>Scan Result</h4>
                <div id="result" style="
                    padding: 15px; 
                    border: 2px solid #ccc; 
                    border-radius: 5px; 
                    background-color: #f5f5f5; 
                    color: #333; 
                    font-size: 18px; 
                    word-wrap: break-word; 
                    display: inline-block;">Result goes here</div>
                <button id="copyEANButton" onclick="copyEAN()" style="
                    padding: 10px 20px; 
                    margin-top: 10px; 
                    font-size: 16px; 
                    background-color: #4CAF50; 
                    color: white; 
                    border: none; 
                    border-radius: 5px; 
                    cursor: pointer;">Copy EAN</button>
                <div id="copyMessage" style="
                    margin-top: 10px; 
                    font-size: 14px; 
                    color: #4CAF50; 
                    display: none;">EAN copied to clipboard!</div>
            </div>
            <script>
                function onScanSuccess(qrCodeMessage) {
                    // Change border to green on success
                    const readerElement = document.getElementById("reader");
                    readerElement.style.border = "5px solid green";
                    
                    // Update the scan result
                    document.getElementById("result").innerHTML =
                        '<span>' + qrCodeMessage + "</span>";
                }

                function onScanError(errorMessage) {
                    console.warn("Scan error:", errorMessage);
                }

                // Render the QR code scanner with customized box
                const html5QrCodeScanner = new Html5QrcodeScanner("reader", {
                    fps: 10,
                    qrbox: { width: 250, height: 200 }
                });
                html5QrCodeScanner.render(onScanSuccess, onScanError);

                function copyEAN() {
                    const ean = document.getElementById("result").innerText;
                    const copyMessage = document.getElementById("copyMessage");
                    if (ean) {
                        navigator.clipboard.writeText(ean).then(function() {
                            // Show success message
                            copyMessage.style.display = "block";
                            setTimeout(() => { copyMessage.style.display = "none"; }, 2000);
                        }).catch(function(error) {
                            copyMessage.style.color = "red";
                            copyMessage.innerText = "Failed to copy EAN!";
                            copyMessage.style.display = "block";
                            setTimeout(() => { copyMessage.style.display = "none"; }, 2000);
                        });
                    }
                }
            </script>
        </body>
        </html>
        """,
        height=730,
    )

    # Form to add product
    with st.form("add_product_form", clear_on_submit=True):
        ean_no = st.text_input(
            "Product EAN Number",
            value=st.session_state.scanned_ean,
            key="scanned_ean_field",
            placeholder="Enter or scan EAN"
        )
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
                st.session_state.scanned_ean = ""  # Reset after submission
            else:
                st.error("Please fill in all fields.")

elif st.session_state.page == "View Database":
    st.title("Product Database")
    data = load_database()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info("No records found.")
