#!/usr/bin/env python3
"""
AI-Powered Interactive Learning Assistant
Unified core functionality supporting both Qwen2.5-7B (OpenVINO) and Groq API
"""

import os
import json
import re
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Iterator
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BaseLearningAssistant(ABC):
    """Base class for learning assistants"""
    
    def __init__(self):
        self.rewards = ["🌟 Excellent!", "🎯 Great job!", "✨ Fantastic!", "🏆 Outstanding!", "💫 Brilliant!"]
    
    @abstractmethod
    def generate_response(self, prompt: str, system_message: str = None, max_tokens: int = 1024) -> str:
        pass
    
    @abstractmethod
    def generate_response_stream(self, prompt: str, system_message: str = None, max_tokens: int = 1024) -> Iterator[str]:
        pass
    
    def generate_content(self, topic: str, content_type: str, grade_level: str) -> str:
        """Generate educational content based on topic and grade level"""
        prompts = {
            "notes": f"Generate comprehensive class notes on '{topic}' for {grade_level} students. Include key concepts, definitions, and examples. Format with clear headings.",
            "quiz": f"Create a 5-question quiz on '{topic}' for {grade_level} students. Include multiple choice and short answer questions with answers at the end.",
            "summary": f"Summarize '{topic}' for {grade_level} students in simple terms. Include the most important points and real-world applications."
        }
        
        prompt = prompts.get(content_type, prompts["summary"])
        system_msg = f"You are an expert educator creating content for {grade_level} students. Make it engaging and age-appropriate."
        
        return self.generate_response(prompt, system_msg, max_tokens=1500)
    
    def solve_doubt(self, question: str, subject: str = "general", grade_level: str = "high school") -> str:
        """Solve student doubts with clear explanations"""
        prompt = f"Student question ({grade_level}, {subject}): {question}\n\nProvide a clear, detailed explanation with examples if helpful."
        system_msg = f"You are a patient teacher explaining concepts to {grade_level} students. Break down complex ideas into simple parts."
        
        return self.generate_response(prompt, system_msg)
    
    def generate_curriculum(self, subject: str, duration: str, study_type: str = "both") -> str:
        """Generate a curriculum plan for a subject"""
        prompt = f"""Create a detailed curriculum plan for:
Subject: {subject}
Duration: {duration}
Study Type: {study_type} (theory/practical/both)

Include:
1. Week-by-week or month-by-month breakdown
2. Learning objectives for each period
3. Practical exercises if applicable
4. Assessment methods
5. Current industry trends and emerging topics
6. Resources and materials needed"""
        
        system_msg = "You are an expert curriculum designer. Create comprehensive, modern curriculum plans that balance theory and practice."
        
        return self.generate_response(prompt, system_msg, max_tokens=2000)
    
    def grade_code(self, code: str, language: str = "python", problem_description: str = "") -> Dict:
        """Grade code submission with detailed feedback"""
        prompt = f"""Grade this {language} code submission:

Problem: {problem_description if problem_description else 'General code review'}

Code:
```{language}
{code}
```

Evaluate based on:
1. Correctness (40 points) - Does it solve the problem? Consider partial credit
2. Readability (20 points) - Clear variable names, comments, structure
3. Efficiency (20 points) - Time/space complexity
4. Code Quality (20 points) - Best practices, error handling

Provide:
- Total score out of 100 after adding scores for each criterion
- Detailed feedback for each criterion
- Suggestions for improvement
- Recognition of alternative approaches"""
        
        system_msg = "You are an expert code reviewer and educator. Be encouraging while providing constructive feedback."
        
        response = self.generate_response(prompt, system_msg, max_tokens=1500)
        
        # Parse response to extract score
        score_match = re.search(r'(?:Total Score:|Score:|Grade:)\s*(\d+)/100', response, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 0
        
        return {
            "score": score,
            "feedback": response,
            "passed": score >= 60
        }
    
    def student_mode_qa(self, subject: str, grade_level: str, topic: str = "") -> Dict:
        """Generate a question for student practice"""
        prompt = f"Generate one educational question for {grade_level} {subject} class{f' on {topic}' if topic else ''}. Make it thought-provoking but appropriate for the level."
        
        question = self.generate_response(prompt, max_tokens=200)
        
        # Generate the answer separately
        answer_prompt = f"What is the correct answer to this question: {question}\nProvide a clear, educational answer."
        answer = self.generate_response(answer_prompt, max_tokens=300)
        
        return {
            "question": question,
            "answer": answer,
            "subject": subject,
            "grade_level": grade_level
        }
    
    def check_student_answer(self, question: str, student_answer: str, correct_answer: str) -> Dict:
        """Check student's answer and provide feedback"""
        prompt = f"""Question: {question}
Correct Answer: {correct_answer}
Student's Answer: {student_answer}

Evaluate if the student's answer is correct. Be strict but fair in your evaluation.
- If the answer is completely wrong or nonsensical, mark it as incorrect
- Only mark as correct if the student demonstrates understanding of the concept
- Consider partial credit only for answers that show some correct understanding
- For mathematical problems, the approach and final answer both matter

Provide encouraging but honest feedback. If wrong, explain what the correct approach should be.

Start your response with either "CORRECT:" or "INCORRECT:" followed by your feedback."""
        
        system_msg = "You are a fair and encouraging teacher. Be honest in evaluation - don't mark wrong answers as correct. Provide constructive feedback."
        
        response = self.generate_response(prompt, system_msg, max_tokens=500)
        
        # More robust correctness check
        is_correct = response.strip().upper().startswith("CORRECT:")
        
        # Clean up the feedback by removing the CORRECT:/INCORRECT: prefix
        feedback = response.replace("CORRECT:", "").replace("INCORRECT:", "").replace("correct:", "").replace("incorrect:", "").strip()
        
        return {
            "is_correct": is_correct,
            "feedback": feedback,
            "reward": random.choice(self.rewards) if is_correct else "Keep trying! 💪"
        }
    
    def teacher_feedback(self, teaching_method: str, curriculum_details: str, challenges: str = "") -> str:
        """Provide feedback for teachers on their methods"""
        prompt = f"""As an educational consultant, provide feedback on:

Teaching Method: {teaching_method}
Curriculum Details: {curriculum_details}
Challenges Faced: {challenges if challenges else 'None specified'}

Provide:
1. Strengths of current approach
2. Areas for improvement
3. Specific suggestions and best practices
4. Resources or techniques to try
5. Ways to increase student engagement"""
        
        system_msg = "You are an experienced educational consultant helping teachers improve their practice. Be supportive and practical."
        
        return self.generate_response(prompt, system_msg, max_tokens=1500)
    
    def explain_concept(self, concept: str, grade_level: str = "high school", use_analogy: bool = True) -> str:
        """Explain a concept in simple terms with optional analogies"""
        prompt = f"Explain '{concept}' for {grade_level} students in simple, clear terms."
        if use_analogy:
            prompt += " Include a relatable analogy or real-world example."
        
        system_msg = f"You are an expert at explaining complex concepts to {grade_level} students. Make it engaging and easy to understand."
        
        return self.generate_response(prompt, system_msg)
    
    def generate_study_plan(self, subjects: List[str], exam_date: str, study_hours_per_day: int) -> str:
        """Generate a personalized study plan"""
        prompt = f"""Create a detailed study plan for:
Subjects: {', '.join(subjects)}
Exam Date: {exam_date}
Available Study Hours per Day: {study_hours_per_day}

Include:
1. Daily schedule with time allocation
2. Subject rotation strategy
3. Review sessions
4. Practice test schedule
5. Tips for effective studying
6. Break times and wellness reminders"""
        
        system_msg = "You are an expert study coach. Create realistic, effective study plans that balance all subjects."
        
        return self.generate_response(prompt, system_msg, max_tokens=2000)
    
    @abstractmethod
    def chat_response(self, message: str, conversation_history: List[Dict] = None) -> str:
        """General chat response with conversation context - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def chat_response_stream(self, message: str, conversation_history: List[Dict] = None) -> Iterator[str]:
        """Streaming chat response with conversation context - must be implemented by subclasses"""
        pass


class OpenVINOLearningAssistant(BaseLearningAssistant):
    """OpenVINO-based learning assistant using Qwen2.5-7B"""
    
    def __init__(self, model_path: str = "Qwen2.5-7B-Instruct-int4-ov", device: str = "CPU"):
        super().__init__()
        self.model_path = model_path
        self.device = device
        self.pipe = None
        
        # Generation config
        self.generation_config = {
            "max_new_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "do_sample": True,
            "repetition_penalty": 1.1,
        }
        
        self.load_model()
    
    def load_model(self):
        """Load the Qwen model"""
        try:
            import openvino_genai as ov_genai
            print(f"Loading Qwen2.5-7B-Instruct INT4 model on {self.device}...")
            self.pipe = ov_genai.LLMPipeline(self.model_path, self.device)
            print("✅ Qwen model loaded successfully!")
        except ImportError:
            raise RuntimeError("OpenVINO GenAI not installed. Please install with: pip install openvino-genai")
        except Exception as e:
            raise RuntimeError(f"Failed to load Qwen model: {e}")
    
    def _format_conversation(self, messages: List[Dict], system_message: str = None) -> str:
        """Format conversation history for Qwen model"""
        if system_message is None:
            system_message = "You are an expert teaching assistant. Respond clearly and accurately. Use simple language for younger students."
        
        # Build the conversation in Qwen format
        formatted = f"<|im_start|>system\n{system_message}<|im_end|>\n"
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                formatted += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif role == "assistant":
                formatted += f"<|im_start|>assistant\n{content}<|im_end|>\n"
        
        # Add the assistant prompt at the end
        formatted += "<|im_start|>assistant\n"
        
        return formatted
    
    def generate_response(self, prompt: str, system_message: str = None, max_tokens: int = 1024) -> str:
        """Generate response from the model"""
        if not self.pipe:
            raise RuntimeError("Model not loaded")
        
        if system_message is None:
            system_message = "You are an expert teaching assistant. Respond clearly and accurately. Use simple language for younger students."
        
        # Format prompt for Qwen
        formatted_prompt = f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        # Update generation config
        config = self.generation_config.copy()
        config["max_new_tokens"] = max_tokens
        
        # Generate response
        response = self.pipe.generate(formatted_prompt, **config)
        
        # Clean response
        response = response.replace("<|im_end|>", "").strip()
        if "<|im_start|>assistant" in response:
            response = response.split("<|im_start|>assistant")[-1].strip()
        
        return response
    
    def generate_response_stream(self, prompt: str, system_message: str = None, max_tokens: int = 1024) -> Iterator[str]:
        """Generate streaming response - OpenVINO doesn't support streaming, so simulate it"""
        response = self.generate_response(prompt, system_message, max_tokens)
        
        # Simulate streaming by yielding chunks
        words = response.split()
        for i in range(0, len(words), 3):
            chunk = ' '.join(words[i:i+3])
            if i + 3 < len(words):
                chunk += ' '
            yield chunk
    
    def chat_response(self, message: str, conversation_history: List[Dict] = None) -> str:
        """General chat response with conversation context"""
        messages = conversation_history.copy() if conversation_history else []
        messages.append({"role": "user", "content": message})
        
        # Format the full conversation for Qwen
        formatted_prompt = self._format_conversation(messages)
        
        # Update generation config
        config = self.generation_config.copy()
        config["max_new_tokens"] = 1024
        
        # Generate response
        try:
            response = self.pipe.generate(formatted_prompt, **config)
            
            # Clean response
            response = response.replace("<|im_end|>", "").strip()
            if "<|im_start|>assistant" in response:
                response = response.split("<|im_start|>assistant")[-1].strip()
            
            # Remove any remaining control tokens
            response = response.replace("<|im_start|>", "").replace("<|endoftext|>", "").strip()
            
            return response
        except Exception as e:
            raise RuntimeError(f"Error in chat: {e}")
    
    def chat_response_stream(self, message: str, conversation_history: List[Dict] = None) -> Iterator[str]:
        """Streaming chat response with conversation context"""
        # Since OpenVINO doesn't support true streaming, we'll generate the full response
        # and simulate streaming
        full_response = self.chat_response(message, conversation_history)
        
        # Simulate streaming by yielding chunks
        words = full_response.split()
        for i in range(0, len(words), 3):
            chunk = ' '.join(words[i:i+3])
            if i + 3 < len(words):
                chunk += ' '
            yield chunk


class GroqLearningAssistant(BaseLearningAssistant):
    """Groq API-based learning assistant"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it in environment variables or .env file")
        
        from groq import Groq
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
        
        # Generation config
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": True,
        }
    
    def _create_messages(self, prompt: str, system_message: str = None) -> List[Dict]:
        """Create message format for Groq API"""
        if system_message is None:
            system_message = "You are an expert teaching assistant. Respond clearly and accurately. Use simple language for younger students."
        
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    
    def generate_response(self, prompt: str, system_message: str = None, max_tokens: int = 1024) -> str:
        """Generate response from Groq API"""
        messages = self._create_messages(prompt, system_message)
        
        # Update generation config
        config = self.generation_config.copy()
        config["stream"] = False  # Non-streaming for simple responses
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **config
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")
    
    def generate_response_stream(self, prompt: str, system_message: str = None, max_tokens: int = 1024) -> Iterator[str]:
        """Generate streaming response from Groq API"""
        messages = self._create_messages(prompt, system_message)
        
        # Update generation config
        config = self.generation_config.copy()
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **config
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise RuntimeError(f"Error generating stream: {e}")
    
    def chat_response(self, message: str, conversation_history: List[Dict] = None) -> str:
        """General chat response with conversation context"""
        messages = conversation_history if conversation_history else []
        messages.append({"role": "user", "content": message})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                stream=False
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Error in chat: {e}")
    
    def chat_response_stream(self, message: str, conversation_history: List[Dict] = None) -> Iterator[str]:
        """Streaming chat response with conversation context"""
        messages = conversation_history if conversation_history else []
        messages.append({"role": "user", "content": message})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise RuntimeError(f"Error in chat stream: {e}")


class UnifiedLearningAssistant:
    """Unified assistant that can switch between OpenVINO and Groq models"""
    
    def __init__(self, model_type: str = "auto"):
        """
        Initialize with specified model type
        model_type: "openvino", "groq", or "auto" (tries OpenVINO first, falls back to Groq)
        """
        self.model_type = model_type
        self.assistant = None
        self.current_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the specified model"""
        if self.model_type == "openvino" or self.model_type == "auto":
            try:
                self.assistant = OpenVINOLearningAssistant()
                self.current_model = "openvino"
                print("✅ Using OpenVINO Qwen model")
            except Exception as e:
                if self.model_type == "openvino":
                    raise RuntimeError(f"Failed to load OpenVINO model: {e}")
                else:
                    print(f"⚠️ OpenVINO model not available: {e}")
                    print("Falling back to Groq API...")
                    self._use_groq()
        
        elif self.model_type == "groq":
            self._use_groq()
        
        else:
            raise ValueError(f"Invalid model_type: {self.model_type}")
    
    def _use_groq(self):
        """Initialize Groq model"""
        try:
            self.assistant = GroqLearningAssistant()
            self.current_model = "groq"
            print("✅ Using Groq API")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Groq API: {e}")
    
    def switch_model(self, model_type: str):
        """Switch to a different model"""
        if model_type == self.current_model:
            return
        
        old_model = self.current_model
        self.model_type = model_type
        
        try:
            self._initialize_model()
        except Exception as e:
            # Restore old model on failure
            self.model_type = old_model
            self._initialize_model()
            raise
    
    def get_current_model(self) -> str:
        """Get the currently active model"""
        return self.current_model
    
    # Delegate all methods to the active assistant
    def __getattr__(self, name):
        if self.assistant:
            return getattr(self.assistant, name)
        raise AttributeError(f"No assistant initialized")


# Utility functions for API
def create_assistant(model_type: str = "auto") -> UnifiedLearningAssistant:
    """Create and return a UnifiedLearningAssistant instance"""
    return UnifiedLearningAssistant(model_type)

if __name__ == "__main__":
    # Test the unified assistant
    print("🎓 Testing Unified AI Learning Assistant...")
    
    try:
        # Test auto mode
        assistant = UnifiedLearningAssistant("auto")
        print(f"Current model: {assistant.get_current_model()}")
        
        # Test content generation
        print("\nGenerating sample content...")
        notes = assistant.generate_content("photosynthesis", "summary", "8th grade")
        print(f"Sample output: {notes[:200]}...")
        
        print("\n✅ All systems operational!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please ensure either Qwen model is downloaded or GROQ_API_KEY is set")