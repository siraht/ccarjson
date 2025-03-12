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

# New section for inputting text and selecting options
with st.expander("Additional information needed for CNAI"):
    st.header("Input Client Data Fields")
    with st.form(key='client_data_form'):
        first_contact_date = st.text_input("First contact date")
        date_of_admission = st.text_input("Date of admission")
        type_of_insurance = st.selectbox("Type of insurance", ["Medicaid", "CHP+", "Commercial", "Self-pay"])
        medicaid_rae = st.text_input("Medicaid RAE") if type_of_insurance in ["Medicaid", "CHP+"] else ""
        medicaid_id = st.text_input("Medicaid ID") if type_of_insurance in ["Medicaid", "CHP+"] else ""
        healthie_id = st.text_input("Healthie ID")
        date_of_birth = st.text_input("Date of birth")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        gender = st.text_input("Gender")
        county_of_residence = st.text_input("County of residence")
        zip_code = st.text_input("Zip code")
        staff_id = st.text_input("Staff ID", value="EA")
        primary_diagnosis_icd10 = st.text_input("Primary Diagnosis ICD10 code")
        action_type = st.selectbox("Action type", ["Admission", "Update", "Discharge", "Evaluation Only"])
        update_type = st.selectbox("Update type", ["", "Annual", "Interim/reassessment", "Psychiatric Hospital Admission", "Psychiatric Hospital Discharge"])
        discharge_date = st.text_input("Discharge Date") if action_type in ["Discharge", "Evaluation Only"] else ""
        date_of_last_contact = st.text_input("Date of Last Contact") if action_type in ["Discharge", "Evaluation Only"] else ""
        type_of_discharge = st.selectbox("Type of Discharge", ["1– Treatment completed", "2– Transferred/Referred", "3– Treatment not completed"]) if action_type in ["Discharge", "Evaluation Only"] else ""
        discharge_termination_referral = st.text_input("Discharge/Termination Referral") if action_type in ["Discharge", "Evaluation Only"] else ""
        reason_for_discharge = st.selectbox("Reason for Discharge", ["01=Attendance", "02=Client Decision", "03=Client stopped coming and contact efforts failed", "04=Financial/Payments", "05=Lack of Progress", "06=Medical Reasons", "07=Military Deployment", "08=Moved", "09=Incarcerated", "10=Died", "11=Agency closed/No longer in business"]) if action_type in ["Discharge", "Evaluation Only"] else ""
        
        submit_button = st.form_submit_button(label='Copy to Clipboard')
        
        if submit_button:
            client_data = {
                "First contact date": first_contact_date,
                "Date of admission": date_of_admission,
                "Medicaid RAE": medicaid_rae,
                "Medicaid ID": medicaid_id,
                "Healthie ID": healthie_id,
                "Date of birth": date_of_birth,
                "First Name": first_name,
                "Last Name": last_name,
                "Gender": gender,
                "County of residence": county_of_residence,
                "Zip code": zip_code,
                "Staff ID": staff_id,
                "Primary Diagnosis ICD10 code": primary_diagnosis_icd10,
                "Type of insurance": type_of_insurance,
                "Action type": action_type,
                "Update type": update_type,
                "Discharge Date": discharge_date,
                "Date of Last Contact": date_of_last_contact,
                "Type of Discharge": type_of_discharge,
                "Discharge/Termination Referral": discharge_termination_referral,
                "Reason for Discharge": reason_for_discharge
            }
            
            # Check that all required fields have values
            required_fields = ["First contact date", "Date of admission", "Healthie ID", "Date of birth", "First Name", "Last Name", "Gender", "County of residence", "Zip code", "Staff ID", "Primary Diagnosis ICD10 code", "Type of insurance", "Action type"]
            missing_fields = [field for field in required_fields if not client_data[field]]
            
            if missing_fields:
                st.error(f"Missing required fields: {', '.join(missing_fields)}")
            else:
                # Display the JSON data in a text area for manual copying
                st.text_area("Client Data JSON", json.dumps(client_data), height=200)
                st.success("Client data ready to be copied")

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

# Add a text area for pasting fixed-length text
st.header("Paste Fixed-Length Text")
fixed_length_text = st.text_area("Paste fixed-length text here")

# Button to process the pasted fixed-length text
if st.button("Process Pasted Text"):
    if fixed_length_text:
        st.session_state['lines'] = fixed_length_text.split('\n')
        st.success("Pasted text processed and added to text file")
    else:
        st.error("No text to process")

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

# Function to extract the latest Effective Date
def get_latest_effective_date(lines, config_df):
    latest_date = None
    for line in lines:
        start = 0
        for _, row in config_df.sort_values('order').iterrows():
            field_name = row['name']
            length = int(row['length'])
            value = line[start:start + length].strip()
            start += length
            if field_name.lower() == 'effective date':
                try:
                    # Parse the date in MMDDYYYY format
                    date_value = pd.to_datetime(value, format='%m%d%Y')
                    if latest_date is None or date_value > latest_date:
                        latest_date = date_value
                except ValueError:
                    continue
    return latest_date

# Manage Text File
st.header("Manage Text File")
col1, col2 = st.columns(2)
with col1:
    if st.session_state['lines']:
        # Convert lines to CRLF line terminators
        file_content = '\r\n'.join(st.session_state['lines']) + '\r\n'
        file_content = file_content.encode('utf-8')
        
        # Get the latest Effective Date
        latest_date = get_latest_effective_date(st.session_state['lines'], st.session_state['config_df'])
        if latest_date:
            file_name = f"194{latest_date.strftime('%m%y')}.car"
        else:
            file_name = "clients_data.car"
        
        st.download_button(
            label="Download Text File",
            data=file_content,
            file_name=file_name,
            mime="text/plain"
        )
    else:
        st.info("No data to download")
with col2:
    if st.button("Clear Text File"):
        st.session_state['lines'] = []
        st.success("Text file cleared")