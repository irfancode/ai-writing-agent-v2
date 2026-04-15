"""Health Dashboard - Real-time provider status monitoring"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    """Health status for a provider"""
    name: str
    status: ProviderStatus
    latency_ms: float = 0
    last_check: float = 0
    error_count: int = 0
    consecutive_failures: int = 0
    is_default: bool = False


class HealthDashboard:
    """Monitor and display provider health status"""
    
    def __init__(self):
        self.providers: Dict[str, ProviderHealth] = {}
        self.check_interval = 30
        self._monitor_task: Optional[asyncio.Task] = None
    
    async def check_provider(self, provider, name: str) -> ProviderHealth:
        """Check health of a single provider"""
        start = time.time()
        
        try:
            is_healthy = await provider.health_check()
            latency = (time.time() - start) * 1000
            
            existing = self.providers.get(name, ProviderHealth(name=name, status=ProviderStatus.UNKNOWN))
            
            if is_healthy:
                status = ProviderStatus.HEALTHY if latency < 2000 else ProviderStatus.DEGRADED
                return ProviderHealth(
                    name=name,
                    status=status,
                    latency_ms=latency,
                    last_check=time.time(),
                    error_count=0,
                    consecutive_failures=0,
                    is_default=existing.is_default,
                )
            else:
                return ProviderHealth(
                    name=name,
                    status=ProviderStatus.OFFLINE,
                    latency_ms=latency,
                    last_check=time.time(),
                    error_count=existing.error_count + 1,
                    consecutive_failures=existing.consecutive_failures + 1,
                    is_default=existing.is_default,
                )
                
        except Exception as e:
            existing = self.providers.get(name, ProviderHealth(name=name, status=ProviderStatus.UNKNOWN))
            return ProviderHealth(
                name=name,
                status=ProviderStatus.OFFLINE,
                latency_ms=0,
                last_check=time.time(),
                error_count=existing.error_count + 1,
                consecutive_failures=existing.consecutive_failures + 1,
                is_default=existing.is_default,
            )
    
    async def check_all(self, registry) -> Dict[str, ProviderHealth]:
        """Check health of all registered providers"""
        results = {}
        
        for name, provider in registry._providers.items():
            results[name] = await self.check_provider(provider, name)
        
        self.providers = results
        return results
    
    def get_best_provider(self) -> Optional[str]:
        """Get the best available provider"""
        available = [
            (name, h) for name, h in self.providers.items()
            if h.status == ProviderStatus.HEALTHY
        ]
        
        if not available:
            available = [
                (name, h) for name, h in self.providers.items()
                if h.status == ProviderStatus.DEGRADED
            ]
        
        if not available:
            return None
        
        available.sort(key=lambda x: x[1].latency_ms)
        return available[0][0]
    
    def format_status(self) -> str:
        """Format health status as string"""
        lines = ["🟢 Provider Status:"]
        
        if not self.providers:
            lines.append("  No providers checked yet")
            return "\n".join(lines)
        
        for name, health in self.providers.items():
            status_icon = {
                ProviderStatus.HEALTHY: "🟢",
                ProviderStatus.DEGRADED: "🟡",
                ProviderStatus.OFFLINE: "🔴",
                ProviderStatus.UNKNOWN: "⚪",
            }[health.status]
            
            latency_str = f"{health.latency_ms:.0f}ms" if health.latency_ms else "N/A"
            
            default_marker = " (default)" if health.is_default else ""
            
            lines.append(f"  {status_icon} {name}{default_marker}: {health.status.value} ({latency_str})")
        
        return "\n".join(lines)
    
    def get_fallback_chain(self, preferred: str) -> List[str]:
        """Get fallback chain for a provider"""
        chain = [preferred]
        
        others = [(n, h) for n, h in self.providers.items() if n != preferred]
        others.sort(key=lambda x: x[1].latency_ms)
        
        for name, _ in others:
            if self.providers[name].status != ProviderStatus.OFFLINE:
                chain.append(name)
        
        return chain


health_dashboard = HealthDashboard()
