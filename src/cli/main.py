"""CLI - Command Line Interface for AI Writing Agent"""

import asyncio
import argparse
import os
import sys

from ..core.providers.registry import init_registry
from ..core.modes.orchestrator import DualModeOrchestrator
from ..core.modes.thinking import ThinkingType
from ..core.modes.non_thinking import WritingStyle
from ..core.memory.context import HighContextMemory
from ..core.output_formatter import OutputFormat, OutputFormatter
from ..core.quality_scorer import QualityScorer
from ..core.brand_voice import BrandVoiceAnalyzer
from ..core.version_history import VersionHistory
from ..core.template_library import TemplateLibrary
from ..core.logger import get_logger

logger = get_logger()


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    logger.info(f"Header: {text}")
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}\n")


def print_success(text: str):
    logger.success(text)
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_info(text: str):
    logger.info(text)
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")


def print_error(text: str):
    logger.error(text)
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


class CLI:
    """Command-line interface"""
    
    def __init__(self):
        self.registry = None
        self.orchestrator = None
    
    async def initialize(self):
        """Initialize the system"""
        print_info("Initializing AI Writing Agent...")
        
        self.registry = init_registry()
        memory = HighContextMemory()
        self.orchestrator = DualModeOrchestrator(self.registry, memory)
        
        health = await self.registry.health_check_all()
        available = [k for k, v in health.items() if v]
        
        if available:
            if "mock" in available:
                print_success("Ready! (Demo mode - for real AI, set GROQ_API_KEY)")
            else:
                print_success(f"Connected to: {', '.join(available)}")
        else:
            print_error("No providers available. Check your configuration.")
    
    async def think(self, prompt: str, thinking_type: str = "outline", depth: str = "medium"):
        """Run thinking mode"""
        type_map = {
            "outline": ThinkingType.OUTLINE,
            "character": ThinkingType.CHARACTER,
            "plot": ThinkingType.PLOT,
            "research": ThinkingType.RESEARCH,
            "structure": ThinkingType.STRUCTURE,
        }
        
        result = await self.orchestrator.think(
            prompt=prompt,
            thinking_type=type_map.get(thinking_type, ThinkingType.OUTLINE),
            depth=depth,
        )
        
        print_header("Thinking Output")
        print(result.content)
        
        if result.thinking_steps:
            print_header("Reasoning Steps")
            for step in result.thinking_steps:
                print(f"  {step.get('step', '?')}. {step.get('thought', '')}")
    
    async def write(self, prompt: str, style: str = "narrative"):
        """Run writing mode"""
        style_map = {
            "narrative": WritingStyle.NARRATIVE,
            "technical": WritingStyle.TECHNICAL,
            "marketing": WritingStyle.MARKETING,
            "concise": WritingStyle.CONCISE,
            "creative": WritingStyle.CREATIVE,
        }
        
        result = await self.orchestrator.write(
            prompt=prompt,
            style=style_map.get(style, WritingStyle.NARRATIVE),
        )
        
        print_header("Generated Content")
        print(result.content)
    
    async def edit(self, text: str, instruction: str, show_reasoning: bool = False):
        """Edit content"""
        result = await self.orchestrator.edit(
            text=text,
            instruction=instruction,
            show_reasoning=show_reasoning,
        )
        
        print_header("Edited Content")
        print(result.content)
        
        if show_reasoning and result.reasoning:
            print_header("Reasoning")
            print(result.reasoning)
    
    async def pipeline(self, topic: str, style: str = "narrative"):
        """Run think + write pipeline"""
        thinking_result, draft_result = await self.orchestrator.plan_and_draft(
            topic=topic,
            draft_style=WritingStyle[style.upper()] if style.upper() != "NARRATIVE" else WritingStyle.NARRATIVE,
        )
        
        print_header("Outline/Plan")
        print(thinking_result.content)
        
        print_header("Draft")
        print(draft_result.content)
    
    async def interactive(self):
        """Interactive mode"""
        print_header("AI Writing Agent - Interactive Mode")
        print("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            try:
                mode = input(f"{Colors.CYAN}(write)> {Colors.ENDC}").strip()
                
                if mode.lower() == "exit":
                    break
                
                if mode.lower() == "help":
                    self.print_help()
                    continue
                
                if mode.lower() == "models":
                    models = self.registry.list_models()
                    print_header("Available Models")
                    for m in models[:10]:
                        print(f"  {m.id} ({m.mode.value})")
                    continue
                
                if mode:
                    await self.write(mode)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print_error(f"Error: {e}")
        
        print_success("Goodbye!")
    
    def print_help(self):
        """Print help text"""
        print("""
Commands:
  write <prompt>       - Generate content
  think <prompt>       - Deep thinking/planning
  edit <text>         - Edit existing content
  pipeline <topic>     - Think + write pipeline
  format <prompt>      - Generate with format preset (blog, linkedin, etc.)
  quality <text>      - Analyze content quality
  voice create        - Create brand voice from samples
  voice list          - List saved voices
  template list       - List available templates
  template apply     - Apply a template
  version save        - Save content version
  version list        - List versions
  version rollback   - Rollback to version
  models              - List available models
  interactive         - Interactive mode
  gui                 - Launch Desktop GUI
  tui                 - Launch Terminal UI
  help                - Show this help
  exit                - Exit
        """)


async def main():
    parser = argparse.ArgumentParser(description="AI Writing Agent CLI")
    parser.add_argument("--version", action="version", version="2.0.0")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Think command
    think_parser = subparsers.add_parser("think", help="Deep thinking mode")
    think_parser.add_argument("prompt", help="Topic to think about")
    think_parser.add_argument("--type", "-t", default="outline", choices=["outline", "character", "plot", "research"])
    think_parser.add_argument("--depth", "-d", default="medium", choices=["shallow", "medium", "deep"])
    
    # Write command
    write_parser = subparsers.add_parser("write", help="Writing mode")
    write_parser.add_argument("prompt", help="Writing prompt")
    write_parser.add_argument("--style", "-s", default="narrative", choices=["narrative", "technical", "marketing", "concise", "creative"])
    
    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit content")
    edit_parser.add_argument("--text", required=True, help="Text to edit")
    edit_parser.add_argument("--instruction", "-i", required=True, help="Edit instruction")
    edit_parser.add_argument("--show-reasoning", action="store_true", help="Show reasoning")
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Think + write pipeline")
    pipeline_parser.add_argument("topic", help="Topic")
    pipeline_parser.add_argument("--style", "-s", default="narrative")
    
    # Interactive
    subparsers.add_parser("interactive", help="Interactive mode")
    
    # Models
    subparsers.add_parser("models", help="List available models")
    
    # Interface commands
    subparsers.add_parser("gui", help="Launch Desktop GUI")
    subparsers.add_parser("tui", help="Launch Terminal UI")
    
    # New enhanced commands
    format_parser = subparsers.add_parser("format", help="Generate content with format preset")
    format_parser.add_argument("prompt", help="Writing prompt")
    format_parser.add_argument("--format", "-f", default="blog_post", 
                                choices=["blog_post", "linkedin_post", "email", "twitter_thread", 
                                        "landing_page", "product_desc", "press_release", "newsletter",
                                        "case_study", "how_to_guide", "faq"])
    
    quality_parser = subparsers.add_parser("quality", help="Score content quality")
    quality_parser.add_argument("text", help="Text to analyze")
    quality_parser.add_argument("--seo", action="store_true", help="Include SEO scoring")
    
    voice_parser = subparsers.add_parser("voice", help="Brand voice DNA")
    voice_parser.add_argument("action", choices=["create", "list", "use"], help="Voice action")
    voice_parser.add_argument("--name", help="Voice profile name")
    voice_parser.add_argument("--samples", nargs="*", help="Sample texts for analysis")
    
    template_parser = subparsers.add_parser("template", help="Template library")
    template_parser.add_argument("action", choices=["list", "apply"], help="Template action")
    template_parser.add_argument("--id", help="Template ID")
    template_parser.add_argument("--var", action="append", help="Variables (key=value)")
    
    version_parser = subparsers.add_parser("version", help="Version history")
    version_parser.add_argument("action", choices=["save", "list", "rollback"], help="Version action")
    version_parser.add_argument("--doc", default="default", help="Document ID")
    version_parser.add_argument("--version-id", help="Version ID to rollback to")
    version_parser.add_argument("--content", help="Content to save")
    
    # Health check command
    subparsers.add_parser("health", help="Check provider status")
    
    # Onboarding
    subparsers.add_parser("onboard", help="Interactive onboarding wizard")
    
    args = parser.parse_args()
    
    # Handle interface launching
    if args.command == "gui":
        import os
        os.environ['TK_SILENCE_DEPRECATION'] = '1'
        from ..gui.main import run_gui
        run_gui()
        return
    
    if args.command == "tui":
        from ..tui.main import run_tui
        import sys
        sys.argv = ["tui"]
        run_tui()
        return
    
    cli = CLI()
    await cli.initialize()
    
    if args.command == "think":
        await cli.think(args.prompt, args.type, args.depth)
    elif args.command == "write":
        await cli.write(args.prompt, args.style)
    elif args.command == "edit":
        await cli.edit(args.text, args.instruction, args.show_reasoning)
    elif args.command == "pipeline":
        await cli.pipeline(args.topic, args.style)
    elif args.command == "interactive":
        await cli.interactive()
    elif args.command == "models":
        models = cli.registry.list_models()
        for m in models[:15]:
            print(f"{m.id} ({m.mode.value})")
    elif args.command == "format":
        from ..core.output_formatter import OutputFormat
        format_enum = OutputFormat(args.format)
        formatted_prompt = OutputFormatter.format_prompt(args.prompt, format_enum)
        style = getattr(args, 'style', 'narrative')
        await cli.write(formatted_prompt, style)
    elif args.command == "quality":
        scorer = QualityScorer()
        score = scorer.score(args.text, args.seo)
        print(scorer.format_report(score))
    elif args.command == "voice":
        if args.action == "list":
            analyzer = BrandVoiceAnalyzer()
            voices = analyzer.list_voices()
            if voices:
                print("Saved voices:", ", ".join(voices))
            else:
                print("No voice profiles. Create one with: ./run.sh voice create --name myvoice --samples 'text1' 'text2'")
        elif args.action == "create" and args.name and args.samples:
            analyzer = BrandVoiceAnalyzer()
            voice = analyzer.analyze(args.samples, args.name)
            print(f"✓ Created voice profile: {voice.name}")
            print(f"  Tone: {', '.join(voice.tone_markers)}")
            print(f"  Style: {voice.sentence_patterns.get('pattern', 'medium')}-length sentences")
        elif args.action == "use" and args.name:
            analyzer = BrandVoiceAnalyzer()
            voice = analyzer.get_voice(args.name)
            if voice:
                prompt = analyzer.generate_system_prompt(voice)
                print(f"Using voice: {args.name}")
                print(f"System prompt:\n{prompt}")
            else:
                print(f"Voice '{args.name}' not found")
    elif args.command == "template":
        if args.action == "list":
            templates = TemplateLibrary.list_all()
            print("\nAvailable Templates:")
            for t in templates:
                print(f"  {t['id']:20} - {t['name']}")
                print(f"    {t['description']}")
                print(f"    Variables: {', '.join(t['variables'])}")
                print()
        elif args.action == "apply" and args.id and args.var:
            variables = {}
            for v in args.var:
                if "=" in v:
                    key, val = v.split("=", 1)
                    variables[key] = val
            prompt = TemplateLibrary.apply_template(args.id, variables)
            await cli.write(prompt, "narrative")
    elif args.command == "version":
        vh = VersionHistory()
        if args.action == "save" and args.content:
            version_id = vh.save_version(args.doc, args.content)
            print(f"✓ Saved version: {version_id}")
        elif args.action == "list":
            versions = vh.list_versions(args.doc)
            print(f"Versions for '{args.doc}':")
            for v in versions:
                print(f"  {v['version_id']} - {v['word_count']} words - {v.get('delta', 'initial')}")
        elif args.action == "rollback" and args.version_id:
            version_id = vh.rollback(args.doc, args.version_id)
            print(f"✓ Rolled back to: {version_id}")
    elif args.command == "health":
        from ..core.health_dashboard import health_dashboard
        health = await health_dashboard.check_all(cli.registry)
        print(health_dashboard.format_status())
        best = health_dashboard.get_best_provider()
        if best:
            print(f"\n✓ Best provider: {best}")
    elif args.command == "onboard":
        from ..cli.onboarding import run_onboarding
        run_onboarding()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
