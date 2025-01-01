import pandas as pd

# Path to the CSV file
csv_file_path = "//workspaces//Expiry-Notifier//data//U2RZ_inventory_csv.csv"

# Load the CSV file into a pandas DataFrame
data = pd.read_csv(csv_file_path)

# Get unique values for each specified field
unique_segments = data['Segment'].unique()
unique_families = data['Family'].unique()
unique_classes = data['Class'].unique()

# Print the unique values
print("Unique Segments:", unique_segments)
print("Unique Families:", unique_families)
print("Unique Classes:", unique_classes)
