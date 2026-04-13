"""Dual-Mode Orchestrator - Seamless switching between Thinking and Non-Thinking modes"""

from typing import List, Optional, Dict, Any, AsyncIterator, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..providers.registry import ModelRegistry
from ..providers.base import ModelMode
from ..memory.context import HighContextMemory
from .thinking import ThinkingMode, ThinkingType, ThinkingRequest
from .non_thinking import NonThinkingMode, WritingStyle, DraftRequest
from ..logger import get_logger

logger = get_logger()


class Mode(Enum):
    """Writing modes"""
    THINKING = "thinking"
    NON_THINKING = "non_thinking"


@dataclass
class WritingSession:
    """A writing session with context"""
    session_id: str
    topic: str
    mode: Mode = Mode.NON_THINKING
    context: Dict[str, Any] = field(default_factory=dict)
    memory: Optional[HighContextMemory] = None
    created_at: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WritingResponse:
    """Response from writing operation"""
    content: str
    mode: Mode
    reasoning: Optional[str] = None
    thinking_steps: Optional[List] = None
    changes: Optional[List] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DualModeOrchestrator:
    """
    Orchestrates between Thinking and Non-Thinking modes.
    
    Key Features:
    - Seamless mode switching
    - Shared context across modes
    - High-context memory integration
    - Multi-agent collaboration
    """
    
    def __init__(
        self,
        registry: ModelRegistry,
        memory: Optional[HighContextMemory] = None,
    ):
        self.registry = registry
        self.memory = memory or HighContextMemory()
        logger.info("DualModeOrchestrator initialized")
        
        # Initialize modes
        self.thinking = ThinkingMode(registry)
        self.non_thinking = NonThinkingMode(registry)
        
        # Session management
        self._sessions: Dict[str, WritingSession] = {}
        self._current_session: Optional[WritingSession] = None
    
    def create_session(
        self,
        session_id: str,
        topic: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> WritingSession:
        """Create a new writing session"""
        session = WritingSession(
            session_id=session_id,
            topic=topic,
            context=context or {},
            memory=self.memory.create_session(session_id),
        )
        
        self._sessions[session_id] = session
        self._current_session = session
        
        return session
    
    def set_session(self, session_id: str):
        """Set the current active session"""
        if session_id in self._sessions:
            self._current_session = self._sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[WritingSession]:
        """Get a session by ID"""
        return self._sessions.get(session_id)
    
    async def think(
        self,
        prompt: str,
        thinking_type: ThinkingType = ThinkingType.OUTLINE,
        context: Optional[Dict[str, Any]] = None,
        depth: str = "medium",
        model: Optional[str] = None,
    ) -> WritingResponse:
        logger.debug(f"Thinking mode requested. Type: {thinking_type.value}, Depth: {depth}")
        """
        Execute thinking mode for planning/structure.
        
        This is where Qwen3's and DeepSeek-R1's reasoning
        capabilities shine.
        """
        request = ThinkingRequest(
            task=prompt,
            thinking_type=thinking_type,
            context=context or {},
            depth=depth,
            model=model,
        )
        
        result = await self.thinking.think(request)
        
        if self._current_session:
            self._current_session.mode = Mode.THINKING
            self._current_session.memory.add_to_context(
                "thinking",
                {
                    "type": thinking_type.value,
                    "prompt": prompt,
                    "steps": [s.to_dict() for s in result.steps],
                    "conclusion": result.conclusion,
                }
            )
        
        return WritingResponse(
            content=result.conclusion,
            mode=Mode.THINKING,
            reasoning="\n".join([s.thought for s in result.steps]) if result.steps else None,
            thinking_steps=[s.to_dict() for s in result.steps],
            metadata={
                "thinking_type": thinking_type.value,
                "model": model or self.thinking.default_model,
            },
        )
    
    async def write(
        self,
        prompt: str,
        style: WritingStyle = WritingStyle.NARRATIVE,
        tone: str = "neutral",
        constraints: Optional[List[str]] = None,
        model: Optional[str] = None,
    ) -> WritingResponse:
        """
        Execute non-thinking mode for quick drafting.
        
        Uses speed-optimized models like MiMo-V2.
        """
        if not model:
            best_model = self.registry.get_best_model(mode=ModelMode.NON_THINKING)
            if best_model:
                model = best_model
        
        request = DraftRequest(
            content=prompt,
            task="draft",
            style=style,
            tone=tone,
            constraints=constraints or [],
            model=model,
        )
        
        content = await self.non_thinking.draft(request)
        
        if self._current_session:
            self._current_session.mode = Mode.NON_THINKING
            self._current_session.memory.add_to_context(
                "draft",
                {"prompt": prompt, "style": style.value, "content": content}
            )
        
        return WritingResponse(
            content=content,
            mode=Mode.NON_THINKING,
            metadata={
                "style": style.value,
                "model": model or self.non_thinking.default_model,
            },
        )
    
    async def edit(
        self,
        text: str,
        instruction: str,
        show_reasoning: bool = False,
        style: Optional[WritingStyle] = None,
    ) -> WritingResponse:
        """
        Edit text with optional reasoning traces.
        
        This provides transparency into how the AI
        arrived at suggestions.
        """
        result = await self.non_thinking.edit(
            text=text,
            instruction=instruction,
            show_reasoning=show_reasoning,
            style=style,
        )
        
        return WritingResponse(
            content=result.edited,
            mode=Mode.NON_THINKING,
            reasoning=result.reasoning,
            changes=[c.__dict__ for c in result.changes],
            metadata={
                "instruction": instruction,
                "original_length": len(text),
                "edited_length": len(result.edited),
            },
        )
    
    async def plan_and_draft(
        self,
        topic: str,
        outline_depth: str = "medium",
        draft_style: WritingStyle = WritingStyle.NARRATIVE,
    ) -> tuple[WritingResponse, WritingResponse]:
        """
        Complete workflow: think then write.
        
        1. Use Thinking Mode to create outline/structure
        2. Use Non-Thinking Mode to generate draft
        
        This is the signature Dual-Mode workflow.
        """
        # Step 1: Think - create outline
        thinking_result = await self.think(
            prompt=f"Create a detailed outline for: {topic}",
            thinking_type=ThinkingType.OUTLINE,
            depth=outline_depth,
        )
        
        # Step 2: Draft - use outline to write
        draft_prompt = f"""Write content based on this outline:

{thinking_result.content}

Topic: {topic}

Write in the specified style, following the structure provided."""
        
        draft_result = await self.write(
            prompt=draft_prompt,
            style=draft_style,
        )
        
        # Combine metadata
        draft_result.metadata["thinking_result"] = {
            "steps": thinking_result.thinking_steps,
            "conclusion": thinking_result.content,
        }
        
        return thinking_result, draft_result
    
    async def refine(
        self,
        content: str,
        iterations: int = 2,
        focus: Optional[str] = None,
    ) -> WritingResponse:
        """
        Iterative refinement with thinking + non-thinking.
        
        Multiple passes of improvement.
        """
        current = content
        
        for i in range(iterations):
            # Think about improvements
            _think_result = await self.think(
                prompt=f"Analyze this content and suggest improvements:\n\n{current}",
                thinking_type=ThinkingType.PROBLEM_SOLVING,
                depth="medium",
            )
            
            # Apply improvements
            instruction = focus or "Improve clarity, flow, and engagement"
            edit_result = await self.non_thinking.edit(
                text=current,
                instruction=instruction,
                show_reasoning=False,
            )
            
            current = edit_result.edited
        
        return WritingResponse(
            content=current,
            mode=Mode.NON_THINKING,
            metadata={
                "iterations": iterations,
                "focus": focus,
            },
        )
    
    async def collaborative_write(
        self,
        topic: str,
        agents: List[Callable],
    ) -> str:
        """
        Multi-agent collaborative writing.
        
        Multiple specialized agents work on the same document.
        """
        # Create shared session
        session = self.create_session(
            session_id=f"collab_{id(topic)}",
            topic=topic,
        )
        
        current_content = ""
        
        for agent in agents:
            # Each agent contributes
            result = await agent(topic, current_content, session.memory)
            current_content += result
        
        return current_content
    
    async def stream_write(
        self,
        prompt: str,
        style: WritingStyle = WritingStyle.NARRATIVE,
    ) -> AsyncIterator[str]:
        """Stream draft content as it's generated"""
        async for token in self.non_thinking.stream_draft(
            DraftRequest(
                content=prompt,
                task="draft",
                style=style,
            )
        ):
            yield token
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get accumulated context for a session"""
        session = self._sessions.get(session_id)
        if session and session.memory:
            return session.memory.get_full_context()
        return None
    
    def list_sessions(self) -> List[WritingSession]:
        """List all active sessions"""
        return list(self._sessions.values())
    
    def close_session(self, session_id: str):
        """Close and cleanup a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            if self._current_session and self._current_session.session_id == session_id:
                self._current_session = None
