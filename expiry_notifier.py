import streamlit as st
import pandas as pd
from pymongo import MongoClient, errors
from datetime import datetime
import streamlit.components.v1 as components

# MongoDB setup
MONGO_URI = "mongodb+srv://kadamjay100:gRXKF2x1S0GjL4zg@cluster0.288bi.mongodb.net/myDatabase?retryWrites=true&w=majority&appName=Cluster0"
#mongodb+srv://kadamjay100:<db_password>@cluster0.288bi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
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
        records = list(collection.find({}, {"_id": 0}))  # Include all fields
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

# Load CSV data
@st.cache_data
def load_csv(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error("CSV file not found. Please check the path.")
        return pd.DataFrame()

inventory_df = load_csv("data/U2RZ_inventory_csv.csv")

# Initialize session state
if "product_details" not in st.session_state:
    st.session_state.product_details = {
        "product_name": "",
        "article_num": "",
        "segment": "",
        "family": "",
        "prod_class": "",
    }

# Sidebar navigation
st.sidebar.markdown("<h2 style='text-align: center;'>Navigation</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    if st.button("➕ Add Product"):
        st.session_state.page = "Add Product"
with col2:
    if st.button("📋 View Database"):
        st.session_state.page = "View Database"
with col3:
    if st.button("✏️ Modify Database"):
        st.session_state.page = "Modify Database"

# Main App Logic
if "page" not in st.session_state:
    st.session_state.page = "Add Product"

if st.session_state.page == "Add Product":
    st.title("U2RZ - Article Submission")

    # JavaScript QR Code Scanner
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

    # Ensure EAN column is treated as a string and remove `.0` suffix if present
    inventory_df["EAN"] = inventory_df["EAN"].fillna("").astype(str)
    inventory_df["EAN"] = inventory_df["EAN"].str.rstrip(".0")  # Remove `.0` suffix from EANs
    inventory_df["Article_num"] = inventory_df["Article_num"].fillna("").astype(str)
    inventory_df["Article_num"] = inventory_df["Article_num"].str.rstrip(".0")

    # Input EAN and Fetch Details button
    ean_no = st.text_input("Product EAN Number", key="scanned_ean_field", placeholder="Enter or scan EAN")


    # Fetch matching details when button is clicked
    if st.button("Fetch Details"):
        if not ean_no:
            st.warning("Please enter or scan a valid EAN number.")
        else:
            matching_row = inventory_df[inventory_df["EAN"] == ean_no]
            st.write("Matching Rows:", matching_row)  # Debug log for matching rows

            if not matching_row.empty:
                # Populate session state with details
                st.session_state.product_details["product_name"] = matching_row.iloc[0]["Material_description"]
                st.session_state.product_details["article_num"] = matching_row.iloc[0]["Article_num"]
                st.session_state.product_details["segment"] = matching_row.iloc[0]["Segment"]
                st.session_state.product_details["family"] = matching_row.iloc[0]["Family"]
                st.session_state.product_details["prod_class"] = matching_row.iloc[0]["Class"]
                st.success("Details fetched successfully!")
            else:
                # Clear session state and warn user
                st.session_state.product_details = {key: "" for key in st.session_state.product_details}
                st.warning("Details not found in the inventory.")




    # Form for submitting product details
    with st.form("add_product_form", clear_on_submit=True):
        product_name = st.text_input(
            "Product Name", value=st.session_state.product_details["product_name"], key="product_name", placeholder="Mandatory, Enter if not fetched!"
        )
        article_num = st.text_input(
            "Article Number", value=st.session_state.product_details["article_num"], key="article_num", placeholder="optional"
        )
        segment = st.text_input(
            "Segment", value=st.session_state.product_details["segment"], key="segment", placeholder="optional"
        )
        family = st.text_input(
            "Family", value=st.session_state.product_details["family"], key="family", placeholder="optional"
        )
        prod_class = st.text_input(
            "Class", value=st.session_state.product_details["prod_class"], key="prod_class", placeholder="optional"
        )
        expiry_date = st.date_input("Expiry Date", key="expiry_date")

        submit = st.form_submit_button("Add Product")

        if submit:
            if ean_no and product_name and expiry_date:
                new_entry = {
                    "EAN_No": ean_no,
                    "product_name": product_name,
                    "article_number": article_num or None,
                    "segment": segment or None,
                    "family": family or None,
                    "class": prod_class or None,
                    "expiry_date": expiry_date.strftime("%d/%m/%Y"),
                    "timestamp": datetime.now(),
                }
                add_record(new_entry)
                st.success("Product added successfully!")
            else:
                st.error("Please fill in all required fields (EAN, Product Name, and Expiry Date).")






if st.session_state.page == "Modify Database":
    st.title("Modify Database")

    # Ask user for the operation
    operation = st.radio("Which operation would you like to perform?", 
                          options=["Update Record", "Delete Record"], 
                          key="operation_choice")

    # EAN field for searching
    ean_value = st.text_input("Enter EAN to search:").strip()

    if ean_value:
        # Fetch matching records from the database
        query = {"EAN_No": str(ean_value)}  # Convert EAN to string to match MongoDB format
        records = list(collection.find(query, {"_id": 0}))

        if records:
            df = pd.DataFrame(records)
            st.dataframe(df)

            if operation == "Update Record":
                # Select a single record for updating
                record_to_update = st.selectbox(
                    "Select a record to update", 
                    options=records, 
                    format_func=lambda x: f"EAN: {x['EAN_No']}, Name: {x['product_name']}"
                )

                if record_to_update:
                    # Show editable fields
                    updated_record = {
                        "EAN_No": st.text_input("EAN", value=record_to_update["EAN_No"]),
                        "product_name": st.text_input("Product Name", value=record_to_update["product_name"]),
                        "article_number": st.text_input("Article Number", value=record_to_update.get("article_number", "")),
                        "segment": st.text_input("Segment", value=record_to_update.get("segment", "")),
                        "family": st.text_input("Family", value=record_to_update.get("family", "")),
                        "class": st.text_input("Class", value=record_to_update.get("class", "")),
                        "expiry_date": st.text_input("Expiry Date", value=record_to_update["expiry_date"])
                    }

                    # Confirm and update record
                    if st.button("Modify Record"):
                        try:
                            collection.update_one(
                                {"EAN_No": record_to_update["EAN_No"]},
                                {"$set": updated_record}
                            )
                            st.success("Record updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating record: {e}")

            elif operation == "Delete Record":
                # Allow user to select multiple records to delete
                records_to_delete = st.multiselect(
                    "Select records to delete", 
                    options=records, 
                    format_func=lambda x: f"EAN: {x['EAN_No']}, Name: {x['product_name']}"
                )

                if records_to_delete:
                    if st.button("Delete Selected Record(s)"):
                        try:
                            delete_query = {"$or": [{"EAN_No": rec["EAN_No"]} for rec in records_to_delete]}
                            collection.delete_many(delete_query)
                            st.success("Selected records deleted successfully!")
                        except Exception as e:
                            st.error(f"Error deleting records: {e}")
        else:
            st.warning(f"No records found for EAN: {ean_value}")
    else:
        st.info("Enter an EAN to search.")









if st.session_state.page == "View Database":
    st.title("Product Database")
    
    # Load data from MongoDB
    data = load_database()
    if data:
        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Display DataFrame in Streamlit
        st.dataframe(df)
    else:
        st.info("No records found.")
