"""Model Registry - Central hub for all model providers"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import asyncio

from .base import (
    ModelProvider, ModelConfig, GenerationResult, GenerationOptions,
    ProviderType, ModelMode
)


@dataclass
class ProviderConfig:
    """Configuration for a provider instance"""
    provider_type: ProviderType
    enabled: bool = True
    priority: int = 0  # Higher = preferred
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[str] = field(default_factory=list)  # Allowed models
    exclude_models: List[str] = field(default_factory=list)  # Excluded models


class ModelRegistry:
    """
    Central registry for all model providers.
    
    Manages:
    - Provider lifecycle
    - Model routing
    - Fallback chains
    - Load balancing
    """
    
    def __init__(self):
        self._providers: Dict[str, ModelProvider] = {}
        self._provider_configs: Dict[str, ProviderConfig] = {}
        self._model_to_provider: Dict[str, str] = {}
        self._mode_routing: Dict[ModelMode, List[str]] = {
            ModelMode.THINKING: [],
            ModelMode.NON_THINKING: [],
            ModelMode.LOCAL: [],
            ModelMode.ANY: [],
        }
        self._locks: Dict[str, asyncio.Lock] = {}
    
    def register_provider(
        self,
        name: str,
        provider: ModelProvider,
        config: Optional[ProviderConfig] = None,
    ):
        """Register a provider"""
        self._providers[name] = provider
        self._provider_configs[name] = config or ProviderConfig(
            provider_type=provider.provider_type
        )
        
        # Build model index
        for model in provider.list_registered_models():
            self._model_to_provider[model.id] = name
            
            # Add to mode routing
            if model.mode in self._mode_routing:
                self._mode_routing[model.mode].append(model.id)
            self._mode_routing[ModelMode.ANY].append(model.id)
    
    def get_provider(self, name: str) -> Optional[ModelProvider]:
        """Get a provider by name"""
        return self._providers.get(name)
    
    def get_provider_for_model(self, model_id: str) -> Optional[ModelProvider]:
        """Get the provider for a specific model"""
        provider_name = self._model_to_provider.get(model_id)
        if provider_name:
            return self._providers.get(provider_name)
        
        # Search all providers
        for provider in self._providers.values():
            if provider.get_model(model_id):
                return provider
        
        return None
    
    def list_models(
        self,
        mode: Optional[ModelMode] = None,
        capability: Optional[str] = None,
    ) -> List[ModelConfig]:
        """List all available models, optionally filtered"""
        models = []
        
        for provider in self._providers.values():
            for model in provider.list_registered_models():
                if mode and model.mode != mode and model.mode != ModelMode.ANY:
                    continue
                if capability and capability not in model.capabilities:
                    continue
                models.append(model)
        
        return models
    
    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """Get configuration for a model"""
        provider = self.get_provider_for_model(model_id)
        if provider:
            return provider.get_model(model_id)
        return None
    
    def get_best_model(
        self,
        mode: ModelMode = ModelMode.ANY,
        speed_preference: str = "balanced",
        api_key_available: bool = False,
    ) -> Optional[str]:
        """
        Get the best available model for a mode.
        
        Args:
            mode: The writing mode
            speed_preference: "fast", "balanced", or "quality"
            api_key_available: Whether an API key is available (prefer paid if so)
        """
        candidates = self._mode_routing.get(mode, []) + self._mode_routing.get(ModelMode.ANY, [])
        
        if not candidates:
            return None
        
        scored = []
        for model_id in set(candidates):
            config = self.get_model_config(model_id)
            if not config:
                continue
            
            score = 0
            
            api_key_required = config.metadata.get("api_key_required", False)
            if not api_key_available and api_key_required:
                continue
            
            if api_key_required and api_key_available:
                score += 30
            
            if config.mode == mode:
                score += 100
            
            if speed_preference == "fast" and "fast" in config.capabilities:
                score += 50
            elif speed_preference == "quality" and "reasoning" in config.capabilities:
                score += 50
            
            if config.metadata.get("free"):
                score += 20
            
            score += config.context_window / 1000000
            
            scored.append((score, model_id))
        
        scored.sort(reverse=True)
        
        if scored:
            return scored[0][1]
        
        return None
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        mode: ModelMode = ModelMode.ANY,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
    ) -> GenerationResult:
        """
        Generate using specified model or auto-select best.
        """
        # Auto-select model if not specified
        if not model:
            model = self.get_best_model(mode=mode)
            if not model:
                raise ValueError(f"No model available for mode {mode}")
        
        provider = self.get_provider_for_model(model)
        if not provider:
            raise ValueError(f"Provider not found for model {model}")
        
        return await provider.generate(
            prompt=prompt,
            model=model,
            options=options,
            system_prompt=system_prompt,
            messages=messages,
        )
    
    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        mode: ModelMode = ModelMode.ANY,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ):
        """Stream generation"""
        if not model:
            model = self.get_best_model(mode=mode)
            if not model:
                raise ValueError(f"No model available for mode {mode}")
        
        provider = self.get_provider_for_model(model)
        if not provider:
            raise ValueError(f"Provider not found for model {model}")
        
        async for token in provider.stream(
            prompt=prompt,
            model=model,
            options=options,
            system_prompt=system_prompt,
        ):
            yield token
    
    async def generate_with_fallback(
        self,
        prompt: str,
        models: List[str],
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> GenerationResult:
        """
        Try models in order, falling back on errors.
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
        Generate for multiple prompts concurrently.
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
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all providers"""
        results = {}
        
        for name, provider in self._providers.items():
            try:
                results[name] = await provider.health_check()
            except Exception:
                results[name] = False
        
        return results
    
    async def close_all(self):
        """Close all provider connections"""
        for provider in self._providers.values():
            if hasattr(provider, 'close'):
                await provider.close()


# Global registry instance
_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    """Get the global registry instance"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


def init_registry(config: Optional[Dict] = None) -> ModelRegistry:
    """Initialize registry with providers - auto-detects best available option"""
    registry = get_registry()
    
    if registry._providers:
        return registry
    
    from .ollama import OllamaProvider
    from .mock import MockProvider
    from .free import FreeProvider
    
    ollama_provider = OllamaProvider()
    
    import httpx
    try:
        response = httpx.get("http://localhost:11434/", timeout=5)
        is_healthy = response.status_code == 200
    except Exception:
        is_healthy = False
    
    if is_healthy:
        registry.register_provider("ollama", ollama_provider, ProviderConfig(
            provider_type=ProviderType.OLLAMA,
            enabled=True,
            priority=100,
        ))
        print("✓ Connected to Ollama (Local AI)")
    else:
        free_provider = FreeProvider()
        
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            async def check_free():
                return await free_provider.health_check()
            
            if asyncio.get_event_loop().is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, check_free())
                    free_healthy = future.result()
            else:
                free_healthy = asyncio.run(check_free())
        except Exception:
            free_healthy = False
        
        if free_healthy:
            registry.register_provider("free", free_provider, ProviderConfig(
                provider_type=ProviderType.OPENAI,
                enabled=True,
                priority=90,
            ))
            print("✓ Connected to Free Providers (Groq/Together)")
        else:
            mock_provider = MockProvider()
            registry.register_provider("mock", mock_provider, ProviderConfig(
                provider_type=ProviderType.OPENAI,
                enabled=True,
                priority=50,
            ))
            print("⚠ Demo mode - No API keys detected. Set GROQ_API_KEY for real AI.")
    
    return registry
