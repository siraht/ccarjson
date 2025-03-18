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
st.title("CCAR batch upload tool")
st.markdown("""
This app makes creating batch uploads for CCARs easy.

- **Step 1**: Use the Additional Information form to make sure that you're providing all the required information for a CCAR generation.
- **Step 2**: In Clinical Notes AI, generate Documentation using the CCAR Fixed Length template, pasting in the contents of the client's evaluation note + the output from the Additional Information form.
- **Step 3**: Copy and paste the output from Clinical Notes AI into the "Paste Clinical Notes AI output here" section.
- **Step 4**: Click "Process Client Data" to process the data and add it to the text file.
- **Step 5**: Repeat Steps 1-4 for all clients you want to process
- **Step 6**: Verify the data, if necessary, and download the .car file.
- **Step 7**: Upload the .car file to the CCAR portal.
""")

# Initialize session state for form fields if not present
if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'action_type': "Admission",
        'first_contact_date': "",
        'date_of_admission': "",
        'type_of_insurance': "Medicaid",
        'medicaid_rae': "",
        'medicaid_id': "",
        'healthie_id': "",
        'date_of_birth': "",
        'first_name': "",
        'last_name': "",
        'gender': "",
        'county_of_residence': "",
        'zip_code': "",
        'staff_id': "EA",
        'primary_diagnosis_icd10': "",
        'update_type': "",
        'discharge_date': "",
        'date_of_last_contact': "",
        'type_of_discharge': "1– Treatment completed",
        'discharge_termination_referral': "",
        'reason_for_discharge': "01=Attendance"
    }

# Callback functions to update session state when inputs change
def update_form_field(field):
    st.session_state.form_data[field] = st.session_state[field]

# Function to clear all form fields
def clear_form():
    # Reset form data to default values
    st.session_state.form_data = {
        'first_contact_date': "",
        'action_type': "Admission",
        'date_of_admission': "",
        'type_of_insurance': "Medicaid",
        'medicaid_rae': "",
        'medicaid_id': "",
        'healthie_id': "",
        'date_of_birth': "",
        'first_name': "",
        'last_name': "",
        'gender': "",
        'county_of_residence': "",
        'zip_code': "",
        'staff_id': "EA",
        'primary_diagnosis_icd10': "",
        'update_type': "",
        'discharge_date': "",
        'date_of_last_contact': "",
        'type_of_discharge': "1– Treatment completed",
        'discharge_termination_referral': "",
        'reason_for_discharge': "01=Attendance"
    }
    
    # Reset widget state values to match form data
    for key in st.session_state.form_data:
        if key in st.session_state:
            st.session_state[key] = st.session_state.form_data[key]

