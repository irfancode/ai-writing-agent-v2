"""API Server - FastAPI-based REST API"""

from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json

from ..core.providers.registry import init_registry, get_registry
from ..core.modes.orchestrator import DualModeOrchestrator
from ..core.modes.thinking import ThinkingType
from ..core.modes.non_thinking import WritingStyle
from ..core.memory.context import HighContextMemory
from ..core.agents.multi_agent import MultiAgentSystem


# Global systems
orchestrator: Optional[DualModeOrchestrator] = None
multi_agent: Optional[MultiAgentSystem] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global orchestrator, multi_agent
    
    # Startup
    registry = init_registry()
    memory = HighContextMemory()
    orchestrator = DualModeOrchestrator(registry, memory)
    multi_agent = MultiAgentSystem(registry, memory)
    print("✓ AI Writing Agent initialized")
    
    yield
    
    # Shutdown
    if registry:
        await registry.close_all()
    print("✓ Shutdown complete")


app = FastAPI(
    title="AI Writing Agent API",
    description="Enterprise Open-Source AI Writing System",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Enterprise Auth Middleware (Mock) ---
@app.middleware("http")
async def enterprise_auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/v1/") and request.url.path not in ["/api/v1/auth/login"]:
        auth = request.headers.get("Authorization")
        if not auth:
            pass  # Allow for demo
    return await call_next(request)


# --- Request Models ---
class ThinkRequest(BaseModel):
    prompt: str
    thinking_type: str = "outline"
    depth: str = "medium"
    context: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


class WriteRequest(BaseModel):
    prompt: str
    style: str = "narrative"
    task: str = "draft"
    context: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


class EditRequest(BaseModel):
    text: str
    instruction: str
    context: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


class PipelineRequest(BaseModel):
    topic: str
    thinking_type: str = "outline"
    draft_style: str = "narrative"
    context: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


class RefineRequest(BaseModel):
    text: str
    instruction: str
    iterations: int = 3
    context: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str = "pw"


# --- Routes ---
@app.get("/")
async def root():
    return {
        "name": "AI Writing Agent API",
        "version": "2.0.0",
        "status": "healthy",
    }


@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    """Mock Enterprise SSO endpoint"""
    if request.username == "admin":
        return {"token": "mock-admin-jwt", "role": "admin"}
    elif request.username == "pro":
        return {"token": "mock-pro-jwt", "role": "pro"}
    else:
        return {"token": "mock-user-jwt", "role": "user"}


@app.get("/health")
async def health():
    registry = get_registry()
    health_status = await registry.health_check_all()
    return {
        "status": "healthy" if any(health_status.values()) else "degraded",
        "providers": health_status,
    }


@app.post("/api/v1/think")
async def think(request: ThinkRequest):
    """Execute thinking mode for planning and structure"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    thinking_type_map = {
        "outline": ThinkingType.OUTLINE,
        "character": ThinkingType.CHARACTER,
        "plot": ThinkingType.PLOT,
        "research": ThinkingType.RESEARCH,
        "structure": ThinkingType.STRUCTURE,
        "style_analysis": ThinkingType.STYLE_ANALYSIS,
        "problem_solving": ThinkingType.PROBLEM_SOLVING,
    }
    
    result = await orchestrator.think(
        prompt=request.prompt,
        thinking_type=thinking_type_map.get(request.thinking_type, ThinkingType.OUTLINE),
        depth=request.depth,
        model=request.model,
    )
    
    return {
        "content": result.content,
        "reasoning": {
            "steps": result.thinking_steps or [],
        },
    }


@app.post("/api/v1/write")
async def write(request: WriteRequest):
    """Execute writing mode"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    style_map = {
        "narrative": WritingStyle.NARRATIVE,
        "technical": WritingStyle.TECHNICAL,
        "marketing": WritingStyle.MARKETING,
        "concise": WritingStyle.CONCISE,
        "creative": WritingStyle.CREATIVE,
        "formal": WritingStyle.FORMAL,
        "casual": WritingStyle.CASUAL,
        "academic": WritingStyle.ACADEMIC,
    }
    
    result = await orchestrator.write(
        prompt=request.prompt,
        style=style_map.get(request.style, WritingStyle.NARRATIVE),
        model=request.model,
    )
    
    return {
        "content": result.content,
    }


@app.post("/api/v1/write/stream")
async def write_stream(request: WriteRequest):
    """Execute writing mode with streaming"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    style_map = {
        "narrative": WritingStyle.NARRATIVE,
        "technical": WritingStyle.TECHNICAL,
        "marketing": WritingStyle.MARKETING,
        "concise": WritingStyle.CONCISE,
        "creative": WritingStyle.CREATIVE,
        "formal": WritingStyle.FORMAL,
        "casual": WritingStyle.CASUAL,
        "academic": WritingStyle.ACADEMIC,
    }
    
    async def event_generator():
        async for chunk in orchestrator.stream_write(
            prompt=request.prompt,
            style=style_map.get(request.style, WritingStyle.NARRATIVE),
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/v1/edit")
async def edit(request: EditRequest):
    """Execute editing mode"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    result = await orchestrator.edit(
        text=request.text,
        instruction=request.instruction,
        context=request.context,
        model=request.model,
    )
    
    return {
        "content": result.content,
    }


@app.post("/api/v1/pipeline")
async def pipeline(request: PipelineRequest):
    """Execute full pipeline: think + write"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    thinking_type_map = {
        "outline": ThinkingType.OUTLINE,
        "character": ThinkingType.CHARACTER,
        "plot": ThinkingType.PLOT,
        "research": ThinkingType.RESEARCH,
        "structure": ThinkingType.STRUCTURE,
    }
    
    style_map = {
        "narrative": WritingStyle.NARRATIVE,
        "technical": WritingStyle.TECHNICAL,
        "marketing": WritingStyle.MARKETING,
        "concise": WritingStyle.CONCISE,
        "creative": WritingStyle.CREATIVE,
    }
    
    thinking_result, draft_result = await orchestrator.plan_and_draft(
        topic=request.topic,
        thinking_type=thinking_type_map.get(request.thinking_type, ThinkingType.OUTLINE),
        draft_style=style_map.get(request.draft_style, WritingStyle.NARRATIVE),
        context=request.context,
        model=request.model,
    )
    
    return {
        "thinking": {
            "content": thinking_result.content,
        },
        "draft": {
            "content": draft_result.content,
        },
    }


@app.post("/api/v1/refine")
async def refine(request: RefineRequest):
    """Execute iterative refinement"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    result = await orchestrator.refine(
        text=request.text,
        instruction=request.instruction,
        iterations=request.iterations,
        context=request.context,
        model=request.model,
    )
    
    return {
        "content": result.content,
    }


@app.get("/api/v1/sessions")
async def list_sessions():
    """List all sessions"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    sessions = orchestrator.list_sessions()
    return {"sessions": sessions}


@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session context"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    context = orchestrator.get_session_context(session_id)
    return {"session_id": session_id, "context": context}


@app.get("/api/v1/models")
async def list_models():
    """List available models"""
    registry = get_registry()
    models = registry.list_models()
    return {
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "mode": m.mode.value,
                "context_window": m.context_window,
            }
            for m in models
        ]
    }


@app.get("/api/v1/providers")
async def list_providers():
    """List available providers"""
    registry = get_registry()
    health = await registry.health_check_all()
    return {
        "providers": list(registry._providers.keys()),
        "health": health,
    }


# --- Main ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
