# FunnX.Ai/api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- API Key Configuration ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initial check for API keys
if not GEMINI_API_KEY:
    print("WARNING: GOOGLE_API_KEY not found in .env file. Gemini API calls may fail.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Gemini API configured.")
    except Exception as e:
        print(f"ERROR: Failed to configure Gemini API: {e}. Check GOOGLE_API_KEY.")

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not found in .env file. OpenRouter API calls may fail.")
else:
    print("OpenRouter API Key loaded.")


# --- API Endpoints ---

@app.route("/")
def home():
    """Simple health check endpoint."""
    return "FunnX.Ai Backend is running!"

# --- NEW: /ping endpoint for frontend to wake up backend ---
@app.route("/ping", methods=["GET"])
def ping():
    """
    A simple endpoint to confirm the backend is alive.
    Used by the frontend to wake up the backend.
    """
    print("Received ping request. Backend is active.")
    return jsonify({"status": "active", "message": "Backend is alive!"}), 200
# --- END NEW /ping endpoint ---


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    # --- Simplified Login: Any email/password combination works ---
    print(f"Simulating login for: {email}")
    return jsonify({"success": True, "message": "Simulated login successful."}), 200
    # --- End Simplified Login ---


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    model_name = data.get("model")
    research_mode = data.get("research_mode", False)
    user_email = data.get("user_email")

    print(f"Processing chat request: Message='{user_message}', Model='{model_name}'")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    ai_response_text = "Sorry, I couldn't get a response."

    if model_name == "Gemini":
        if not GEMINI_API_KEY:
            print("Gemini API Key is missing for this request. Returning 500.")
            return jsonify({"error": "Gemini API Key is missing. Please set GOOGLE_API_KEY in your .env file."}), 500
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            convo = model.start_chat(history=[])
            gemini_raw_response = convo.send_message(user_message)

            if gemini_raw_response and gemini_raw_response.candidates and gemini_raw_response.candidates[0].content.parts:
                ai_response_text = gemini_raw_response.candidates[0].content.parts[0].text
            else:
                ai_response_text = "Gemini returned an empty or unparseable response. Try again."
                print(f"DEBUG: Gemini empty/malformed response for: '{user_message}'. Raw: {gemini_raw_response}")

        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"
            print(f"ERROR during Gemini API call: {error_msg}")
            if "404 models/" in str(e):
                error_msg += ". Model not found or not available in your region. Check Google Cloud Console."
            elif "authentication" in str(e).lower() or "api key" in str(e).lower() or "permission" in str(e).lower():
                error_msg += ". Please check your GOOGLE_API_KEY for validity and permissions."
            return jsonify({"error": error_msg}), 500

    elif model_name == "DeepSeek (via OpenRouter)":
        if not OPENROUTER_API_KEY:
            print("OpenRouter API Key is missing for this request. Returning 500.")
            return jsonify({"error": "OpenRouter API Key is missing. Please set OPENROUTER_API_KEY in your .env file."}), 500
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://funnx.ai",
                "X-Title": "FunnX.Ai"
            }
            deepseek_url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {
                "model": "deepseek/deepseek-r1",
                "messages": [{"role": "user", "content": user_message}]
            }

            print(f"DEBUG: Sending request to OpenRouter URL: {deepseek_url}")
            print(f"DEBUG: OpenRouter Request Headers: {headers}")
            print(f"DEBUG: OpenRouter Request Payload: {json.dumps(payload, indent=2)}")

            response_from_router = requests.post(deepseek_url, headers=headers, json=payload, timeout=60)
            response_from_router.raise_for_status()

            deepseek_data = response_from_router.json()
            print(f"DEBUG: Received raw DeepSeek response (full): {json.dumps(deepseek_data, indent=2)}")

            if deepseek_data and 'choices' in deepseek_data and len(deepseek_data['choices']) > 0 and \
               'message' in deepseek_data['choices'][0] and 'content' in deepseek_data['choices'][0]['message']:
                ai_response_text = deepseek_data['choices'][0]['message']['content']
            else:
                ai_response_text = "DeepSeek returned an empty or unparseable response. Please try again or select a different model."
                print(f"WARNING: DeepSeek response was malformed or empty for: '{user_message}'. Full response: {json.dumps(deepseek_data, indent=2)}")

        except requests.exceptions.HTTPError as e:
            error_body = ""
            try:
                error_body = e.response.json()
                error_body_str = json.dumps(error_body, indent=2)
            except json.JSONDecodeError:
                error_body_str = e.response.text
            error_msg = f"OpenRouter API HTTP error (Status: {e.response.status_code}): {error_body_str}"
            print(f"ERROR during OpenRouter API call (HTTPError): {error_msg}")
            if e.response.status_code == 401:
                error_msg += ". This usually means your OPENROUTER_API_KEY is incorrect or invalid."
            elif e.response.status_code == 404:
                error_msg += ". Model not found or incorrect model ID ('deepseek/deepseek-r1'?) on OpenRouter. Check OpenRouter's model list."
            elif e.response.status_code == 429:
                error_msg += ". Rate limit exceeded on OpenRouter. Try again after some time."
            return jsonify({"error": error_msg}), 500
        except requests.exceptions.ConnectionError:
            error_msg = "OpenRouter API Connection Error: Backend could not connect to OpenRouter. Check internet."
            print(f"ERROR: {error_msg}")
            return jsonify({"error": error_msg}), 500
        except requests.exceptions.Timeout:
            error_msg = "OpenRouter API request timed out after 60 seconds. Server might be slow."
            print(f"ERROR: {error_msg}")
            return jsonify({"error": error_msg}), 500
        except Exception as e:
            error_msg = f"Unexpected DeepSeek API error: {str(e)}"
            print(f"ERROR during DeepSeek API call (General): {error_msg}")
            return jsonify({"error": error_msg}), 500
    else:
        return jsonify({"error": "Invalid model selected"}), 400

    return jsonify({"response": ai_response_text})

@app.route("/get_history", methods=["POST"])
def get_history():
    """Returns an empty history, as database is not used."""
    return jsonify({"history": []})

if __name__ == "__main__":
    app.run(debug=True)