# New section for inputting text and selecting options
with st.expander("## Additional information Form"):
    # Action type selection (affects visibility of other fields)
    action_type = st.selectbox(
        "Action type", 
        ["Admission", "Update", "Discharge", "Evaluation Only"],
        key="action_type",
        on_change=update_form_field,
        args=("action_type",)
    )
    
    # Common fields for all action types
    col1, col2 = st.columns(2)
    with col1:
        first_contact_date = st.text_input(
            "First contact date", 
            value=st.session_state.form_data["first_contact_date"],
            key="first_contact_date",
            on_change=update_form_field,
            args=("first_contact_date",)
        )
    
    with col2:
        # Only show date of admission for certain action types
        if action_type in ["Admission", "Evaluation Only"]:
            date_of_admission = st.text_input(
                "Date of admission", 
                value=st.session_state.form_data["date_of_admission"],
                key="date_of_admission",
                on_change=update_form_field,
                args=("date_of_admission",)
            )
        else:
            st.session_state.form_data["date_of_admission"] = ""
    
    # Insurance information
    type_of_insurance = st.selectbox(
        "Type of insurance", 
        ["Medicaid", "CHP+", "Commercial", "Self-pay"],
        key="type_of_insurance",
        on_change=update_form_field,
        args=("type_of_insurance",)
    )
    
    # Only show Medicaid fields for certain insurance types
    if type_of_insurance in ["Medicaid", "CHP+"]:
        col1, col2 = st.columns(2)
        with col1:
            medicaid_rae = st.text_input(
                "Medicaid RAE", 
                value=st.session_state.form_data["medicaid_rae"],
                key="medicaid_rae",
                on_change=update_form_field,
                args=("medicaid_rae",)
            )
        with col2:
            medicaid_id = st.text_input(
                "Medicaid ID", 
                value=st.session_state.form_data["medicaid_id"],
                key="medicaid_id",
                on_change=update_form_field,
                args=("medicaid_id",)
            )
    else:
        st.session_state.form_data["medicaid_rae"] = ""
        st.session_state.form_data["medicaid_id"] = ""
    
    # Client identification fields
    col1, col2 = st.columns(2)
    with col1:
        healthie_id = st.text_input(
            "Healthie ID", 
            value=st.session_state.form_data["healthie_id"],
            key="healthie_id",
            on_change=update_form_field,
            args=("healthie_id",)
        )
    with col2:
        date_of_birth = st.text_input(
            "Date of birth", 
            value=st.session_state.form_data["date_of_birth"],
            key="date_of_birth",
            on_change=update_form_field,
            args=("date_of_birth",)
        )
    
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input(
            "First Name", 
            value=st.session_state.form_data["first_name"],
            key="first_name",
            on_change=update_form_field,
            args=("first_name",)
        )
    with col2:
        last_name = st.text_input(
            "Last Name", 
            value=st.session_state.form_data["last_name"],
            key="last_name",
            on_change=update_form_field,
            args=("last_name",)
        )
    
    col1, col2 = st.columns(2)
    with col1:
        gender = st.text_input(
            "Gender", 
            value=st.session_state.form_data["gender"],
            key="gender",
            on_change=update_form_field,
            args=("gender",)
        )
    
    # Location and staff information
    col1, col2 = st.columns(2)
    with col1:
        county_of_residence = st.text_input(
            "County of residence", 
            value=st.session_state.form_data["county_of_residence"],
            key="county_of_residence",
            on_change=update_form_field,
            args=("county_of_residence",)
        )
    with col2:
        zip_code = st.text_input(
            "Zip code", 
            value=st.session_state.form_data["zip_code"],
            key="zip_code",
            on_change=update_form_field,
            args=("zip_code",)
        )
    
    col1, col2 = st.columns(2)
    with col1:
        staff_id = st.text_input(
            "Staff ID", 
            value=st.session_state.form_data["staff_id"],
            key="staff_id",
            on_change=update_form_field,
            args=("staff_id",)
        )
    with col2:
        primary_diagnosis_icd10 = st.text_input(
            "Primary Diagnosis ICD10 code", 
            value=st.session_state.form_data["primary_diagnosis_icd10"],
            key="primary_diagnosis_icd10",
            on_change=update_form_field,
            args=("primary_diagnosis_icd10",)
        )
    
    # Update type (only show for Update action type)
    if action_type == "Update":
        update_type = st.selectbox(
            "Update type", 
            ["", "Annual", "Interim/reassessment", "Psychiatric Hospital Admission", "Psychiatric Hospital Discharge"],
            key="update_type",
            on_change=update_form_field,
            args=("update_type",)
        )
    else:
        st.session_state.form_data["update_type"] = ""
    
    # Discharge fields (only show for Discharge or Evaluation Only action types)
    if action_type in ["Discharge", "Evaluation Only"]:
        col1, col2 = st.columns(2)
        with col1:
            discharge_date = st.text_input(
                "Discharge Date", 
                value=st.session_state.form_data["discharge_date"],
                key="discharge_date",
                on_change=update_form_field,
                args=("discharge_date",)
            )
        with col2:
            date_of_last_contact = st.text_input(
                "Date of Last Contact", 
                value=st.session_state.form_data["date_of_last_contact"],
                key="date_of_last_contact",
                on_change=update_form_field,
                args=("date_of_last_contact",)
            )
        
        type_of_discharge = st.selectbox(
            "Type of Discharge", 
            ["1– Treatment completed", "2– Transferred/Referred", "3– Treatment not completed"],
            key="type_of_discharge",
            on_change=update_form_field,
            args=("type_of_discharge",)
        )
        
        discharge_termination_referral = st.text_input(
            "Discharge/Termination Referral", 
            value=st.session_state.form_data["discharge_termination_referral"],
            key="discharge_termination_referral",
            on_change=update_form_field,
            args=("discharge_termination_referral",)
        )
        
        reason_for_discharge = st.selectbox(
            "Reason for Discharge", 
            ["01=Attendance", "02=Client Decision", "03=Client stopped coming and contact efforts failed", "04=Financial/Payments", "05=Lack of Progress", "06=Medical Reasons", "07=Military Deployment", "08=Moved", "09=Incarcerated", "10=Died", "11=Agency closed/No longer in business"],
            key="reason_for_discharge",
            on_change=update_form_field,
            args=("reason_for_discharge",)
        )
    else:
        st.session_state.form_data["discharge_date"] = ""
        st.session_state.form_data["date_of_last_contact"] = ""
        st.session_state.form_data["type_of_discharge"] = ""
        st.session_state.form_data["discharge_termination_referral"] = ""
        st.session_state.form_data["reason_for_discharge"] = ""
    
    # Add buttons in columns for better layout
    col1, col2 = st.columns(2)
    with col1:
        clear_button = st.button('Clear Form', on_click=clear_form)
    with col2:
        generate_button = st.button('Generate Client Data JSON')
    
    if generate_button:
        client_data = {
            "First contact date": st.session_state.form_data["first_contact_date"],
            "Date of admission": st.session_state.form_data["date_of_admission"],
            "Medicaid RAE": st.session_state.form_data["medicaid_rae"],
            "Medicaid ID": st.session_state.form_data["medicaid_id"],
            "Healthie ID": st.session_state.form_data["healthie_id"],
            "Date of birth": st.session_state.form_data["date_of_birth"],
            "First Name": st.session_state.form_data["first_name"],
            "Last Name": st.session_state.form_data["last_name"],
            "Gender": st.session_state.form_data["gender"],
            "County of residence": st.session_state.form_data["county_of_residence"],
            "Zip code": st.session_state.form_data["zip_code"],
            "Staff ID": st.session_state.form_data["staff_id"],
            "Primary Diagnosis ICD10 code": st.session_state.form_data["primary_diagnosis_icd10"],
            "Type of insurance": st.session_state.form_data["type_of_insurance"],
            "Action type": st.session_state.form_data["action_type"],
            "Update type": st.session_state.form_data["update_type"],
            "Discharge Date": st.session_state.form_data["discharge_date"],
            "Date of Last Contact": st.session_state.form_data["date_of_last_contact"],
            "Type of Discharge": st.session_state.form_data["type_of_discharge"],
            "Discharge/Termination Referral": st.session_state.form_data["discharge_termination_referral"],
            "Reason for Discharge": st.session_state.form_data["reason_for_discharge"]
        }
        
        # Check that all required fields have values
        required_fields = ["First contact date", "Healthie ID", "Date of birth", "First Name", "Last Name", "Gender", "County of residence", "Zip code", "Staff ID", "Primary Diagnosis ICD10 code", "Type of insurance", "Action type"]
        
        # Add conditional required fields
        if action_type in ["Admission", "Evaluation Only"]:
            required_fields.append("Date of admission")
            
        missing_fields = [field for field in required_fields if not client_data[field]]
        
        if missing_fields:
            st.error(f"Missing required fields: {', '.join(missing_fields)}")
        else:
            # Display the JSON data in a text area for manual copying
            st.text_area("Client Data JSON", json.dumps(client_data), height=200)
            st.success("Client data ready to be copied")

