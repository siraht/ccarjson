import streamlit as st

# Callback functions to update session state when inputs change
def update_form_field(field):
    st.session_state.form_data[field] = st.session_state[field]

# Function to clear all form fields
def clear_form():
    # Reset form data to default values
    st.session_state.form_data = {
        'first_contact_date': "",
        'action_type': "Admission",
        'effective_date': "",
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

# Initialize form data in session state
def initialize_form_data():
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'action_type': "Admission",
            'first_contact_date': "",
            'effective_date': "",
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

# Function to render the additional information form
def render_additional_info_form():
    with st.expander("## Additional information Form"):
        # Action type selection (affects visibility of other fields)
        action_type = st.selectbox(
            "Action type", 
            ["Admission", "Update", "Discharge", "Evaluation Only"],
            key="action_type",
            on_change=update_form_field,
            args=("action_type",)
        )
        
        # Common fields for all action types except Discharge
        if action_type != "Discharge":
            col1, col2 = st.columns(2)
            with col1:
                first_contact_date = st.text_input(
                    "First contact date", 
                    value=st.session_state.form_data["first_contact_date"],
                    key="first_contact_date",
                    on_change=update_form_field,
                    args=("first_contact_date",)
                )
        
        # Show Effective Date for all action types
        col1, col2 = st.columns(2)
        with col1:
            effective_date = st.text_input(
                "Effective Date", 
                value=st.session_state.form_data["effective_date"],
                key="effective_date",
                help="This date will be used as Date of Admission for Admission actions or Discharge Date for Discharge actions",
                on_change=update_form_field,
                args=("effective_date",)
            )
        
        # Insurance information - hide for Discharge
        if action_type != "Discharge":
            type_of_insurance = st.selectbox(
                "Type of insurance", 
                ["Medicaid", "CHP+", "Commercial", "Self-pay"],
                key="type_of_insurance",
                on_change=update_form_field,
                args=("type_of_insurance",)
            )
        
        # Only show Medicaid fields for certain insurance types and not for Discharge
        if action_type != "Discharge" and st.session_state.form_data["type_of_insurance"] in ["Medicaid", "CHP+"]:
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
        
        # Client identification fields - hide for Discharge
        if action_type != "Discharge":
            col1, col2 = st.columns(2)
            with col1:
                healthie_id = st.text_input(
                    "Healthie ID", 
                    value=st.session_state.form_data["healthie_id"],
                    key="healthie_id",
                    on_change=update_form_field,
                    args=("healthie_id",)
                )
        if action_type != "Discharge":
            with col2:
                date_of_birth = st.text_input(
                    "Date of birth", 
                    value=st.session_state.form_data["date_of_birth"],
                    key="date_of_birth",
                    on_change=update_form_field,
                    args=("date_of_birth",)
                )
        
        if action_type != "Discharge":
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
        
        # Gender selection - hide for Discharge
        if action_type != "Discharge":
            gender = st.selectbox(
                "Gender", 
                ["1-Male", "2-Female", "3-Other", "4-Unknown"],
                key="gender",
                on_change=update_form_field,
                args=("gender",)
            )
        
        # Location information - hide for Discharge
        if action_type != "Discharge":
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
        
        # Staff and diagnosis information
        col1, col2 = st.columns(2)
        with col1:
            staff_id = st.text_input(
                "Staff ID", 
                value=st.session_state.form_data["staff_id"],
                key="staff_id",
                on_change=update_form_field,
                args=("staff_id",)
            )
        if action_type != "Discharge":
            with col2:
                primary_diagnosis_icd10 = st.text_input(
                    "Primary Diagnosis ICD10 code", 
                    value=st.session_state.form_data["primary_diagnosis_icd10"],
                    key="primary_diagnosis_icd10",
                    on_change=update_form_field,
                    args=("primary_diagnosis_icd10",)
                )
        
        # Update type for Update action
        if action_type == "Update":
            update_type = st.selectbox(
                "Type of Update", 
                ["1-Demographics", "2-Diagnosis", "3-Both"],
                key="update_type",
                on_change=update_form_field,
                args=("update_type",)
            )
        else:
            st.session_state.form_data["update_type"] = ""
        
        # Discharge fields for Discharge action
        if action_type == "Discharge":
            # Use Effective Date as Discharge Date, no need to show a separate field
            # Set discharge_date to effective_date value in session state
            st.session_state.form_data["discharge_date"] = st.session_state.form_data["effective_date"]
            
            col1, col2 = st.columns(2)
            with col1:
                date_of_last_contact = st.text_input(
                    "Date of last contact", 
                    value=st.session_state.form_data["date_of_last_contact"],
                    key="date_of_last_contact",
                    on_change=update_form_field,
                    args=("date_of_last_contact",)
                )
                
            type_of_discharge = st.selectbox(
                "Type of Discharge", 
                ["1– Treatment completed", "2– Evaluation only", "3– Referred elsewhere", "4– Terminated"],
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
            clear_button = st.button('Clear Form', on_click=clear_form, key='clear_form_button_additional_info')
        with col2:
            generate_button = st.button('Generate Client Data JSON', key='generate_button_additional_info')
        
        return generate_button, action_type

# Import the action type map
from action_type_map import ACTION_TYPE_MAP

# Function to generate client data dictionary from form data
def generate_client_data():
    action_type = st.session_state.form_data["action_type"]
    action_type_code = ACTION_TYPE_MAP.get(action_type, "")
    
    client_data = {
        "First contact date": st.session_state.form_data["first_contact_date"],
        "Effective Date": st.session_state.form_data["effective_date"],
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
        "Action Type": action_type_code,
        "Update type": st.session_state.form_data["update_type"],
        "Date of Last Contact": st.session_state.form_data["date_of_last_contact"],
        "Type of Discharge": st.session_state.form_data["type_of_discharge"][0] if st.session_state.form_data["type_of_discharge"] else "",
        "Discharge/Termination Referral": st.session_state.form_data["discharge_termination_referral"],
        "Reason for Discharge": st.session_state.form_data["reason_for_discharge"]
    }
    
    # Check that all required fields have values based on action type
    required_fields = ["Staff ID", "Action Type"]
    
    # Add Healthie ID as required for non-Discharge action types
    if action_type != "Discharge":
        required_fields.append("Healthie ID")
    
    # Add fields that are only required for non-Discharge action types
    if action_type != "Discharge":
        additional_required_fields = ["First contact date", "Date of birth", "First Name", "Last Name", "Gender", "County of residence", "Zip code", "Primary Diagnosis ICD10 code", "Type of insurance"]
        required_fields.extend(additional_required_fields)
    
    # Add conditional required fields
    required_fields.append("Effective Date")
    
    # Add Date of Admission or Discharge Date based on Action Type
    if action_type == "Admission" or action_type == "Evaluation Only":
        client_data["Date of admission"] = st.session_state.form_data["effective_date"]
    elif action_type == "Discharge":
        # For Discharge, use the Effective Date as the Discharge Date
        client_data["Discharge Date"] = st.session_state.form_data["effective_date"]
        # Also update the discharge_date in session state to match effective_date
        st.session_state.form_data["discharge_date"] = st.session_state.form_data["effective_date"]
    
    missing_fields = [field for field in required_fields if not client_data.get(field, "")]
    
    if missing_fields:
        st.error(f"Please fill in the following required fields: {', '.join(missing_fields)}")
        return None
    
    return client_data
