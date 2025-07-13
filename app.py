# FunnX.Ai/app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Ensure this URL is correct. It should be the same as your Flask app's default.


FLASK_API_URL = "https://funnx-ai-backend.onrender.com"


# Set Streamlit page configuration
st.set_page_config(page_title="FunnX.Ai", layout="wide")

# --- Session State Initialization ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "page" not in st.session_state:
    st.session_state["page"] = "home" # Default page if not authenticated
if "messages" not in st.session_state: # Initialize chat messages for the session
    st.session_state["messages"] = []

# --- Helper Function: Call Flask API ---
def call_flask_api(endpoint, data):
    try:
        # Added a timeout to prevent infinite waiting
        response = requests.post(f"{FLASK_API_URL}/{endpoint}", json=data, timeout=30)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Backend at {FLASK_API_URL} not running or reachable. Please start your Flask backend (`python api.py`).")
        return {"error": "Backend not reachable."}
    except requests.exceptions.Timeout:
        st.error(f"Backend request timed out. The server might be slow or unresponsive. (URL: {FLASK_API_URL}/{endpoint})")
        return {"error": "Request timed out."}
    except requests.exceptions.HTTPError as e:
        error_details = {}
        try:
            # Try to parse JSON error details from backend
            error_details = e.response.json()
        except requests.exceptions.JSONDecodeError:
            # If not JSON, use raw text
            error_details = {"message": e.response.text}

        st.error(f"Backend returned an error: {e.response.status_code} - {error_details.get('error', error_details.get('message', 'Unknown backend error'))}")
        return {"error": str(e)}
    except Exception as e:
        st.error(f"An unexpected error occurred while calling the backend: {e}")
        return {"error": str(e)}

# --- Inject Custom CSS (Permanent Dark Mode & Chat Bubbles) ---
# st.markdown(
#     """
#     <style>
#     /* Overall App Styling (Dark Mode) */
#     .stApp {
#         background-color: #1a1a1a; /* Main background */
#         color: #ffffff; /* Default text color */
#     }

#     /* Input fields and select boxes */
#     .stTextInput>div>div>input, .stTextArea>div>div>textarea,
#     .stSelectbox>div>div>div { /* Target selectbox display area */
#         background-color: #333333; /* Darker grey for inputs/selects */
#         color: #ffffff; /* White text in inputs */
#         border: 1px solid #555555;
#     }
#     .stSelectbox>div>div>div:focus { /* Focus state for selectbox */
#         border-color: #007bff;
#         box-shadow: 0 0 0 0.1rem rgba(0, 123, 255, 0.25);
#     }
#     .stSelectbox div[role="listbox"] { /* Dropdown list for selectbox */
#         background-color: #333333;
#         border: 1px solid #555555;
#     }
#     .stSelectbox div[role="option"] { /* Options in selectbox dropdown */
#         color: #ffffff;
#     }
#     .stSelectbox div[role="option"]:hover { /* Hover on selectbox options */
#         background-color: #555555;
#     }

#     /* Labels and general text */
#     h1, h2, h3, h4, h5, h6, label, p, a, li, ul, .stMarkdown, .stText, .stAlert, .stButton, .stProgress, .stSpinner {
#         color: #ffffff;
#     }

#     /* Chat message bubbles */
#     .stChatMessage {
#         background-color: #333333; /* Default message bubble background */
#         color: #ffffff;
#         border-radius: 10px;
#         padding: 10px 15px;
#         margin-bottom: 10px;
#         width: fit-content; /* Make bubble fit content */
#         max-width: 80%; /* Limit bubble width */
#     }
#     .stChatMessage:nth-child(odd) { /* User messages (first message, third, etc.) */
#         background-color: #444444; /* Slightly different for user message */
#         margin-left: auto; /* Push user message to the right */
#         margin-right: 0;
#     }
#     .stChatMessage:nth-child(even) { /* Assistant messages (second message, fourth, etc.) */
#         background-color: #333333; /* Keep assistant message as original */
#         margin-right: auto; /* Push assistant message to the left */
#         margin-left: 0;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# Define logo path here, so it can be used in both authenticated and unauthenticated states
LOGO_PATH = "FunnX.Ai.jpg" # Using the path you provided. Ensure this is correct.

# --- Authentication UI ---
def show_login(): # Renamed the function
    # --- Logo Addition on Login Start ---
    if os.path.exists(LOGO_PATH):
        col1, col_logo, col3 = st.columns([1, 2, 1])
        with col_logo:
            st.image(LOGO_PATH, width=250)
    else:
        st.warning(f"Logo file '{LOGO_PATH}' not found. Please ensure it's in the app directory.")
    # --- Logo Addition on Login End ---

    st.title("Welcome to FunnX.Ai! 👋")
    st.subheader("Login to continue") # Updated subheader

    # No tabs, direct login form
    st.subheader("Email & Password Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", use_container_width=True):
        response = call_flask_api("login", {"email": login_email, "password": login_password})
        if response and "success" in response:
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = login_email
            st.session_state["page"] = "chat"
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error(f"Login failed: {response.get('error', 'Unknown error')}")

    st.markdown("---")
    st.subheader("Or Login with Google")
    if st.button("Sign In with Google", use_container_width=True, help="Note: This is a simulated Google Sign-in."):
        st.session_state["authenticated"] = True
        st.session_state["user_email"] = "google_user@example.com" # Default email for simulated Google login
        st.session_state["page"] = "chat"
        st.success("Simulated Google Sign-In successful!")
        st.rerun()

