# RADHA - Responsive AI for Dynamic Holistic Assistance

A unified AI-powered interactive learning assistant that combines the power of OpenVINO-optimized Qwen model (local) and Groq API (cloud) to provide comprehensive educational support.

## Detailed Report

You can find the detailed report at: https://drive.google.com/file/d/19fIHyRv-5KbtKiW2g3yp9R4Vx6rLZpao/view?usp=drive_link

## 🌟 Features

- *Dual AI Models*: Choose between local Qwen 2.5-7B (privacy-focused) or Groq Llama 3.3-70B (performance-focused)
- *Interactive Chat Assistant*: Natural conversations with context retention
- *Content Generation*: Create notes, quizzes, and summaries
- *Doubt Solving*: Get instant answers with detailed explanations
- *Curriculum Planning*: Design comprehensive learning paths
- *Code Grading*: Automatic evaluation with constructive feedback
- *Practice Mode*: Interactive Q&A with immediate feedback
- *Teacher Tools*: AI-powered teaching insights and improvements
- *Concept Explorer*: Deep explanations with analogies
- *Study Planner*: Personalized exam preparation schedules
- *Multimodal Support*: Speech input and text-to-speech output
- *Beautiful UI*: Modern, responsive Streamlit interface
- *CLI Support*: Full-featured command-line interface

## 📁 Project Structure

```
RADHA/
├── main.py              # Unified core functionality for both models
├── api.py               # FastAPI backend server
├── app.py               # Streamlit web interface
├── cli.py               # Command-line interface
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── README.md            # This file
└── Qwen2.5-7B-Instruct-int4-ov/  # Qwen model directory (optional)
    ├── openvino_tokenizer.xml
    ├── openvino_tokenizer.bin
    ├── openvino_model.xml
    ├── openvino_model.bin
    └── config.json
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Git
- Microphone (for speech input)
- Speakers (for text-to-speech)

### Step 1: Clone the Repository

```
git clone https://github.com/yourusername/RADHA.git
cd RADHA
```

### Step 2: Create Virtual Environment

```
# Windows
python -m venv venv
venv\Scripts\activate
```
```
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```
pip install -r requirements.txt
```

### Step 4: Set Up Models

#### Option A: Groq API (Recommended for Quick Start)

1. Sign up for a free Groq API key at [https://console.groq.com](https://console.groq.com)
2. Create a .env file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

#### Option B: Qwen Model (Local, Privacy-Focused)

1. Download the Qwen 2.5-7B INT4 model:

```
# Using Hugging Face CLI
pip install huggingface-hub
huggingface-cli download OpenVINO/Qwen2.5-7B-Instruct-int4-ov --local-dir ./Qwen2.5-7B-Instruct-int4-ov
```
#### Or manually download from:
#### https://huggingface.co/OpenVINO/Qwen2.5-7B-Instruct-int4-ov


2. Ensure the model files are in the Qwen2.5-7B-Instruct-int4-ov/ directory

#### Option C: Both Models (Maximum Flexibility)

Follow both Option A and Option B to have both models available for switching.

## 📝 requirements.txt

Create a requirements.txt file with the following content:

```
# Core dependencies
fastapi
uvicorn
streamlit
python-dotenv
requests
pydantic

# AI Models
groq
openvino-genai
huggingface-hub

# Speech and Audio
pyttsx3
SpeechRecognition
pyaudio  # For microphone support

# Utilities
colorama
python-multipart
```

## 🎮 Usage

### 1. Start the API Server

First, always start the backend API server:

```
python api.py
```

The API will start on http://localhost:8000

### 2. Choose Your Interface

#### Option A: Web Interface (Recommended)

In a new terminal:

```
streamlit run app.py
```

Open your browser to http://localhost:8501

#### Option B: Command Line Interface

In a new terminal:

```
# Interactive mode
python cli.py

# Quick mode examples
python cli.py --mode quick --action explain --query "quantum computing"
python cli.py --mode quick --action doubt --query "How does photosynthesis work?"

# Specify model
python cli.py --model qwen  # Use Qwen model
python cli.py --model groq  # Use Groq API
python cli.py --model auto  # Auto-select (default)
```

## 🔧 Configuration

### Environment Variables

Create a .env file with:

```
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Optional: OpenVINO Configuration
OPENVINO_DEVICE=CPU  # or GPU, AUTO
```

### Model Selection

The system automatically selects the best available model:
1. Tries Qwen model first (if available)
2. Falls back to Groq API (if API key is set)
3. Shows error if neither is available

You can manually switch models in:
- *Web UI*: Use the model selector in the sidebar
- *CLI*: Use the /model command or --model flag
- *API*: POST to /switch-model endpoint

## 💡 Features Guide

### Chat Assistant
- Natural conversations with context retention
- Remembers previous messages in the session
- Supports follow-up questions

### Content Generation
- *Notes*: Comprehensive study notes with key concepts
- *Quiz*: 5-question quizzes with answers
- *Summary*: Concise summaries for quick revision

### Code Grading
- Supports Python, Java, JavaScript, C++, C
- Evaluates correctness, readability, efficiency, and quality
- Provides constructive feedback and improvement suggestions

### Practice Mode
- Generates grade-appropriate questions
- Immediate feedback on answers
- Rewards for correct answers

### Speech Features
- *Speech Input*: Click the microphone button to speak
- *Text-to-Speech*: Enable TTS to hear responses

## 🚨 Troubleshooting

### Common Issues

1. *"Cannot connect to API server"*
   - Ensure python api.py is running
   - Check if port 8000 is available

2. *"No models available"*
   - Check if Qwen model is downloaded correctly
   - Verify GROQ_API_KEY in .env file

3. *Speech Recognition Not Working*
   - Install PyAudio: pip install pyaudio
   - On Linux: sudo apt-get install portaudio19-dev
   - On Mac: brew install portaudio

4. *OpenVINO Import Error*
   - Reinstall: pip install --upgrade openvino-genai
   - Check Python version compatibility

5. *Groq API Error*
   - Verify API key is correct
   - Check internet connection
   - Ensure you have API credits

### Model-Specific Notes

*Qwen Model:*
- Requires ~5GB disk space
- Runs on CPU by default
- First load may take 30-60 seconds
- Subsequent loads are faster

*Groq API:*
- Requires internet connection
- Subject to rate limits (free tier)
- Faster response times
- Larger context window

## 🔐 Privacy & Security

- *Qwen Model*: All processing happens locally, no data leaves your device
- *Groq API*: Data is sent to Groq servers (see Groq's privacy policy)
- *Speech Data*: Processed locally, only text is sent to models
- *No Persistent Storage*: Conversations are not saved between sessions

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🙏 Acknowledgments

- OpenVINO team for model optimization
- Groq for fast inference API
- Streamlit for the beautiful UI framework
- The open-source community

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review closed issues for solutions

---

Made with ❤ for learners everywhere
