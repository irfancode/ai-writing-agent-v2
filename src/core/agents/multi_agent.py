"""Multi-Agent System - Draft, Edit, and Polish agents working together"""

from typing import List, Optional, Dict, Any, Callable, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
import asyncio

from ..providers.registry import ModelRegistry
from ..providers.base import GenerationOptions, ModelMode
from ..memory.context import HighContextMemory
from ..modes.non_thinking import WritingStyle


class AgentType(Enum):
    """Types of writing agents"""
    DRAFT = "draft"
    EDIT = "edit"
    POLISH = "polish"


@dataclass
class AgentConfig:
    """Configuration for an agent"""
    agent_type: AgentType
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = ""
    capabilities: List[str] = field(default_factory=list)


@dataclass
class Task:
    """A task for an agent"""
    task_id: str
    agent_type: AgentType
    content: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on


@dataclass
class TaskResult:
    """Result from a task"""
    task_id: str
    agent_type: AgentType
    content: str
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class PipelineResult:
    """Result from a pipeline run"""
    results: List[TaskResult]
    final_content: str
    total_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class DraftAgent:
    """
    Draft Agent - Generates initial content.
    
    Uses creative models for initial generation.
    """
    
    SYSTEM_PROMPT = """You are an expert content drafter. Generate high-quality initial drafts that:

- Capture the essence of the topic
- Use engaging language and structure
- Follow the provided style guidelines
- Include relevant details and examples
- Leave room for refinement

Generate the best possible draft based on the input."""
    
    def __init__(
        self,
        registry: ModelRegistry,
        model: str = "MiniMaxAI/MiniMax-M2",
        config: Optional[AgentConfig] = None,
    ):
        self.registry = registry
        self.model = model
        self.config = config or AgentConfig(
            agent_type=AgentType.DRAFT,
            model=model,
            temperature=0.8,
            max_tokens=8192,
            system_prompt=self.SYSTEM_PROMPT,
            capabilities=["draft", "generate", "create"],
        )
    
    async def write(
        self,
        prompt: str,
        style: WritingStyle = WritingStyle.NARRATIVE,
        context: Optional[str] = None,
        constraints: Optional[List[str]] = None,
    ) -> str:
        """Generate initial draft"""
        full_prompt = self._build_prompt(prompt, style, context, constraints)
        
        result = await self.registry.generate(
            prompt=full_prompt,
            model=self.model,
            options=GenerationOptions(
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            ),
            system_prompt=self.config.system_prompt,
        )
        
        return result.content
    
    async def write_from_outline(
        self,
        outline: str,
        topic: str,
        style: WritingStyle = WritingStyle.NARRATIVE,
    ) -> str:
        """Generate draft from outline"""
        prompt = f"""Write content based on this outline:

Outline:
{outline}

Topic: {topic}

Expand each section fully, maintaining consistent style and voice."""
        
        return await self.write(prompt, style)
    
    async def expand(
        self,
        content: str,
        target_length: int = 1000,
    ) -> str:
        """Expand existing content"""
        prompt = f"""Expand this content to approximately {target_length} words:

{content}

Add more detail, examples, and elaboration while maintaining the same style."""
        
        return await self.write(prompt)
    
    def _build_prompt(
        self,
        prompt: str,
        style: WritingStyle,
        context: Optional[str],
        constraints: Optional[List[str]],
    ) -> str:
        """Build the full prompt"""
        full_prompt = f"Task: {prompt}\n\n"
        
        if context:
            full_prompt += f"Context:\n{context}\n\n"
        
        if constraints:
            full_prompt += "Constraints:\n"
            for c in constraints:
                full_prompt += f"- {c}\n"
            full_prompt += "\n"
        
        full_prompt += f"Style: {style.value}\n"
        
        return full_prompt


