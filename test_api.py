import streamlit as st
import os
from loguru import logger

def test_openai():
    """Simple OpenAI API test using LangChain."""
    st.title("OpenAI API Test using LangChain")
    st.write("This tool will test your OpenAI API key using LangChain")
    
    # Input API key
    api_key = st.text_input("Enter your OpenAI API key", type="password")
    
    # Test button
    if st.button("Test API Connection"):
        if not api_key:
            st.error("Please enter an API key")
            return
            
        try:
            # Import ChatOpenAI instead of OpenAI for chat models
            from langchain_openai import ChatOpenAI
            
            st.info("Testing API connection with LangChain ChatOpenAI...")
            
            # Create a LangChain ChatOpenAI instance for chat models
            llm = ChatOpenAI(
                temperature=0,
                api_key=api_key,
                model_name="gpt-3.5-turbo"
            )
            
            # Make a simple request
            response = llm.invoke("Say hello")
            
            # Display result
            st.success(f"API call successful! Response: {response}")
            
            # Option to continue
            if st.button("Continue to main app"):
                # Save the API key to environment variable
                os.environ["OPENAI_API_KEY"] = api_key
                # Redirect to main app
                import subprocess
                subprocess.Popen(["streamlit", "run", "app.py"])
                st.stop()
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.write("Detailed error information for debugging:")
            st.code(str(e))
            
            # Common troubleshooting tips
            st.subheader("Troubleshooting Tips")
            st.markdown("""
            - Check if your API key is valid and has sufficient credits
            - Ensure you have proper internet connectivity
            - If the error mentions 'openai.RateLimitError', wait a few minutes and try again
            - If issues persist, try using the API key in another application to verify it works
            """)

if __name__ == "__main__":
    test_openai() 