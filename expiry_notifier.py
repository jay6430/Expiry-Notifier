import streamlit as st
import pandas as pd
from pymongo import MongoClient, errors
from datetime import datetime
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


# MongoDB setup
MONGO_URI = "mongodb+srv://kadamjay100:gRXKF2x1S0GjL4zg@cluster0.288bi.mongodb.net/myDatabase?retryWrites=true&w=majority&appName=Cluster0"
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["expiry_notifier"]
    inventory_collection = db["Inventory"]  # For fetching EAN details
    products_collection = db["Products"]  # For storing, modifying, and viewing products
    product_count_collection = db["Product_count"]  # New collection for product count data

    client.server_info()  # Test connection
except errors.ServerSelectionTimeoutError as e:
    st.error(f"Could not connect to MongoDB: {e}")
    st.stop()



# Unique options for segment, family, and prod_class
unique_segments = [
    'PROCESSED FOOD', 'FRAGRANCES', 'CONFECTIONARY & SNACKS', 'FURNISHINGS & DECOR', 
    'STAPLES', 'AUTO ACCESSORIES', 'PERSONAL CARE', 'STATIONERY', 'BABY CARE', 
    'HOME CARE', 'HEALTH', 'GM FMCG', 'BEVERAGES', 'FROZEN VEG. / SNACKS', 'DAIRY', 
    'HOUSEWARE', 'TOYS', 'CONSUMABLES', 'FRESH FRUITS & VEGETABLES', 'FURNITURE', 
    'GIFT SOLUTIONS', 'COSMETICS', 'BEAUTY', '3902', 'LUGGAGE', 
    'CONCESSIONAIRE SERVICES', 'SPORTING GOODS & FITNESS EQUIPMENTS', 'Devices', 
    'SERVICES', 'HARDLINES'
]
unique_families = [
    'BISCUITS & BRANDED BAKERY', 'MASS MENS FRAGRANCE', 'CONFECTIONERY', 'FURNISHINGS', 
    'SPICES & CONDIMENTS', 'TWO WHEELER', 'SKIN PRODUCTS', 'WRITING INSTRUMENTS & ACCESSORIES', 
    'READY TO EAT', 'BABY HYGN', 'FLOURS', 'READY TO COOK', 'PULSES', 'HOUSEHOLD NEEDS', 
    'OTC', 'Pooja Needs', 'RICE', 'PAPER PRODUCTS', 'FABRIC CARE', 'SNACKS', 'HAIR PRODUCTS', 
    'TEA & COFFEE', 'OFFICE CONSUMABLES & STATIONERY', "P'SONAL HYGN", 'Hardlines', 'SKIN CARE', 
    'FROZEN SNACKS', 'Disposable Goods', 'DAIRY - STAPLE', 'DRY FRUITS', 'INSECT CONTROL', 
    'HOUSEHOLD CLEANING', 'DRINKS', 'Home Essential', 'Kitchen Storage', 'SCHOOL & ART PRODUCTS', 
    'TABLEWARE', 'PERSONAL WASH', 'JUICES', "H'HOLD CLNG/CARENG/CARE", 'COOKWARE', 'VEHICLES & ACCESSORIES', 
    'EDIBLE OILS', 'AYURVEDIC', 'HEALTH DRINKS', 'BRANDED BAKERY FRESH BAKERY', 
    'FRESH MILK PRODUCTS', 'SALT', 'Bottle and lunch box', 'OTHER TOYS', 'DC / STORE CONSUMABLES', 
    'FRESH FRUITS', 'HOME DÉCOR', 'PERSONAL HYGIENE', 'DAIRY - CHILLED', 
    'FROZEN FRUITS & VEGETABLES', 'Deo', 'GIFTS'
]
unique_classes = [
    'BISCUITS', 'BODY SPRAYS', 'CONFECTIONERY', 'TABLE & KITCHEN', 'BLENDED SPICES', 
    'POWDER SPICES', 'SPICES HING', 'SAFETY', 'SKIN CARE', 'PENS & ACCESSORIES', 
    'JAMS & SPREADS', 'BABY HYGN/GROOMING', 'FLOURS', 'BODY WASHING', 'NOODLES & PASTA', 
    'PULSES', 'AIR FRESHNERS', 'SKIN/SCALP TREATMENT PRODUCTS', 'Incense & Dhoop', 
    'SAUCES', 'RICE', 'GASTROINTESTINAL REMEDY PRODUCTS', 'WHOLE SPICES', 'NOTE BOOKS', 
    'LAUNDRY DETERGENTS', 'SNACKS', 'DESSERTS & MIXES', 'HAIR CARE', 'TEA', 
    'FOLDERS & ACCESSORIES', 'ORAL HYGN', 'Bonding & Sealing', 'FACE CARE', 'BAKERY BASED', 
    'BREAKFAST CEREALS', 'Face Tissues', 'GHEE', 'DRY FRUITS', 'INSECT CONTROL PRODUCTS', 
    'FEM HYGN', 'HEALTH SUPPLEMENTS', 'SURFACE CLEANING', 'CARBONATED SOFT DRINKS'
]