class EditAgent:
    """
    Edit Agent - Improves and revises content.
    
    Uses reasoning models for careful editing.
    """
    
    SYSTEM_PROMPT = """You are an expert editor. Improve content by:

- Enhancing clarity and flow
- Strengthening arguments
- Improving structure
- Fixing inconsistencies
- Maintaining author voice

Provide thoughtful, specific improvements."""
    
    def __init__(
        self,
        registry: ModelRegistry,
        model: str = "Qwen/Qwen3-235B-A22B",
        config: Optional[AgentConfig] = None,
    ):
        self.registry = registry
        self.model = model
        self.config = config or AgentConfig(
            agent_type=AgentType.EDIT,
            model=model,
            temperature=0.5,
            max_tokens=4096,
            system_prompt=self.SYSTEM_PROMPT,
            capabilities=["edit", "revise", "improve", "clarify"],
        )
    
    async def revise(
        self,
        content: str,
        focus: str = "all",
        context: Optional[str] = None,
    ) -> str:
        """Revise content with focus"""
        prompt = f"""Revise this content with focus on: {focus}

Original:
{content}"""

        if context:
            prompt += f"\n\nContext:\n{context}"
        
        result = await self.registry.generate(
            prompt=prompt,
            model=self.model,
            options=GenerationOptions(
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            ),
            system_prompt=self.config.system_prompt,
        )
        
        return result.content
    
    async def improve_structure(
        self,
        content: str,
    ) -> str:
        """Improve content structure"""
        return await self.revise(content, focus="structure_organization")
    
    async def improve_clarity(
        self,
        content: str,
    ) -> str:
        """Improve content clarity"""
        return await self.revise(content, focus="clarity_simplification")
    
    async def strengthen_arguments(
        self,
        content: str,
    ) -> str:
        """Strengthen arguments and logic"""
        return await self.revise(content, focus="arguments_logic")


class PolishAgent:
    """
    Polish Agent - Final refinement.
    
    Uses precision models for final polish.
    """
    
    SYSTEM_PROMPT = """You are a professional polish editor. Perform final refinements:

- Check grammar and spelling
- Ensure consistent tone
- Optimize word choice
- Add smooth transitions
- Final quality check

Make it publication-ready."""
    
    def __init__(
        self,
        registry: ModelRegistry,
        model: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        config: Optional[AgentConfig] = None,
    ):
        self.registry = registry
        self.model = model
        self.config = config or AgentConfig(
            agent_type=AgentType.POLISH,
            model=model,
            temperature=0.3,
            max_tokens=2048,
            system_prompt=self.SYSTEM_PROMPT,
            capabilities=["polish", "finalize", "grammar", "tone"],
        )
    
    async def finalize(
        self,
        content: str,
        checks: Optional[List[str]] = None,
    ) -> str:
        """Final polish with checks"""
        checks = checks or ["grammar", "tone", "consistency"]
        
        prompt = f"""Polish this content. Perform these checks:
{', '.join(checks)}

Content:
{content}"""
        
        result = await self.registry.generate(
            prompt=prompt,
            model=self.model,
            options=GenerationOptions(
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            ),
            system_prompt=self.config.system_prompt,
        )
        
        return result.content
    
    async def grammar_check(
        self,
        content: str,
    ) -> str:
        """Check and fix grammar"""
        return await self.finalize(content, checks=["grammar", "spelling", "punctuation"])
    
    async def tone_match(
        self,
        content: str,
        reference: str,
    ) -> str:
        """Match tone to reference"""
        prompt = f"""Rewrite this content to match the tone of the reference:

Reference tone:
{reference}

Content to adjust:
{content}"""
        
        result = await self.registry.generate(
            prompt=prompt,
            model=self.model,
            options=GenerationOptions(
                temperature=0.3,
                max_tokens=len(content.split()) * 2,
            ),
            system_prompt="Match the tone and style of the reference.",
        )
        
        return result.content


