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
    st.write(API_URL)

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
            "Select an Hospital",
            options=["Sidra Medicine English", "Sidra Medicine Arabic","Abid Hospital", "Pak Health Consultant", "IICI", "EMRChains", "EMRChains_Arabic"],
            # index=0 if st.session_state["language"] == "English" else 1,
            index=0 if st.session_state["language"] == "Sidra Medicine English" else (
                1 if st.session_state["language"] == "Sidra Medicine Arabic" else (
                    2 if st.session_state["language"] == "Abid Hospital" else (
                        3 if st.session_state["language"] == "Pak Health Consultant" else (
                            4 if st.session_state["language"] == "IICI" else (
                                5 if st.session_state["language"] == "EMRChains" else (
                                    6 if st.session_state["language"] == "EMRChains_Arabic" else 0
                                )
                            )
                        )
                    )
                )
            ),
            key="language_selector"
        )
        
        # Check if language has changed
        if selected_language != st.session_state["language"]:
            st.session_state["language"] = selected_language
            st.session_state["messages"] = []  # Clear messages
            st.session_state["api_history"] = []  # Clear API history
            st.rerun()  # Refresh the page
    
    # Set the unique_id based on selected language
    if st.session_state["language"] == "Sidra Medicine Arabic":
        unique_id = os.getenv("Unique_ID_Arabic")
    elif st.session_state["language"] == "Abid Hospital":
        unique_id = os.getenv("Unique_ID_Abid_Hospital")
    elif st.session_state["language"] == "Pak Health Consultant":
        unique_id = os.getenv("Unique_ID_Pak_Health")
    elif st.session_state["language"] == "EMRChains":
        unique_id = os.getenv("Unique_ID_EMRChains")
    elif st.session_state["language"] == "IICI":
        unique_id = os.getenv("Unique_ID_IICI")
    elif st.session_state["language"] == "EMRChains_Arabic":
        unique_id = os.getenv("Unique_ID_EMRChains_Arabic")
    else :
        unique_id = os.getenv("Unique_ID_Eng")
    # st.write(unique_id)
    # Initialize chat history if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        
    # Initialize a separate history array for API requests if it doesn't exist
    if "api_history" not in st.session_state:
        st.session_state["api_history"] = []
    
    # Display previous chat messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            if st.session_state["language"] == "Arabic":
                # Add RTL direction for Arabic messages
                html_content = f'<div dir="rtl" style="text-align: right;">{msg["content"]}</div>'
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])
    
    # Change placeholder text based on language
    placeholder_text = "أدخل سؤالك هنا..." if st.session_state["language"] == "Arabic" else "Ask a query..."
    
    # Add RTL support for Arabic
    if st.session_state["language"] == "Arabic":
        st.markdown("""
        <style>
        .element-container, .stTextInput, .stButton, .css-1p0bytv {
            direction: rtl;
            text-align: right;
        }
        </style>
        """, unsafe_allow_html=True)
        
    # Chat input field for user query
    if query := st.chat_input(placeholder_text):
        # Append user message to chat history
        st.session_state["messages"].append({"role": "user", "content": query})
        
        # Add user query to API history
        st.session_state["api_history"].append(f"User: {query}")
        
        # Display the user's message
        with st.chat_message("user"):
            if st.session_state["language"] == "Arabic":
                html_content = f'<div dir="rtl" style="text-align: right;">{query}</div>'
                st.markdown(html_content, unsafe_allow_html=True)
            else:
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
                # Send POST request with streaming response with additional headers
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Accept': 'text/plain; charset=utf-8',
                    'Accept-Encoding': 'identity'
                }
                response = requests.post(API_URL, json=data, stream=True, headers=headers)
                
                # Use the same approach that works in Jupyter notebook
                for chunk in response.iter_content(chunk_size=64, decode_unicode=True):
                    if chunk:
                        response_text += chunk
                        
                        # Display with proper RTL formatting for Arabic
                        if st.session_state["language"] == "Arabic":
                            html_content = f'<div dir="rtl" style="text-align: right;">{response_text}</div>'
                            response_container.markdown(html_content, unsafe_allow_html=True)
                        else:
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
    
    # Add explicit UTF-8 encoding meta tag
    st.markdown('<meta charset="UTF-8">', unsafe_allow_html=True)
    
    # Call the chat interface function
    chat_interface()