html_component="""
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
                    display: inline-block;">---   EAN   ---</div>
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
        """


# MongoDB helper functions
def load_products():
    """Load all product records from the Products collection."""
    try:
        records = list(products_collection.find({}, {"_id": 0}))  # Exclude MongoDB ID
        return records
    except Exception as e:
        st.error(f"Error loading products: {e}")
        return []


def add_product(data, collection):
    """Insert a new product record into the specified collection."""
    try:
        collection.insert_one(data)
    except Exception as e:
        st.error(f"Error adding product: {e}")


def fetch_inventory_details(ean):
    """Fetch details from the Inventory collection based on EAN."""
    try:
        return inventory_collection.find_one({"EAN": ean}, {"_id": 0})
    except Exception as e:
        st.error(f"Error fetching inventory details: {e}")
        return None


# Function to get unique segments or families from the Products collection
def get_unique_values(field):
    try:
        values = sorted({rec.get(field, "") for rec in products_collection.find({}, {field: 1})})
        return values
    except Exception as e:
        st.error(f"Error fetching unique {field}s: {e}")
        return []


# Function to fetch the inventory data for the selected segment or family
def fetch_inventory_for_value(field, value):
    try:
        query = {field: value}
        return list(inventory_collection.find(query, {"EAN": 1, "Material_description": 1, "_id": 0}))
    except Exception as e:
        st.error(f"Error fetching inventory for {field} '{value}': {e}")
        return []


# Function to fetch the products data for the selected segment or family
def fetch_products_for_value(field, value):
    try:
        query = {field: value}
        return list(products_collection.find(query, {"EAN_No": 1, "product_name": 1, "_id": 0}))
    except Exception as e:
        st.error(f"Error fetching products for {field} '{value}': {e}")
        return []







# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Add Product"
if "product_details" not in st.session_state:
    st.session_state.product_details = {
        "product_name": "",
        "article_num": "",
        "segment": "",
        "family": "",
        "prod_class": "",
    }

# Professional Sidebar Navigation
st.sidebar.title("Expiry Notifier")
st.sidebar.caption("Manage your inventory with ease.")

# Use page_link to create navigation
pages = {
    "Add Product": "➕ Add Product",
    "View Database": "📋 View Database",
    "Modify Database": "✏️ Modify Database",
    "Expiry Notifier Dashboard" : "Expiry Notifier Dashboard",
}

selected_page = st.sidebar.radio(
    "Navigation",
    list(pages.values()),
    index=list(pages.keys()).index(st.session_state.page),
    key="sidebar_navigation"
)

# Map selection back to session state
st.session_state.page = list(pages.keys())[list(pages.values()).index(selected_page)]