# --- Main App Logic (After Authentication) ---
if not st.session_state["authenticated"]:
    show_login() # Call the renamed login function
else:
    # --- Sidebar Navigation and Logout ---
    st.sidebar.title("FunnX.Ai")

    # --- Logo Addition for Sidebar ---
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    else:
        st.sidebar.warning(f"Logo file '{LOGO_PATH}' not found. Please ensure it's in the app directory.")
    # --- Logo Addition for Sidebar End ---

    st.sidebar.write(f"Logged in as: **{st.session_state['user_email']}**")

    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["user_email"] = ""
        st.session_state["page"] = "home"
        st.session_state["messages"] = []
        st.info("You have been logged out.")
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation")
    if st.sidebar.button("Home", key="nav_home"):
        st.session_state["page"] = "home"
        st.rerun()
    if st.sidebar.button("Chat", key="nav_chat"):
        st.session_state["page"] = "chat"
        st.rerun()

    # --- Page Content Based on Navigation ---
    if st.session_state["page"] == "home":
        st.title(f"Welcome, Dear user! 👋")
        st.write("This is your FunnX.Ai dashboard.")

        st.subheader("Your Recent Conversations")
        st.info("No persistent chat history available. Start a new chat!")

        st.image("https://images.unsplash.com/photo-1510519159390-e4b77f924747?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", caption="AI Powered Conversations", use_container_width=True)

    elif st.session_state["page"] == "chat":
        st.title("AI Chat Platform")
        st.write("Choose your model and start chatting!")

        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        col_res, col_model = st.columns([1, 1])

        with col_res:
            research_mode = st.toggle("Enable Research Mode (Deep Answers)", key="research_mode_toggle")
            st.markdown(
                '<small style="color: gray;">Research mode provides more detailed AI responses.</small>',
                unsafe_allow_html=True
            )

        with col_model:
            selected_model_option = st.selectbox(
                "Select AI Model:",
                ("Gemini", "DeepSeek (via OpenRouter)", "Try Both"),
                key="model_selector_dropdown"
            )
            if selected_model_option == "Try Both":
                st.info("Try Both mode displays responses from Gemini and DeepSeek simultaneously.")

        user_input = st.chat_input("Type your message here...")

        if user_input:
            st.session_state["messages"].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.spinner("Getting response..."):
                if selected_model_option == "Try Both":
                    ai_response_col1, ai_response_col2 = st.columns(2)

                    with ai_response_col1:
                        st.subheader("Gemini's Response:")
                        chat_data_gemini = {
                            "message": user_input,
                            "model": "Gemini",
                            "research_mode": research_mode,
                            "user_email": st.session_state["user_email"]
                        }
                        response_gemini = call_flask_api("chat", chat_data_gemini)
                        if response_gemini and "response" in response_gemini:
                            gemini_response_content = response_gemini["response"]
                            st.markdown(gemini_response_content)
                            st.session_state["messages"].append({"role": "assistant", "content": f"**Gemini:** {gemini_response_content}"})
                        else:
                            st.error("Failed to get Gemini response.")
                            st.session_state["messages"].append({"role": "assistant", "content": "Error: Gemini response failed."})

                    with ai_response_col2:
                        st.subheader("DeepSeek's Response:")
                        chat_data_deepseek = {
                            "message": user_input,
                            "model": "DeepSeek (via OpenRouter)",
                            "research_mode": research_mode,
                            "user_email": st.session_state["user_email"]
                        }
                        response_deepseek = call_flask_api("chat", chat_data_deepseek)
                        if response_deepseek and "response" in response_deepseek:
                            deepseek_response_content = response_deepseek["response"]
                            st.markdown(deepseek_response_content)
                            st.session_state["messages"].append({"role": "assistant", "content": f"**DeepSeek:** {deepseek_response_content}"})
                        else:
                            st.error("Failed to get DeepSeek response.")
                            st.session_state["messages"].append({"role": "assistant", "content": "Error: DeepSeek response failed."})

                else:
                    chat_data = {
                        "message": user_input,
                        "model": selected_model_option,
                        "research_mode": research_mode,
                        "user_email": st.session_state["user_email"]
                    }
                    flask_response = call_flask_api("chat", chat_data)

                    if flask_response and "response" in flask_response:
                        ai_response_content = flask_response["response"]
                        st.session_state["messages"].append({"role": "assistant", "content": ai_response_content})
                        with st.chat_message("assistant"):
                            st.markdown(ai_response_content)
                    else:
                        st.error("Failed to get AI response from backend.")
                        st.session_state["messages"].append({"role": "assistant", "content": "Error: Could not get response."})
            st.rerun()

if __name__ == "__main__":
    pass