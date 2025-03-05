import streamlit as st
import pandas as pd
import json
import os

# App title and instructions
st.title("Fixed-Length Text File Generator")
st.markdown("""
This app processes client data from JSON input into a fixed-length text file based on a predefined configuration.
- **Step 1**: Ensure `config.csv` is in the app directory.
- **Step 2**: Paste JSON data for a client and click "Process Client Data" to add it to the text file.
- **Step 3**: Preview the text file, download it as `clients_data.txt`, or clear its contents.
""")

# Initialize session state for text file lines and configuration
if 'lines' not in st.session_state:
    st.session_state['lines'] = []

if 'config_df' not in st.session_state:
    st.session_state['config_df'] = None

# Load configuration file from app directory
config_file_path = 'config.csv'
if os.path.exists(config_file_path):
    try:
        df = pd.read_csv(config_file_path)
        required_columns = ['order', 'name', 'length', 'alignment']
        if not all(col in df.columns for col in required_columns):
            st.error("Configuration file must contain columns: order, name, length, alignment")
        else:
            st.session_state['config_df'] = df
            st.success("Configuration file loaded successfully")
    except Exception as e:
        st.error(f"Error reading configuration file: {e}")
else:
    st.error(f"Configuration file '{config_file_path}' not found in the app directory")

# Section 1: Input Client JSON Data
st.header("Input Client JSON Data")
json_input = st.text_area("Paste JSON here (e.g., {'name': 'John', 'id': '123'})")
process_button = st.button("Process Client Data")

# Section 2: Process JSON Data
if process_button:
    if st.session_state['config_df'] is None:
        st.error("Configuration file is not loaded properly. Check the error message above.")
    else:
        try:
            # Parse JSON input
            data = json.loads(json_input)
            if not isinstance(data, dict):
                st.error("JSON must be a dictionary")
            else:
                # Get configuration DataFrame
                config_df = st.session_state['config_df']
                line = ""
                # Process each field in order
                for _, row in config_df.sort_values('order').iterrows():
                    field_name = row['name']
                    length = int(row['length'])
                    alignment = row['alignment'].lower()
                    # Remove all whitespace from the value
                    value = ''.join(str(data.get(field_name, '')).split())
                    # Format based on alignment
                    if alignment == 'left':
                        formatted_value = value[:length].ljust(length)
                    elif alignment == 'right':
                        formatted_value = value[:length].rjust(length)
                    else:
                        st.error(f"Invalid alignment for field {field_name}: {alignment}")
                        break
                    line += formatted_value
                else:
                    # If no errors, append line to text file
                    st.session_state['lines'].append(line)
                    st.success("Client data processed and added to text file")
        except json.JSONDecodeError:
            st.error("Invalid JSON input")
        except Exception as e:
            st.error(f"Error processing data: {e}")

# Section 3: Preview Text File
st.header("Preview Text File")
if st.session_state['lines']:
    preview_text = '\n'.join(st.session_state['lines'])
    st.code(preview_text, language='text')  # Display as preformatted text
else:
    st.info("No data in text file yet")

# Section 4: Manage Text File (Download or Clear)
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
