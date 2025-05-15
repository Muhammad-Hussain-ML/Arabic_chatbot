import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API URL from the .env file
API_URL = os.getenv("API_URL")
unique_id = os.getenv("Unique_ID")

# Define the chat interface function
def chat_interface():
    """Testing Chatbot Interface."""
    
    st.markdown("<style>h1 { margin-top: -50px; }</style>", unsafe_allow_html=True)
    
    # Create a column layout for the title
    st.title("💬 Interface for Testing Chatbot.")
    
    # Initialize chat history if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        
    # Initialize a separate history array for API requests if it doesn't exist
    if "api_history" not in st.session_state:
        st.session_state["api_history"] = []
    
    # Display previous chat messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input field for user query
    if query := st.chat_input("Ask a query..."):
        # Append user message to chat history
        st.session_state["messages"].append({"role": "user", "content": query})
        
        # Add user query to API history
        st.session_state["api_history"].append(f"User: {query}")
        
        # Display the user's message
        with st.chat_message("user"):
            st.markdown(query)
        
        # Prepare data for the API request, including the full history
        data = {
            "query": query,
            "unique_id": unique_id,
            "history": st.session_state["api_history"]
        }
        
        # Placeholder for assistant response (streaming)
        with st.chat_message("assistant"):
            response_container = st.empty()  # Placeholder for response streaming
            response_text = ""
            
            try:
                # Send POST request with streaming response
                response = requests.post(API_URL, json=data, stream=True)
                
                # Stream the response character by character
                for char in response.iter_content(chunk_size=1024):
                    if char:
                        try:
                            chunk = char.decode('utf-8')  # Attempt to decode
                        except UnicodeDecodeError:
                            chunk = char.decode('utf-8', errors='replace')
                        response_text += chunk
                
                response_container.markdown(response_text)
                
                # Append assistant response to chat history
                st.session_state["messages"].append({"role": "assistant", "content": response_text})
                
                # Add assistant response to API history
                st.session_state["api_history"].append(f"Assistant: {response_text}")
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to API: {e}")

# Main block to run the Streamlit app
if __name__ == "__main__":
    # Set the page configuration (optional)
    st.set_page_config(page_title="Chat Interface", layout="wide")
    
    # Call the chat interface function
    chat_interface()

