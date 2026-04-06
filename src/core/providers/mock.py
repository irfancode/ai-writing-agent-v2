"""Mock Provider - Simulates AI responses for testing without API keys"""

import time
import asyncio
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass

from .base import (
    ModelProvider, ModelConfig, GenerationResult, GenerationOptions,
    ProviderType, ModelMode, ReasoningStep
)


MOCK_RESPONSES = {
    "write": {
        "haiku": """```
Code compiles clean,
Errors vanish in the night,
Pure logic flows free.
```""",
        "blog": """# The Future of AI Writing

In 2026, artificial intelligence has transformed how we create content. From blog posts to technical documentation, AI writing agents are becoming indispensable tools for creators everywhere.

## Key Benefits

1. **Speed**: Generate content in seconds
2. **Consistency**: Maintain brand voice across all content
3. **Scalability**: Produce more content without burnout
4. **Cost-effective**: Free-tier APIs make AI accessible to everyone

## The Zero-Cost Revolution

The democratization of AI writing tools is here. With free APIs from Groq, Together AI, and HuggingFace, anyone can harness the power of large language models without breaking the bank.

## Conclusion

AI writing agents are not here to replace human creativity—they're here to augment it, handling the heavy lifting so creators can focus on what matters most: meaningful ideas.""",
        "email": """Subject: Quick Update on Project Status

Hi Team,

Just wanted to share a quick update on our progress this week.

## Completed
- Finalized API integration
- Completed user testing phase
- Documented all endpoints

## In Progress
- Performance optimization
- UI refinements based on feedback

## Next Week
- Launch preparation
- Marketing materials review

Let me know if you have any questions or concerns.

Best regards,
[Your Name]""",
        "linkedin": """🚀 Excited to share that I've been exploring the intersection of AI and content creation!

The landscape of AI writing tools has evolved dramatically. What once required expensive API subscriptions now offers generous free tiers from multiple providers.

Key insight: The best AI writing agent isn't the most powerful—it's the one that works seamlessly with your workflow.

What AI tools are you using? 👇""",
        "technical": """# API Integration Guide

## Overview

This guide covers integrating the AI Writing Agent with your existing systems.

## Prerequisites

- Python 3.10+
- API key from your preferred provider
- Basic understanding of async programming

## Installation

```bash
pip install ai-writing-agent
```

## Basic Usage

```python
from ai_writing_agent import DualModeOrchestrator

orchestrator = DualModeOrchestrator()

# Generate content
result = await orchestrator.write(
    prompt="Write an introduction for a tech blog",
    style="technical"
)
```

## Advanced Configuration

Configure multiple providers for automatic failover:

```python
orchestrator = DualModeOrchestrator(
    providers=["groq", "together", "huggingface"]
)
```

## Error Handling

Always implement proper error handling:

```python
try:
    result = await orchestrator.write(prompt)
except ProviderError as e:
    # Fallback logic here
    pass
```""",
    },
    "think": {
        "outline": """# Structure Analysis: The Discovery

## I. Introduction
- Hook: The moment everything changed
- Context: Setting the scene

## II. Rising Action
- First signs of discovery
- Character's initial reaction
- Building tension

## III. The Revelation
- Main discovery moment
- Emotional impact
- Stakes raised

## IV. Consequences
- Immediate aftermath
- Character growth opportunity
- New challenges introduced

## V. Closing
- Reflection point
- Setup for next chapter
- Thematic resonance""",
        "character": """# Character Analysis: Dr. Sarah Chen

## Background
- Former marine biologist
- Lost partner in research expedition
- Driven by need for answers

## Motivation
- Primary: Prove theory about deep-sea ecosystems
- Secondary: Honor partner's legacy
- Hidden: Fear of failure repeating

## Personality Traits
- Analytical and methodical
- Stubborn to a fault
- Warm heart beneath tough exterior

## Arc
- Beginning: Isolated, grief-stricken
- Middle: Opens up to team
- End: Accepts past, embraces future

## Relationships
- Partner (deceased): Professional and romantic
- Protagonist: Mentor figure
- Antagonist: Competing for same discovery""",
        "research": """# Research: The Discovery

## What We Know
- Significant archaeological find
- Dating suggests ancient advanced civilization
- Location偏僻但可访问

## Key Questions
1. How did they achieve this technology?
2. What happened to this civilization?
3. How does this change our understanding?

## Evidence Analysis
- Radiocarbon dating: Confirmed
- Artifacts: Multiple categories
- Preservation: Exceptional condition

## Expert Opinions
- Dr. Smith: "Revolutionary find"
- Dr. Johnson: "Raises more questions"
- Consensus: Needs further study

## Next Steps
1. Expand excavation
2. Form international team
3. Publish preliminary findings""",
    },
    "edit": {
        "grammar": """The quick brown fox jumps over the lazy dog. This classic sentence has been used for centuries to demonstrate the variety of letters in the English alphabet.""",
        "tone_professional": """I am writing to inform you of a recent development regarding our project timeline. After careful consideration, we have determined that an extension would be beneficial to ensure the quality of deliverables meets our standards. Please review the attached revised schedule and provide your feedback at your earliest convenience.""",
        "tone_casual": """Hey! Just wanted to let you know we've pushed back the deadline a bit. We're taking extra time to make sure everything's solid. Check out the new timeline when you get a chance!""",
        "clarity": """The system utilizes advanced machine learning algorithms trained on vast datasets of human-generated text. It processes input through multiple neural network layers, generating contextually appropriate responses that maintain coherence across extended conversations.""",
    },
}


