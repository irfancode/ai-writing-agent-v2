"""API Server - FastAPI-based REST API"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from ..core.providers.registry import init_registry, get_registry
from ..core.modes.orchestrator import DualModeOrchestrator
from ..core.modes.thinking import ThinkingType
from ..core.modes.non_thinking import WritingStyle
from ..core.memory.context import HighContextMemory
from ..core.agents.multi_agent import MultiAgentSystem


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    init_registry()
    print("✓ Model registry initialized")
    yield
    # Shutdown
    registry = get_registry()
    await registry.close_all()


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


# Request/Response Models
class ThinkRequest(BaseModel):
    prompt: str
    thinking_type: str = "outline"
    depth: str = "medium"
    model: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    show_reasoning: bool = True


class WriteRequest(BaseModel):
    prompt: str
    style: str = "narrative"
    task: str = "draft"
    model: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    constraints: Optional[List[str]] = None


class EditRequest(BaseModel):
    content: str
    instruction: str
    show_reasoning: bool = False
    style: Optional[str] = None


class PipelineRequest(BaseModel):
    topic: str
    outline_depth: str = "medium"
    draft_style: str = "narrative"
    iterations: int = 2


# Initialize systems
orchestrator: Optional[DualModeOrchestrator] = None
multi_agent: Optional[MultiAgentSystem] = None


@app.on_event("startup")
async def startup():
    global orchestrator, multi_agent
    
    registry = get_registry()
    memory = HighContextMemory()
    
    orchestrator = DualModeOrchestrator(registry, memory)
    multi_agent = MultiAgentSystem(registry, memory)


@app.get("/")
async def root():
    return {
        "name": "AI Writing Agent API",
        "version": "2.0.0",
        "status": "healthy",
    }


@app.get("/health")
async def health():
    registry = get_registry()
    health_status = await registry.health_check_all()
    return {
        "status": "healthy" if any(health_status.values()) else "degraded",
        "providers": health_status,
    }


@app.get("/models")
async def list_models():
    registry = get_registry()
    models = registry.list_models()
    return {
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "mode": m.mode.value,
                "context_window": m.context_window,
                "capabilities": m.capabilities,
            }
            for m in models
        ]
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
        context=request.context,
        depth=request.depth,
        model=request.model,
    )
    
    return {
        "content": result.content,
        "reasoning": {
            "steps": result.thinking_steps,
        } if request.show_reasoning else None,
        "metadata": result.metadata,
    }


@app.post("/api/v1/write")
async def write(request: WriteRequest):
    """Execute non-thinking mode for drafting"""
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
        constraints=request.constraints,
        model=request.model,
    )
    
    return {
        "content": result.content,
        "metadata": result.metadata,
    }


@app.post("/api/v1/edit")
async def edit(request: EditRequest):
    """Edit existing content"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    style = WritingStyle[request.style.upper()] if request.style else None
    
    result = await orchestrator.edit(
        text=request.content,
        instruction=request.instruction,
        show_reasoning=request.show_reasoning,
        style=style,
    )
    
    return {
        "content": result.content,
        "changes": result.changes,
        "reasoning": result.reasoning if request.show_reasoning else None,
        "metadata": result.metadata,
    }


@app.post("/api/v1/pipeline")
async def pipeline(request: PipelineRequest):
    """Execute complete think + draft pipeline"""
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
    }
    
    thinking_result, draft_result = await orchestrator.plan_and_draft(
        topic=request.topic,
        outline_depth=request.outline_depth,
        draft_style=style_map.get(request.draft_style, WritingStyle.NARRATIVE),
    )
    
    return {
        "outline": thinking_result.content,
        "draft": draft_result.content,
        "thinking_steps": thinking_result.thinking_steps,
        "metadata": draft_result.metadata,
    }


@app.post("/api/v1/refine")
async def refine(
    content: str,
    iterations: int = 2,
    focus: Optional[str] = None,
):
    """Iterative refinement"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    result = await orchestrator.refine(
        content=content,
        iterations=iterations,
        focus=focus,
    )
    
    return {
        "content": result.content,
        "metadata": result.metadata,
    }


@app.post("/api/v1/multi-agent")
async def multi_agent_write(
    topic: str,
    agents: List[str] = ["draft", "edit", "polish"],
    style: str = "narrative",
):
    """Multi-agent collaborative writing"""
    if not multi_agent:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    from ..core.agents.multi_agent import AgentType
    
    agent_map = {
        "draft": AgentType.DRAFT,
        "edit": AgentType.EDIT,
        "polish": AgentType.POLISH,
    }
    
    agent_types = [agent_map.get(a, AgentType.DRAFT) for a in agents]
    
    result = await multi_agent.collaborative_write(
        prompt=topic,
        agents=agent_types,
    )
    
    return {
        "content": result,
    }


@app.get("/api/v1/sessions")
async def list_sessions():
    """List active writing sessions"""
    if not orchestrator:
        return {"sessions": []}
    
    sessions = orchestrator.list_sessions()
    return {
        "sessions": [
            {
                "id": s.session_id,
                "topic": s.topic,
                "mode": s.mode.value,
                "created_at": s.created_at,
            }
            for s in sessions
        ]
    }


@app.get("/api/v1/context/{session_id}")
async def get_session_context(session_id: str):
    """Get context for a session"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    context = orchestrator.get_session_context(session_id)
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return context


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server"""
    uvicorn.run(
        "src.api.server:app",
        host=host,
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    run_server()
