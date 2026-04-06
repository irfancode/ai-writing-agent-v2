"""CLI - Command Line Interface for AI Writing Agent"""

import asyncio
import sys
from typing import Optional
import argparse
import os

from ..core.providers.registry import init_registry, get_registry
from ..core.modes.orchestrator import DualModeOrchestrator
from ..core.modes.thinking import ThinkingType
from ..core.modes.non_thinking import WritingStyle
from ..core.memory.context import HighContextMemory


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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")


def print_error(text: str):
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
  think <prompt>      - Deep thinking/planning
  edit <text>         - Edit existing content
  pipeline <topic>     - Think + write pipeline
  models              - List available models
  help                - Show this help
  exit                - Exit
        """)


async def main():
    parser = argparse.ArgumentParser(description="AI Writing Agent CLI")
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
    subparsers.add_parser("models", help="List models")
    
    args = parser.parse_args()
    
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
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