@dataclass
class MockGenerationResult:
    content: str
    model: str
    latency_ms: float


class MockProvider(ModelProvider):
    """
    Mock provider for testing without API keys.
    
    Provides realistic responses for all supported operations.
    """
    
    def __init__(
        self,
        latency_ms: int = 500,
        error_rate: float = 0.0,
    ):
        super().__init__(
            name="mock",
            provider_type=ProviderType.OPENAI,
        )
        self.latency_ms = latency_ms
        self.error_rate = error_rate
        self._register_mock_models()
    
    def _register_mock_models(self):
        models = [
            ModelConfig(
                id="mock/llama-3.3-70b",
                name="Mock Llama 3.3 70B",
                mode=ModelMode.NON_THINKING,
                context_window=128000,
                capabilities=["text", "fast", "creative"],
                metadata={"mock": True},
            ),
            ModelConfig(
                id="mock/mixtral-8x7b",
                name="Mock Mixtral 8x7B",
                mode=ModelMode.THINKING,
                context_window=32768,
                capabilities=["text", "reasoning", "fast"],
                metadata={"mock": True},
            ),
        ]
        for model in models:
            self.register_model(model)
    
    def _get_mock_response(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        
        if "haiku" in prompt_lower:
            return MOCK_RESPONSES["write"]["haiku"]
        elif "blog" in prompt_lower or "post" in prompt_lower:
            return MOCK_RESPONSES["write"]["blog"]
        elif "email" in prompt_lower:
            return MOCK_RESPONSES["write"]["email"]
        elif "linkedin" in prompt_lower:
            return MOCK_RESPONSES["write"]["linkedin"]
        elif "technical" in prompt_lower or "api" in prompt_lower or "documentation" in prompt_lower:
            return MOCK_RESPONSES["write"]["technical"]
        elif "outline" in prompt_lower:
            return MOCK_RESPONSES["think"]["outline"]
        elif "character" in prompt_lower:
            return MOCK_RESPONSES["think"]["character"]
        elif "research" in prompt_lower:
            return MOCK_RESPONSES["think"]["research"]
        elif "grammar" in prompt_lower or "fix" in prompt_lower:
            return MOCK_RESPONSES["edit"]["grammar"]
        elif "professional" in prompt_lower:
            return MOCK_RESPONSES["edit"]["tone_professional"]
        elif "casual" in prompt_lower or "friendly" in prompt_lower:
            return MOCK_RESPONSES["edit"]["tone_casual"]
        elif "clarity" in prompt_lower or "simplify" in prompt_lower:
            return MOCK_RESPONSES["edit"]["clarity"]
        else:
            return f"""# Generated Content

Thank you for your prompt. This content was generated by the AI Writing Agent mock provider.

**Prompt received:** {prompt[:100]}...

## Key Features Demonstrated

1. **Dual-Mode Architecture**: Seamless switching between thinking and non-thinking modes
2. **Multi-Provider Support**: Works with Groq, Together AI, HuggingFace, and more
3. **Zero-Cost Ready**: Designed for free-tier APIs

## Next Steps

To test with real APIs, set your API key:
```bash
export GROQ_API_KEY="your-key-here"
export TOGETHER_API_KEY="your-key-here"
```
"""
    
    async def generate(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
    ) -> GenerationResult:
        start_time = time.time()
        
        if self.error_rate > 0 and asyncio.current_task():
            await asyncio.sleep(0.01)
        
        await asyncio.sleep(self.latency_ms / 1000)
        
        content = self._get_mock_response(prompt)
        
        return GenerationResult(
            content=content,
            model=model,
            provider=self.name,
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
                "total_tokens": len(prompt.split()) + len(content.split()),
            },
            latency_ms=(time.time() - start_time) * 1000,
            finish_reason="stop",
            metadata={"mock": True},
        )
    
    async def stream(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        content = self._get_mock_response(prompt)
        
        for word in content.split():
            await asyncio.sleep(0.05)
            yield word + " "
    
    async def list_models(self) -> List[ModelConfig]:
        return self.list_registered_models()
    
    async def health_check(self) -> bool:
        return True