# Function to parse fixed-width text into a dictionary
def parse_fixed_width_text(text, config_df):
    """Parse fixed-width text based on config_df specifications."""
    fields = {}
    text = text.strip()
    
    if not text:
        return fields
    
    # Sort config by order to ensure correct parsing
    sorted_config = config_df.sort_values('order')
    
    # Keep track of the current position in the text
    pos = 0
    
    for _, row in sorted_config.iterrows():
        field_name = row['name']
        length = int(row['length'])
        
        # Extract the value for this field
        if pos < len(text):
            # Get the slice of text for this field
            value = text[pos:pos+length].strip()
            
            # Store non-empty values
            if value:
                fields[field_name] = value
            
            # Move to the next position
            pos += length
        else:
            # We've reached the end of the text
            break
    
    return fields

# Function to merge two JSON objects based on json_priority
def merge_json_by_priority(json1, json2, config_df):
    # Create a copy of the first JSON as the base
    merged_json = json1.copy()
    
    # Create a mapping of field names to their priority
    field_priorities = {}
    for _, row in config_df.iterrows():
        field_name = row['name']
        # Default to 'admissions' if json_priority not specified
        priority = row.get('json_priority', 'admissions')
        field_priorities[field_name] = priority
    
    # Merge fields from json2 based on priority
    for field_name, value in json2.items():
        # Skip empty values
        if not value:
            continue
            
        # If field exists in json1 and has value, check priority
        if field_name in json1 and json1[field_name]:
            # Get priority for this field (default to 'admissions' if not found)
            priority = field_priorities.get(field_name, 'admissions')
            
            # If priority is 'discharge', use json2's value
            if priority == 'discharge':
                merged_json[field_name] = value
        else:
            # If field doesn't exist in json1 or has no value, use json2's value
            merged_json[field_name] = value
    
    return merged_json

# Input Client JSON Data
st.header("Paste Clinical Notes AI output here")

# Create two tabs for JSON inputs
tab1, tab2 = st.tabs(["Primary JSON", "Secondary JSON (Optional)"])

