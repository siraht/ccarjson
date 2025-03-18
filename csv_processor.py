import pandas as pd
import csv
import io

def process_csv_to_fixed_length(csv_text, csv_to_fl_config):
    """
    Process CSV formatted text into fixed length text according to csvToFL.csv specifications.
    Assumes columns are in the correct order without headers.
    
    Args:
        csv_text (str): CSV formatted text input
        csv_to_fl_config (pd.DataFrame): Configuration from csvToFL.csv with order, name, output_length, alignment
        
    Returns:
        str: Fixed-length formatted text
    """
    # Read the CSV input text into a DataFrame without headers
    try:
        # Use header=None to indicate there are no headers, and assign column indexes
        csv_input = pd.read_csv(io.StringIO(csv_text), header=None)
    except Exception as e:
        return f"Error parsing CSV: {str(e)}"
    
    # Prepare output
    output_lines = []
    
    # Process each row in the CSV input
    for _, row in csv_input.iterrows():
        line_parts = []
        
        # Format each field according to the configuration
        # Sort config by order to ensure fields are processed in the correct sequence
        for idx, config_row in enumerate(csv_to_fl_config.sort_values('order').itertuples()):
            # Get the value from the CSV input using the column index
            if idx < len(row) and pd.notna(row[idx]):
                value = str(row[idx])
            else:
                value = ""
                
            # Apply length and alignment
            output_length = int(config_row.output_length)
            alignment = config_row.alignment
            
            if output_length > 0:  # Skip fields with 0 length
                if alignment == 'right':
                    formatted_value = value.rjust(output_length)
                else:  # left alignment
                    formatted_value = value.ljust(output_length)
                
                # Ensure the value doesn't exceed the specified length
                formatted_value = formatted_value[:output_length]
                line_parts.append(formatted_value)
        
        # Join all parts for this row and add to output
        output_lines.append(''.join(line_parts))
    
    return '\n'.join(output_lines)

def validate_csv_input(csv_text, csv_to_fl_config):
    """
    Basic validation for CSV input - just checks if it can be parsed.
    Assumes columns are in the correct order without headers.
    
    Args:
        csv_text (str): CSV formatted text input
        csv_to_fl_config (pd.DataFrame): Configuration from csvToFL.csv
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Just try to parse the CSV to see if it's valid
        csv_input = pd.read_csv(io.StringIO(csv_text), header=None)
        
        # Get the number of expected columns from the config
        expected_column_count = len(csv_to_fl_config)
        
        # Check if we have enough data in at least one row
        if csv_input.shape[0] == 0:
            return False, "CSV input is empty"
            
        # Basic validation passed
        return True, "CSV input is valid"
    except Exception as e:
        return False, f"Error validating CSV: {str(e)}"
