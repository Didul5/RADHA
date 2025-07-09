#!/usr/bin/env python3
"""
Streamlit Frontend for Unified AI Learning Assistant
Beautiful, interactive interface with model switching support
"""

import streamlit as st
import requests
import json
import pyttsx3
import speech_recognition as sr
from datetime import datetime
import time
from typing import Dict, List
import os
from dotenv import load_dotenv
import re
import threading

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Learning Assistant - Powered by Qwen & Groq",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoint
API_BASE = "http://localhost:8000"

# Initialize session state
if 'model_type' not in st.session_state:
    st.session_state.model_type = None

if 'model_initialized' not in st.session_state:
    st.session_state.model_initialized = False

if 'stats' not in st.session_state:
    st.session_state.stats = {
        'interactions': 0,
        'questions_asked': 0,
        'content_generated': 0,
        'concepts_explored': 0,
        'study_streak': 0,
        'last_activity': datetime.now()
    }

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'tts_queue' not in st.session_state:
    st.session_state.tts_queue = []

if 'last_tts_content' not in st.session_state:
    st.session_state.last_tts_content = ""

if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = 0

# Global TTS engine
tts_engine = None
tts_lock = threading.Lock()

# Initialize TTS engine
def init_tts():
    """Initialize text-to-speech engine with female voice"""
    global tts_engine
    try:
        if tts_engine is None:
            tts_engine = pyttsx3.init()
            # Set properties
            tts_engine.setProperty('rate', 150)
            # Try to set female voice
            voices = tts_engine.getProperty('voices')
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower() or "hazel" in voice.name.lower():
                    tts_engine.setProperty('voice', voice.id)
                    break
        return tts_engine
    except:
        return None

# Initialize speech recognition
def init_speech_recognition():
    """Initialize speech recognition"""
    return sr.Recognizer()

# Custom CSS for beautiful UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Text outside boxes and all form labels set to white */
    .stApp .stMarkdown, 
    .stApp label, 
    .stApp .stRadio label, 
    .stApp .stCheckbox label, 
    .stApp .stMultiSelect label, 
    .stApp .stDateInput label {
        color: white !important;
    }

    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e8ba3 100%);
        min-height: 100vh;
    }
    
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        animation: slideDown 0.6s ease-out;
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .model-selector {
        background: rgba(255, 255, 255, 0.98);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .model-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .model-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    }
    
    .model-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .stat-card:hover {
        transform: scale(1.05);
        background: linear-gradient(135deg, rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.9));
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .grade-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 30px;
        display: inline-block;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); }
        50% { box-shadow: 0 4px 25px rgba(16, 185, 129, 0.5); }
        100% { box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); }
    }
    
    .reward-animation {
        animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        font-size: 3rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    @keyframes bounceIn {
        0% { opacity: 0; transform: scale(0.3); }
        50% { opacity: 1; transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.9);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.5rem;
        border-radius: 16px;
        backdrop-filter: blur(10px);
        margin-right: 0;
        overflow-x: auto;
        white-space: nowrap;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: white;
        font-weight: 500;
        background: transparent;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .success-notification {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .sidebar .stButton > button {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        width: 100%;
    }
    
    .sidebar .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    h1, h2, h3 {
        font-weight: 600;
        color: white !important;
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .upload-section {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: rgba(255, 255, 255, 0.5);
        background: rgba(255, 255, 255, 0.1);
    }
    
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Make all sidebar text black without affecting stat cards */
    section[data-testid="stSidebar"] * {
        color: black !important;
    }
    
    /* Chat message styles */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        animation: fadeIn 0.3s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: rgba(102, 126, 234, 0.1);
        margin-left: 20%;
        color: white !important;
    }
    
    .assistant-message {
        background: rgba(255, 255, 255, 0.1);
        margin-right: 20%;
        color: white !important;
    }
    
    /* Fix question box visibility */
    .stInfo {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1a1a1a !important;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    .stInfo > div {
        color: #1a1a1a !important;
        font-weight: 500;
    }
    
    /* Fix success box visibility */
    .stSuccess {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #047857 !important;
        border: 2px solid rgba(16, 185, 129, 0.5);
        font-weight: 500;
    }
    
    .stSuccess > div {
        color: #047857 !important;
    }
    
    /* Fix warning box visibility */
    .stWarning {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #92400e !important;
        border: 2px solid rgba(245, 158, 11, 0.5);
    }
    
    .stWarning > div {
        color: #92400e !important;
    }
    
    /* Fix all alert box visibility */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-width: 2px !important;
    }
    
    .stAlert > div {
        font-weight: 500;
    }
    
    /* Fix error box visibility */
    .stError {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #991b1b !important;
        border: 2px solid rgba(239, 68, 68, 0.5);
    }
    
    .stError > div {
        color: #991b1b !important;
    }
    
    /* Remove white space at end of tabs */
    .stTabs [data-baseweb="tab-list"]::after {
        content: none;
        display: none;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent;
    }
    
    /* Hide tab scroll indicators */
    .stTabs [data-baseweb="tab-list"] > div:last-child {
        display: none !important;
    }
    
    /* Home page feature cards */
    .home-feature-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(0, 0, 0, 0.05);
        cursor: pointer;
        height: 100%;
        display: flex;
        flex-direction: column;
        position: relative;
        overflow: hidden;
    }
    
    .home-feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    }
    
    .home-feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, transparent, rgba(102, 126, 234, 0.1));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .home-feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .feature-title {
        color: #1a1a1a !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        color: #4a5568 !important;
        font-size: 1rem;
        line-height: 1.6;
        flex-grow: 1;
    }
    
    .feature-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 1rem;
    }
    
    .home-hero {
        text-align: center;
        padding: 4rem 2rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        backdrop-filter: blur(20px);
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
    }
    
    .home-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        animation: rotate 30s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 3rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-stat {
        text-align: center;
    }
    
    .hero-stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        display: block;
    }
    
    .hero-stat-label {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.8);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        margin-top: 2rem;
        display: inline-block;
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(102, 126, 234, 0.4);
    }