# Add product App Logic
if st.session_state.page == "Add Product":
    st.title("Add Product")

    # Tab layout for "Add Product for expiry" and "Add Product for count"
    tab1, tab2 = st.tabs(["Add Product for Expiry", "Add Product for Count"])

    with tab1:
        st.subheader("Add Product for Expiry")

        # JavaScript QR Code Scanner
        components.html(
            html_component,
            height=730,
        )

        # Input EAN
        ean_no = st.text_input("Product EAN Number", key="scanned_ean_field_tab2", placeholder="Enter or scan EAN")
        if st.button("Fetch Details_tab1"):
            if ean_no:
                details = fetch_inventory_details(ean_no)
                if details:
                    # Populate session state
                    st.session_state.product_details.update({
                        "product_name": details.get("Material_description", ""),
                        "article_num": details.get("Article_num", ""),
                        "segment": details.get("Segment", ""),
                        "family": details.get("Family", ""),
                        "prod_class": details.get("Class", ""),
                    })
                    st.success("Details fetched successfully!")
                else:
                    st.warning("Details not found in the inventory.")
            else:
                st.warning("Please enter a valid EAN number.")


        # Form for submitting product details
        with st.form("add_product_form", clear_on_submit=True):
            product_name = st.text_input(
                "Product Name", 
                value=st.session_state.product_details.get("product_name", ""), 
                placeholder="Mandatory"
            )
            article_num = st.text_input(
                "Article Number", 
                value=st.session_state.product_details.get("article_num", ""), 
                placeholder="Optional"
            )
            segment = st.selectbox(
                "Segment", 
                options=[st.session_state.product_details.get("segment", "")] + unique_segments
            )
            family = st.selectbox(
                "Family", 
                options=[st.session_state.product_details.get("family", "")] + unique_families
            )
            prod_class = st.selectbox(
                "Class", 
                options=[st.session_state.product_details.get("prod_class", "")] + unique_classes
            )
            expiry_date = st.date_input("Expiry Date")

            if st.form_submit_button("Add Product"):
                if product_name and expiry_date:
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
                    add_product(new_entry, products_collection)
                    st.success("Product added successfully!")
                else:
                    st.error("Please fill in all mandatory fields.")

    with tab2:
        st.subheader("Add Product for Count")

        # JavaScript QR Code Scanner
        components.html(
            html_component,
            height=730,
        )

        # Input EAN
        ean_no = st.text_input("Product EAN Number", key="scanned_ean_field_tab1", placeholder="Enter or scan EAN")
        if st.button("Fetch Details_tab2"):
            if ean_no:
                details = fetch_inventory_details(ean_no)
                if details:
                    # Populate session state
                    st.session_state.product_details.update({
                        "product_name": details.get("Material_description", ""),
                        "article_num": details.get("Article_num", ""),
                        "segment": details.get("Segment", ""),
                        "family": details.get("Family", ""),
                        "prod_class": details.get("Class", ""),
                    })
                    st.success("Details fetched successfully!")
                else:
                    st.warning("Details not found in the inventory.")
            else:
                st.warning("Please enter a valid EAN number.")


        # Form for submitting product details (for count)
        with st.form("add_product_count_form", clear_on_submit=True):
            product_name = st.text_input(
                "Product Name", 
                value=st.session_state.product_details.get("product_name", ""), 
                placeholder="Mandatory"
            )
            article_num = st.text_input(
                "Article Number", 
                value=st.session_state.product_details.get("article_num", ""), 
                placeholder="Optional"
            )
            segment = st.selectbox(
                "Segment", 
                options=[st.session_state.product_details.get("segment", "")] + unique_segments
            )
            family = st.selectbox(
                "Family", 
                options=[st.session_state.product_details.get("family", "")] + unique_families
            )
            prod_class = st.selectbox(
                "Class", 
                options=[st.session_state.product_details.get("prod_class", "")] + unique_classes
            )
            product_count = st.number_input("Product Count", min_value=0, value=0)

            if st.form_submit_button("Add Product"):
                if product_name and product_count >= 0:
                    new_entry = {
                        "EAN_No": ean_no,
                        "product_name": product_name,
                        "article_number": article_num or None,
                        "segment": segment or None,
                        "family": family or None,
                        "class": prod_class or None,
                        "product_count": product_count,
                        "timestamp": datetime.now(),
                    }
                    add_product(new_entry, product_count_collection)
                    st.success("Product count added successfully!")
                else:
                    st.error("Please fill in all mandatory fields.")




