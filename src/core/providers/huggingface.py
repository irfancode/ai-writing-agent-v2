"""HuggingFace Provider - Access to Qwen3, DeepSeek-R1, and more"""

import asyncio
import os
import time
import json
from typing import List, Optional, Dict, AsyncIterator
import httpx

from .base import (
    ModelConfig, GenerationResult, GenerationOptions,
    ProviderType, ModelMode, ReasoningProvider, ReasoningStep
)


class HuggingFaceProvider(ReasoningProvider):
    """
    Provider for Hugging Face Inference API and Inference Endpoints.
    
    Supports:
    - Qwen3-235B-A22B (Creative Writing)
    - DeepSeek-R1 (Reasoning)
    - MiniMax-M2 (High-Speed)
    - And thousands of other open-source models
    """
    
    BASE_URL = "https://api-inference.huggingface.co"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_timeout: int = 120,
    ):
        super().__init__(
            name="huggingface",
            provider_type=ProviderType.HUGGINGFACE,
            api_key=api_key or os.getenv("HF_API_KEY"),
            base_url=base_url or self.BASE_URL,
            default_timeout=default_timeout,
        )
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=default_timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "Content-Type": "application/json",
            }
        )
        
        self._register_default_models()
    
    def _register_default_models(self):
        """Register best 2026 open-source models"""
        models = [
            ModelConfig(
                id="Qwen/Qwen3-235B-A22B",
                name="Qwen3-235B",
                mode=ModelMode.THINKING,
                context_window=128000,
                capabilities=["text", "reasoning", "creative"],
                metadata={"provider": "huggingface", "size": "235B"},
            ),
            ModelConfig(
                id="deepseek-ai/DeepSeek-R1",
                name="DeepSeek-R1",
                mode=ModelMode.THINKING,
                context_window=256000,
                capabilities=["text", "reasoning", "coding"],
                metadata={"provider": "huggingface", "size": "671B"},
            ),
            ModelConfig(
                id="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
                name="DeepSeek-R1 (32B)",
                mode=ModelMode.THINKING,
                context_window=128000,
                capabilities=["text", "reasoning"],
                metadata={"provider": "huggingface", "size": "32B"},
            ),
            ModelConfig(
                id="deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
                name="DeepSeek-R1 (70B)",
                mode=ModelMode.THINKING,
                context_window=128000,
                capabilities=["text", "reasoning"],
                metadata={"provider": "huggingface", "size": "70B"},
            ),
            ModelConfig(
                id="MiniMaxAI/MiniMax-M2",
                name="MiniMax-M2",
                mode=ModelMode.NON_THINKING,
                context_window=128000,
                max_output_tokens=16384,
                capabilities=["text", "fast"],
                metadata={"provider": "huggingface", "size": "456B"},
            ),
            ModelConfig(
                id="google/gemma-3-12b-it",
                name="Gemma 3 12B",
                mode=ModelMode.LOCAL,
                context_window=128000,
                capabilities=["text", "local"],
                metadata={"provider": "huggingface", "size": "12B"},
            ),
            ModelConfig(
                id="microsoft/phi-4",
                name="Phi-4",
                mode=ModelMode.LOCAL,
                context_window=128000,
                capabilities=["text", "local", "edge"],
                metadata={"provider": "huggingface", "size": "14B"},
            ),
            ModelConfig(
                id="mistralai/Mistral-Small-3.1-24B-Instruct-2503",
                name="Mistral Small 3.1",
                mode=ModelMode.NON_THINKING,
                context_window=128000,
                capabilities=["text", "fast"],
                metadata={"provider": "huggingface", "size": "24B"},
            ),
            ModelConfig(
                id="anthropics/claude-3.5-sonnet",
                name="Claude 3.5 Sonnet",
                mode=ModelMode.ANY,
                context_window=200000,
                capabilities=["text", "reasoning", "creative"],
                metadata={"provider": "openrouter", "size": "unknown"},
            ),
        ]
        
        for model in models:
            self.register_model(model)
    
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
        model_config = self.get_model(model) or ModelConfig(id=model)
        
        # Build messages format for chat models
        inputs = []
        if messages:
            for msg in messages:
                inputs.append({"role": msg.get("role", "user"), "content": msg["content"]})
        else:
            inputs = [{"role": "user", "content": prompt}]
        
        if system_prompt:
            inputs.insert(0, {"role": "system", "content": system_prompt})
        
        payload = {
            "inputs": inputs if model_config.capabilities else prompt,
            "model": model,
            "parameters": {
                "temperature": options.temperature or model_config.temperature,
                "max_new_tokens": options.max_tokens or model_config.max_output_tokens,
                "top_p": options.top_p or model_config.top_p,
                "top_k": options.top_k or model_config.top_k,
                "repetition_penalty": model_config.repeat_penalty,
                "return_full_text": False,
                "do_sample": options.temperature is not None and options.temperature > 0,
            },
            "options": {
                "use_cache": True,
                "wait_for_model": True,
            }
        }
        
        if options.stop:
            payload["parameters"]["stop"] = options.stop
        
        if options.include_reasoning:
            payload["parameters"]["thinking"] = {"type": "enabled", "budget": 4096}
        
        try:
            response = await self.client.post(
                "/v1/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Handle reasoning content if present
            reasoning = None
            if "thinking" in data.get("choices", [{}])[0]:
                reasoning = data["choices"][0].get("thinking", {}).get("content")
            
            usage = data.get("usage", {})
            
            return GenerationResult(
                content=content,
                model=model,
                provider=self.name,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                latency_ms=(time.time() - start_time) * 1000,
                finish_reason=data.get("choices", [{}])[0].get("finish_reason"),
                reasoning=reasoning,
                metadata={"raw_response": data},
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                # Model loading, retry with backoff
                for attempt in range(options.max_retries):
                    await asyncio.sleep(2 ** attempt)
                    try:
                        response = await self.client.post("/v1/chat/completions", json=payload)
                        response.raise_for_status()
                        data = response.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        return GenerationResult(
                            content=content,
                            model=model,
                            provider=self.name,
                            latency_ms=(time.time() - start_time) * 1000,
                            warnings=["Model loaded after retry"],
                        )
                    except Exception:
                        continue
            
            raise RuntimeError(f"HuggingFace API error: {e}")
    
    async def stream(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        options = options or GenerationOptions()
        model_config = self.get_model(model) or ModelConfig(id=model)
        
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        payload = {
            "inputs": messages,
            "model": model,
            "parameters": {
                "temperature": options.temperature or model_config.temperature,
                "max_new_tokens": options.max_tokens or model_config.max_output_tokens,
                "top_p": options.top_p or model_config.top_p,
                "do_sample": True,
                "stream": True,
            },
        }
        
        async with self.client.stream("POST", "/v1/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if data.get("choices"):
                        content = data["choices"][0].get("delta", {}).get("content", "")
                        if content:
                            yield content
    
    async def list_models(self) -> List[ModelConfig]:
        """List models from HuggingFace"""
        try:
            response = await self.client.get("/v1/models")
            response.raise_for_status()
            data = response.json()
            return [
                ModelConfig(
                    id=m["id"],
                    name=m.get("name", m["id"]),
                    context_window=128000,
                    capabilities=["text"],
                )
                for m in data.get("models", [])
            ]
        except Exception:
            return self.list_registered_models()
    
    async def health_check(self) -> bool:
        """Check if HuggingFace API is accessible"""
        try:
            response = await self.client.get("/v1/models", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> tuple[GenerationResult, List[ReasoningStep]]:
        """Generate with reasoning steps"""
        options = options or GenerationOptions()
        options.include_reasoning = True
        
        result = await self.generate(
            prompt=prompt,
            model=model,
            options=options,
            system_prompt=system_prompt,
        )
        
        # Parse reasoning steps from result
        reasoning_steps = []
        if result.reasoning:
            for i, step in enumerate(result.reasoning.split("\n")):
                if step.strip():
                    reasoning_steps.append(ReasoningStep(
                        step_number=i + 1,
                        thought=step.strip(),
                    ))
        
        return result, reasoning_steps
    
    async def think(
        self,
        problem: str,
        model: str,
        max_steps: int = 10,
    ) -> List[ReasoningStep]:
        """Pure reasoning mode"""
        prompt = f"""Think through this problem step by step, showing your reasoning process.

Problem: {problem}

Think out loud, exploring different angles and approaches. Structure your thinking clearly.
"""
        
        result = await self.generate(
            prompt=prompt,
            model=model,
            options=GenerationOptions(
                temperature=0.7,
                max_tokens=4096,
                include_reasoning=True,
            ),
            system_prompt="You are a careful thinker. Show your reasoning process clearly.",
        )
        
        steps = []
        current_step = 0
        
        # Parse reasoning into structured steps
        lines = (result.reasoning or result.content).split("\n")
        for line in lines:
            if line.strip():
                current_step += 1
                steps.append(ReasoningStep(
                    step_number=current_step,
                    thought=line.strip(),
                ))
                if current_step >= max_steps:
                    break
        
        return steps
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