with tab1:
    json_input_primary = st.text_area("Paste primary JSON here (e.g., {'field_A': 'X'})")

with tab2:
    st.info("You can provide either a secondary JSON or fixed-width text. Values will be merged based on json_priority in config.csv.")
    secondary_input = st.text_area("Paste secondary input here (JSON or fixed-width text)", "",
                                help="The system will automatically detect if this is JSON or fixed-width format")

# Option to enable merging
enable_merge = st.checkbox("Merge both JSON inputs", 
                         value=False, 
                         help="When checked, both JSON inputs will be merged according to priority rules")

process_button = st.button("Process Client Data")

# Process JSON Data
if process_button:
    try:
        # Clean the input by removing everything before the opening curly brace
        cleaned_input_primary = json_input_primary[json_input_primary.find('{'):] if '{' in json_input_primary else json_input_primary
        
        # Parse primary JSON
        fields = json.loads(cleaned_input_primary)
        if not isinstance(fields, dict):
            st.error("Primary JSON must be a dictionary")
        else:
            # Check if we need to merge with secondary input
            if enable_merge and secondary_input.strip():
                secondary_data = {}
                merge_occurred = False
                
                # Detect if the input is JSON or fixed-width text
                try:
                    # First try to parse as JSON
                    if '{' in secondary_input:
                        # Clean and parse as JSON
                        cleaned_input_secondary = secondary_input[secondary_input.find('{'):]
                        secondary_data_json = json.loads(cleaned_input_secondary)
                        
                        if not isinstance(secondary_data_json, dict):
                            st.error("Secondary JSON must be a dictionary")
                        else:
                            # Add to secondary data
                            secondary_data.update(secondary_data_json)
                            merge_occurred = True
                            st.success("Successfully parsed secondary input as JSON")
                    else:
                        # Try to parse as fixed-width text
                        fixed_width_data = parse_fixed_width_text(secondary_input, st.session_state['config_df'])
                        
                        if fixed_width_data:
                            # Add to secondary data
                            secondary_data.update(fixed_width_data)
                            merge_occurred = True
                            st.success("Successfully parsed secondary input as fixed-width text")
                        else:
                            # If no data was parsed, try JSON again without the curly brace check
                            try:
                                secondary_data_json = json.loads(secondary_input)
                                if isinstance(secondary_data_json, dict):
                                    secondary_data.update(secondary_data_json)
                                    merge_occurred = True
                                    st.success("Successfully parsed secondary input as JSON")
                                else:
                                    st.error("Secondary input could not be parsed as either JSON or fixed-width text")
                            except json.JSONDecodeError:
                                st.error("Could not parse secondary input - it doesn't appear to be valid JSON or fixed-width text")
                    
                    # Merge the data if we have secondary data
                    if secondary_data and merge_occurred:
                        fields = merge_json_by_priority(fields, secondary_data, st.session_state['config_df'])
                        st.success("Successfully merged inputs based on priority rules")
                        
                except Exception as e:
                    st.error(f"Error processing secondary input: {e}")
            
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
        st.error("Invalid primary JSON input")
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
# This section is hidden but kept for future use
show_fixed_length_section = False  # Set to True to show this section
if show_fixed_length_section:
    st.header("Paste Fixed-Length Text")
    fixed_length_text = st.text_area("Paste fixed-length text here")

    # Button to process the pasted fixed-length text
    if st.button("Process Pasted Text"):
        if fixed_length_text:
            st.session_state['lines'] = fixed_length_text.split('\n')
            st.success("Pasted text processed and added to text file")
        else:
            st.error("No text to process")

# Verify Client Data
st.header("Verify Client Data")

# Toggle for showing/hiding verification sections
show_verification = st.checkbox("Show verification sections", value=False)

if show_verification:
    # Verify Client Data (Individual Clients)
    st.subheader("Individual Client Data")
    st.markdown("Select a client to verify their individual field values based on the fixed-length format.")
    if st.session_state['lines']:
        # Create a list of client names for the selectbox
        client_names = []
        client_data_list = []
        
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
            
            client_names.append(label)
            client_data_list.append(client_data)
        
        # Create a selectbox for choosing a client
        selected_client_index = st.selectbox("Select a client to view details", range(len(client_names)), format_func=lambda i: client_names[i])
        
        # Display the selected client's data
        st.subheader(f"Details for {client_names[selected_client_index]}")
        df = pd.DataFrame(list(client_data_list[selected_client_index].items()), columns=["Field", "Value"])
        st.dataframe(df)
    else:
        st.info("No client data to verify")

    # Verify Client Data (Table View)
    st.subheader("All Clients Data Table")
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