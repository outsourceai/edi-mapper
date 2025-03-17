import streamlit as st
import pandas as pd
import os
import base64
from loguru import logger

# Import our custom modules
from app.config import init_session_state, save_api_key, get_api_key
# Use ChatOpenAI instead of OpenAI for chat models
from langchain_openai import ChatOpenAI

# Custom CSS styling
def apply_custom_css():
    st.markdown("""
    <style>
        .main {
            background-color: #f5f7f9;
        }
        .stTextArea textarea {
            font-family: monospace;
        }
        .success-msg {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .error-msg {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .info-box {
            background-color: #e2f0fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .output-box {
            background-color: #272822;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 5px;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            padding: 10px 20px;
        }
        .stTextInput>div>div>input {
            border: 1px solid #ddd;
            padding: 8px;
        }
        .mode-selector {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: flex;
            justify-content: center;
        }
        .tab-content {
            padding-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

def get_download_link(file_path, link_text):
    """Generate a download link for a file"""
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
        
        b64 = base64.b64encode(file_content.encode()).decode()
        filename = os.path.basename(file_path)
        return f'<a href="data:text/plain;base64,{b64}" download="{filename}">{link_text}</a>'
    except Exception as e:
        logger.error(f"Error generating download link: {str(e)}")
        return None

def validate_api_key(api_key):
    """Validate the OpenAI API key using LangChain."""
    try:
        # Basic length check
        if not api_key or len(api_key.strip()) < 10:
            return False
            
        # Create a LangChain LLM with ChatOpenAI for chat models
        logger.info("Testing OpenAI API key with LangChain ChatOpenAI")
        llm = ChatOpenAI(
            temperature=0,
            api_key=api_key,
            model_name="gpt-3.5-turbo"
        )
        
        # Make a simple request
        response = llm.invoke("Hello")
        logger.info("API key validation successful")
        return True
    except Exception as e:
        logger.error(f"API key validation error: {str(e)}")
        return False

def main():
    """Main application function"""
    # Note: set_page_config() is already called in app.py, so we don't call it here
    
    # Initialize session state
    init_session_state()
    
    # Apply custom CSS
    apply_custom_css()
    
    # App header
    st.title("EDI 944 Converter")
    st.markdown("""
    <div class="info-box">
        This application converts tabular EDI 944 data to standard EDI 944 code format using AI.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for API key configuration
    st.sidebar.title("Configuration")
    
    # Check if API key is already set
    if not get_api_key():
        with st.sidebar.form("api_key_form"):
            api_key = st.text_input("Enter your OpenAI API Key", type="password", 
                                    help="Your API key will not be stored on the server")
            submit_button = st.form_submit_button("Save API Key")
            
            if submit_button:
                if api_key and len(api_key.strip()) > 10:
                    logger.info("Attempting to validate API key")
                    if validate_api_key(api_key):
                        save_api_key(api_key)
                        st.success("API key saved successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid API key. Please check and try again.")
                else:
                    st.error("Please enter a valid API key.")
    else:
        st.sidebar.success("API key is configured ✅")
        if st.sidebar.button("Change API Key"):
            # Clear the API key from session state
            st.session_state['api_key'] = ""
            st.rerun()
            
    # Sidebar tips
    st.sidebar.title("Tips")
    st.sidebar.info("""
    1. Ensure your tabular data is well-formatted
    2. Include all required fields for EDI 944 format
    3. Double-check the generated code before using in production
    4. Choose the appropriate conversion mode for your needs
    """)
    
    # Main content area - only show if API key is configured
    if get_api_key():
        # Create tabs for the main content
        tab1, tab2, tab3 = st.tabs(["Standard EDI 944", "Synapse EDI 944", "Conversion History"])
        
        with tab1:
            st.header("Convert to Standard EDI 944")
            st.markdown("""
            <div class="info-box">
                Convert tabular data to standard EDI 944 format that follows general EDI specifications.
            </div>
            """, unsafe_allow_html=True)
            
            # Input area for tabular data
            st.subheader("Input Tabular Data")
            standard_data = st.text_area(
                "Paste your tabular EDI 944 data here:",
                height=300,
                help="Paste tabular EDI 944 data in standard format",
                key="standard_data"
            )
            
            # Sample data option
            if st.checkbox("Show sample data", key="standard_sample_checkbox"):
                st.info("""
                Here's a sample tabular EDI 944 data format you can use for testing:
                
                Warehouse ID: WH001
                Receipt Date: 2023-10-15
                Receipt Number: RN12345
                Shipment Number: SH67890
                Container Number: CN54321
                Sender ID: SENDER01
                Receiver ID: RECEIVER01
                
                Item Number | Description | Quantity | Unit | Status
                ------------|-------------|----------|------|-------
                ITEM001 | Widget A | 50 | EA | Received
                ITEM002 | Widget B | 25 | CS | Received
                ITEM003 | Widget C | 10 | BX | Damaged
                """)
            
            # Process the data
            standard_convert_button = st.button(
                "Convert to Standard EDI 944", 
                type="primary", 
                key="standard_convert_button"
            )
            
            if standard_convert_button:
                if not standard_data:
                    st.error("Please enter tabular data to convert.")
                else:
                    with st.spinner("Converting data... This may take a moment."):
                        try:
                            # Create a converter with standard mode
                            from app.converter import EDI944Converter
                            converter = EDI944Converter(get_api_key(), mode="standard")
                            
                            # Convert the data
                            edi_code = converter.convert_tabular_to_edi944(standard_data)
                            
                            # Save to file for download
                            file_path = converter.save_to_file(edi_code)
                            st.session_state['temp_file_path'] = file_path
                            
                            # Add to conversion history
                            timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state['conversion_history'].append({
                                "timestamp": timestamp,
                                "mode": "Standard EDI 944",
                                "input": standard_data[:100] + "..." if len(standard_data) > 100 else standard_data,
                                "output": edi_code[:100] + "..." if len(edi_code) > 100 else edi_code,
                                "file_path": file_path
                            })
                            
                            # Display the result
                            st.success("Conversion completed successfully!")
                            st.subheader("Generated Standard EDI 944 Code")
                            st.markdown(f"""
                            <div class="output-box">
                            {edi_code}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Download button
                            download_link = get_download_link(file_path, "Download Standard EDI 944 Code")
                            st.markdown(download_link, unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Error during conversion: {str(e)}")
                            logger.error(f"Conversion error: {str(e)}")
        
        with tab2:
            st.header("Convert to Synapse EDI 944")
            st.markdown("""
            <div class="info-box">
                Convert tabular data to Synapse-specific EDI 944 format that matches the Synapse system requirements.
            </div>
            """, unsafe_allow_html=True)
            
            # Input area for tabular data
            st.subheader("Input Tabular Data")
            synapse_data = st.text_area(
                "Paste your tabular EDI 944 data here:",
                height=300,
                help="Paste tabular EDI 944 data for Synapse format conversion",
                key="synapse_data"
            )
            
            # Sample data option
            if st.checkbox("Show sample data", key="synapse_sample_checkbox"):
                st.info("""
                Here's a sample tabular EDI 944 data format for Synapse conversion:
                
                Customer ID: CUST123
                Transaction Set: 944
                Direction: O
                Synapse Order ID: ORDER456
                Synapse Ship ID: SHIP789
                Warehouse Receipt Number: WRN123-456
                Customer Order Number: CON789-012
                Receipt Date: 2023-11-15
                Shipper: VENDOR001
                Shipper Name: ABC Supplies Inc.
                
                Line | Item | Description | Lot | UOM | Qty Received | Qty Good | Qty Damaged | Qty Ordered | Status
                -----|------|-------------|-----|-----|--------------|----------|-------------|-------------|-------
                1 | ITEM001 | Widget Type A | LOT123 | EA | 100 | 95 | 5 | 100 | Received
                2 | ITEM002 | Widget Type B | LOT124 | CS | 50 | 50 | 0 | 50 | Received
                3 | ITEM003 | Widget Type C | LOT125 | BX | 75 | 65 | 10 | 80 | Partial
                """)
            
            # Process the data
            synapse_convert_button = st.button(
                "Convert to Synapse EDI 944", 
                type="primary", 
                key="synapse_convert_button"
            )
            
            if synapse_convert_button:
                if not synapse_data:
                    st.error("Please enter tabular data to convert.")
                else:
                    with st.spinner("Converting data... This may take a moment."):
                        try:
                            # Create a converter with synapse mode
                            from app.converter import EDI944Converter
                            converter = EDI944Converter(get_api_key(), mode="synapse")
                            
                            # Convert the data
                            edi_code = converter.convert_tabular_to_edi944(synapse_data)
                            
                            # Save to file for download
                            file_path = converter.save_to_file(edi_code)
                            st.session_state['temp_file_path'] = file_path
                            
                            # Add to conversion history
                            timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state['conversion_history'].append({
                                "timestamp": timestamp,
                                "mode": "Synapse EDI 944",
                                "input": synapse_data[:100] + "..." if len(synapse_data) > 100 else synapse_data,
                                "output": edi_code[:100] + "..." if len(edi_code) > 100 else edi_code,
                                "file_path": file_path
                            })
                            
                            # Display the result
                            st.success("Conversion completed successfully!")
                            st.subheader("Generated Synapse EDI 944 Code")
                            st.markdown(f"""
                            <div class="output-box">
                            {edi_code}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Download button
                            download_link = get_download_link(file_path, "Download Synapse EDI 944 Code")
                            st.markdown(download_link, unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"Error during conversion: {str(e)}")
                            logger.error(f"Conversion error: {str(e)}")
            
        with tab3:
            st.header("Conversion History")
            
            if not st.session_state['conversion_history']:
                st.info("No conversion history yet. Convert some data to see it here.")
            else:
                # Display history in reverse chronological order
                for i, entry in enumerate(reversed(st.session_state['conversion_history'])):
                    with st.expander(f"Conversion {len(st.session_state['conversion_history']) - i}: {entry['timestamp']} ({entry.get('mode', 'Standard EDI 944')})"):
                        st.text("Input Preview:")
                        st.text(entry['input'])
                        st.text("Output Preview:")
                        st.text(entry['output'])
                        
                        # Only show download link if file still exists
                        if os.path.exists(entry['file_path']):
                            download_link = get_download_link(
                                entry['file_path'], 
                                f"Download {entry.get('mode', 'EDI 944')} Code"
                            )
                            st.markdown(download_link, unsafe_allow_html=True)
                        else:
                            st.warning("Download file no longer available.")
    else:
        # Show information when no API key is configured
        st.info("Please enter your OpenAI API key in the sidebar to start using the application.")
        
        # Sample UI preview
        st.subheader("Application Preview")
        st.write("Once you configure your API key, you'll be able to:")
        st.markdown("""
        - Choose between Standard EDI 944 and Synapse EDI 944 conversion
        - Input tabular EDI 944 data 
        - Convert it to the appropriate EDI 944 code format
        - Download the generated code
        - View your conversion history
        """)

# Only run main directly when this file is run directly
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        logger.exception("Unhandled exception in main application:") 