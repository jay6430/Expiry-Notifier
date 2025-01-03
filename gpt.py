import streamlit as st
import pandas as pd
from pymongo import MongoClient, errors
from datetime import datetime
import streamlit.components.v1 as components
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
    'PROCESSED FOOD', ....
]
unique_families = [
    'BISCUITS & BRANDED BAKERY', ....
]
unique_classes = [
    'BISCUITS', ....
]

html_component="""
        <html content>
        """


# MongoDB helper functions
def load_products_from_products_collection():
    """Load all product records from the Products collection."""
    try:
        records = list(products_collection.find({}, {"_id": 0}))  # Exclude MongoDB ID
        return records
    except Exception as e:
        st.error(f"Error loading products: {e}")
        return []


def load_products_from_product_count_collection():
    """Load all product records from the Products collection."""
    try:
        records = list(product_count_collection.find({}, {"_id": 0}))  # Exclude MongoDB ID
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
def get_unique_values_product_collection(field):
    try:
        values = sorted({rec.get(field, "") for rec in products_collection.find({}, {field: 1})})
        return values
    except Exception as e:
        st.error(f"Error fetching unique {field}s: {e}")
        return []
# Function to get unique segments or families from the Products collection
def get_unique_values_product_count_collection(field):
    try:
        values = sorted({rec.get(field, "") for rec in product_count_collection.find({}, {field: 1})})
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


# Function to fetch the products count data for the selected segment or family
def fetch_products_count_for_value(field, value):
    try:
        query = {field: value}
        return list(product_count_collection.find(query, {"EAN_No": 1, "product_name": 1, "_id": 0}))
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
st.sidebar.title("U2RZ Navigation")
st.sidebar.caption("Manage your inventory with ease.")