# Modify Database section for deleting records
elif st.session_state.page == "Modify Database":
    st.title("Modify Database")

    # Ask user for the operation
    operation = st.radio(
        "Which operation would you like to perform?",
        options=["Update Record", "Delete Single/Multiple Records", "Delete Entire Segment", "Delete Entire Class"],
        key="operation_choice"
    )

    # Fetch all records from the Products collection
    records = load_products()

    if records:
        # Prepare dropdown options with combined text of EAN_No and product_name
        dropdown_options = [
            {
                "EAN_No": rec["EAN_No"],
                "product_name": rec["product_name"],
                "record": rec,
                "display": f"{rec['EAN_No']} - {rec['product_name']}"
            }
            for rec in records
        ]
        dropdown_labels = [opt["display"] for opt in dropdown_options]

        if operation == "Update Record":
            # Dropdown for updating a single record
            selected_record_label = st.selectbox("Select a record to update", options=dropdown_labels)
            selected_record = next(opt["record"] for opt in dropdown_options if opt["display"] == selected_record_label)

            if selected_record:
                # Show editable fields
                updated_record = {
                    "EAN_No": st.text_input("EAN", value=selected_record["EAN_No"]),
                    "product_name": st.text_input("Product Name", value=selected_record["product_name"]),
                    "article_number": st.text_input("Article Number", value=selected_record.get("article_number", "")),
                    "segment": st.text_input("Segment", value=selected_record.get("segment", "")),
                    "family": st.text_input("Family", value=selected_record.get("family", "")),
                    "class": st.text_input("Class", value=selected_record.get("class", "")),
                    "expiry_date": st.date_input("Expiry Date", value=datetime.strptime(selected_record["expiry_date"], "%d/%m/%Y"))
                }

                # Format expiry_date to 15/07/2026
                if updated_record["expiry_date"]:
                    updated_record["expiry_date"] = updated_record["expiry_date"].strftime("%d/%m/%Y")

                # Confirm and update record
                if st.button("Modify Record"):
                    try:
                        products_collection.update_one(
                            {"EAN_No": selected_record["EAN_No"]},
                            {"$set": updated_record}
                        )
                        st.success("Record updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating record: {e}")

        elif operation == "Delete Single/Multiple Records":
            # Dropdown for deleting multiple records
            selected_records_labels = st.multiselect("Select records to delete", options=dropdown_labels)
            selected_records = [opt["record"] for opt in dropdown_options if opt["display"] in selected_records_labels]

            if selected_records:
                if st.button("Delete Selected Record(s)"):
                    try:
                        delete_query = {"$or": [{"EAN_No": rec["EAN_No"]} for rec in selected_records]}
                        products_collection.delete_many(delete_query)
                        st.success("Selected records deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting records: {e}")

        elif operation == "Delete Entire Segment":
            # Fetch unique segments from the records
            unique_segments = sorted({rec.get("segment", "") for rec in records if rec.get("segment", "")})

            selected_segment = st.selectbox("Select a segment to delete", options=unique_segments)

            if selected_segment and st.button("Delete Segment"):
                try:
                    delete_query = {"segment": selected_segment}
                    products_collection.delete_many(delete_query)
                    st.success(f"All records under segment '{selected_segment}' deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting segment: {e}")

        elif operation == "Delete Entire Class":
            # Fetch unique classes from the records
            unique_classes = sorted({rec.get("class", "") for rec in records if rec.get("class", "")})

            selected_class = st.selectbox("Select a class to delete", options=unique_classes)

            if selected_class and st.button("Delete Class"):
                try:
                    delete_query = {"class": selected_class}
                    products_collection.delete_many(delete_query)
                    st.success(f"All records under class '{selected_class}' deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting class: {e}")

    else:
        st.warning("No records found in the database.")



