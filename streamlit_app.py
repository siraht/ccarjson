import streamlit as st
import pandas as pd
import json
import os

# Function to apply rules to fields
def apply_rules(fields, rules):
    """
    Apply conditional rules to update field values.
    
    Args:
        fields (dict): Dictionary of field names and their current values.
        rules (list): List of rule dictionaries from rules.json.
    
    Returns:
        dict: Updated fields dictionary after applying all rules.
    """
    for rule in rules:
        if 'target' not in rule:
            continue  # Skip any object without a 'target' key
        target = rule['target']
        conditions_values = rule.get('conditions_values', [])
        default = rule.get('default', None)
        for cv in conditions_values:
            conditions = cv['conditions']
            value = cv['value']
            # Check if all conditions match current field values
            if all(fields.get(cond_field) == cond_value for cond_field, cond_value in conditions.items()):
                fields[target] = value
                break
        else:
            # Apply default value if no conditions match and default is specified
            if default is not None:
                fields[target] = default
    return fields

# Load config and rules into session state if not already loaded
if 'config_df' not in st.session_state:
    try:
        st.session_state['config_df'] = pd.read_csv('config.csv')
        required_columns = ['order', 'name', 'length', 'alignment']
        if not all(col in st.session_state['config_df'].columns for col in required_columns):
            st.error("config.csv must contain columns: order, name, length, alignment")
            st.stop()
    except Exception as e:
        st.error(f"Error loading config.csv: {e}")
        st.stop()

if 'rules' not in st.session_state:
    try:
        with open('rules.json', 'r') as f:
            st.session_state['rules'] = json.load(f)
    except Exception as e:
        st.error(f"Error loading rules.json: {e}")
        st.stop()

# Initialize lines if not present
if 'lines' not in st.session_state:
    st.session_state['lines'] = []

# App title and instructions
st.title("Fixed-Length Text File Generator with Rules")
st.markdown("""
This app processes client data from JSON input into a fixed-length text file based on a predefined configuration and rules.

- **Step 1**: Ensure `config.csv` and `rules.json` are in the same directory as this app.
- **Step 2**: Paste JSON data for a client and click "Process Client Data" to add it to the text file.
- **Step 3**: Preview the text file, verify the data, and download it as `clients_data.txt` or clear its contents.

**Note**: Rules in `rules.json` must be ordered correctly to handle dependencies between fields.
""")

# Input Client JSON Data
st.header("Input Client JSON Data")
json_input = st.text_area("Paste JSON here (e.g., {'field_A': 'X'})")
process_button = st.button("Process Client Data")

# Process JSON Data
if process_button:
    try:
        fields = json.loads(json_input)
        if not isinstance(fields, dict):
            st.error("JSON must be a dictionary")
        else:
            # Apply rules to update field values
            fields = apply_rules(fields, st.session_state['rules'])
            # Format into fixed-length string
            config_df = st.session_state['config_df']
            line = ""
            for _, row in config_df.sort_values('order').iterrows():
                field_name = row['name']
                length = int(row['length'])
                alignment = row['alignment'].lower()
                # Remove all spaces from the value and convert to string
                value = ''.join(str(fields.get(field_name, '')).split())
                if alignment == 'left':
                    formatted_value = value[:length].ljust(length)
                elif alignment == 'right':
                    formatted_value = value[:length].rjust(length)
                else:
                    st.error(f"Invalid alignment for field {field_name}: {alignment}")
                    break
                line += formatted_value
            else:
                st.session_state['lines'].append(line)
                st.success("Client data processed and added to text file")
    except json.JSONDecodeError:
        st.error("Invalid JSON input")
    except Exception as e:
        st.error(f"Error processing data: {e}")

# Preview Text File
st.header("Preview Text File")
if st.session_state['lines']:
    preview_text = '\n'.join(st.session_state['lines'])
    st.code(preview_text, language='text')
else:
    st.info("No data in text file yet")

# Verify Client Data (Expanders)
st.header("Verify Client Data (Expanders)")
st.markdown("Expand each client to verify the individual field values based on the fixed-length format.")
if st.session_state['lines']:
    for index, line in enumerate(st.session_state['lines']):
        client_data = {}
        start = 0
        for _, row in st.session_state['config_df'].sort_values('order').iterrows():
            field_name = row['name']
            length = int(row['length'])
            # Extract the exact value including spaces
            value = line[start:start + length]
            client_data[field_name] = value
            start += length
        # Get first and last name for label, stripping spaces for display
        first_name = client_data.get("First Name", "").strip()
        last_name = client_data.get("Last Name", "").strip()
        # Construct label using First Name and Last Name; if missing, use placeholders
        label = f"{first_name} {last_name}".strip() or f"Unnamed Client {index + 1}"
        with st.expander(label):
            # Create DataFrame with exact values including spaces
            df = pd.DataFrame(list(client_data.items()), columns=["Field", "Value"])
            st.dataframe(df)
else:
    st.info("No client data to verify")

# Verify Client Data (Table View)
st.header("Verify Client Data (Table View)")
st.markdown("This table shows each client's data with fields split into columns as defined in config.csv. Headers include the order number, field names, and required lengths.")
if st.session_state['lines']:
    # Prepare headers with order number, field names, and lengths
    headers = [f"{row['order']}: {row['name']} (Length: {row['length']})" 
               for _, row in st.session_state['config_df'].sort_values('order').iterrows()]
    # Prepare data for the table
    table_data = []
    for line in st.session_state['lines']:
        start = 0
        row_data = []
        for _, row in st.session_state['config_df'].sort_values('order').iterrows():
            length = int(row['length'])
            # Extract the exact value including spaces
            value = line[start:start + length]
            row_data.append(value)
            start += length
        table_data.append(row_data)
    # Create DataFrame
    df_table = pd.DataFrame(table_data, columns=headers)
    # Display the DataFrame
    st.dataframe(df_table)
else:
    st.info("No client data to verify")

# Manage Text File
st.header("Manage Text File")
col1, col2 = st.columns(2)
with col1:
    if st.session_state['lines']:
        file_content = '\n'.join(st.session_state['lines']).encode('utf-8')
        st.download_button(
            label="Download Text File",
            data=file_content,
            file_name="clients_data.txt",
            mime="text/plain"
        )
    else:
        st.info("No data to download")
with col2:
    if st.button("Clear Text File"):
        st.session_state['lines'] = []
        st.success("Text file cleared")