"""Thinking Mode - Deep planning and reasoning for writing"""

from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio

from ..providers.registry import ModelRegistry
from ..providers.base import GenerationOptions, ModelMode, ReasoningStep, GenerationResult


class ThinkingType(Enum):
    """Types of thinking/planning"""
    OUTLINE = "outline"
    CHARACTER = "character"
    PLOT = "plot"
    RESEARCH = "research"
    STRUCTURE = "structure"
    STYLE_ANALYSIS = "style_analysis"
    PROBLEM_SOLVING = "problem_solving"


@dataclass
class ThinkingRequest:
    """Request for thinking mode"""
    task: str
    thinking_type: ThinkingType
    context: Dict[str, Any] = field(default_factory=dict)
    depth: str = "medium"  # "shallow", "medium", "deep"
    model: Optional[str] = None
    max_steps: int = 10


@dataclass
class ThinkingResult:
    """Result from thinking mode"""
    steps: List[ReasoningStep]
    conclusion: str
    plan: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ThinkingMode:
    """
    Thinking Mode for deep planning, structure, and reasoning.
    
    Uses reasoning-heavy models like DeepSeek-R1 for:
    - Outlining and structure planning
    - Character development
    - Plot point tracking
    - Brand voice definition
    - Complex problem solving
    """
    
    SYSTEM_PROMPTS = {
        ThinkingType.OUTLINE: """You are an expert outline architect. Think deeply about structure before writing.

When creating outlines:
- Consider the overall arc and flow
- Break down into logical sections
- Include key points and sub-points
- Think about transitions
- Consider the reader's journey

Show your thinking process clearly.""",

        ThinkingType.CHARACTER: """You are an expert character developer. Think deeply about character creation.

When developing characters:
- Consider backstory and motivations
- Think about personality traits and quirks
- Consider relationships with other characters
- Plan character arcs and growth
- Think about consistent voice and dialogue patterns

Show your reasoning for each character decision.""",

        ThinkingType.PLOT: """You are an expert plot architect. Think deeply about narrative structure.

When planning plots:
- Consider pacing and tension
- Think about conflict escalation
- Plan reveals and twists
- Consider subplot integration
- Think about satisfying resolution

Show your thinking about why each plot point works.""",

        ThinkingType.RESEARCH: """You are a thorough researcher. Think deeply about topic exploration.

When researching:
- Consider multiple perspectives
- Think about what the audience needs to know
- Consider counterarguments
- Think about supporting evidence
- Consider knowledge gaps

Show your reasoning process for understanding.""",

        ThinkingType.STRUCTURE: """You are an expert document architect. Think deeply about content structure.

When structuring documents:
- Consider the purpose and audience
- Think about information hierarchy
- Consider flow and readability
- Plan for different learning styles
- Think about action items

Show your thinking about structural decisions.""",

        ThinkingType.STYLE_ANALYSIS: """You are an expert style analyst. Think deeply about voice and tone.

When analyzing style:
- Consider the author's unique patterns
- Think about rhythm and flow
- Consider word choice and tone
- Think about what makes this voice distinctive
- Plan how to replicate or contrast

Show your reasoning about style elements.""",

        ThinkingType.PROBLEM_SOLVING: """You are a logical problem solver. Think step by step.

When solving problems:
- Break down the problem clearly
- Consider multiple approaches
- Think through consequences
- Look for patterns
- Consider edge cases

Show your complete reasoning process.""",
    }
    
    def __init__(
        self,
        registry: ModelRegistry,
        default_model: str = "qwen2.5:latest",
    ):
        self.registry = registry
        self.default_model = default_model
        self.history: List[ThinkingResult] = []
    
    async def think(
        self,
        request: ThinkingRequest,
    ) -> ThinkingResult:
        """
        Execute deep thinking/planning.
        
        Args:
            request: The thinking request with task and type
            
        Returns:
            ThinkingResult with reasoning steps and conclusions
        """
        system_prompt = self.SYSTEM_PROMPTS.get(
            request.thinking_type,
            "You are a careful thinker. Show your reasoning process clearly."
        )
        
        # Enhance prompt with context
        enhanced_prompt = self._build_prompt(request)
        
        # Generate with reasoning
        model = request.model or self.default_model
        
        try:
            provider = self.registry.get_provider_for_model(model)
            
            if provider and hasattr(provider, 'think'):
                steps = await provider.think(
                    problem=enhanced_prompt,
                    model=model,
                    max_steps=request.max_steps,
                )
            else:
                # Fallback: generate with reasoning enabled
                result = await self.registry.generate(
                    prompt=enhanced_prompt,
                    model=model,
                    options=GenerationOptions(
                        temperature=0.7,
                        max_tokens=4096,
                        include_reasoning=True,
                    ),
                    system_prompt=system_prompt,
                )
                
                steps = self._parse_reasoning_steps(result.reasoning or result.content)
            
            # Extract conclusion from last step or generate summary
            conclusion = steps[-1].thought if steps else ""
            
            # Build structured plan if applicable
            plan = self._extract_plan(steps, request.thinking_type)
            
            thinking_result = ThinkingResult(
                steps=steps,
                conclusion=conclusion,
                plan=plan,
                metadata={
                    "thinking_type": request.thinking_type.value,
                    "model": model,
                    "depth": request.depth,
                },
            )
            
            self.history.append(thinking_result)
            return thinking_result
            
        except Exception as e:
            raise RuntimeError(f"Thinking mode failed: {e}")
    
    async def outline(
        self,
        topic: str,
        context: Optional[Dict] = None,
        num_sections: int = 5,
    ) -> ThinkingResult:
        """Create a detailed outline"""
        context = context or {}
        context["sections"] = num_sections
        
        request = ThinkingRequest(
            task=f"Create a detailed outline for: {topic}",
            thinking_type=ThinkingType.OUTLINE,
            context=context,
        )
        
        return await self.think(request)
    
    async def develop_character(
        self,
        character_name: str,
        context: Dict[str, Any],
    ) -> ThinkingResult:
        """Develop a character"""
        request = ThinkingRequest(
            task=f"Develop the character: {character_name}",
            thinking_type=ThinkingType.CHARACTER,
            context=context,
            depth="deep",
        )
        
        return await self.think(request)
    
    async def plan_plot(
        self,
        premise: str,
        num_chapters: int = 10,
    ) -> ThinkingResult:
        """Plan plot structure"""
        context = {"chapters": num_chapters}
        
        request = ThinkingRequest(
            task=f"Plan the plot for: {premise}",
            thinking_type=ThinkingType.PLOT,
            context=context,
            depth="deep",
        )
        
        return await self.think(request)
    
    async def research_topic(
        self,
        topic: str,
        focus_areas: Optional[List[str]] = None,
    ) -> ThinkingResult:
        """Research a topic deeply"""
        context = {"focus_areas": focus_areas or []}
        
        request = ThinkingRequest(
            task=f"Research and understand: {topic}",
            thinking_type=ThinkingType.RESEARCH,
            context=context,
        )
        
        return await self.think(request)
    
    async def analyze_style(
        self,
        text: str,
        author_name: Optional[str] = None,
    ) -> ThinkingResult:
        """Analyze writing style"""
        context = {"text": text, "author": author_name}
        
        request = ThinkingRequest(
            task=f"Analyze the style of this writing" + (f" by {author_name}" if author_name else ""),
            thinking_type=ThinkingType.STYLE_ANALYSIS,
            context=context,
            depth="deep",
        )
        
        return await self.think(request)
    
    async def solve_problem(
        self,
        problem: str,
        constraints: Optional[List[str]] = None,
    ) -> ThinkingResult:
        """Solve a complex problem"""
        context = {"constraints": constraints or []}
        
        request = ThinkingRequest(
            task=problem,
            thinking_type=ThinkingType.PROBLEM_SOLVING,
            context=context,
        )
        
        return await self.think(request)
    
    def _build_prompt(self, request: ThinkingRequest) -> str:
        """Build the thinking prompt with context"""
        prompt = request.task
        
        if request.context:
            context_str = "\n\nContext:\n"
            for key, value in request.context.items():
                context_str += f"- {key}: {value}\n"
            prompt += context_str
        
        depth_instructions = {
            "shallow": "Provide a quick overview with main points only.",
            "medium": "Provide a thorough analysis with key details.",
            "deep": "Provide an exhaustive analysis with all relevant details, examples, and considerations.",
        }
        
        prompt += f"\n\n{depth_instructions.get(request.depth, depth_instructions['medium'])}"
        
        return prompt
    
    def _parse_reasoning_steps(self, content: str) -> List[ReasoningStep]:
        """Parse reasoning content into steps"""
        steps = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # Try to extract action/observation patterns
                action = None
                observation = None
                
                if "->" in line:
                    parts = line.split("->", 1)
                    line = parts[0].strip()
                    observation = parts[1].strip()
                
                steps.append(ReasoningStep(
                    step_number=i + 1,
                    thought=line,
                    action=action,
                    observation=observation,
                ))
        
        return steps
    
    def _extract_plan(
        self,
        steps: List[ReasoningStep],
        thinking_type: ThinkingType,
    ) -> Optional[Dict[str, Any]]:
        """Extract structured plan from reasoning steps"""
        plan = {
            "type": thinking_type.value,
            "items": [],
        }
        
        for step in steps:
            if step.thought:
                plan["items"].append(step.thought)
        
        return plan
    
    def get_history(self) -> List[ThinkingResult]:
        """Get thinking history"""
        return self.history
    
    def clear_history(self):
        """Clear thinking history"""
        self.history = []