# Expiry Notifier Dashboard Page
elif st.session_state.page == "Expiry Notifier Dashboard":
    st.title("Expiry Notifier Dashboard")
    
    # Tab layout for Segment Dashboard, Family Dashboard, and Near Expiry Dashboard
    tab1, tab2, tab3 = st.tabs(["Segment Dashboard", "Family Dashboard", "Near Expiry Dashboard"])

    with tab1:
        st.subheader("Segment Dashboard (Scanning status)")
        
        # Dropdown to select segment
        unique_segments = get_unique_values("segment")
        selected_segment = st.selectbox("Select Segment", options=unique_segments)

        if selected_segment:
            # Fetch data for selected segment
            inventory_data = fetch_inventory_for_value("Segment", selected_segment)
            products_data = fetch_products_for_value("segment", selected_segment)

            # Count of products in the inventory vs. products in products collection
            total_inventory_products = len(inventory_data)
            scanned_products = len([prod for prod in products_data if prod["EAN_No"] in [inv["EAN"] for inv in inventory_data]])
            remaining_products = total_inventory_products - scanned_products

            # Calculate scanned vs remaining percentage
            scanned_percentage = (scanned_products / total_inventory_products) * 100 if total_inventory_products > 0 else 0
            remaining_percentage = 100 - scanned_percentage

            # Plot the percentage graph
            fig = px.pie(
                names=["Scanned", "Remaining"],
                values=[scanned_percentage, remaining_percentage],
                title=f"Product Scanned vs Remaining in {selected_segment}",
                hole=0.3
            )
            st.plotly_chart(fig)

            # Display remaining products in tabular form
            remaining_products_data = [inv for inv in inventory_data if inv["EAN"] not in [prod["EAN_No"] for prod in products_data]]
            
            if remaining_products_data:
                remaining_df = pd.DataFrame(remaining_products_data)
                st.write(f"**Remaining Products in {selected_segment}**")
                st.dataframe(remaining_df)
            else:
                st.info(f"All products in segment '{selected_segment}' are already scanned.")

    with tab2:
        st.subheader("Family Dashboard (Scanning status)")
        
        # Dropdown to select family
        unique_families = get_unique_values("family")
        selected_family = st.selectbox("Select Family", options=unique_families)

        if selected_family:
            # Fetch data for selected family
            inventory_data = fetch_inventory_for_value("Family", selected_family)  # Fetching inventory by family
            products_data = fetch_products_for_value("family", selected_family)  # Fetching products by family

            # Count of products in the inventory vs. products in products collection
            total_inventory_products = len(inventory_data)
            scanned_products = len([prod for prod in products_data if prod["EAN_No"] in [inv["EAN"] for inv in inventory_data]])
            remaining_products = total_inventory_products - scanned_products

            # Calculate scanned vs remaining percentage
            scanned_percentage = (scanned_products / total_inventory_products) * 100 if total_inventory_products > 0 else 0
            remaining_percentage = 100 - scanned_percentage

            # Plot the percentage graph
            fig = px.pie(
                names=["Scanned", "Remaining"],
                values=[scanned_percentage, remaining_percentage],
                title=f"Product Scanned vs Remaining in {selected_family}",
                hole=0.3
            )
            st.plotly_chart(fig)

            # Display remaining products in tabular form
            remaining_products_data = [inv for inv in inventory_data if inv["EAN"] not in [prod["EAN_No"] for prod in products_data]]
            
            if remaining_products_data:
                remaining_df = pd.DataFrame(remaining_products_data)
                st.write(f"**Remaining Products in {selected_family}**")
                st.dataframe(remaining_df)
            else:
                st.info(f"All products in family '{selected_family}' are already scanned.")
    
    with tab3:
        st.subheader("Near Expiry Dashboard")
        
        # Dropdown to select expiry range
        expiry_range = st.selectbox("Select Expiry Range", options=[15, 20, 30], index=0)
        today = pd.to_datetime("today")
        expiry_date_limit = today + pd.Timedelta(days=expiry_range)

        # Fetch products that are going to expire in the next selected days
        products_data = list(products_collection.find({
            "expiry_date": {"$lte": expiry_date_limit.strftime("%d/%m/%Y")}
        }))
        
        # Calculate the percentage of products near expiry vs remaining products
        total_products = len(products_data)
        expiring_products = len([prod for prod in products_data if pd.to_datetime(prod["expiry_date"], format="%d/%m/%Y") <= expiry_date_limit])
        remaining_products = total_products - expiring_products

        # Calculate expiring vs remaining percentage
        expiring_percentage = (expiring_products / total_products) * 100 if total_products > 0 else 0
        remaining_percentage = 100 - expiring_percentage

        # Plot the percentage graph
        fig = px.pie(
            names=["Expiring", "Remaining"],
            values=[expiring_percentage, remaining_percentage],
            title=f"Products Expiring in Next {expiry_range} Days",
            hole=0.3
        )
        st.plotly_chart(fig)

        # Display the products expiring in the selected range
        expiring_products_data = [prod for prod in products_data if pd.to_datetime(prod["expiry_date"], format="%d/%m/%Y") <= expiry_date_limit]
        
        if expiring_products_data:
            expiring_df = pd.DataFrame(expiring_products_data)
            st.write(f"**Products Expiring in Next {expiry_range} Days**")
            st.dataframe(expiring_df)
        else:
            st.info(f"No products are expiring in the next {expiry_range} days.")



elif st.session_state.page == "View Database":
    df = pd.DataFrame(load_products())
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No data found.")
