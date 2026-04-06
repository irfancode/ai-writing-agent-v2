"""Non-Thinking Mode - Fast drafting and editing"""

from typing import List, Optional, Dict, Any, AsyncIterator, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio

from ..providers.registry import ModelRegistry
from ..providers.base import GenerationOptions, ModelMode


class WritingStyle(Enum):
    """Available writing styles"""
    NARRATIVE = "narrative"
    TECHNICAL = "technical"
    MARKETING = "marketing"
    CONCISE = "concise"
    CREATIVE = "creative"
    FORMAL = "formal"
    CASUAL = "casual"
    ACADEMIC = "academic"


@dataclass
class DraftRequest:
    """Request for non-thinking mode"""
    content: str  # The content to generate/edit
    task: str = "draft"  # "draft", "edit", "rephrase", "expand", "condense"
    style: WritingStyle = WritingStyle.NARRATIVE
    tone: str = "neutral"
    context: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    model: Optional[str] = None


@dataclass
class EditResult:
    """Result from editing"""
    original: str
    edited: str
    changes: List[EditChange]
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EditChange:
    """A single change made during editing"""
    change_type: str  # "grammar", "clarity", "style", "tone", "structure"
    original_segment: str
    new_segment: str
    reason: str
    position: int  # Character position
    confidence: float = 0.9


