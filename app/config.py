import streamlit as st
from dotenv import load_dotenv
import os
from loguru import logger
import datetime
import tempfile

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize logger
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, f"app_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logger.add(log_file, rotation="10 MB", retention="7 days", level="INFO")

def init_session_state():
    """Initialize session state variables"""
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = ""
        
    if 'temp_file_path' not in st.session_state:
        st.session_state['temp_file_path'] = None
        
    if 'conversion_history' not in st.session_state:
        st.session_state['conversion_history'] = []
        
    # Initialize conversion mode if not already set
    if 'conversion_mode' not in st.session_state:
        st.session_state['conversion_mode'] = "standard"

def save_api_key(api_key):
    """Save API key to session state"""
    st.session_state['api_key'] = api_key
    logger.info("API key saved to session state")

def get_api_key():
    """Get API key from session state or environment"""
    # First check session state
    if st.session_state['api_key']:
        return st.session_state['api_key']
    
    # Then check environment variable
    env_api_key = os.environ.get("OPENAI_API_KEY", "")
    if env_api_key:
        # If found in environment, save to session state
        save_api_key(env_api_key)
        return env_api_key
        
    return ""
    
def set_conversion_mode(mode):
    """Set the conversion mode in session state"""
    if mode in ["standard", "synapse"]:
        st.session_state['conversion_mode'] = mode
        logger.info(f"Conversion mode set to {mode}")
    else:
        logger.warning(f"Invalid conversion mode: {mode}")
        
def get_conversion_mode():
    """Get the current conversion mode from session state"""
    return st.session_state.get('conversion_mode', "standard") 