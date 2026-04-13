"""Model Provider Base Classes - Open Source Model Agnostic Architecture"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, AsyncIterator
from enum import Enum


class ModelMode(Enum):
    """Writing modes for model selection"""
    THINKING = "thinking"  # Planning, structure, reasoning
    NON_THINKING = "non_thinking"  # Fast drafting, editing
    LOCAL = "local"  # Local/offline models
    ANY = "any"  # Any model can handle


class ProviderType(Enum):
    """Provider types"""
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    VLLM = "vllm"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class ModelConfig:
    """Configuration for a model"""
    id: str  # Model identifier (e.g., "deepseek-ai/DeepSeek-R1")
    name: str = ""  # Display name
    mode: ModelMode = ModelMode.ANY
    provider: ProviderType = ProviderType.HUGGINGFACE
    context_window: int = 128000  # Context window size in tokens
    max_output_tokens: int = 8192
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    repeat_penalty: float = 1.1
    stop: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=lambda: ["text"])
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.name:
            self.name = self.id.split("/")[-1] if "/" in self.id else self.id


@dataclass
class GenerationResult:
    """Result from model generation"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0.0
    finish_reason: Optional[str] = None
    reasoning: Optional[str] = None  # Chain-of-thought reasoning
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
            "finish_reason": self.finish_reason,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
        }


@dataclass 
class ReasoningStep:
    """A single step in the AI's reasoning process"""
    step_number: int
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "thought": self.thought,
            "action": self.action,
            "observation": self.observation,
        }


@dataclass
class GenerationOptions:
    """Options for generation"""
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop: Optional[List[str]] = None
    seed: Optional[int] = None
    stream: bool = False
    thinking: bool = False  # Enable chain-of-thought reasoning
    include_reasoning: bool = False  # Include reasoning in output
    retry_on_error: bool = True
    max_retries: int = 3


class ModelProvider(ABC):
    """
    Abstract base class for model providers.
    
    All providers (HuggingFace, Ollama, vLLM, etc.) implement this interface,
    enabling seamless model swapping and hybrid setups.
    """
    
    def __init__(
        self,
        name: str,
        provider_type: ProviderType,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_timeout: int = 120,
    ):
        self.name = name
        self.provider_type = provider_type
        self.api_key = api_key
        self.base_url = base_url
        self.default_timeout = default_timeout
        self._models: Dict[str, ModelConfig] = {}
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
    ) -> GenerationResult:
        """
        Generate content from the model.
        
        Args:
            prompt: The user's prompt
            model: Model identifier
            options: Generation options
            system_prompt: System prompt for context
            messages: Chat messages for conversation context
            
        Returns:
            GenerationResult with content and metadata
        """
        pass
    
    @abstractmethod
    async def stream(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Stream generation tokens.
        
        Yields:
            Individual tokens as they're generated
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> List[ModelConfig]:
        """List available models from this provider"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and accessible"""
        pass
    
    def register_model(self, config: ModelConfig):
        """Register a model configuration"""
        self._models[config.id] = config
    
    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """Get model configuration"""
        return self._models.get(model_id)
    
    def list_registered_models(self) -> List[ModelConfig]:
        """List all registered models"""
        return list(self._models.values())
    
    async def generate_with_fallback(
        self,
        prompt: str,
        models: List[str],
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> GenerationResult:
        """
        Try multiple models in order, falling back on errors.
        
        Useful for production systems where one model might be overloaded.
        """
        last_error = None
        
        for model_id in models:
            try:
                return await self.generate(
                    prompt=prompt,
                    model=model_id,
                    options=options,
                    system_prompt=system_prompt,
                )
            except Exception as e:
                last_error = e
                continue
        
        raise RuntimeError(f"All models failed. Last error: {last_error}")
    
    async def batch_generate(
        self,
        prompts: List[str],
        model: str,
        options: Optional[GenerationOptions] = None,
        max_concurrent: int = 5,
    ) -> List[GenerationResult]:
        """
        Generate content for multiple prompts concurrently.
        
        Args:
            prompts: List of prompts to generate for
            model: Model to use
            options: Generation options
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of generation results in same order as prompts
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_one(prompt: str) -> GenerationResult:
            async with semaphore:
                return await self.generate(
                    prompt=prompt,
                    model=model,
                    options=options,
                )
        
        return await asyncio.gather(*[generate_one(p) for p in prompts])


class ReasoningProvider(ModelProvider):
    """
    Extended provider that supports chain-of-thought reasoning.
    
    Used for Thinking Mode to show reasoning traces.
    """
    
    @abstractmethod
    async def generate_with_reasoning(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> tuple[GenerationResult, List[ReasoningStep]]:
        """
        Generate with explicit reasoning steps.
        
        Returns:
            Tuple of (result, reasoning_steps)
        """
        pass
    
    @abstractmethod
    async def think(
        self,
        problem: str,
        model: str,
        max_steps: int = 10,
    ) -> List[ReasoningStep]:
        """
        Pure reasoning mode - only output thinking process.
        
        Used for planning and structure before writing.
        """
        pass


class StreamingProviderMixin:
    """Mixin for providers that support streaming"""
    
    async def stream_with_reasoning(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[tuple[str, bool]]:
        """
        Stream tokens, distinguishing reasoning from content.
        
        Yields:
            Tuple of (token, is_reasoning)
        """
        raise NotImplementedError
