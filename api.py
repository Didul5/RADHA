#!/usr/bin/env python3
"""
FastAPI Backend for Unified AI Learning Assistant
Serves API endpoints on localhost:8000 with streaming support
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
from datetime import datetime
import json
import asyncio
from main import create_assistant, UnifiedLearningAssistant

# Initialize FastAPI app
app = FastAPI(title="Unified AI Learning Assistant API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global assistant instance
assistant: UnifiedLearningAssistant = None

# Pydantic models for request/response
class ModelSwitchRequest(BaseModel):
    model_type: str  # "openvino" or "groq"

class ContentRequest(BaseModel):
    topic: str
    content_type: str = "summary"  # notes, quiz, summary
    grade_level: str = "high school"

class DoubtRequest(BaseModel):
    question: str
    subject: str = "general"
    grade_level: str = "high school"

class CurriculumRequest(BaseModel):
    subject: str
    duration: str
    study_type: str = "both"  # theory, practical, both

class CodeGradingRequest(BaseModel):
    code: str
    language: str = "python"
    problem_description: str = ""

class StudentQARequest(BaseModel):
    subject: str
    grade_level: str
    topic: Optional[str] = ""

class AnswerCheckRequest(BaseModel):
    question: str
    student_answer: str
    correct_answer: str

class TeacherFeedbackRequest(BaseModel):
    teaching_method: str
    curriculum_details: str
    challenges: Optional[str] = ""

class ConceptRequest(BaseModel):
    concept: str
    grade_level: str = "high school"
    use_analogy: bool = True

class StudyPlanRequest(BaseModel):
    subjects: List[str]
    exam_date: str
    study_hours_per_day: int

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []

@app.on_event("startup")
async def startup_event():
    """Initialize the assistant on startup"""
    global assistant
    try:
        assistant = create_assistant("auto")  # Auto-detect model
        print(f"✅ AI Assistant initialized successfully with {assistant.get_current_model()}")
    except Exception as e:
        print(f"❌ Failed to initialize assistant: {e}")
        print("Make sure either Qwen model is available or GROQ_API_KEY is set")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Unified AI Learning Assistant API",
        "status": "operational" if assistant else "error",
        "current_model": assistant.get_current_model() if assistant else "none",
        "available_models": ["openvino", "groq"],
        "endpoints": [
            "/model-info",
            "/switch-model",
            "/chat",
            "/chat-stream",
            "/generate-content",
            "/solve-doubt",
            "/generate-curriculum",
            "/grade-code",
            "/student-qa",
            "/check-answer",
            "/teacher-feedback",
            "/explain-concept",
            "/study-plan"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if assistant else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "model": assistant.get_current_model() if assistant else "none"
    }

@app.get("/model-info")
async def model_info():
    """Get current model information"""
    return {
        "current_model": assistant.get_current_model() if assistant else "none",
        "model_details": {
            "openvino": "Qwen2.5-7B-Instruct INT4 (Local)",
            "groq": "Llama 3.3 70B (Cloud API)"
        }.get(assistant.get_current_model() if assistant else "none", "Unknown")
    }

@app.post("/switch-model")
async def switch_model(request: ModelSwitchRequest):
    """Switch between models"""
    try:
        assistant.switch_model(request.model_type)
        return {
            "success": True,
            "current_model": assistant.get_current_model(),
            "message": f"Successfully switched to {request.model_type}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint for general conversation"""
    try:
        response = assistant.chat_response(
            request.message,
            request.conversation_history
        )
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "model": assistant.get_current_model()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat-stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint"""
    async def generate():
        try:
            for chunk in assistant.chat_response_stream(
                request.message,
                request.conversation_history
            ):
                yield json.dumps({"content": chunk}) + "\n"
                await asyncio.sleep(0.01)  # Small delay for smooth streaming
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
    
    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )

@app.post("/generate-content")
async def generate_content(request: ContentRequest):
    """Generate educational content"""
    try:
        content = assistant.generate_content(
            request.topic,
            request.content_type,
            request.grade_level
        )
        return {
            "content": content,
            "metadata": {
                "topic": request.topic,
                "type": request.content_type,
                "grade_level": request.grade_level,
                "model": assistant.get_current_model()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/solve-doubt")
async def solve_doubt(request: DoubtRequest):
    """Solve student doubts"""
    try:
        solution = assistant.solve_doubt(
            request.question,
            request.subject,
            request.grade_level
        )
        return {
            "solution": solution,
            "question": request.question,
            "model": assistant.get_current_model()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-curriculum")
async def generate_curriculum(request: CurriculumRequest):
    """Generate curriculum plan"""
    try:
        curriculum = assistant.generate_curriculum(
            request.subject,
            request.duration,
            request.study_type
        )
        return {
            "curriculum": curriculum,
            "metadata": {
                "subject": request.subject,
                "duration": request.duration,
                "study_type": request.study_type,
                "model": assistant.get_current_model()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/grade-code")
async def grade_code(request: CodeGradingRequest):
    """Grade code submission"""
    try:
        result = assistant.grade_code(
            request.code,
            request.language,
            request.problem_description
        )
        result["model"] = assistant.get_current_model()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/student-qa")
async def student_qa(request: StudentQARequest):
    """Generate question for student practice"""
    try:
        qa = assistant.student_mode_qa(
            request.subject,
            request.grade_level,
            request.topic
        )
        qa["model"] = assistant.get_current_model()
        return qa
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-answer")
async def check_answer(request: AnswerCheckRequest):
    """Check student's answer"""
    try:
        result = assistant.check_student_answer(
            request.question,
            request.student_answer,
            request.correct_answer
        )
        result["model"] = assistant.get_current_model()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/teacher-feedback")
async def teacher_feedback(request: TeacherFeedbackRequest):
    """Provide feedback for teachers"""
    try:
        feedback = assistant.teacher_feedback(
            request.teaching_method,
            request.curriculum_details,
            request.challenges
        )
        return {
            "feedback": feedback,
            "model": assistant.get_current_model()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-concept")
async def explain_concept(request: ConceptRequest):
    """Explain a concept"""
    try:
        explanation = assistant.explain_concept(
            request.concept,
            request.grade_level,
            request.use_analogy
        )
        return {
            "explanation": explanation,
            "concept": request.concept,
            "model": assistant.get_current_model()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/study-plan")
async def generate_study_plan(request: StudyPlanRequest):
    """Generate personalized study plan"""
    try:
        plan = assistant.generate_study_plan(
            request.subjects,
            request.exam_date,
            request.study_hours_per_day
        )
        return {
            "study_plan": plan,
            "metadata": {
                "subjects": request.subjects,
                "exam_date": request.exam_date,
                "hours_per_day": request.study_hours_per_day,
                "model": assistant.get_current_model()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api:app",
        host="localhost",
        port=8000,
        reload=False,
        log_level="info"
    )