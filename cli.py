#!/usr/bin/env python3
"""
CLI Interface for Unified AI Learning Assistant
Simple command-line access to all features with model switching
"""

import argparse
import sys
from main import UnifiedLearningAssistant
import pyttsx3
import speech_recognition as sr
from colorama import init, Fore, Style
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize colorama
init()

class CLI:
    def __init__(self, model_type="auto"):
        try:
            self.assistant = UnifiedLearningAssistant(model_type)
            current_model = self.assistant.get_current_model()
            if current_model == "openvino":
                print(f"{Fore.GREEN}✅ Connected to Qwen 2.5 7B (Local) successfully!{Style.RESET_ALL}")
            elif current_model == "groq":
                print(f"{Fore.GREEN}✅ Connected to Groq API (Llama 3.3 70B) successfully!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to initialize: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please ensure either Qwen model is available or GROQ_API_KEY is set in your .env file{Style.RESET_ALL}")
            sys.exit(1)
            
        self.tts_engine = None
        self.recognizer = sr.Recognizer()
        
    def init_tts(self):
        """Initialize TTS if not already done"""
        if not self.tts_engine:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
            except:
                print(f"{Fore.YELLOW}Warning: TTS not available{Style.RESET_ALL}")
    
    def speak(self, text):
        """Speak text if TTS is enabled"""
        if self.tts_engine:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
    
    def get_speech_input(self):
        """Get speech input"""
        try:
            with sr.Microphone() as source:
                print(f"{Fore.CYAN}🎤 Listening... Speak now!{Style.RESET_ALL}")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print(f"{Fore.CYAN}Processing speech...{Style.RESET_ALL}")
                text = self.recognizer.recognize_google(audio)
                print(f"{Fore.GREEN}Heard: {text}{Style.RESET_ALL}")
                return text
        except Exception as e:
            print(f"{Fore.RED}Speech recognition error: {e}{Style.RESET_ALL}")
            return None
    
    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{text}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
    
    def print_model_info(self):
        """Print current model information"""
        current_model = self.assistant.get_current_model()
        if current_model == "openvino":
            print(f"{Fore.YELLOW}Current Model: Qwen 2.5 7B INT4 (Local){Style.RESET_ALL}")
        elif current_model == "groq":
            print(f"{Fore.YELLOW}Current Model: Llama 3.3 70B (Groq Cloud API){Style.RESET_ALL}")
    
    def switch_model_flow(self):
        """Model switching workflow"""
        self.print_header("🤖 Switch AI Model")
        print("Available models:")
        print("1. Qwen 2.5 7B (Local OpenVINO)")
        print("2. Llama 3.3 70B (Groq Cloud API)")
        
        choice = input("\nSelect model (1 or 2): ").strip()
        
        if choice == "1":
            model_type = "openvino"
        elif choice == "2":
            model_type = "groq"
        else:
            print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
            return
        
        try:
            self.assistant.switch_model(model_type)
            self.print_model_info()
            print(f"{Fore.GREEN}Model switched successfully!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Failed to switch model: {e}{Style.RESET_ALL}")
    
    def print_streaming_response(self, prompt, system_msg=None):
        """Print streaming response from the assistant"""
        print(f"{Fore.CYAN}AI> {Style.RESET_ALL}", end="", flush=True)
        try:
            for chunk in self.assistant.generate_response_stream(prompt, system_msg):
                print(chunk, end="", flush=True)
            print()  # New line after response
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    def interactive_mode(self):
        """Run interactive chat mode"""
        self.print_header("🎓 AI Learning Assistant - Interactive Mode")
        self.print_model_info()
        print(f"{Fore.YELLOW}Commands:{Style.RESET_ALL}")
        print("  /content - Generate educational content")
        print("  /doubt - Ask a question")
        print("  /curriculum - Generate curriculum")
        print("  /grade - Grade code")
        print("  /practice - Practice with Q&A")
        print("  /explain - Explain a concept")
        print("  /model - Switch AI model")
        print("  /speech - Toggle speech input")
        print("  /tts - Toggle text-to-speech")
        print("  /help - Show commands")
        print("  /exit - Exit")
        
        use_speech = False
        use_tts = False
        conversation_history = []
        
        while True:
            try:
                if use_speech:
                    print(f"\n{Fore.CYAN}Press Enter to speak or type your message:{Style.RESET_ALL}")
                    user_input = input()
                    if not user_input:
                        user_input = self.get_speech_input()
                        if not user_input:
                            continue
                else:
                    user_input = input(f"\n{Fore.GREEN}You> {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == '/exit':
                    print(f"{Fore.YELLOW}Goodbye! 👋{Style.RESET_ALL}")
                    break
                
                elif user_input.lower() == '/help':
                    self.interactive_mode()
                    continue
                
                elif user_input.lower() == '/model':
                    self.switch_model_flow()
                    continue
                
                elif user_input.lower() == '/speech':
                    use_speech = not use_speech
                    print(f"{Fore.YELLOW}Speech input: {'ON' if use_speech else 'OFF'}{Style.RESET_ALL}")
                    continue
                
                elif user_input.lower() == '/tts':
                    use_tts = not use_tts
                    if use_tts:
                        self.init_tts()
                    print(f"{Fore.YELLOW}Text-to-Speech: {'ON' if use_tts else 'OFF'}{Style.RESET_ALL}")
                    continue
                
                elif user_input.lower() == '/content':
                    self.content_generation_flow()
                
                elif user_input.lower() == '/doubt':
                    self.doubt_solving_flow()
                
                elif user_input.lower() == '/curriculum':
                    self.curriculum_flow()
                
                elif user_input.lower() == '/grade':
                    self.code_grading_flow()
                
                elif user_input.lower() == '/practice':
                    self.practice_flow()
                
                elif user_input.lower() == '/explain':
                    self.explain_concept_flow()
                
                else:
                    # Direct chat with streaming
                    conversation_history.append({"role": "user", "content": user_input})
                    
                    print(f"\n{Fore.CYAN}AI> {Style.RESET_ALL}", end="", flush=True)
                    
                    full_response = ""
                    for chunk in self.assistant.chat_response_stream(user_input, conversation_history[:-1]):
                        print(chunk, end="", flush=True)
                        full_response += chunk
                    print()  # New line
                    
                    conversation_history.append({"role": "assistant", "content": full_response})
                    
                    if use_tts and full_response:
                        self.speak(full_response[:300])
                        
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Use /exit to quit{Style.RESET_ALL}")
                continue
    
    def content_generation_flow(self):
        """Content generation workflow"""
        self.print_header("📚 Content Generation")
        topic = input("Topic: ")
        content_type = input("Type (notes/quiz/summary): ").lower()
        grade = input("Grade level: ")
        
        print(f"\n{Fore.CYAN}Generating {content_type}...{Style.RESET_ALL}")
        content = self.assistant.generate_content(topic, content_type, grade)
        print(f"\n{content}")
        
        save = input(f"\n{Fore.YELLOW}Save to file? (y/n): {Style.RESET_ALL}")
        if save.lower() == 'y':
            filename = f"{topic}_{content_type}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"{Fore.GREEN}Saved to {filename}{Style.RESET_ALL}")
    
    def doubt_solving_flow(self):
        """Doubt solving workflow with streaming"""
        self.print_header("❓ Doubt Solving")
        question = input("Your question: ")
        subject = input("Subject (optional): ") or "general"
        grade = input("Grade level: ") or "high school"
        
        print(f"\n{Fore.CYAN}Finding answer...{Style.RESET_ALL}")
        prompt = f"Student question ({grade}, {subject}): {question}\n\nProvide a clear, detailed explanation with examples if helpful."
        system_msg = f"You are a patient teacher explaining concepts to {grade} students. Break down complex ideas into simple parts."
        
        self.print_streaming_response(prompt, system_msg)
    
    def curriculum_flow(self):
        """Curriculum generation workflow"""
        self.print_header("📅 Curriculum Generator")
        subject = input("Subject/Course: ")
        duration = input("Duration (e.g., 6 months): ")
        study_type = input("Type (theory/practical/both): ") or "both"
        
        print(f"\n{Fore.CYAN}Creating curriculum...{Style.RESET_ALL}")
        curriculum = self.assistant.generate_curriculum(subject, duration, study_type)
        print(f"\n{curriculum}")
        
        save = input(f"\n{Fore.YELLOW}Save curriculum? (y/n): {Style.RESET_ALL}")
        if save.lower() == 'y':
            filename = f"{subject}_curriculum.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(curriculum)
            print(f"{Fore.GREEN}Saved to {filename}{Style.RESET_ALL}")
    
    def code_grading_flow(self):
        """Code grading workflow"""
        self.print_header("💻 Code Grading")
        language = input("Language (python/java/c++/etc): ")
        problem = input("Problem description (optional): ")
        
        print("Enter your code (type 'END' on a new line when done):")
        code_lines = []
        while True:
            line = input()
            if line == 'END':
                break
            code_lines.append(line)
        
        code = '\n'.join(code_lines)
        
        print(f"\n{Fore.CYAN}Grading code...{Style.RESET_ALL}")
        result = self.assistant.grade_code(code, language, problem)
        
        score = result['score']
        if score >= 80:
            color = Fore.GREEN
        elif score >= 60:
            color = Fore.YELLOW
        else:
            color = Fore.RED
        
        print(f"\n{color}Score: {score}/100{Style.RESET_ALL}")
        print(f"\n{result['feedback']}")
    
    def practice_flow(self):
        """Practice Q&A workflow"""
        self.print_header("🎯 Practice Mode")
        subject = input("Subject: ")
        grade = input("Grade level: ")
        topic = input("Specific topic (optional): ")
        
        qa = self.assistant.student_mode_qa(subject, grade, topic)
        print(f"\n{Fore.CYAN}Question:{Style.RESET_ALL}")
        print(qa['question'])
        
        answer = input("\nYour answer: ")
        
        result = self.assistant.check_student_answer(qa['question'], answer, qa['answer'])
        
        if result['is_correct']:
            print(f"\n{Fore.GREEN}{result['reward']}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}Not quite right!{Style.RESET_ALL}")
        
        print(f"\n{result['feedback']}")
        print(f"\n{Fore.CYAN}Correct answer:{Style.RESET_ALL} {qa['answer']}")
    
    def explain_concept_flow(self):
        """Concept explanation workflow with streaming"""
        self.print_header("🧠 Concept Explorer")
        concept = input("Concept to explain: ")
        grade = input("Grade level: ") or "high school"
        use_analogy = input("Include analogies? (y/n): ").lower() == 'y'
        
        print(f"\n{Fore.CYAN}Explaining {concept}...{Style.RESET_ALL}")
        
        prompt = f"Explain '{concept}' for {grade} students in simple, clear terms."
        if use_analogy:
            prompt += " Include a relatable analogy or real-world example."
        
        system_msg = f"You are an expert at explaining complex concepts to {grade} students. Make it engaging and easy to understand."
        
        self.print_streaming_response(prompt, system_msg)

def main():
    parser = argparse.ArgumentParser(description='Unified AI Learning Assistant CLI')
    parser.add_argument('--model', choices=['openvino', 'groq', 'auto'], default='auto',
                       help='Model to use (default: auto)')
    parser.add_argument('--mode', choices=['interactive', 'quick'], default='interactive',
                       help='CLI mode (default: interactive)')
    parser.add_argument('--action', choices=['content', 'doubt', 'curriculum', 'grade', 'explain'],
                       help='Quick action to perform')
    parser.add_argument('--query', type=str, help='Query for quick actions')
    
    args = parser.parse_args()
    
    # Display startup message
    print(f"{Fore.CYAN}{'='*60}")
    print(f"🎓 RADHA - Responsive AI for Dynamic Holistic Assistance")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    cli = CLI(args.model)
    
    if args.mode == 'interactive':
        cli.interactive_mode()
    elif args.action and args.query:
        # Quick mode
        if args.action == 'doubt':
            answer = cli.assistant.solve_doubt(args.query)
            print(answer)
        elif args.action == 'explain':
            explanation = cli.assistant.explain_concept(args.query)
            print(explanation)
        # Add more quick actions as needed
    else:
        parser.print_help()

if __name__ == "__main__":
    main()