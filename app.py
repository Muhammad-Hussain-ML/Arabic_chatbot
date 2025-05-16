import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API URL from the .env file
API_URL = os.getenv("API_URL")

# Define the chat interface function
def chat_interface():
    """Testing Chatbot Interface."""
    
    st.markdown("<style>h1 { margin-top: -50px; }</style>", unsafe_allow_html=True)
    
    # Create a layout with columns for the title and dropdown
    col1, col2 = st.columns([3, 1])
    
    # Title in the first column
    with col1:
        st.title("💬 Interface for Testing Chatbot.")
    
    # Language dropdown in the second column
    with col2:
        # Get the current language from session state or default to English
        if "language" not in st.session_state:
            st.session_state["language"] = "English"
        
        # Create the dropdown
        selected_language = st.selectbox(
            "Select Language",
            options=["English", "Arabic"],
            index=0 if st.session_state["language"] == "English" else 1,
            key="language_selector"
        )
        
        # Check if language has changed
        if selected_language != st.session_state["language"]:
            st.session_state["language"] = selected_language
            st.session_state["messages"] = []  # Clear messages
            st.session_state["api_history"] = []  # Clear API history
            st.rerun()  # Refresh the page
    
    # Set the unique_id based on selected language
    if st.session_state["language"] == "Arabic":
        unique_id = os.getenv("Unique_ID_Arabic")
    else:
        unique_id = os.getenv("Unique_ID_Eng")
    
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
    
    # Change placeholder text based on language
    placeholder_text = "أدخل سؤالك هنا..." if st.session_state["language"] == "Arabic" else "Ask a query..."
    
    # Chat input field for user query
    if query := st.chat_input(placeholder_text):
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
                response = requests.post(API_URL, json=data, stream=True, headers={'Content-Type': 'application/json; charset=utf-8'})
                
                # Stream the response in smaller chunks for smoother streaming
                for chunk in response.iter_content(chunk_size=64):  # Smaller chunks for more frequent updates
                    if chunk:
                        try:
                            decoded_chunk = chunk.decode('utf-8')  # Attempt to decode
                        except UnicodeDecodeError:
                            decoded_chunk = chunk.decode('utf-8', errors='replace')
                        
                        response_text += decoded_chunk
                        # Update the display with each chunk to show streaming effect
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
    st.markdown('<meta charset="UTF-8">', unsafe_allow_html=True)
    # Call the chat interface function
    chat_interface()
