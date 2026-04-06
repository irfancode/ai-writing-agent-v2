"""Tests for AI Writing Agent"""

import pytest
import asyncio


class TestModelRegistry:
    """Test model registry"""
    
    def test_registry_initialization(self):
        from src.core.providers.registry import ModelRegistry
        registry = ModelRegistry()
        assert registry is not None
    
    def test_list_models(self):
        from src.core.providers.registry import ModelRegistry
        registry = ModelRegistry()
        models = registry.list_models()
        assert isinstance(models, list)


class TestHighContextMemory:
    """Test high-context memory"""
    
    def test_add_entry(self):
        from src.core.memory.context import HighContextMemory
        memory = HighContextMemory()
        memory.add("test", "value", "general")
        assert memory.get("test") == "value"
    
    def test_character_profiles(self):
        from src.core.memory.context import HighContextMemory, CharacterProfile
        memory = HighContextMemory()
        char = CharacterProfile(
            name="Alice",
            traits=["brave", "curious"],
            voice_patterns=["speaks clearly"],
        )
        memory.add_character(char)
        assert memory.get_character("Alice") is not None
    
    def test_plot_points(self):
        from src.core.memory.context import HighContextMemory, PlotPoint
        memory = HighContextMemory()
        point = PlotPoint(
            chapter=1,
            title="The Beginning",
            description="Alice discovers the portal",
        )
        memory.add_plot_point(point)
        timeline = memory.get_plot_timeline()
        assert len(timeline) == 1
        assert timeline[0].chapter == 1


class TestDualModeOrchestrator:
    """Test dual-mode orchestrator"""
    
    def test_orchestrator_initialization(self):
        from src.core.modes.orchestrator import DualModeOrchestrator
        from src.core.providers.registry import ModelRegistry
        registry = ModelRegistry()
        orchestrator = DualModeOrchestrator(registry)
        assert orchestrator is not None
    
    def test_session_creation(self):
        from src.core.modes.orchestrator import DualModeOrchestrator
        from src.core.providers.registry import ModelRegistry
        registry = ModelRegistry()
        orchestrator = DualModeOrchestrator(registry)
        session = orchestrator.create_session("test", "Test Topic")
        assert session.session_id == "test"
        assert session.topic == "Test Topic"


class TestRAGLoader:
    """Test RAG system"""
    
    def test_loader_initialization(self):
        from src.core.rag.loader import RAGLoader
        loader = RAGLoader()
        assert loader.chunk_size == 1000
    
    def test_chunking(self):
        from src.core.rag.loader import RAGLoader
        loader = RAGLoader(chunk_size=50, chunk_overlap=10)
        text = "This is a test text. " * 10
        chunks = loader._chunk_text(text)
        assert len(chunks) > 0


class TestWritingStyles:
    """Test writing style enums"""
    
    def test_thinking_types(self):
        from src.core.modes.thinking import ThinkingType
        assert ThinkingType.OUTLINE.value == "outline"
        assert ThinkingType.CHARACTER.value == "character"
    
    def test_writing_styles(self):
        from src.core.modes.non_thinking import WritingStyle
        assert WritingStyle.NARRATIVE.value == "narrative"
        assert WritingStyle.TECHNICAL.value == "technical"


class TestMultiAgentSystem:
    """Test multi-agent system"""
    
    def test_agent_config(self):
        from src.core.agents.multi_agent import AgentConfig, AgentType
        config = AgentConfig(
            agent_type=AgentType.DRAFT,
            model="test-model",
        )
        assert config.agent_type == AgentType.DRAFT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
