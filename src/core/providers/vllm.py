"""vLLM Provider - Production-Grade High-Throughput Serving"""

import os
import time
import json
from typing import List, Optional, Dict, Any, AsyncIterator
import httpx

from .base import (
    ModelProvider, ModelConfig, GenerationResult, GenerationOptions,
    ProviderType, ModelMode
)


class VLLMProvider(ModelProvider):
    """
    Provider for vLLM inference servers.
    
    Optimized for production with:
    - Tensor parallelism
    - Paged attention
    - Continuous batching
    - Speculative decoding
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        default_timeout: int = 300,
    ):
        super().__init__(
            name="vllm",
            provider_type=ProviderType.VLLM,
            api_key=api_key,
            base_url=base_url,
            default_timeout=default_timeout,
        )
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=default_timeout,
            headers={
                "Authorization": f"Bearer {api_key}" if api_key else "",
            }
        )
    
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
        
        # Build OpenAI-compatible chat format
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        if messages:
            formatted_messages.extend(messages)
        else:
            formatted_messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": options.temperature or model_config.temperature,
            "max_tokens": options.max_tokens or model_config.max_output_tokens,
            "top_p": options.top_p or model_config.top_p,
            "top_k": options.top_k or model_config.top_k,
            "frequency_penalty": model_config.frequency_penalty,
            "presence_penalty": model_config.presence_penalty,
            "stop": options.stop or model_config.stop,
            "stream": False,
        }
        
        try:
            response = await self.client.post("/v1/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
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
                metadata={"raw_response": data},
            )
            
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"vLLM API error: {e}")
    
    async def stream(
        self,
        prompt: str,
        model: str,
        options: Optional[GenerationOptions] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        options = options or GenerationOptions()
        model_config = self.get_model(model) or ModelConfig(id=model)
        
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": options.temperature or model_config.temperature,
            "max_tokens": options.max_tokens or model_config.max_output_tokens,
            "stream": True,
        }
        
        async with self.client.stream("POST", "/v1/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    if line.strip() == "data: [DONE]":
                        break
                    try:
                        data = json.loads(line[6:])
                        content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
    
    async def list_models(self) -> List[ModelConfig]:
        """List models served by vLLM"""
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
                    metadata={"provider": "vllm"},
                )
                for m in data.get("data", [])
            ]
        except:
            return []
    
    async def health_check(self) -> bool:
        """Check if vLLM server is healthy"""
        try:
            response = await self.client.get("/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vLLM server statistics"""
        try:
            response = await self.client.get("/stats")
            response.raise_for_status()
            return response.json()
        except:
            return {}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