</style>
""", unsafe_allow_html=True)

# Helper functions
def clean_text_for_tts(text):
    """Remove markdown formatting and special characters for TTS"""
    # Remove markdown headers
    text = re.sub(r'#{1,6}\s*', '', text)
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}([^\*]+)\*{1,3}', r'\1', text)
    # Remove underscores
    text = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', text)
    # Remove code blocks
    text = re.sub(r'```[^`]*```', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove horizontal rules
    text = re.sub(r'[-=]{3,}', '', text)
    # Remove bullet points
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    # Remove numbered lists
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def update_stats(stat_type: str, increment: int = 1):
    """Update statistics in real-time"""
    if stat_type in st.session_state.stats:
        st.session_state.stats[stat_type] += increment
        st.session_state.stats['last_activity'] = datetime.now()
        
        # Update study streak
        if stat_type == 'interactions':
            st.session_state.stats['study_streak'] = min(st.session_state.stats['interactions'] // 5, 100)

def speak_text(text: str, force=False):
    """Convert text to speech in a separate thread"""
    if st.session_state.get('enable_tts', False) and text:
        # Check if this is new content or forced
        if force or text != st.session_state.get('last_tts_content', ''):
            st.session_state.last_tts_content = text
            
            def tts_worker():
                global tts_engine
                with tts_lock:
                    try:
                        if tts_engine is None:
                            tts_engine = init_tts()
                        if tts_engine:
                            # Clean text for TTS
                            clean_text = clean_text_for_tts(text)
                            # Limit text length to prevent long waits
                            clean_text = clean_text[:1000]
                            tts_engine.say(clean_text)
                            tts_engine.runAndWait()
                    except Exception as e:
                        print(f"TTS Error: {e}")
                        # Reset engine on error
                        tts_engine = None
            
            # Run TTS in a separate thread
            tts_thread = threading.Thread(target=tts_worker)
            tts_thread.daemon = True
            tts_thread.start()

def get_speech_input():
    """Get speech input from microphone"""
    recognizer = init_speech_recognition()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            st.info("🔄 Processing speech...")
            text = recognizer.recognize_google(audio)
            update_stats('interactions')
            return text
    except sr.RequestError:
        st.error("Could not request results from speech recognition service")
    except sr.UnknownValueError:
        st.warning("Could not understand audio. Please try again.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    return None

def make_api_request(endpoint: str, data: dict) -> dict:
    """Make API request to backend"""
    try:
        response = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=2400)
        if response.status_code == 200:
            update_stats('interactions')
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please ensure the backend is running on localhost:8000")
        st.info("Run: python api.py")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def stream_api_request(endpoint: str, data: dict):
    """Make streaming API request to backend"""
    try:
        response = requests.post(
            f"{API_BASE}{endpoint}",
            json=data,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            update_stats('interactions')
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'content' in chunk:
                            yield chunk['content']
                    except json.JSONDecodeError:
                        continue
        else:
            st.error(f"API Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please ensure the backend is running on localhost:8000")
        st.info("Run: python api.py")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def get_model_info():
    """Get current model information from API"""
    try:
        response = requests.get(f"{API_BASE}/model-info", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def switch_model(model_type: str):
    """Switch to a different model"""
    result = make_api_request("/switch-model", {"model_type": model_type})
    if result and result.get("success"):
        st.session_state.model_type = model_type
        return True
    return False

# Main app
def main():
    # Check model initialization
    if not st.session_state.model_initialized:
        model_info = get_model_info()
        if model_info:
            st.session_state.model_type = model_info.get("current_model", "unknown")
            st.session_state.model_initialized = True
    
    # Header with animation
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; font-size: 3.5rem; margin: 0; font-weight: 700;">🎓 RADHA</h1>
        <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.3rem; margin-top: 0.5rem;">Responsive AI for Dynamic Holistic Assistance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Model selector (before sidebar)
    if st.session_state.model_initialized:
        st.markdown('<div class="model-selector">', unsafe_allow_html=True)
        st.markdown("### 🤖 Select AI Model")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🖥️ Qwen 2.5 7B (Local)", 
                        key="select_openvino",
                        use_container_width=True,
                        type="primary" if st.session_state.model_type == "openvino" else "secondary"):
                if switch_model("openvino"):
                    st.success("✅ Switched to Qwen model")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Failed to switch model. Make sure Qwen model is available.")
        
        with col2:
            if st.button("☁️ Llama 3.3 70B (Cloud)", 
                        key="select_groq",
                        use_container_width=True,
                        type="primary" if st.session_state.model_type == "groq" else "secondary"):
                if switch_model("groq"):
                    st.success("✅ Switched to Groq API")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Failed to switch model. Make sure GROQ_API_KEY is set.")
        
        # Show current model info
        if st.session_state.model_type == "openvino":
            st.info("🖥️ **Current Model:** Qwen 2.5 7B INT4 - Running locally on your device")
        elif st.session_state.model_type == "groq":
            st.info("☁️ **Current Model:** Llama 3.3 70B - Powered by Groq's cloud API")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # Input mode
        input_mode = st.radio("Input Mode", ["Text", "Speech 🎤"])
        st.session_state['enable_tts'] = st.checkbox("Enable Text-to-Speech 🔊", value=False)
        
        # Grade level
        grade_level = st.selectbox(
            "Grade Level",
            ["Elementary", "Middle School", "High School", "College", "Graduate"],
            index=2
        )
        
        # Model Status
        if st.session_state.model_initialized:
            if st.session_state.model_type == "openvino":
                st.success("✅ Qwen Model Active")
            elif st.session_state.model_type == "groq":
                api_key = os.getenv("GROQ_API_KEY")
                if api_key:
                    st.success("✅ Groq API Active")
                else:
                    st.warning("⚠️ No API Key Found")
                    st.info("Set GROQ_API_KEY in .env file")
        else:
            st.error("❌ No Model Active")
        
        st.markdown("---")
        st.markdown("### 📊 Real-time Stats")
        
        # Animated stats display
        stats_placeholder = st.empty()
        
        def display_stats():
            with stats_placeholder.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <p class="stat-number">{st.session_state.stats['interactions']}</p>
                        <p class="stat-label">Interactions</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="stat-card" style="margin-top: 1rem;">
                        <p class="stat-number">{st.session_state.stats['questions_asked']}</p>
                        <p class="stat-label">Questions</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <p class="stat-number">{st.session_state.stats['content_generated']}</p>
                        <p class="stat-label">Content</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="stat-card" style="margin-top: 1rem;">
                        <p class="stat-number">{st.session_state.stats['study_streak']}%</p>
                        <p class="stat-label">Progress</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        display_stats()
        
        # API Status
        st.markdown("---")
        if st.button("🔄 Check API Status", use_container_width=True):
            try:
                response = requests.get(f"{API_BASE}/health", timeout=2400)
                if response.status_code == 200:
                    health = response.json()
                    st.success(f"✅ API Connected")
                    st.info(f"Model: {health.get('model', 'Unknown')}")
                else:
                    st.error("❌ API Error")
            except:
                st.error("❌ API Offline")
    
    # Main content tabs
    tabs = st.tabs([
        "🏠 Home",
        "💬 Chat Assistant",
        "📚 Content Generation",
        "❓ Doubt Solving",
        "📅 Curriculum Planning",
        "💻 Code Grading",
        "🎯 Practice Mode",
        "👨‍🏫 Teacher Tools",
        "🧠 Concept Explorer",
        "📖 Study Planner"
    ])
    
    # Tab 0: Home
    with tabs[0]:
        # Hero Section
        st.markdown("""
        <div class="home-hero">
            <h1 class="hero-title">Welcome to RADHA</h1>
            <p class="hero-subtitle">Your AI-Powered Learning Companion</p>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; max-width: 800px; margin: 0 auto; position: relative; z-index: 1;">
                Experience the future of education with personalized learning, instant support, and intelligent feedback powered by cutting-edge AI technology.
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <span class="hero-stat-number">9</span>
                    <span class="hero-stat-label">Features</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-number">2-3s</span>
                    <span class="hero-stat-label">Response Time</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-number">24/7</span>
                    <span class="hero-stat-label">Available</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Features Grid
        st.markdown("## 🚀 Explore Our Features")
        st.markdown("Click on any feature card to get started!")
        
        # First row of features
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("", key="home_chat", use_container_width=True):
                st.session_state.selected_tab = 1
                st.rerun()
            st.markdown("""
            <div class="home-feature-card">
                <div class="feature-icon">💬</div>
                <h3 class="feature-title">Chat Assistant</h3>
                <p class="feature-description">Engage in natural conversations with our AI assistant. Ask questions, seek clarification, or explore topics in depth.</p>
                <span class="feature-badge">Most Popular</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            if st.button("", key="home_content", use_container_width=True):
                st.session_state.selected_tab = 2
                st.rerun()
            st.markdown("""
            <div class="home-feature-card">
                <div class="feature-icon">📚</div>
                <h3 class="feature-title">Content Generation</h3>
                <p class="feature-description">Generate customized study materials including notes, summaries, and quizzes tailored to your grade level.</p>
                <span class="feature-badge">Save Time</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            if st.button("", key="home_doubt", use_container_width=True):
                st.session_state.selected_tab = 3
                st.rerun()
            st.markdown("""
            <div class="home-feature-card">
                <div class="feature-icon">❓</div>
                <h3 class="feature-title">Doubt Solving</h3>
                <p class="feature-description">Get instant, detailed answers to your academic questions across all subjects with step-by-step explanations.</p>
                <span class="feature-badge">Real-time</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Second row of features
        col4, col5, col6 = st.columns(3)
        
        with col4:
            if st.button("", key="home_curriculum", use_container_width=True):
                st.session_state.selected_tab = 4
                st.rerun()
            st.markdown("""
            <div class="home-feature-card">
                <div class="feature-icon">📅</div>
                <h3 class="feature-title">Curriculum Planning</h3>
                <p class="feature-description">Design comprehensive learning paths with balanced theory and practical components for any duration.</p>
                <span class="feature-badge">Structured</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col5:
            if st.button("", key="home_code", use_container_width=True):
                st.session_state.selected_tab = 5
                st.rerun()
            st.markdown("""
            <div class="home-feature-card">
                <div class="feature-icon">💻</div>
                <h3 class="feature-title">Code Grading</h3>
                <p class="feature-description">Submit your code for instant evaluation with detailed feedback on correctness, efficiency, and style.</p>
                <span class="feature-badge">Multi-language</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col6:
            if st.button("", key="home_practice", use_container_width=True):
                st.session_state.selected_tab = 6
                st.rerun()
            st.markdown("""
            <div class="home-feature-card">
                <div class="feature-icon">🎯</div>
                <h3 class="feature-title">Practice Mode</h3>
                <p class="feature-description">Test your knowledge with interactive questions and receive immediate feedback with detailed explanations.</p>
                <span class="feature-badge">Gamified</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Third row of features
        col7, col8, col9 = st.columns(3)
        
        with col7:
            if st.button("", key="home_teacher", use_container_width=True):
                st.session_state.selected_tab = 7
                st.rerun()
            st.markdown("""
            <div class="home-feature-card">
                <div class="feature-icon">👨‍🏫</div>
                <h3 class="feature-title">Teacher Tools</h3>
                <p class="feature-description">Enhance your teaching methods with AI-powered insights, feedback, and curriculum improvements.</p>
                <span class="feature-badge">For Educators</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col8:
            if st.button("", key="home_concept", use_container_width=True):
                st.session_state.selected_tab = 8
                st.rerun()
            st.markdown("""
            <div class="home-feature-card">
                <div class="feature-icon">🧠</div>
                <h3 class="feature-title">Concept Explorer</h3>
                <p class="feature-description">Deep dive into any concept with clear explanations, real-world analogies, and visual representations.</p>
                <span class="feature-badge">In-depth</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col9:
            if st.button("", key="home_study", use_container_width=True):
                st.session_state.selected_tab = 9
                st.rerun()
            st.markdown("""
            <div class="home-feature-card">
                <div class="feature-icon">📖</div>
                <h3 class="feature-title">Study Planner</h3>
                <p class="feature-description">Create personalized study schedules optimized for your exam dates and available study hours.</p>
                <span class="feature-badge">Personalized</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Key Features Section
        st.markdown("---")
        st.markdown("## 🌟 Why Choose RADHA?")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-bottom: 1rem;">
                <h3 style="color: white; margin-bottom: 1rem;">⚡ Lightning Fast</h3>
                <p style="color: rgba(255, 255, 255, 0.9);">Choose between local Qwen model or Groq's cloud API for optimal performance.</p>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-bottom: 1rem;">
                <h3 style="color: white; margin-bottom: 1rem;">🎯 Personalized Learning</h3>
                <p style="color: rgba(255, 255, 255, 0.9);">Adaptive content generation based on your grade level and learning preferences.</p>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px;">
                <h3 style="color: white; margin-bottom: 1rem;">🔊 Multimodal Support</h3>
                <p style="color: rgba(255, 255, 255, 0.9);">Learn through text or speech - input and output in the way that suits you best.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_right:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-bottom: 1rem;">
                <h3 style="color: white; margin-bottom: 1rem;">📊 Comprehensive Coverage</h3>
                <p style="color: rgba(255, 255, 255, 0.9);">From elementary to graduate level, covering all major subjects and topics.</p>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-bottom: 1rem;">
                <h3 style="color: white; margin-bottom: 1rem;">🤖 Dual AI Models</h3>
                <p style="color: rgba(255, 255, 255, 0.9);">Switch between Qwen 2.5 7B (local) and Llama 3.3 70B (cloud) models.</p>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px;">
                <h3 style="color: white; margin-bottom: 1rem;">🏆 Instant Feedback</h3>
                <p style="color: rgba(255, 255, 255, 0.9);">Get immediate, constructive feedback on your answers and assignments.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Call to Action
        st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <h2 style="color: white; margin-bottom: 1rem;">Ready to Transform Your Learning Experience?</h2>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin-bottom: 2rem;">
                Choose any feature from above to begin your AI-powered learning journey!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tab 1: Chat Assistant (previously Tab 0)
    with tabs[1]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 💬 Interactive Chat Assistant")
        st.markdown("Ask me anything about learning, education, or any topic!")
        
        # Chat history display
        chat_container = st.container()
        
        # Display existing chat history
        with chat_container:
            for msg in st.session_state.conversation_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message">👤 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant-message">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
        
        # Input area
        col1, col2 = st.columns([5, 1])
        with col1:
            if input_mode == "Speech 🎤":
                if st.button("🎤 Speak Message", use_container_width=True):
                    speech_text = get_speech_input()
                    if speech_text:
                        st.session_state['chat_input'] = speech_text
            
            user_input = st.text_input(
                "Your message:",
                value=st.session_state.get('chat_input', ''),
                placeholder="Type your message here...",
                key="chat_input_field"
            )
        
        with col2:
            send_button = st.button("Send 📤", use_container_width=True)
        
        if send_button and user_input:
            # Add user message to history
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Clear input
            st.session_state['chat_input'] = ''
            
            # Create placeholder for streaming response
            response_placeholder = st.empty()
            
            # Stream the response
            full_response = ""
            
            for chunk in stream_api_request("/chat-stream", {
                "message": user_input,
                "conversation_history": st.session_state.conversation_history[:-1]
            }):
                full_response += chunk
                with response_placeholder.container():
                    st.markdown(f'<div class="chat-message assistant-message">🤖 {full_response}</div>', unsafe_allow_html=True)
            
            # Add assistant response to history
            if full_response:
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": full_response
                })
                
                # Speak the response after it's complete
                if st.session_state.get('enable_tts'):
                    speak_text(full_response, force=True)
            
            st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.conversation_history = []
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: Content Generation (previously Tab 1)
    with tabs[2]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 📚 Generate Educational Content")
        st.markdown("Create customized learning materials instantly")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if input_mode == "Speech 🎤":
                if st.button("🎤 Speak Topic", use_container_width=True):
                    speech_text = get_speech_input()
                    if speech_text:
                        st.session_state['content_topic'] = speech_text
                        st.success(f"Heard: {speech_text}")
            
            topic = st.text_input(
                "Enter Topic",
                value=st.session_state.get('content_topic', ''),
                placeholder="e.g., Photosynthesis, World War II, Quadratic Equations"
            )
        
        with col2:
            content_type = st.selectbox(
                "Content Type",
                ["summary", "notes", "quiz"],
                format_func=lambda x: x.capitalize()
            )
        
        if st.button("✨ Generate Content", type="primary", use_container_width=True):
            if topic:
                with st.spinner("🤖 AI is creating content..."):
                    result = make_api_request("/generate-content", {
                        "topic": topic,
                        "content_type": content_type,
                        "grade_level": grade_level.lower()
                    })
                    
                    if result:
                        update_stats('content_generated')
                        st.markdown('<div class="success-notification">✅ Content Generated Successfully!</div>', unsafe_allow_html=True)
                        content = result.get('content', '')
                        
                        # Display content in a nice container
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-top: 1rem; color: white;">
                            {content}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.session_state.get('enable_tts'):
                            speak_text(content, force=True)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Content",
                            data=content,
                            file_name=f"{topic}_{content_type}_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
            else:
                st.warning("⚠️ Please enter a topic!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: Doubt Solving (previously Tab 2)
    with tabs[3]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## ❓ Real-time Doubt Solving")
        st.markdown("Get instant answers to your questions")
        
        subject = st.selectbox("Subject", ["Mathematics", "Science", "History", "English", "Computer Science", "General"])
        
        if input_mode == "Speech 🎤":
            if st.button("🎤 Ask Your Question", use_container_width=True):
                speech_text = get_speech_input()
                if speech_text:
                    st.session_state['doubt_question'] = speech_text
        
        question = st.text_area(
            "Your Question",
            value=st.session_state.get('doubt_question', ''),
            placeholder="Type or speak your question here...",
            height=100
        )
        
        if st.button("🔍 Get Answer", type="primary", use_container_width=True):
            if question:
                update_stats('questions_asked')
                with st.spinner("🤔 AI is thinking..."):
                    result = make_api_request("/solve-doubt", {
                        "question": question,
                        "subject": subject.lower(),
                        "grade_level": grade_level.lower()
                    })
                    
                    if result:
                        st.markdown('<div class="success-notification">✅ Answer Found!</div>', unsafe_allow_html=True)
                        answer = result.get('solution', '')
                        
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-top: 1rem; color: white;">
                            <h4>💡 Answer:</h4>
                            {answer}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.session_state.get('enable_tts'):
                            speak_text(answer, force=True)
            else:
                st.warning("⚠️ Please enter a question!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 4: Curriculum Planning (previously Tab 3)
    with tabs[4]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 📅 Curriculum Generator")
        st.markdown("Design comprehensive learning paths")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            subject = st.text_input("Subject/Course", placeholder="e.g., Data Science, Biology")
        with col2:
            duration = st.text_input("Duration", placeholder="e.g., 6 months, 1 semester")
        with col3:
            study_type = st.selectbox("Study Type", ["both", "theory", "practical"])
        
        if st.button("📋 Generate Curriculum", type="primary", use_container_width=True):
            if subject and duration:
                update_stats('content_generated')
                with st.spinner("📊 Creating curriculum plan..."):
                    result = make_api_request("/generate-curriculum", {
                        "subject": subject,
                        "duration": duration,
                        "study_type": study_type
                    })
                    
                    if result:
                        st.markdown('<div class="success-notification">✅ Curriculum Generated!</div>', unsafe_allow_html=True)
                        curriculum = result.get('curriculum', '')
                        
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-top: 1rem; color: white;">
                            {curriculum}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 Download Curriculum",
                            data=curriculum,
                            file_name=f"{subject}_curriculum_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
            else:
                st.warning("⚠️ Please fill all fields!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 5: Code Grading (previously Tab 4)
    with tabs[5]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 💻 Automatic Code Grading")
        st.markdown("Get instant feedback on your code")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            problem_desc = st.text_area(
                "Problem Description (Optional)",
                placeholder="Describe what the code should do...",
                height=80
            )
        with col2:
            language = st.selectbox("Language", ["python", "java", "javascript", "c++", "c"])
        
        code_input = st.text_area(
            "Submit Your Code",
            value=st.session_state.get('code_input', ''),
            height=300,
            placeholder="# Enter your code here"
        )
        st.session_state['code_input'] = code_input
        
        if st.button("📊 Grade Code", type="primary", use_container_width=True):
            if code_input:
                update_stats('interactions')
                with st.spinner("🔍 Analyzing code..."):
                    result = make_api_request("/grade-code", {
                        "code": code_input,
                        "language": language,
                        "problem_description": problem_desc
                    })
                    
                    if result:
                        score = result.get('score', 0)
                        feedback = result.get('feedback', '')
                        passed = result.get('passed', False)
                        
                        # Display score with visual feedback
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if passed:
                                st.markdown(f'<div class="grade-badge" style="font-size: 2rem; text-align: center; width: 100%;">Score: {score}/100 ✅</div>', unsafe_allow_html=True)
                                st.balloons()
                            else:
                                st.markdown(f'<div style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 1rem; border-radius: 30px; font-size: 2rem; text-align: center; font-weight: 600;">Score: {score}/100 ❌</div>', unsafe_allow_html=True)
                        
                        st.markdown("### 📝 Detailed Feedback")
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-top: 1rem; color: white;">
                            {feedback}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please enter some code to grade!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 6: Practice Mode (previously Tab 5)
    with tabs[6]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 🎯 Student Practice Mode")
        st.markdown("Test your knowledge with interactive questions")
        
        col1, col2 = st.columns(2)
        with col1:
            practice_subject = st.selectbox(
                "Select Subject",
                ["Mathematics", "Science", "History", "English", "Computer Science"]
            )
        with col2:
            topic = st.text_input("Specific Topic (Optional)", placeholder="e.g., Algebra, Photosynthesis")
        
        if st.button("🎲 Generate Question", type="primary", use_container_width=True):
            update_stats('questions_asked')
            with st.spinner("Creating question..."):
                result = make_api_request("/student-qa", {
                    "subject": practice_subject.lower(),
                    "grade_level": grade_level.lower(),
                    "topic": topic
                })
                
                if result:
                    st.session_state['current_qa'] = result
                    st.session_state['show_answer'] = False
                    st.session_state['answer_checked'] = False
        
        # Display question
        if 'current_qa' in st.session_state:
            qa = st.session_state['current_qa']
            st.markdown("### ❓ Question:")
            st.info(qa['question'])
            
            # Create a unique key for this question
            question_key = f"q_{hash(qa['question'])}"
            
            if st.session_state.get('enable_tts') and st.session_state.get('last_question_key') != question_key:
                speak_text(qa['question'], force=True)
                st.session_state['last_question_key'] = question_key
            
            # Student answer input
            if input_mode == "Speech 🎤":
                if st.button("🎤 Speak Your Answer", use_container_width=True):
                    speech_text = get_speech_input()
                    if speech_text:
                        st.session_state['student_answer'] = speech_text
            
            student_answer = st.text_area(
                "Your Answer:",
                value=st.session_state.get('student_answer', ''),
                height=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Check Answer", type="primary", use_container_width=True):
                    if student_answer:
                        update_stats('interactions')
                        with st.spinner("Checking..."):
                            check_result = make_api_request("/check-answer", {
                                "question": qa['question'],
                                "student_answer": student_answer,
                                "correct_answer": qa['answer']
                            })
                            
                            if check_result:
                                st.session_state['check_result'] = check_result
                                st.session_state['answer_checked'] = True
                    else:
                        st.warning("⚠️ Please enter an answer!")
            
            with col2:
                if st.button("👁️ Show Answer", use_container_width=True):
                    st.session_state['show_answer'] = True
            
            # Display check result
            if st.session_state.get('answer_checked') and 'check_result' in st.session_state:
                check_result = st.session_state['check_result']
                if check_result['is_correct']:
                    st.markdown(f'<div class="reward-animation">{check_result["reward"]}</div>', unsafe_allow_html=True)
                    st.success("🎉 Correct! Well done!")
                else:
                    st.warning("💪 Not quite right. Keep trying!")
                
                st.markdown("### 💬 Feedback:")
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 12px; color: #1a1a1a; border: 2px solid rgba(102, 126, 234, 0.2);">
                    <p style="margin: 0; color: #1a1a1a !important; font-size: 1rem; line-height: 1.6;">{check_result['feedback']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.session_state.get('show_answer', False):
                st.markdown("### ✅ Correct Answer:")
                st.success(qa['answer'])
        
        # Reset question state when generating new question
        if st.button("🔄 New Question"):
            st.session_state.pop('current_qa', None)
            st.session_state.pop('show_answer', None)
            st.session_state.pop('answer_checked', None)
            st.session_state.pop('check_result', None)
            st.session_state.pop('student_answer', None)
            st.session_state.pop('last_question_key', None)
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 7: Teacher Tools (previously Tab 6)
    with tabs[7]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 👨‍🏫 Teacher Feedback System")
        st.markdown("Improve your teaching methods with AI insights")
        
        teaching_method = st.text_area(
            "Describe Your Teaching Method",
            placeholder="e.g., I use interactive demonstrations and group discussions...",
            height=100
        )
        
        curriculum_details = st.text_area(
            "Current Curriculum Details",
            placeholder="e.g., Following state standards, covering topics A, B, C over 3 months...",
            height=100
        )
        
        challenges = st.text_area(
            "Challenges Faced (Optional)",
            placeholder="e.g., Student engagement, resource limitations...",
            height=80
        )
        
        if st.button("💡 Get Feedback", type="primary", use_container_width=True):
            if teaching_method and curriculum_details:
                update_stats('interactions')
                with st.spinner("🔍 Analyzing teaching approach..."):
                    result = make_api_request("/teacher-feedback", {
                        "teaching_method": teaching_method,
                        "curriculum_details": curriculum_details,
                        "challenges": challenges
                    })
                    
                    if result:
                        st.markdown('<div class="success-notification">✅ Feedback Generated!</div>', unsafe_allow_html=True)
                        feedback = result.get('feedback', '')
                        
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-top: 1rem; color: white;">
                            {feedback}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 Download Feedback Report",
                            data=feedback,
                            file_name=f"teaching_feedback_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
            else:
                st.warning("⚠️ Please fill in the required fields!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 8: Concept Explorer (previously Tab 7)
    with tabs[8]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 🧠 Concept Explorer")
        st.markdown("Deep dive into any concept with clear explanations")
        
        if input_mode == "Speech 🎤":
            if st.button("🎤 Speak Concept", use_container_width=True):
                speech_text = get_speech_input()
                if speech_text:
                    st.session_state['concept'] = speech_text
        
        concept = st.text_input(
            "Enter Concept to Explore",
            value=st.session_state.get('concept', ''),
            placeholder="e.g., Quantum Physics, Machine Learning, Democracy"
        )
        
        use_analogy = st.checkbox("Include Real-world Analogies 🌍", value=True)
        
        if st.button("🔍 Explain Concept", type="primary", use_container_width=True):
            if concept:
                update_stats('concepts_explored')
                with st.spinner("🧠 Generating explanation..."):
                    result = make_api_request("/explain-concept", {
                        "concept": concept,
                        "grade_level": grade_level.lower(),
                        "use_analogy": use_analogy
                    })
                    
                    if result:
                        st.markdown('<div class="success-notification">✅ Concept Explained!</div>', unsafe_allow_html=True)
                        explanation = result.get('explanation', '')
                        
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-top: 1rem; color: white;">
                            <h3>💡 {concept}</h3>
                            {explanation}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.session_state.get('enable_tts'):
                            speak_text(explanation, force=True)
            else:
                st.warning("⚠️ Please enter a concept to explore!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 9: Study Planner (previously Tab 8)
    with tabs[9]:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 📖 Personalized Study Planner")
        st.markdown("Create optimized study schedules for your exams")
        
        # Subject selection
        subjects = st.multiselect(
            "Select Subjects",
            ["Mathematics", "Science", "History", "English", "Computer Science", "Physics", "Chemistry", "Biology"],
            default=["Mathematics", "Science"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            exam_date = st.date_input("Exam Date 📅", min_value=datetime.now().date())
        with col2:
            study_hours = st.slider("Study Hours per Day ⏰", 1, 12, 4)
        
        if st.button("📅 Generate Study Plan", type="primary", use_container_width=True):
            if subjects:
                update_stats('content_generated')
                with st.spinner("📊 Creating personalized study plan..."):
                    result = make_api_request("/study-plan", {
                        "subjects": subjects,
                        "exam_date": exam_date.strftime("%Y-%m-%d"),
                        "study_hours_per_day": study_hours
                    })
                    
                    if result:
                        st.markdown('<div class="success-notification">✅ Study Plan Generated!</div>', unsafe_allow_html=True)
                        plan = result.get('study_plan', '')
                        
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); padding: 2rem; border-radius: 16px; margin-top: 1rem; color: white;">
                            {plan}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 Download Study Plan",
                            data=plan,
                            file_name=f"study_plan_{exam_date.strftime('%Y%m%d')}.txt",
                            mime="text/plain"
                        )
            else:
                st.warning("⚠️ Please select at least one subject!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 2rem; color: rgba(255, 255, 255, 0.9);">
            <p style="font-size: 1.1rem; margin: 0;">🎓 RADHA • Powered by Qwen 2.5 & Groq API</p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.8;">AI Education for Everyone • Made with ❤️ for Learners</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()