class NonThinkingMode:
    """
    Non-Thinking Mode for fast drafting and editing.
    
    Uses speed-optimized models like MiMo-V2 for:
    - Quick content generation
    - Editing and rephrasing
    - Format conversion
    - Inline suggestions
    """
    
    TASK_PROMPTS = {
        "draft": "Write high-quality content based on the request. Be clear and engaging.",
        "edit": "Edit the provided text to improve it based on the instructions.",
        "rephrase": "Rephrase the text while maintaining meaning and improving flow.",
        "expand": "Expand the text with more detail, examples, or elaboration.",
        "condense": "Condense the text to be more concise while preserving key points.",
        "grammar": "Check and fix any grammar, spelling, or punctuation errors.",
        "tone": "Adjust the tone of the text as specified.",
        "translate": "Translate the text to the specified language while preserving style.",
    }
    
    def __init__(
        self,
        registry: ModelRegistry,
        default_model: str = "groq/llama-3.1-8b-instant",
    ):
        self.registry = registry
        self.default_model = default_model
        self.edit_history: List[EditResult] = []
    
    async def draft(
        self,
        request: DraftRequest,
    ) -> str:
        """
        Generate draft content quickly.
        
        Args:
            request: Draft request with content/prompt and style
            
        Returns:
            Generated draft content
        """
        prompt = self._build_draft_prompt(request)
        
        model = request.model or self.default_model
        
        style_context = self._get_style_context(request.style)
        
        result = await self.registry.generate(
            prompt=prompt,
            model=model,
            options=GenerationOptions(
                temperature=0.8,
                max_tokens=4096,
            ),
            system_prompt=style_context,
        )
        
        return result.content
    
    async def edit(
        self,
        text: str,
        instruction: str,
        show_reasoning: bool = False,
        style: Optional[WritingStyle] = None,
    ) -> EditResult:
        """
        Edit text with optional reasoning traces.
        
        Args:
            text: Text to edit
            instruction: What to do (improve, fix grammar, etc.)
            show_reasoning: Whether to include reasoning
            style: Target writing style
            
        Returns:
            EditResult with changes and optionally reasoning
        """
        style_context = self._get_style_context(style) if style else ""
        
        prompt = f"""Edit the following text based on the instruction.

Instruction: {instruction}

Text to edit:
{text}

{"Provide a brief explanation of the changes you made." if show_reasoning else ""}
"""
        
        result = await self.registry.generate(
            prompt=prompt,
            model=self.default_model,
            options=GenerationOptions(
                temperature=0.5,
                max_tokens=2048,
                include_reasoning=show_reasoning,
            ),
            system_prompt=style_context,
        )
        
        # Parse changes
        changes = self._parse_changes(text, result.content)
        
        edit_result = EditResult(
            original=text,
            edited=result.content,
            changes=changes,
            reasoning=result.reasoning if show_reasoning else None,
            metadata={
                "instruction": instruction,
                "model": self.default_model,
            },
        )
        
        self.edit_history.append(edit_result)
        return edit_result
    
    async def rephrase(
        self,
        text: str,
        target_style: Optional[WritingStyle] = None,
    ) -> str:
        """Rephrase text"""
        request = DraftRequest(
            content=text,
            task="rephrase",
            style=target_style or WritingStyle.NARRATIVE,
        )
        return await self.draft(request)
    
    async def expand(
        self,
        text: str,
        target_length: int = 500,
    ) -> str:
        """Expand text with more detail"""
        request = DraftRequest(
            content=text,
            task="expand",
            context={"target_length": target_length},
        )
        return await self.draft(request)
    
    async def condense(
        self,
        text: str,
        target_length: Optional[int] = None,
    ) -> str:
        """Condense text"""
        request = DraftRequest(
            content=text,
            task="condense",
            context={"target_length": target_length} if target_length else {},
        )
        return await self.draft(request)
    
    async def grammar_check(
        self,
        text: str,
    ) -> EditResult:
        """Check and fix grammar"""
        return await self.edit(
            text=text,
            instruction="Fix any grammar, spelling, or punctuation errors. Keep the meaning intact.",
            show_reasoning=True,
        )
    
    async def inline_suggestions(
        self,
        text: str,
        interval: int = 50,  # Characters between checks
    ) -> List[EditChange]:
        """
        Generate inline editing suggestions for segments of text.
        
        This is the core of "real-time editing" - the AI reviews
        text in chunks and suggests improvements.
        """
        suggestions = []
        
        # Split text into chunks
        words = text.split()
        chunk_size = interval
        
        chunks = []
        current_pos = 0
        
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            prompt = f"""Review this text segment for improvements.
            
Text: {chunk_text}

Suggest 0-3 edits for clarity, grammar, or style.
Format each suggestion as:
[POS:{current_pos}] [ORIGINAL] -> [NEW] [REASON]

Only suggest if genuinely needed."""
            
            try:
                result = await self.registry.generate(
                    prompt=prompt,
                    model=self.default_model,
                    options=GenerationOptions(
                        temperature=0.3,
                        max_tokens=500,
                    ),
                )
                
                # Parse suggestions
                parsed = self._parse_inline_suggestions(
                    result.content,
                    text,
                    current_pos,
                )
                suggestions.extend(parsed)
                
            except Exception:
                continue
            
            current_pos += len(chunk_text) + 1
        
        return suggestions
    
    async def stream_draft(
        self,
        request: DraftRequest,
    ) -> AsyncIterator[str]:
        """Stream draft content as it's generated"""
        prompt = self._build_draft_prompt(request)
        style_context = self._get_style_context(request.style)
        
        async for token in self.registry.stream(
            prompt=prompt,
            model=self.default_model,
            options=GenerationOptions(
                temperature=0.8,
                max_tokens=4096,
            ),
            system_prompt=style_context,
        ):
            yield token
    
    def _build_draft_prompt(self, request: DraftRequest) -> str:
        """Build the draft prompt"""
        prompt = f"Task: {request.task}\n\n"
        
        if request.content:
            prompt += f"Content: {request.content}\n\n"
        
        if request.context:
            prompt += "Context:\n"
            for key, value in request.context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        if request.constraints:
            prompt += "Constraints:\n"
            for constraint in request.constraints:
                prompt += f"- {constraint}\n"
            prompt += "\n"
        
        prompt += f"Style: {request.style.value}\n"
        prompt += f"Tone: {request.tone}\n"
        
        return prompt
    
    def _get_style_context(self, style: WritingStyle) -> str:
        """Get system prompt for writing style"""
        contexts = {
            WritingStyle.NARRATIVE: "You are a skilled storyteller. Write engaging narrative content with vivid descriptions and compelling flow.",
            WritingStyle.TECHNICAL: "You are a technical writer. Write clear, precise technical content that is easy to understand.",
            WritingStyle.MARKETING: "You are a marketing copywriter. Write persuasive, engaging marketing content with clear value propositions.",
            WritingStyle.CONCISE: "You are a minimalist writer. Write clear, concise content with no unnecessary words.",
            WritingStyle.CREATIVE: "You are a creative writer. Write imaginative, original content with unique voice.",
            WritingStyle.FORMAL: "You are a professional writer. Write formal content appropriate for business contexts.",
            WritingStyle.CASUAL: "You are a conversational writer. Write in a friendly, approachable tone.",
            WritingStyle.ACADEMIC: "You are an academic writer. Write well-structured, citeable content with proper terminology.",
        }
        return contexts.get(style, contexts[WritingStyle.NARRATIVE])
    
    def _parse_changes(
        self,
        original: str,
        edited: str,
    ) -> List[EditChange]:
        """Parse changes between original and edited text"""
        changes = []
        
        # Simple diff-based change detection
        orig_words = original.split()
        edit_words = edited.split()
        
        i, j = 0, 0
        pos = 0
        
        while i < len(orig_words) or j < len(edit_words):
            if i >= len(orig_words):
                # Addition
                changes.append(EditChange(
                    change_type="addition",
                    original_segment="",
                    new_segment=" ".join(edit_words[j:j+5]),
                    reason="Added content",
                    position=pos,
                    confidence=0.8,
                ))
                break
            
            if j >= len(edit_words):
                # Deletion
                changes.append(EditChange(
                    change_type="deletion",
                    original_segment=" ".join(orig_words[i:i+5]),
                    new_segment="",
                    reason="Removed content",
                    position=pos,
                    confidence=0.8,
                ))
                break
            
            if orig_words[i] == edit_words[j]:
                i += 1
                j += 1
                pos += len(orig_words[i-1]) + 1
            else:
                # Change detected
                changes.append(EditChange(
                    change_type="modification",
                    original_segment=orig_words[i],
                    new_segment=edit_words[j],
                    reason="Text modification",
                    position=pos,
                    confidence=0.9,
                ))
                i += 1
                j += 1
                pos += len(orig_words[i-1]) + 1
        
        return changes
    
    def _parse_inline_suggestions(
        self,
        content: str,
        original: str,
        offset: int,
    ) -> List[EditChange]:
        """Parse inline suggestions from model output"""
        suggestions = []
        
        for line in content.split("\n"):
            if "[POS:" in line and "->" in line:
                try:
                    # Extract position
                    pos_start = line.index("[POS:") + 5
                    pos_end = line.index("]", pos_start)
                    pos = int(line[pos_start:pos_end]) + offset
                    
                    # Extract original and new
                    arrow_pos = line.index("->")
                    original_segment = line[pos_end+2:arrow_pos-1].strip()
                    new_segment = line[arrow_pos+2:].strip()
                    
                    # Extract reason
                    reason_end = len(new_segment)
                    if "[" in new_segment:
                        reason_end = new_segment.index("[")
                    reason = new_segment[reason_end:].strip()
                    new_segment = new_segment[:reason_end].strip()
                    
                    suggestions.append(EditChange(
                        change_type="suggestion",
                        original_segment=original_segment,
                        new_segment=new_segment,
                        reason=reason,
                        position=pos,
                        confidence=0.8,
                    ))
                except:
                    continue
        
        return suggestions
    
    def get_edit_history(self) -> List[EditResult]:
        """Get editing history"""
        return self.edit_history
