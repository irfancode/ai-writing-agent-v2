"""Free Provider - Zero-cost AI inference with automatic fallback"""

import os
import time
import json
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass
import httpx
import asyncio

from .base import (
    ModelProvider, ModelConfig, GenerationResult, GenerationOptions,
    ProviderType, ModelMode, ReasoningProvider, ReasoningStep
)


@dataclass
class FreeProviderEndpoint:
    """A free API endpoint configuration"""
    name: str
    base_url: str
    api_key_required: bool = False
    api_key: Optional[str] = None
    requires_auth: bool = False


class FreeProvider(ReasoningProvider):
    """
    Zero-cost provider with multiple free tier endpoints.
    
    Providers:
    - Groq (fastest, llama-3.3-70b, mixtral-8x7b)
    - Together AI (free tier, Qwen3, DeepSeek-R1)
    - HuggingFace Inference (free tier, rate limited)
    - OpenRouter (free models)
    """
    
    GROQ_BASE = "https://api.groq.com/openai/v1"
    TOGETHER_BASE = "https://api.together.xyz/v1"
    HF_INFERENCE_BASE = "https://api-inference.huggingface.co"
    HF_CHAT_BASE = "https://api-inference.huggingface.co/models"
    OPENROUTER_BASE = "https://openrouter.ai/api/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_timeout: int = 60,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("TOGETHER_API_KEY")
        self.providers_config = {
            "groq": FreeProviderEndpoint(
                name="Groq",
                base_url=self.GROQ_BASE,
                api_key_required=True,
                api_key=os.getenv("GROQ_API_KEY"),
            ),
            "together": FreeProviderEndpoint(
                name="Together AI",
                base_url=self.TOGETHER_BASE,
                api_key_required=True,
                api_key=os.getenv("TOGETHER_API_KEY"),
            ),
            "hf_free": FreeProviderEndpoint(
                name="HuggingFace Free",
                base_url=self.HF_INFERENCE_BASE,
                api_key_required=False,
            ),
            "openrouter": FreeProviderEndpoint(
                name="OpenRouter",
                base_url=self.OPENROUTER_BASE,
                api_key_required=True,
                api_key=self.api_key,
            ),
        }
        
        self._active_provider = "groq"
        self.client = httpx.AsyncClient(timeout=default_timeout)
        
        super().__init__(
            name="free",
            provider_type=ProviderType.OPENAI,
            api_key=self.api_key,
            default_timeout=default_timeout,
        )
        
        self._register_default_models()
    
    def _register_default_models(self):
        """Register models available on free tiers"""
        hf_token = os.getenv("HF_API_KEY")
        
        models = [
            ModelConfig(
                id="groq/llama-3.3-70b-versatile",
                name="Llama 3.3 70B (Groq)",
                mode=ModelMode.NON_THINKING,
                context_window=128000,
                capabilities=["text", "fast", "creative"],
                metadata={"provider": "groq", "free": True, "speed": "fastest", "api_key_required": True},
            ),
            ModelConfig(
                id="groq/mixtral-8x7b-32768",
                name="Mixtral 8x7B (Groq)",
                mode=ModelMode.THINKING,
                context_window=32768,
                capabilities=["text", "reasoning", "fast"],
                metadata={"provider": "groq", "free": True, "speed": "fast", "api_key_required": True},
            ),
            ModelConfig(
                id="groq/llama-3.1-8b-instant",
                name="Llama 3.1 8B (Groq)",
                mode=ModelMode.NON_THINKING,
                context_window=128000,
                capabilities=["text", "fast", "ultra-fast"],
                metadata={"provider": "groq", "free": True, "speed": "ultra-fast", "api_key_required": True},
            ),
            ModelConfig(
                id="together/qwen/qwen3-32b",
                name="Qwen3 32B (Together)",
                mode=ModelMode.THINKING,
                context_window=128000,
                capabilities=["text", "reasoning", "creative"],
                metadata={"provider": "together", "free": True, "api_key_required": True},
            ),
            ModelConfig(
                id="together/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
                name="DeepSeek-R1 32B (Together)",
                mode=ModelMode.THINKING,
                context_window=128000,
                capabilities=["text", "reasoning"],
                metadata={"provider": "together", "free": True, "api_key_required": True},
            ),
        ]
        
        if hf_token:
            models.insert(0, ModelConfig(
                id="hf/meta-llama/Llama-3.2-1B-Instruct",
                name="Llama 3.2 1B (HF)",
                mode=ModelMode.NON_THINKING,
                context_window=128000,
                capabilities=["text", "fast"],
                metadata={"provider": "hf_free", "free": True, "rate_limited": True},
            ))
        
        for model in models:
            self.register_model(model)
    
    def _get_provider_for_model(self, model_id: str) -> tuple[str, FreeProviderEndpoint]:
        """Get the provider endpoint for a model"""
        parts = model_id.split("/")
        if len(parts) >= 1:
            prefix = parts[0].lower()
            if prefix in self.providers_config:
                return prefix, self.providers_config[prefix]
        
        if self.api_key:
            return "groq", self.providers_config["groq"]
        
        return "hf_free", self.providers_config["hf_free"]
    
    def _get_api_key_for_provider(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        config = self.providers_config.get(provider)
        if config and config.api_key:
            return config.api_key
        if provider == "hf_free":
            return os.getenv("HF_API_KEY")
        return None
    
    async def generate(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
    ) -> GenerationResult:
        start_time = time.time()
        options = options or GenerationOptions()
        
        provider_name, provider_config = self._get_provider_for_model(model)
        api_key = self._get_api_key_for_provider(provider_name)
        
        model_config = self.get_model(model)
        if not model_config:
            model_config = ModelConfig(id=model)
        
        headers = {"Content-Type": "application/json"}
        if api_key:
            auth_scheme = "Bearer" if provider_name in ["groq", "together", "openrouter"] else "Bearer"
            headers["Authorization"] = f"{auth_scheme} {api_key}"
        
        messages_list = []
        if system_prompt:
            messages_list.append({"role": "system", "content": system_prompt})
        
        if messages:
            messages_list.extend(messages)
        else:
            messages_list.append({"role": "user", "content": prompt})
        
        actual_model = model.split("/")[-1] if "/" in model else model
        
        payload = {
            "model": actual_model,
            "messages": messages_list,
            "temperature": options.temperature or model_config.temperature,
            "max_tokens": options.max_tokens or model_config.max_output_tokens,
            "top_p": options.top_p or model_config.top_p,
            "stream": False,
        }
        
        if options.stop:
            payload["stop"] = options.stop
        
        try:
            response = await self.client.post(
                f"{provider_config.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            
            if response.status_code == 401:
                raise ValueError(f"API key required for {provider_name}. Set GROQ_API_KEY or TOGETHER_API_KEY")
            
            if response.status_code == 429:
                next_provider = await self._find_available_provider(model, exclude=[provider_name])
                if next_provider:
                    return await self.generate(prompt, f"{next_provider}/{actual_model}", options, system_prompt, messages)
                raise RuntimeError(f"Rate limited on {provider_name}. Try again later.")
            
            response.raise_for_status()
            data = response.json()
            
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            
            return GenerationResult(
                content=content,
                model=model,
                provider=f"free:{provider_name}",
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                latency_ms=(time.time() - start_time) * 1000,
                finish_reason=data.get("choices", [{}])[0].get("finish_reason"),
                metadata={"provider": provider_name, "raw_response": data},
            )
            
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Free provider error ({provider_name}): {e}")
    
    async def stream(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        options = options or GenerationOptions()
        provider_name, provider_config = self._get_provider_for_model(model)
        api_key = self._get_api_key_for_provider(provider_name)
        
        model_config = self.get_model(model) or ModelConfig(id=model)
        
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        actual_model = model.split("/")[-1] if "/" in model else model
        
        payload = {
            "model": actual_model,
            "messages": messages,
            "temperature": options.temperature or model_config.temperature,
            "max_tokens": options.max_tokens or model_config.max_output_tokens,
            "stream": True,
        }
        
        async with self.client.stream(
            "POST",
            f"{provider_config.base_url}/chat/completions",
            headers=headers,
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    if line.strip() == "data: [DONE]":
                        break
                    try:
                        data = json.loads(line[6:])
                        if content := data.get("choices", [{}])[0].get("delta", {}).get("content"):
                            yield content
                    except json.JSONDecodeError:
                        continue
    
    async def list_models(self) -> List[ModelConfig]:
        """List all registered free models"""
        return self.list_registered_models()
    
    async def health_check(self) -> bool:
        """Check if any free provider is accessible"""
        for name, config in self.providers_config.items():
            if name == "hf_free":
                continue
            try:
                headers = {}
                if config.api_key:
                    headers["Authorization"] = f"Bearer {config.api_key}"
                response = await self.client.get(
                    f"{config.base_url}/models",
                    headers=headers,
                    timeout=10,
                )
                if response.status_code < 500:
                    return True
            except:
                continue
        return False
    
    async def _find_available_provider(self, model: str, exclude: List[str] = None) -> Optional[str]:
        """Find an available provider for a model, excluding specified ones"""
        exclude = exclude or []
        
        for provider_name, config in self.providers_config.items():
            if provider_name in exclude:
                continue
            api_key = self._get_api_key_for_provider(provider_name)
            if not api_key and provider_name != "hf_free":
                continue
            
            try:
                headers = {}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                response = await self.client.head(
                    f"{config.base_url}/models",
                    headers=headers,
                    timeout=10,
                )
                if response.status_code < 500:
                    return provider_name
            except:
                continue
        
        return None
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> tuple[GenerationResult, List[ReasoningStep]]:
        """Generate with reasoning (for thinking models)"""
        result = await self.generate(prompt, model, options, system_prompt)
        
        reasoning_steps = []
        content = result.content
        
        if "thinking" in content.lower() or "<think>" in content.lower():
            import re
            think_matches = re.findall(r'<think>(.*?)</think>', content, re.DOTALL)
            if think_matches:
                for i, thought in enumerate(think_matches):
                    reasoning_steps.append(ReasoningStep(
                        step_number=i + 1,
                        thought=thought.strip(),
                    ))
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                result = GenerationResult(
                    content=content,
                    model=result.model,
                    provider=result.provider,
                    usage=result.usage,
                    latency_ms=result.latency_ms,
                    finish_reason=result.finish_reason,
                    reasoning="\n".join(s.thought for s in reasoning_steps),
                    metadata=result.metadata,
                )
        
        return result, reasoning_steps
    
    async def think(
        self,
        problem: str,
        model: str,
        max_steps: int = 10,
    ) -> List[ReasoningStep]:
        """Pure reasoning mode"""
        thinking_model = "together/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
        result = await self.generate(
            prompt=f"Think through this step by step:\n\n{problem}",
            model=thinking_model,
            options=GenerationOptions(temperature=0.7, max_tokens=4096),
            system_prompt="You are a careful thinker. Show your reasoning clearly.",
        )
        
        steps = []
        for i, line in enumerate(result.content.split("\n")):
            if line.strip():
                steps.append(ReasoningStep(
                    step_number=i + 1,
                    thought=line.strip(),
                ))
                if i >= max_steps:
                    break
        
        return steps
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
