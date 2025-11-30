"""
Main FastAPI Application for Educational AI Agent
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
from datetime import datetime

from agents.orchestrator import EducationalAgentOrchestrator
from memory.session import SessionManager
from memory.profiles import StudentProfileManager

# Initialize FastAPI app
app = FastAPI(
    title="Educational AI Agent API",
    description="API for AI-powered educational assistance",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active sessions (use Redis in production)
active_orchestrators: Dict[str, EducationalAgentOrchestrator] = {}

# Request/Response Models
class MessageRequest(BaseModel):
    student_id: str
    message: str
    session_id: Optional[str] = None
    allow_web_search: bool = True

class MessageResponse(BaseModel):
    message: str
    session_id: str
    student_level: str
    progress: int
    topics_detected: List[str]
    tools_used: List[str]
    timestamp: str

class SessionSummaryResponse(BaseModel):
    session_id: str
    student_id: str
    duration: float
    messages_count: int
    topics_explored: List[str]
    progress: int
    level: str

class StudentProfileResponse(BaseModel):
    student_id: str
    level: str
    progress: int
    topics: List[str]
    total_questions: int
    last_active: str

class TeacherOverride(BaseModel):
    student_id: str
    session_id: str
    message: str
    reason: str
    topics: Optional[List[str]] = []


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Educational AI Agent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """
    Process student message and return AI response
    
    Implements flowchart steps:
    1. Integrate AI with Systems
    2. Collect Data in Real Time
    3. Maintain Human Control (optional override)
    4. Build Long-Term Learning Graphs
    """
    try:
        # Get or create orchestrator for this student
        orchestrator_key = f"{request.student_id}_{request.session_id or 'new'}"
        
        if orchestrator_key not in active_orchestrators:
            # Load API key from environment
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise HTTPException(
                    status_code=500,
                    detail="ANTHROPIC_API_KEY not configured"
                )
            
            orchestrator = EducationalAgentOrchestrator(
                anthropic_api_key=api_key,
                student_id=request.student_id,
                session_id=request.session_id
            )
            active_orchestrators[orchestrator_key] = orchestrator
        else:
            orchestrator = active_orchestrators[orchestrator_key]
        
        # Process message through agent
        response = orchestrator.process_message(
            user_message=request.message,
            allow_web_search=request.allow_web_search
        )
        
        return MessageResponse(**response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/teacher/override")
async def teacher_override(override: TeacherOverride):
    """
    Allow teacher to override AI response (Human Control - Flowchart Step 3)
    """
    try:
        orchestrator_key = f"{override.student_id}_{override.session_id}"
        
        if orchestrator_key not in active_orchestrators:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        orchestrator = active_orchestrators[orchestrator_key]
        
        response = orchestrator.process_message(
            user_message="",
            teacher_override={
                'message': override.message,
                'reason': override.reason,
                'topics': override.topics
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/summary", response_model=SessionSummaryResponse)
async def get_session_summary(session_id: str):
    """Get comprehensive session summary"""
    try:
        # Find orchestrator with this session
        orchestrator = None
        for key, orch in active_orchestrators.items():
            if orch.session_id == session_id:
                orchestrator = orch
                break
        
        if not orchestrator:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        summary = orchestrator.get_session_summary()
        return SessionSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/{student_id}/profile", response_model=StudentProfileResponse)
async def get_student_profile(student_id: str):
    """Get student profile with learning history"""
    try:
        profile_manager = StudentProfileManager(student_id)
        profile = profile_manager.get_or_create_profile()
        
        return StudentProfileResponse(**profile)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/{student_id}/analytics")
async def get_student_analytics(student_id: str):
    """Get learning analytics and progress graphs"""
    try:
        # This would integrate with analytics tool
        from agents.tools import AnalyticsTool
        
        analytics = AnalyticsTool(student_id)
        progress_summary = analytics.get_progress_summary()
        learning_graph = analytics.generate_learning_graph()
        
        return {
            'student_id': student_id,
            'progress_summary': progress_summary,
            'learning_graph': learning_graph,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/session/{session_id}/end")
async def end_session(session_id: str):
    """End session and cleanup resources"""
    try:
        # Find and remove orchestrator
        keys_to_remove = []
        for key, orch in active_orchestrators.items():
            if orch.session_id == session_id:
                summary = orch.get_session_summary()
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del active_orchestrators[key]
        
        return {
            'status': 'session_ended',
            'session_id': session_id,
            'summary': summary if keys_to_remove else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat/{student_id}")
async def websocket_chat(websocket: WebSocket, student_id: str):
    """
    WebSocket endpoint for real-time chat
    Supports streaming responses and live updates
    """
    await websocket.accept()
    
    try:
        # Initialize orchestrator
        api_key = os.getenv('ANTHROPIC_API_KEY')
        orchestrator = EducationalAgentOrchestrator(
            anthropic_api_key=api_key,
            student_id=student_id
        )
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get('message', '')
            
            if not message:
                continue
            
            # Process message
            response = orchestrator.process_message(
                user_message=message,
                allow_web_search=data.get('allow_web_search', True)
            )
            
            # Send response
            await websocket.send_json({
                'type': 'message',
                'data': response
            })
            
            # Send progress update
            await websocket.send_json({
                'type': 'progress',
                'data': {
                    'progress': response['progress'],
                    'level': response['student_level'],
                    'topics': response['topics_detected']
                }
            })
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for student {student_id}")
    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'data': {'message': str(e)}
        })
        await websocket.close()

# Additional utility endpoints

@app.get("/api/topics")
async def get_available_topics():
    """Get list of available AI topics"""
    return {
        'topics': [
            {
                'id': 'machine_learning',
                'name': 'Machine Learning',
                'level': 'Beginner',
                'description': 'Learn how computers learn from data'
            },
            {
                'id': 'neural_networks',
                'name': 'Neural Networks',
                'level': 'Intermediate',
                'description': 'Understand brain-inspired AI models'
            },
            {
                'id': 'nlp',
                'name': 'Natural Language Processing',
                'level': 'Intermediate',
                'description': 'How AI understands human language'
            },
            {
                'id': 'computer_vision',
                'name': 'Computer Vision',
                'level': 'Intermediate',
                'description': 'Teaching computers to see and understand images'
            },
            {
                'id': 'ai_ethics',
                'name': 'AI Ethics',
                'level': 'Beginner',
                'description': 'Responsible and fair AI development'
            },
            {
                'id': 'generative_ai',
                'name': 'Generative AI',
                'level': 'Advanced',
                'description': 'AI that creates new content'
            }
        ]
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        'status': 'healthy',
        'active_sessions': len(active_orchestrators),
        'timestamp': datetime.now().isoformat(),
        'anthropic_configured': bool(os.getenv('ANTHROPIC_API_KEY'))
    }

if __name__ == "__main__":
    # Run the application
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
