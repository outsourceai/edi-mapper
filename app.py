import os
import sys
import streamlit as st
from loguru import logger

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Set up basic app configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="EDI 944 Converter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run the full application
try:
    # Import the main function
    from app.main import main
    # Run the main function - this will generate the entire UI
    main()
except Exception as e:
    st.error(f"Error loading the application: {str(e)}")
    logger.exception("Error in app.py:") 