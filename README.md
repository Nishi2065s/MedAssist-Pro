# 🏥 MedAssist Pro — Ultra-Premium AI Healthcare Intelligence

![MedAssist Pro Banner](https://via.placeholder.com/1000x300.png?text=MedAssist+Pro+v3.0+-+AI+Healthcare+Ecosystem)

**MedAssist Pro** is an industry-level, high-budget AI-powered healthcare platform designed specifically for South Indian states. It offers a fully unified multilingual conversational AI, integrated Voice Assistant capabilities (Speech-to-Text & Text-to-Speech), an advanced Symptom Checker, real-time Ambulance Tracking simulation, and rapid SOS Emergency systems.

Built with **Streamlit**, powered by **Groq's Llama-3 70B** and **Whisper v3**, and seamlessly handling multiple Indian languages natively.

---

## 🌟 Key Features

1. **Unified Multilingual AI Chat & Voice Assistant**
   - Speak your symptoms directly to the bot using **Groq Whisper API**.
   - Listen to the bot read its medical analysis out loud via **Google TTS**.
   - Speak and read fluently in **English, Tamil, Telugu, Kannada, Malayalam, and Hindi** without ever mixing languages.
   - Beautiful, unified chat input bar acting as a single composite interface.
   
2. **Interactive Symptom Triage**
   - Click-based visual body map to identify symptoms.
   - Intelligent AI triage system that grades symptoms from 'Mild' to 'Emergency' and instantly suggests the next steps.

3. **Live Action Fast-SOS & Ambulance Simulator**
   - One-tap embedded buttons to trigger emergency dispatches directly inside the chat.
   - Comprehensive offline-first 108 Emergency Database covering 150+ cities across 5 states.
   
4. **Health Policy & Document Analysis**
   - Upload any Government Scheme document (PDF/TXT) and dynamically interact with the AI to fetch specialized coverage clauses.

5. **Premium Aesthetic UI/UX**
   - Custom-engineered, highly polished Glassmorphism CSS architecture.
   - Responsive layouts, dynamic hover animations, and intuitive chat history controls.

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit, Vanilla CSS, Custom HTML Widgets
- **AI/LLM Engine:** Groq (Llama-3.3-70B-Versatile) / Google Gemini Fallback
- **Speech Engine:** Groq Whisper-Large-v3 (STT), Google Text-to-Speech (gTTS)
- **Data Toolkit:** Pandas, PyMuPDF, JSON Data Structures
- **Language Stack:** Python 3.9+

---

## 🚀 Quick Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MedAssist-Pro.git
   cd MedAssist-Pro
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory and add your keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GOOGLE_API_KEY=your_gemini_key_here
   ```

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

---

## 🔒 Medical AI Disclaimer
*MedAssist Pro uses advanced conversational AI which can occasionally make mistakes. It is not a replacement for professional medical advice. Always consult a certified doctor for health concerns. We aggressively prompt our AI engines with anti-hallucination guardrails to prioritize factual medical science.*

---

*Built with ❤️ for a Healthier India.*
