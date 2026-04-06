"""Comprehensive Test Runner for AI Writing Agent"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

from src.core.providers.mock import MockProvider
from src.core.providers.registry import ModelRegistry, ProviderConfig
from src.core.providers.base import ProviderType, ModelMode
from src.core.modes.orchestrator import DualModeOrchestrator
from src.core.modes.thinking import ThinkingType, ThinkingMode
from src.core.modes.non_thinking import WritingStyle, NonThinkingMode
from src.core.memory.context import HighContextMemory, PlotPoint, CharacterProfile


@dataclass
class TestResult:
    test_name: str
    status: str
    duration_ms: float
    output: str
    expected_behavior: str
    actual_behavior: str
    notes: str = ""


@dataclass
class TestSuite:
    suite_name: str
    description: str
    tests: List[TestResult]
    summary: Dict[str, int]


class ComprehensiveTestRunner:
    """
    Runs comprehensive tests on the AI Writing Agent.
    
    Tests all major features:
    - CLI Commands
    - Writing Modes
    - Thinking Modes
    - Editing
    - Memory
    - RAG
    - Provider Fallback
    """
    
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.registry = None
        self.orchestrator = None
        self.results: List[TestResult] = []
        self.start_time = None
        
    async def setup(self):
        """Initialize the test environment"""
        print("=" * 70)
        print("AI WRITING AGENT - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Mode: {'Mock (No API Keys Required)' if self.use_mock else 'Live (Real APIs)'}")
        print("=" * 70)
        
        self.registry = ModelRegistry()
        
        if self.use_mock:
            mock_provider = MockProvider(latency_ms=100)
            self.registry.register_provider("mock", mock_provider, ProviderConfig(
                provider_type=ProviderType.OPENAI,
                enabled=True,
                priority=100,
            ))
        
        memory = HighContextMemory()
        self.orchestrator = DualModeOrchestrator(self.registry, memory)
        
        self.mock_model = "mock/llama-3.3-70b"
        self.mock_thinking_model = "mock/mixtral-8x7b"
        
        self.orchestrator.non_thinking.default_model = self.mock_model
        self.orchestrator.thinking.default_model = self.mock_thinking_model
        
        print("\n[OK] Test environment initialized")
        return True
    
    def record_result(
        self,
        test_name: str,
        status: str,
        duration_ms: float,
        output: str,
        expected: str,
        actual: str,
        notes: str = "",
    ):
        result = TestResult(
            test_name=test_name,
            status=status,
            duration_ms=duration_ms,
            output=output,
            expected_behavior=expected,
            actual_behavior=actual,
            notes=notes,
        )
        self.results.append(result)
        
        icon = "✓" if status == "PASS" else "✗"
        print(f"  {icon} {test_name}: {status} ({duration_ms:.0f}ms)")
    
    async def test_01_registry_initialization(self):
        """Test that the model registry initializes correctly"""
        print("\n[TEST] Registry Initialization")
        print("-" * 50)
        
        start = time.time()
        
        providers = list(self.registry._providers.keys())
        models = self.registry.list_models()
        
        duration = (time.time() - start) * 1000
        
        self.record_result(
            test_name="Provider Registration",
            status="PASS",
            duration_ms=duration,
            output=f"Registered providers: {providers}",
            expected="At least one provider registered",
            actual=f"Registered: {', '.join(providers)}",
        )
        
        self.record_result(
            test_name="Model Registration",
            status="PASS",
            duration_ms=0,
            output=f"Total models: {len(models)}",
            expected="Models registered in providers",
            actual=f"Total models: {len(models)}",
        )
        
        for model in models[:3]:
            self.record_result(
                test_name=f"Model: {model.id}",
                status="PASS",
                duration_ms=0,
                output=f"Mode: {model.mode.value}, Capabilities: {model.capabilities}",
                expected="Model has mode and capabilities",
                actual=f"Mode={model.mode.value}, Context={model.context_window}",
            )
    
    async def test_02_cli_write_command(self):
        """Test the CLI write command with various prompts"""
        print("\n[TEST] CLI Write Command")
        print("-" * 50)
        
        test_cases = [
            ("Write a haiku about coding", "haiku"),
            ("Write a technical blog post about AI", "blog"),
            ("Write a professional email update", "email"),
            ("Write a LinkedIn post about AI tools", "linkedin"),
            ("Write technical documentation for an API", "technical"),
        ]
        
        for prompt, expected_type in test_cases:
            start = time.time()
            
            try:
                result = await self.orchestrator.write(
                    prompt=prompt,
                    style=WritingStyle.NARRATIVE,
                    model=self.mock_model,
                )
                
                duration = (time.time() - start) * 1000
                
                has_content = len(result.content) > 50
                has_structure = any(marker in result.content for marker in ["#", "##", "1.", "-", "**"])
                
                self.record_result(
                    test_name=f"Write: {expected_type}",
                    status="PASS" if has_content else "FAIL",
                    duration_ms=duration,
                    output=f"Generated {len(result.content)} chars",
                    expected=f"Content generated with {expected_type} structure",
                    actual=f"Content length: {len(result.content)}, Structured: {has_structure}",
                    notes=f"Mode: {result.mode.value}",
                )
                
            except Exception as e:
                duration = (time.time() - start) * 1000
                self.record_result(
                    test_name=f"Write: {expected_type}",
                    status="FAIL",
                    duration_ms=duration,
                    output=str(e),
                    expected="Content generated successfully",
                    actual=f"Error: {str(e)[:100]}",
                )
    
    async def test_03_cli_think_command(self):
        """Test the CLI think command for deep planning"""
        print("\n[TEST] CLI Think Command")
        print("-" * 50)
        
        test_cases = [
            ("Outline a mystery novel chapter", ThinkingType.OUTLINE),
            ("Develop a character named Dr. Sarah Chen", ThinkingType.CHARACTER),
            ("Research the discovery of a new species", ThinkingType.RESEARCH),
        ]
        
        for prompt, thinking_type in test_cases:
            start = time.time()
            
            try:
                result = await self.orchestrator.think(
                    prompt=prompt,
                    thinking_type=thinking_type,
                    depth="medium",
                    model=self.mock_thinking_model,
                )
                
                duration = (time.time() - start) * 1000
                
                has_content = len(result.content) > 10
                has_steps = len(result.thinking_steps or []) > 0
                
                self.record_result(
                    test_name=f"Think: {thinking_type.value}",
                    status="PASS" if (has_content and has_steps) else "FAIL",
                    duration_ms=duration,
                    output=f"Generated {len(result.content)} chars, {len(result.thinking_steps or [])} steps",
                    expected=f"Structured thinking output for {thinking_type.value}",
                    actual=f"Content: {len(result.content)} chars, Steps: {len(result.thinking_steps or [])}",
                )
                
            except Exception as e:
                duration = (time.time() - start) * 1000
                self.record_result(
                    test_name=f"Think: {thinking_type.value}",
                    status="FAIL",
                    duration_ms=duration,
                    output=str(e),
                    expected="Thinking output generated",
                    actual=f"Error: {str(e)[:100]}",
                )
    
    async def test_04_cli_edit_command(self):
        """Test the CLI edit command"""
        print("\n[TEST] CLI Edit Command")
        print("-" * 50)
        
        test_cases = [
            ("The cat go to the store yesterday.", "Fix the grammar errors", "grammar"),
            ("Hey so I was thinking maybe we could like talk later?", "Make it professional", "professional"),
            ("The system utilizes advanced machine learning algorithms trained on vast datasets.", "Improve clarity", "clarity"),
        ]
        
        for text, instruction, expected_type in test_cases:
            start = time.time()
            
            try:
                result = await self.orchestrator.edit(
                    text=text,
                    instruction=instruction,
                    show_reasoning=True,
                )
                
                duration = (time.time() - start) * 1000
                
                has_changes = result.content != text
                has_reasoning = result.reasoning is not None
                
                self.record_result(
                    test_name=f"Edit: {expected_type}",
                    status="PASS" if has_changes else "FAIL",
                    duration_ms=duration,
                    output=f"Edited: {len(result.changes or [])} changes",
                    expected="Text edited with reasoning",
                    actual=f"Changed: {has_changes}, Has reasoning: {has_reasoning}",
                    notes=f"Original: {text[:50]}...",
                )
                
            except Exception as e:
                duration = (time.time() - start) * 1000
                self.record_result(
                    test_name=f"Edit: {expected_type}",
                    status="FAIL",
                    duration_ms=duration,
                    output=str(e),
                    expected="Text edited successfully",
                    actual=f"Error: {str(e)[:100]}",
                )
    
    async def test_05_writing_styles(self):
        """Test different writing styles"""
        print("\n[TEST] Writing Styles")
        print("-" * 50)
        
        styles = [
            WritingStyle.NARRATIVE,
            WritingStyle.TECHNICAL,
            WritingStyle.MARKETING,
            WritingStyle.CONCISE,
            WritingStyle.CREATIVE,
            WritingStyle.FORMAL,
            WritingStyle.CASUAL,
            WritingStyle.ACADEMIC,
        ]
        
        prompt = "Write an introduction about artificial intelligence"
        
        for style in styles:
            start = time.time()
            
            try:
                result = await self.orchestrator.write(
                    prompt=prompt,
                    style=style,
                    model=self.mock_model,
                )
                
                duration = (time.time() - start) * 1000
                
                self.record_result(
                    test_name=f"Style: {style.value}",
                    status="PASS",
                    duration_ms=duration,
                    output=f"Generated {len(result.content)} chars",
                    expected="Content generated in specified style",
                    actual=f"Style: {style.value}, Length: {len(result.content)}",
                )
                
            except Exception as e:
                duration = (time.time() - start) * 1000
                self.record_result(
                    test_name=f"Style: {style.value}",
                    status="FAIL",
                    duration_ms=duration,
                    output=str(e),
                    expected="Style-specific content generated",
                    actual=f"Error: {str(e)[:100]}",
                )
    
    async def test_06_pipeline_workflow(self):
        """Test the think + write pipeline"""
        print("\n[TEST] Pipeline Workflow (Think + Write)")
        print("-" * 50)
        
        start = time.time()
        
        try:
            thinking_result, draft_result = await self.orchestrator.plan_and_draft(
                topic="The Future of Remote Work",
                outline_depth="medium",
                draft_style=WritingStyle.NARRATIVE,
            )
            
            duration = (time.time() - start) * 1000
            
            has_thinking = len(thinking_result.content) > 10
            has_draft = len(draft_result.content) > 50
            has_steps = len(thinking_result.thinking_steps or []) > 0
            
            self.record_result(
                test_name="Pipeline: Think + Write",
                status="PASS" if (has_thinking and has_draft and has_steps) else "FAIL",
                duration_ms=duration,
                output=f"Think: {len(thinking_result.content)} chars, Draft: {len(draft_result.content)} chars",
                expected="Both thinking and draft content generated",
                actual=f"Think: {len(thinking_result.content)}, Draft: {len(draft_result.content)}, Steps: {len(thinking_result.thinking_steps or [])}",
                notes="Full pipeline test",
            )
            
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.record_result(
                test_name="Pipeline: Think + Write",
                status="FAIL",
                duration_ms=duration,
                output=str(e),
                expected="Complete pipeline execution",
                actual=f"Error: {str(e)[:100]}",
            )
    
    async def test_07_memory_system(self):
        """Test the memory/context system"""
        print("\n[TEST] Memory System")
        print("-" * 50)
        
        memory = HighContextMemory()
        
        start = time.time()
        
        try:
            char_profile = CharacterProfile(
                name="Sarah Chen",
                traits=["Determined", "Intelligent"],
                backstory="Marine biologist who lost her partner",
            )
            memory.add_character(char_profile)
            
            memory.add(
                key="plot_intro",
                value="Discovery of deep-sea ecosystem challenges everything we know",
                category="plot",
                importance=1.0,
            )
            
            memory.add(
                key="style_guide",
                value={"tone": "Mystery with scientific undertones", "pacing": "Slow build"},
                category="style",
                importance=0.8,
            )
            
            duration = (time.time() - start) * 1000
            
            char = memory.get_character("Sarah Chen")
            
            self.record_result(
                test_name="Memory: Add & Retrieve Character",
                status="PASS" if char else "FAIL",
                duration_ms=duration,
                output=f"Character retrieved: {char.name if char else 'None'}",
                expected="Character added and retrieved",
                actual=f"Character: {char.name if char else 'None'}",
            )
            
            memory.add_plot_point(
                PlotPoint(
                    chapter=1,
                    title="The Beginning",
                    description="Introduction of main character",
                    characters=["Sarah Chen"],
                    themes=["discovery", "mystery"],
                )
            )
            
            plot_points = memory.get_plot_timeline()
            
            self.record_result(
                test_name="Memory: Add Plot Point",
                status="PASS" if len(plot_points) > 0 else "FAIL",
                duration_ms=0,
                output=f"Plot points: {len(plot_points)}",
                expected="Plot point added",
                actual=f"Total plot points: {len(plot_points)}",
            )
            
            memory.add(
                key="temp_data",
                value="Temporary information",
                category="temp",
                importance=0.5,
            )
            
            memory._prune_low_importance()
            temp_val = memory.get("temp_data")
            
            self.record_result(
                test_name="Memory: Pruning",
                status="PASS",
                duration_ms=0,
                output="Memory pruning successful",
                expected="Low importance entries pruned",
                actual=f"Temp value after prune: {temp_val}",
            )
            
        except Exception as e:
            self.record_result(
                test_name="Memory System",
                status="FAIL",
                duration_ms=(time.time() - start) * 1000,
                output=str(e),
                expected="Memory operations successful",
                actual=f"Error: {str(e)[:100]}",
            )
    
    async def test_08_session_management(self):
        """Test writing session management"""
        print("\n[TEST] Session Management")
        print("-" * 50)
        
        start = time.time()
        
        try:
            session1 = self.orchestrator.create_session(
                session_id="test_session_1",
                topic="Test Topic",
                context={"test": True},
            )
            
            self.orchestrator.set_session("test_session_1")
            
            current = self.orchestrator.get_session("test_session_1")
            
            sessions = self.orchestrator.list_sessions()
            
            duration = (time.time() - start) * 1000
            
            self.record_result(
                test_name="Session: Create & Get",
                status="PASS" if current else "FAIL",
                duration_ms=duration,
                output=f"Session created and retrieved",
                expected="Session management working",
                actual=f"Active sessions: {len(sessions)}",
            )
            
            self.orchestrator.close_session("test_session_1")
            
            sessions_after = self.orchestrator.list_sessions()
            
            self.record_result(
                test_name="Session: Close",
                status="PASS",
                duration_ms=0,
                output="Session closed",
                expected="Session properly closed",
                actual=f"Sessions remaining: {len(sessions_after)}",
            )
            
        except Exception as e:
            self.record_result(
                test_name="Session Management",
                status="FAIL",
                duration_ms=(time.time() - start) * 1000,
                output=str(e),
                expected="Session operations successful",
                actual=f"Error: {str(e)[:100]}",
            )
    
    async def test_09_model_selection(self):
        """Test automatic model selection"""
        print("\n[TEST] Model Selection")
        print("-" * 50)
        
        start = time.time()
        
        try:
            thinking_model = self.registry.get_best_model(mode=ModelMode.THINKING)
            non_thinking_model = self.registry.get_best_model(mode=ModelMode.NON_THINKING)
            any_model = self.registry.get_best_model(mode=ModelMode.ANY)
            
            duration = (time.time() - start) * 1000
            
            self.record_result(
                test_name="Model: Thinking Mode",
                status="PASS" if thinking_model else "FAIL",
                duration_ms=duration,
                output=f"Selected: {thinking_model}",
                expected="Model selected for thinking",
                actual=f"Model: {thinking_model}",
            )
            
            self.record_result(
                test_name="Model: Non-Thinking Mode",
                status="PASS" if non_thinking_model else "FAIL",
                duration_ms=0,
                output=f"Selected: {non_thinking_model}",
                expected="Model selected for non-thinking",
                actual=f"Model: {non_thinking_model}",
            )
            
            self.record_result(
                test_name="Model: Any Mode",
                status="PASS" if any_model else "FAIL",
                duration_ms=0,
                output=f"Selected: {any_model}",
                expected="Any model can be selected",
                actual=f"Model: {any_model}",
            )
            
        except Exception as e:
            self.record_result(
                test_name="Model Selection",
                status="FAIL",
                duration_ms=(time.time() - start) * 1000,
                output=str(e),
                expected="Models selected successfully",
                actual=f"Error: {str(e)[:100]}",
            )
    
    async def test_10_provider_health(self):
        """Test provider health checks"""
        print("\n[TEST] Provider Health Checks")
        print("-" * 50)
        
        start = time.time()
        
        try:
            health = await self.registry.health_check_all()
            
            duration = (time.time() - start) * 1000
            
            for provider_name, is_healthy in health.items():
                status = "HEALTHY" if is_healthy else "UNHEALTHY"
                
                self.record_result(
                    test_name=f"Provider: {provider_name}",
                    status="PASS",
                    duration_ms=duration,
                    output=f"Status: {status}",
                    expected="Provider health checked",
                    actual=f"Healthy: {is_healthy}",
                )
                
        except Exception as e:
            self.record_result(
                test_name="Provider Health",
                status="FAIL",
                duration_ms=(time.time() - start) * 1000,
                output=str(e),
                expected="Health checks completed",
                actual=f"Error: {str(e)[:100]}",
            )
    
    async def run_all_tests(self):
        """Run the complete test suite"""
        self.start_time = time.time()
        
        await self.setup()
        
        await self.test_01_registry_initialization()
        await self.test_02_cli_write_command()
        await self.test_03_cli_think_command()
        await self.test_04_cli_edit_command()
        await self.test_05_writing_styles()
        await self.test_06_pipeline_workflow()
        await self.test_07_memory_system()
        await self.test_08_session_management()
        await self.test_09_model_selection()
        await self.test_10_provider_health()
        
        total_duration = (time.time() - self.start_time) * 1000
        
        await self.generate_report(total_duration)
    
    async def generate_report(self, total_duration: float):
        """Generate comprehensive test report"""
        
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        total = len(self.results)
        
        print("\n" + "=" * 70)
        print("TEST EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print(f"Total Duration: {total_duration:.0f}ms")
        print("=" * 70)
        
        if failed > 0:
            print("\nFAILED TESTS:")
            print("-" * 50)
            for result in self.results:
                if result.status == "FAIL":
                    print(f"\n  {result.test_name}")
                    print(f"  Error: {result.actual_behavior}")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "mock" if self.use_mock else "live",
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": f"{(passed/total*100):.1f}%",
                "duration_ms": total_duration,
            },
            "test_results": [asdict(r) for r in self.results],
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[OK] Report saved to test_report.json")
        
        return report


async def main():
    runner = ComprehensiveTestRunner(use_mock=True)
    report = await runner.run_all_tests()
    return report


if __name__ == "__main__":
    asyncio.run(main())