class MultiAgentSystem:
    """
    Multi-Agent System - Coordinates Draft, Edit, and Polish agents.
    
    Supports:
    - Sequential pipelines
    - Parallel execution
    - Conditional branching
    - Result caching
    """
    
    def __init__(
        self,
        registry: ModelRegistry,
        memory: Optional[HighContextMemory] = None,
    ):
        self.registry = registry
        self.memory = memory or HighContextMemory()
        
        # Initialize agents
        self.draft_agent = DraftAgent(registry)
        self.edit_agent = EditAgent(registry)
        self.polish_agent = PolishAgent(registry)
        
        # Task queue
        self._tasks: Dict[str, Task] = {}
        self._results: Dict[str, TaskResult] = {}
    
    async def write_and_refine(
        self,
        prompt: str,
        style: WritingStyle = WritingStyle.NARRATIVE,
        iterations: int = 2,
        context: Optional[str] = None,
    ) -> str:
        """
        Complete write and refine pipeline.
        
        1. Draft - Generate initial content
        2. Edit - Improve (x iterations)
        3. Polish - Final polish
        """
        # Step 1: Draft
        current = await self.draft_agent.write(
            prompt=prompt,
            style=style,
            context=context or self.memory.get_for_prompt(),
        )
        
        # Step 2: Edit iterations
        for _ in range(iterations):
            current = await self.edit_agent.revise(
                content=current,
                context=context,
            )
        
        # Step 3: Polish
        final = await self.polish_agent.finalize(current)
        
        return final
    
    async def collaborative_write(
        self,
        prompt: str,
        agents: List[AgentType],
        context: Optional[str] = None,
    ) -> str:
        """
        Run multiple agents in sequence.
        
        Args:
            prompt: Initial prompt
            agents: Order of agents to run
            context: Optional context
        """
        current = ""
        
        for agent_type in agents:
            if agent_type == AgentType.DRAFT:
                current = await self.draft_agent.write(
                    prompt=prompt if not current else current,
                    context=context,
                )
            elif agent_type == AgentType.EDIT:
                current = await self.edit_agent.revise(
                    content=current,
                    context=context,
                )
            elif agent_type == AgentType.POLISH:
                current = await self.polish_agent.finalize(current)
        
        return current
    
    async def parallel_draft(
        self,
        prompts: List[str],
        style: WritingStyle = WritingStyle.NARRATIVE,
    ) -> List[str]:
        """
        Generate multiple drafts in parallel.
        
        Useful for A/B testing or multiple perspectives.
        """
        tasks = [
            self.draft_agent.write(prompt, style=style)
            for prompt in prompts
        ]
        
        return await asyncio.gather(*tasks)
    
    async def best_of_n(
        self,
        prompt: str,
        n: int = 3,
        style: WritingStyle = WritingStyle.NARRATIVE,
        evaluation_focus: str = "quality",
    ) -> str:
        """
        Generate N drafts and select the best.
        
        Useful for high-stakes content.
        """
        # Generate drafts in parallel
        drafts = await self.parallel_draft([prompt] * n, style)
        
        # Evaluate and select best
        best_draft = drafts[0]
        best_score = 0
        
        for draft in drafts[1:]:
            score = self._evaluate_quality(draft, evaluation_focus)
            if score > best_score:
                best_score = score
                best_draft = draft
        
        # Polish the best draft
        return await self.polish_agent.finalize(best_draft)
    
    def _evaluate_quality(self, content: str, focus: str) -> float:
        """Simple quality evaluation"""
        score = 0.5
        
        # Length check
        word_count = len(content.split())
        if 200 < word_count < 2000:
            score += 0.2
        
        # Structure check
        if "\n\n" in content:
            score += 0.1
        
        # Completeness check
        if not content.endswith((".", "!", "?")):
            score -= 0.1
        
        return score
    
    async def stream_pipeline(
        self,
        prompt: str,
        style: WritingStyle = WritingStyle.NARRATIVE,
    ) -> AsyncIterator[tuple[AgentType, str]]:
        """
        Stream the pipeline output by agent.
        
        Yields tuples of (agent, content_chunk)
        """
        # Draft first
        yield AgentType.DRAFT, ""
        async for chunk in self.registry.stream(
            prompt=prompt,
            model=self.draft_agent.model,
            system_prompt=self.draft_agent.config.system_prompt,
        ):
            yield AgentType.DRAFT, chunk
        
        # Then edit
        yield AgentType.EDIT, ""
        draft_content = await self.draft_agent.write(prompt, style)
        edited_content = await self.edit_agent.revise(draft_content)
        yield AgentType.EDIT, edited_content
        
        # Then polish
        yield AgentType.POLISH, ""
        final_content = await self.polish_agent.finalize(edited_content)
        yield AgentType.POLISH, final_content
