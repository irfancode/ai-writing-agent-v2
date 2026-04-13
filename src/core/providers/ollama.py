"""Ollama Provider - Local/Open-Source Model Serving"""

import os
import time
import json
from typing import List, Optional, Dict, Any, AsyncIterator
import httpx

from .base import (
    ModelProvider, ModelConfig, GenerationResult, GenerationOptions,
    ProviderType, ModelMode
)


class OllamaProvider(ModelProvider):
    """
    Provider for Ollama local model serving.
    
    Supports running models locally:
    - Gemma 3 12B
    - Phi-4
    - Llama 3.3
    - Mistral
    - Qwen2.5
    - And more
    """
    
    DEFAULT_BASE_URL = "http://localhost:11434"
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        default_timeout: int = 300,
    ):
        super().__init__(
            name="ollama",
            provider_type=ProviderType.OLLAMA,
            base_url=base_url or os.getenv("OLLAMA_BASE_URL", self.DEFAULT_BASE_URL),
            default_timeout=default_timeout,
        )
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=default_timeout,
        )
        
        # Load available models from Ollama
        self._ollama_available_models = self._discover_ollama_models()
        
        # Build model list from available Ollama models + defaults
        models = []
        
        # Add actually available models first
        for ollama_name in self._ollama_available_models:
            base = ollama_name.split(':')[0]
            if 'llama' in base.lower():
                mode = ModelMode.NON_THINKING
            elif 'deepseek' in base.lower() or 'r1' in base.lower():
                mode = ModelMode.THINKING
            else:
                mode = ModelMode.LOCAL
            
            models.append(ModelConfig(
                id=ollama_name,
                name=ollama_name.replace(':', ' ').title(),
                mode=mode,
                context_window=128000,
                max_output_tokens=4096,
                capabilities=["text"],
                metadata={"provider": "ollama", "from_ollama": True},
            ))
        
        # Only add defaults if no models available
        if not models:
            models = self._get_default_models()
        
        for model in models:
            self.register_model(model)
    
    def _discover_ollama_models(self) -> List[str]:
        """Discover available models from local Ollama instance"""
        try:
            import httpx
            response = httpx.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []
    
    def _get_default_models(self) -> List[ModelConfig]:
        """Get default model configs (fallback when Ollama has no models)"""
        models = [
            ModelConfig(
                id="gemma3:12b",
                name="Gemma 3 12B",
                mode=ModelMode.LOCAL,
                context_window=128000,
                max_output_tokens=8192,
                capabilities=["text", "local", "fast"],
                metadata={"provider": "ollama", "size": "12B"},
            ),
            ModelConfig(
                id="phi4:latest",
                name="Phi-4",
                mode=ModelMode.LOCAL,
                context_window=128000,
                max_output_tokens=8192,
                capabilities=["text", "local", "edge"],
                metadata={"provider": "ollama", "size": "14B"},
            ),
            ModelConfig(
                id="llama3.3:latest",
                name="Llama 3.3",
                mode=ModelMode.NON_THINKING,
                context_window=128000,
                max_output_tokens=8192,
                capabilities=["text", "fast"],
                metadata={"provider": "ollama", "size": "70B"},
            ),
            ModelConfig(
                id="mistral:latest",
                name="Mistral",
                mode=ModelMode.NON_THINKING,
                context_window=128000,
                max_output_tokens=8192,
                capabilities=["text", "fast"],
                metadata={"provider": "ollama", "size": "7B"},
            ),
            ModelConfig(
                id="qwen2.5:latest",
                name="Qwen 2.5",
                mode=ModelMode.NON_THINKING,
                context_window=128000,
                max_output_tokens=8192,
                capabilities=["text", "fast"],
                metadata={"provider": "ollama", "size": "7B"},
            ),
            ModelConfig(
                id="codellama:latest",
                name="Code Llama",
                mode=ModelMode.ANY,
                context_window=128000,
                max_output_tokens=8192,
                capabilities=["text", "code"],
                metadata={"provider": "ollama", "size": "7B"},
            ),
            ModelConfig(
                id="deepseek-r1:14b",
                name="DeepSeek-R1 (14B)",
                mode=ModelMode.THINKING,
                context_window=128000,
                max_output_tokens=8192,
                capabilities=["text", "reasoning"],
                metadata={"provider": "ollama", "size": "14B"},
            ),
            ModelConfig(
                id="nomic-embed-text:latest",
                name="Nomic Embed Text",
                mode=ModelMode.ANY,
                context_window=8192,
                max_output_tokens=4096,
                capabilities=["embeddings"],
                metadata={"provider": "ollama", "type": "embedding"},
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
        
        # Resolve model to actual Ollama model name (handle :latest or no tag)
        model_config = self.get_model(model)
        if model_config:
            ollama_model = model_config.id
        else:
            # Try to find a matching model by base name
            base_name = model.split(':')[0] if ':' in model else model
            for registered_model in self._models:
                if registered_model.id.startswith(base_name):
                    ollama_model = registered_model.id
                    break
            else:
                # Check if it's available in Ollama directly
                for ollama_name in self._ollama_available_models:
                    if ollama_name.startswith(base_name):
                        ollama_model = ollama_name
                        break
                else:
                    ollama_model = model  # Use as-is
        
        # Build chat format for messages
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt,
            })
        
        if messages:
            formatted_messages.extend(messages)
        else:
            formatted_messages.append({
                "role": "user",
                "content": prompt,
            })
        
        payload = {
            "model": ollama_model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": options.temperature or (model_config.temperature if model_config else 0.7),
                "num_predict": options.max_tokens or (model_config.max_output_tokens if model_config else 4096),
                "top_p": options.top_p or (model_config.top_p if model_config else 0.9),
                "top_k": options.top_k or (model_config.top_k if model_config else 40),
                "repeat_penalty": model_config.repeat_penalty if model_config else 1.1,
                "stop": options.stop or (model_config.stop if model_config else []),
            },
        }
        
        try:
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            
            content = data.get("message", {}).get("content", "")
            
            # Estimate tokens from content length
            estimated_tokens = len(content.split()) * 1.3
            
            return GenerationResult(
                content=content,
                model=ollama_model,
                provider=self.name,
                usage={
                    "prompt_tokens": len(prompt.split()) * 1.3,
                    "completion_tokens": estimated_tokens,
                    "total_tokens": (len(prompt.split()) + estimated_tokens) * 1.3,
                },
                latency_ms=(time.time() - start_time) * 1000,
                finish_reason=data.get("done_reason", "stop"),
                metadata={"raw_response": data},
            )
            
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Ollama API error: {e}")
    
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
            "stream": True,
            "options": {
                "temperature": options.temperature or model_config.temperature,
                "num_predict": options.max_tokens or model_config.max_output_tokens,
                "top_p": options.top_p or model_config.top_p,
            },
        }
        
        async with self.client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if data.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
    
    async def list_models(self) -> List[ModelConfig]:
        """List models available in Ollama"""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = []
            for m in data.get("models", []):
                model_id = m.get("name", "")
                models.append(ModelConfig(
                    id=model_id,
                    name=model_id,
                    mode=ModelMode.LOCAL,
                    context_window=128000,  # Ollama typically supports 128K
                    capabilities=["text"],
                    metadata={"provider": "ollama"},
                ))
            
            return models
        except Exception:
            return self.list_registered_models()
    
    async def health_check(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = await self.client.get("/", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    async def pull_model(self, model: str) -> AsyncIterator[Dict[str, Any]]:
        """Pull a model from Ollama library"""
        async with self.client.stream("POST", "/api/pull", json={"name": model}) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    yield json.loads(line)
    
    async def create_embedding(
        self,
        text: str,
        model: str = "nomic-embed-text:latest",
    ) -> List[float]:
        """Create embeddings for text"""
        payload = {
            "model": model,
            "prompt": text,
        }
        
        response = await self.client.post("/api/embeddings", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return data.get("embedding", [])
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