# Use page_link to create navigation
pages = {
    "Add Product": "➕ Add Product",
    "Modify Database": "✏️ Modify Database",
    "Dashboard" : "✨Dashboard",
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
    st.title("U2RZ Inventory Management")

    # JavaScript QR Code Scanner (Common for both tabs)
    st.subheader("Add Product")
    components.html(
        html_component,
        height=730,
    )

    # Input EAN (Common for both tabs)
    ean_no = st.text_input("Product EAN Number", key="scanned_ean_field", placeholder="Enter or scan EAN")
    if st.button("Fetch Details", key = 'Fetch details from inventory'):
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

    # Tab layout for "Add Product for expiry" and "Add Product for count"
    tab1, tab2 = st.tabs(["Add Product for Expiry", "Add Product for Count"])

    with tab1:
        st.subheader("Add Product for Expiry")

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

    # Tab layout for "Add Product for expiry" and "Add Product for count"
    tab1, tab2 = st.tabs(["Modify Database for Product Expiry", "Modify Database for Product Count"])

    with tab1:
        
        # Ask user for the operation
        operation = st.radio(
            "Which operation would you like to perform?",
            options=["Update Record", "Delete Single/Multiple Records", "Delete Entire Segment", "Delete Entire Class"],
            key="operation_choice_product_expiry"
        )

        # Fetch all records from the Products collection
        records = load_products_from_products_collection()

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
                    if st.button("Modify Record", key="Modify Database for Product Expiry"):
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
                    if st.button("Delete Selected Record(s)", key= "Delete Entry for Product Expiry"):
                        try:
                            delete_query = {"$or": [{"EAN_No": rec["EAN_No"]} for rec in selected_records]}
                            products_collection.delete_many(delete_query)
                            st.success("Selected records deleted successfully!")
                        except Exception as e:
                            st.error(f"Error deleting records: {e}")

            elif operation == "Delete Entire Segment":
                # Fetch unique segments from the records
                unique_segments = sorted({rec.get("segment", "") for rec in records if rec.get("segment", "")})

                selected_segment = st.selectbox("Select a segment to delete", options=unique_segments, key = "segment selectbox from product expiry")

                if selected_segment and st.button("Delete Segment", key = "delete segment from product expiry"):
                    try:
                        delete_query = {"segment": selected_segment}
                        products_collection.delete_many(delete_query)
                        st.success(f"All records under segment '{selected_segment}' deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting segment: {e}")

            elif operation == "Delete Entire Class":
                # Fetch unique classes from the records
                unique_classes = sorted({rec.get("class", "") for rec in records if rec.get("class", "")})

                selected_class = st.selectbox("Select a class to delete", options=unique_classes, key = "class selectbox from product expiry")

                if selected_class and st.button("Delete Class", key = "delete class from product expiry"):
                    try:
                        delete_query = {"class": selected_class}
                        products_collection.delete_many(delete_query)
                        st.success(f"All records under class '{selected_class}' deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting class: {e}")

        else:
            st.warning("No records found in the database.")


    with tab2:
        
        # Ask user for the operation
        operation = st.radio(
            "Which operation would you like to perform?",
            options=["Update Record", "Delete Single/Multiple Records", "Delete Entire Segment", "Delete Entire Class"],
            key="operation_choice_product_count"
        )

        # Fetch all records from the Products collection
        records = load_products_from_product_count_collection()

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
                        "product_count": st.number_input("Product Count", min_value=0, value=selected_record.get("product_count", ""))
                    }


                    # Confirm and update record
                    if st.button("Modify Record", key ="Modify Database for Product Count"):
                        try:
                            product_count_collection.update_one(
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
                    if st.button("Delete Selected Record(s)" , key= "Delete Entry for Product Count"):
                        try:
                            delete_query = {"$or": [{"EAN_No": rec["EAN_No"]} for rec in selected_records]}
                            product_count_collection.delete_many(delete_query)
                            st.success("Selected records deleted successfully!")
                        except Exception as e:
                            st.error(f"Error deleting records: {e}")

            elif operation == "Delete Entire Segment":
                # Fetch unique segments from the records
                unique_segments = sorted({rec.get("segment", "") for rec in records if rec.get("segment", "")})

                selected_segment = st.selectbox("Select a segment to delete", options=unique_segments, key = "segment selectbox from product count")

                if selected_segment and st.button("Delete Segment", key = "delete segment from product count"):
                    try:
                        delete_query = {"segment": selected_segment}
                        product_count_collection.delete_many(delete_query)
                        st.success(f"All records under segment '{selected_segment}' deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting segment: {e}")

            elif operation == "Delete Entire Class":
                # Fetch unique classes from the records
                unique_classes = sorted({rec.get("class", "") for rec in records if rec.get("class", "")})

                selected_class = st.selectbox("Select a class to delete", options=unique_classes, key = "class selectbox from product count")

                if selected_class and st.button("Delete Class", key = "delete class from product count"):
                    try:
                        delete_query = {"class": selected_class}
                        product_count_collection.delete_many(delete_query)
                        st.success(f"All records under class '{selected_class}' deleted successfully!")
                    except Exception as e:
                        st.error(f"Error deleting class: {e}")

        else:
            st.warning("No records found in the database.")



# Dashboard Page
elif st.session_state.page == "Dashboard":
    st.title("Dashboard")

    # Tab layout for Expiry Products Scanning Status, Near Expiry Dashboard, and Raw Data
    tab1, tab2, tab3, tab4 = st.tabs(["Expiry Products Scanning Status", "Product Count Scanning Status", "Near Expiry Dashboard", "Raw Data"])

    with tab1:
        st.subheader("Expiry Products Scanning Status")

        # User input to select between Segment or Family
        dashboard_type = st.radio(
            "Select Dashboard Type:", 
            options=["Segment", "Family"], 
            index=0 , 
            key="Expiry Products Scanning Status",
        )

        if dashboard_type == "Segment":
            # Segment Dashboard Logic
            unique_segments = get_unique_values_product_collection("segment")
            selected_segment = st.selectbox("Select Segment", options=unique_segments)

            if selected_segment:
                inventory_data = fetch_inventory_for_value("Segment", selected_segment)
                products_data = fetch_products_for_value("segment", selected_segment)

                total_inventory_products = len(inventory_data)
                scanned_products = len([prod for prod in products_data if prod["EAN_No"] in [inv["EAN"] for inv in inventory_data]])
                remaining_products = total_inventory_products - scanned_products

                scanned_percentage = (scanned_products / total_inventory_products) * 100 if total_inventory_products > 0 else 0
                remaining_percentage = 100 - scanned_percentage

                fig = px.pie(
                    names=["Scanned", "Remaining"],
                    values=[scanned_percentage, remaining_percentage],
                    title=f"Product Scanned vs Remaining in {selected_segment}",
                    hole=0.3
                )
                st.plotly_chart(fig)

                remaining_products_data = [inv for inv in inventory_data if inv["EAN"] not in [prod["EAN_No"] for prod in products_data]]

                if remaining_products_data:
                    remaining_df = pd.DataFrame(remaining_products_data)
                    st.write(f"**Remaining Products in {selected_segment}**")
                    st.dataframe(remaining_df)
                else:
                    st.info(f"All products in segment '{selected_segment}' are already scanned.")

        elif dashboard_type == "Family":
            # Family Dashboard Logic
            unique_families = get_unique_values_product_collection("family")
            selected_family = st.selectbox("Select Family", options=unique_families)

            if selected_family:
                inventory_data = fetch_inventory_for_value("Family", selected_family)
                products_data = fetch_products_for_value("family", selected_family)

                total_inventory_products = len(inventory_data)
                scanned_products = len([prod for prod in products_data if prod["EAN_No"] in [inv["EAN"] for inv in inventory_data]])
                remaining_products = total_inventory_products - scanned_products

                scanned_percentage = (scanned_products / total_inventory_products) * 100 if total_inventory_products > 0 else 0
                remaining_percentage = 100 - scanned_percentage

                fig = px.pie(
                    names=["Scanned", "Remaining"],
                    values=[scanned_percentage, remaining_percentage],
                    title=f"Product Scanned vs Remaining in {selected_family}",
                    hole=0.3
                )
                st.plotly_chart(fig)

                remaining_products_data = [inv for inv in inventory_data if inv["EAN"] not in [prod["EAN_No"] for prod in products_data]]

                if remaining_products_data:
                    remaining_df = pd.DataFrame(remaining_products_data)
                    st.write(f"**Remaining Products in {selected_family}**")
                    st.dataframe(remaining_df)
                else:
                    st.info(f"All products in family '{selected_family}' are already scanned.")

    with tab2:
        st.subheader("Product Count Scanning Status")

                # User input to select between Segment or Family
        dashboard_type = st.radio(
            "Select Dashboard Type:", 
            options=["Segment", "Family"], 
            index=0,
            key="Product Count Scanning Status"
        )

        if dashboard_type == "Segment":
            # Segment Dashboard Logic
            unique_segments = get_unique_values_product_count_collection("segment")
            selected_segment = st.selectbox("Select Segment", options=unique_segments)

            if selected_segment:
                inventory_data = fetch_inventory_for_value("Segment", selected_segment)
                products_data = fetch_products_count_for_value("segment", selected_segment)

                total_inventory_products = len(inventory_data)
                scanned_products = len([prod for prod in products_data if prod["EAN_No"] in [inv["EAN"] for inv in inventory_data]])
                remaining_products = total_inventory_products - scanned_products

                scanned_percentage = (scanned_products / total_inventory_products) * 100 if total_inventory_products > 0 else 0
                remaining_percentage = 100 - scanned_percentage

                fig = px.pie(
                    names=["Scanned", "Remaining"],
                    values=[scanned_percentage, remaining_percentage],
                    title=f"Product Scanned vs Remaining in {selected_segment}",
                    hole=0.3
                )
                st.plotly_chart(fig)

                remaining_products_data = [inv for inv in inventory_data if inv["EAN"] not in [prod["EAN_No"] for prod in products_data]]

                if remaining_products_data:
                    remaining_df = pd.DataFrame(remaining_products_data)
                    st.write(f"**Remaining Products in {selected_segment}**")
                    st.dataframe(remaining_df)
                else:
                    st.info(f"All products in segment '{selected_segment}' are already scanned.")

        elif dashboard_type == "Family":
            # Family Dashboard Logic
            unique_families = get_unique_values_product_count_collection("family")
            selected_family = st.selectbox("Select Family", options=unique_families)

            if selected_family:
                inventory_data = fetch_inventory_for_value("Family", selected_family)
                products_data = fetch_products_count_for_value("family", selected_family)

                total_inventory_products = len(inventory_data)
                scanned_products = len([prod for prod in products_data if prod["EAN_No"] in [inv["EAN"] for inv in inventory_data]])
                remaining_products = total_inventory_products - scanned_products

                scanned_percentage = (scanned_products / total_inventory_products) * 100 if total_inventory_products > 0 else 0
                remaining_percentage = 100 - scanned_percentage

                fig = px.pie(
                    names=["Scanned", "Remaining"],
                    values=[scanned_percentage, remaining_percentage],
                    title=f"Product Scanned vs Remaining in {selected_family}",
                    hole=0.3
                )
                st.plotly_chart(fig)

                remaining_products_data = [inv for inv in inventory_data if inv["EAN"] not in [prod["EAN_No"] for prod in products_data]]

                if remaining_products_data:
                    remaining_df = pd.DataFrame(remaining_products_data)
                    st.write(f"**Remaining Products in {selected_family}**")
                    st.dataframe(remaining_df)
                else:
                    st.info(f"All products in family '{selected_family}' are already scanned.")





    with tab3:
        st.subheader("Near Expiry Dashboard")

        expiry_range = st.selectbox("Select Expiry Range", options=[15, 20, 30], index=0)
        today = pd.to_datetime("today")
        expiry_date_limit = today + pd.Timedelta(days=expiry_range)

        products_data = list(products_collection.find({
            "expiry_date": {"$lte": expiry_date_limit.strftime("%d/%m/%Y")}
        }))

        total_products = len(products_data)
        expiring_products = len([prod for prod in products_data if pd.to_datetime(prod["expiry_date"], format="%d/%m/%Y") <= expiry_date_limit])
        remaining_products = total_products - expiring_products

        expiring_percentage = (expiring_products / total_products) * 100 if total_products > 0 else 0
        remaining_percentage = 100 - expiring_percentage

        fig = px.pie(
            names=["Expiring", "Remaining"],
            values=[expiring_percentage, remaining_percentage],
            title=f"Products Expiring in Next {expiry_range} Days",
            hole=0.3
        )
        st.plotly_chart(fig)

        expiring_products_data = [prod for prod in products_data if pd.to_datetime(prod["expiry_date"], format="%d/%m/%Y") <= expiry_date_limit]

        if expiring_products_data:
            expiring_df = pd.DataFrame(expiring_products_data)
            st.write(f"**Products Expiring in Next {expiry_range} Days**")
            st.dataframe(expiring_df)
        else:
            st.info(f"No products are expiring in the next {expiry_range} days.")

    with tab4:
        st.subheader("Scanned Products Raw Data")

        # User input to select collection
        selected_collection = st.radio(
            "Select Collection:", 
            options=["Expiry Product Database", "Product Count Database"], 
            index=0
        )

        # Map collection names to actual collections
        collection_map = {
            "Expiry Product Database": products_collection,
            "Product Count Database": product_count_collection
        }
        collection = collection_map[selected_collection]

        # User input to filter data
        filter_option = st.selectbox("Filter By:", options=["All Data", "Segment", "Family"], index=0)

        if filter_option == "All Data":
            # Display all data
            data = list(collection.find({}, {"_id": 0}))  # Exclude the `_id` field explicitly
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.info("No data available in the selected collection.")




        elif filter_option == "Segment":
            # Filter by segment
            if selected_collection == "Expiry Product Database":
                unique_segments = get_unique_values_product_collection("segment")
            elif selected_collection == "Product Count Database":
                unique_segments = get_unique_values_product_count_collection("segment")

            selected_segment = st.selectbox("Select Segment", options=unique_segments, key="segment_filter")

            if selected_segment:
                data = list(collection.find({"segment": selected_segment}))
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                else:
                    st.info(f"No data found for segment '{selected_segment}'.")

        elif filter_option == "Family":
            # Filter by family
            if selected_collection == "Expiry Product Database":
                unique_families = get_unique_values_product_collection("family")
            elif selected_collection == "Product Count Database":
                unique_families = get_unique_values_product_count_collection("family")

            selected_family = st.selectbox("Select Family", options=unique_families, key="family_filter")

            if selected_family:
                data = list(collection.find({"family": selected_family}))
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                else:
                    st.info(f"No data found for family '{selected_family}'.")

