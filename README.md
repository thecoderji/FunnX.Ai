# FunnX.Ai - AI Chat Platform

FunnX.Ai is a full-stack AI chat application designed to provide intelligent conversational experiences using multiple Large Language Models (LLMs). It features a secure login, model selection (Google Gemini and DeepSeek), and a "Research Mode" for detailed responses.

## ✨ Features

- **Multi-Model Support:** Interact with Google Gemini and DeepSeek (via OpenRouter).
- **"Try Both" Mode:** Compare responses from Gemini and DeepSeek simultaneously.
- **"Research Mode":** Get more detailed and in-depth answers.
- **Simplified Login:** Easy access with an open-source-friendly login system (simulated Google Sign-in also available).
- **Responsive Design:** Chat interface designed for both desktop and mobile (with updated input field).

## 🚀 Live Demo

Experience FunnX.Ai live on Render:

- **FunnX.Ai Frontend (Streamlit App):** [https://funnx-ai.onrender.com]
  - _Example: `https://funnx-ai-frontend.onrender.com`_
- **FunnX.Ai Backend (Flask API):** [https://funnx-ai-backend.onrender.com]
  - _Example: `https://funnx-ai-backend.onrender.com`_

**Important Note for Live Demo Users:**
This project is built using **entirely free resources and API tiers**. Due to potential limitations or closures of free API access, or "cold start" delays on free hosting (up to 50 seconds or more on first visit after inactivity), you might occasionally experience failed or delayed responses. Please keep patience if this occurs.

For a more consistent experience, you are encouraged to pull the repository locally, add your own API keys (from Google AI Studio and OpenRouter.ai), and run the application on your system.

## 🛠️ Technologies Used

- **Frontend:** Streamlit
- **Backend:** Flask
- **LLMs:** Google Gemini (via Google Generative AI API), DeepSeek (via OpenRouter API)
- **Deployment:** Render.com
- **Dependency Management:** `pip` (with `requirements.txt`)
- **Server Gateway:** Gunicorn (for Flask)
- **Environment Variables:** `python-dotenv`
- **Version Control:** Git & GitHub

## 💻 Local Development Setup

To run FunnX.Ai on your local machine:

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/thecoderji/FunnX.Ai.git](https://github.com/thecoderji/FunnX.Ai.git)
    cd FunnX.Ai
    ```

2.  **Create a virtual environment** (recommended):

    ```bash
    python -m venv venv
    .\venv\Scripts\activate   # On Windows
    source venv/bin/activate # On macOS/Linux
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root of your project directory and add your API keys:

    ```
    GOOGLE_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
    OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"
    ```

    - Get your Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    - Get your OpenRouter API Key from [OpenRouter.ai](https://openrouter.ai/keys).

5.  **Run the Backend (Flask API):**
    Open a **new terminal** and activate your virtual environment. Then run:

    ```bash
    python api.py
    ```

    The backend should run on `http://127.0.0.1:5000`.

6.  **Run the Frontend (Streamlit App):**
    Open **another new terminal** and activate your virtual environment. Then run:
    ```bash
    streamlit run app.py
    ```
    The Streamlit app will open in your browser, typically at `http://localhost:8501`.

## 🧠 Built with AI Guidance

This project was developed with significant guidance and assistance from various AI LLM models, showcasing the power of collaborative development with artificial intelligence.

## 📄 License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).
