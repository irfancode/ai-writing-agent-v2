"""Onboarding Wizard - Interactive first-run setup"""

import os
import sys
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class WriterType(Enum):
    FICTION = "fiction"
    TECHNICAL = "technical"
    MARKETING = "marketing"
    ACADEMIC = "academic"
    GENERAL = "general"


@dataclass
class UserProfile:
    writer_type: WriterType
    preferred_styles: List[str]
    has_api_keys: bool
    use_local: bool
    experience_level: str


class OnboardingWizard:
    """Interactive onboarding for new users"""
    
    INTRO = """
╔══════════════════════════════════════════════════════════════╗
║           Welcome to AI Writing Agent! 🎉                  ║
╚══════════════════════════════════════════════════════════════╝

Let's get you set up in under 2 minutes.

Answer a few quick questions to personalize your experience.
"""

    QUESTIONS = [
        {
            "key": "writer_type",
            "prompt": "What type of writing do you do most?",
            "options": [
                ("1", "Fiction / Novels", WriterType.FICTION),
                ("2", "Technical / Documentation", WriterType.TECHNICAL),
                ("3", "Marketing / Copywriting", WriterType.MARKETING),
                ("4", "Academic / Research", WriterType.ACADEMIC),
                ("5", "General / All-purpose", WriterType.GENERAL),
            ]
        },
        {
            "key": "experience",
            "prompt": "What's your experience with AI writing tools?",
            "options": [
                ("1", "First time user", "beginner"),
                ("2", "Used ChatGPT/Jasper before", "intermediate"),
                ("3", "Power user / Developer", "advanced"),
            ]
        },
    ]
    
    def __init__(self):
        self.answers = {}
        self.profile: Optional[UserProfile] = None
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, text: str):
        print(f"\n{self._color('cyan')}{text}{self._color('reset')}")
    
    def print_option(self, num: str, text: str):
        print(f"  {self._color('yellow')}{num}{self._color('reset')}. {text}")
    
    def print_success(self, text: str):
        print(f"  {self._color('green')}✓{self._color('reset')} {text}")
    
    def _color(self, name: str) -> str:
        colors = {
            "cyan": "\033[96m",
            "yellow": "\033[93m",
            "green": "\033[92m",
            "red": "\033[91m",
            "reset": "\033[0m",
        }
        return colors.get(name, "")
    
    def ask_question(self, question: dict) -> str:
        self.print_header(question["prompt"])
        for num, text, _ in question["options"]:
            self.print_option(num, text)
        
        while True:
            choice = input(f"\n{self._color('cyan')}→{self._color('reset')} ").strip()
            for num, _, value in question["options"]:
                if choice == num:
                    return value
            print(f"{self._color('red')}Invalid choice. Try again.{self._color('reset')}")
    
    def check_providers(self) -> dict:
        providers = {
            "ollama": False,
            "groq": False,
            "together": False,
        }
        
        if os.system("curl -s http://localhost:11434/ > /dev/null 2>&1") == 0:
            providers["ollama"] = True
        
        if os.getenv("GROQ_API_KEY"):
            providers["groq"] = True
        
        if os.getenv("TOGETHER_API_KEY"):
            providers["together"] = True
        
        return providers
    
    def detect_writer_type(self, choice) -> WriterType:
        return choice
    
    def get_recommended_styles(self, writer_type: WriterType) -> List[str]:
        style_map = {
            WriterType.FICTION: ["narrative", "creative"],
            WriterType.TECHNICAL: ["technical", "concise"],
            WriterType.MARKETING: ["marketing", "persuasive"],
            WriterType.ACADEMIC: ["academic", "formal"],
            WriterType.GENERAL: ["narrative", "concise"],
        }
        return style_map.get(writer_type, ["narrative"])
    
    def run(self) -> UserProfile:
        self.clear_screen()
        print(self.INTRO)
        
        writer_type = self.ask_question(self.QUESTIONS[0])
        experience = self.ask_question(self.QUESTIONS[1])
        
        providers = self.check_providers()
        
        print(f"\n{self._color('cyan')}Checking available providers...{self._color('reset')}")
        if providers["ollama"]:
            self.print_success("Ollama (local, private)")
        if providers["groq"]:
            self.print_success("Groq (fast)")
        if providers["together"]:
            self.print_success("Together AI (reasoning)")
        
        if not any(providers.values()):
            print(f"\n{self._color('yellow')}⚠ No providers detected. You'll use demo mode for now.{self._color('reset')}")
            print(f"{self._color('cyan')}Tip: Run ./setup.sh anytime to configure providers.{self._color('reset')}")
        
        self.profile = UserProfile(
            writer_type=writer_type,
            preferred_styles=self.get_recommended_styles(writer_type),
            has_api_keys=providers["groq"] or providers["together"],
            use_local=providers["ollama"],
            experience_level=experience,
        )
        
        self.show_summary()
        
        return self.profile
    
    def show_summary(self):
        print(f"""
{self._color('green')}╔══════════════════════════════════════════════════════════════╗
║                      Setup Complete!                         ║
╚══════════════════════════════════════════════════════════════╝{self._color('reset')}

Based on your profile:
  • Writer Type: {self.profile.writer_type.value.title()}
  • Recommended Styles: {', '.join(self.profile.preferred_styles)}
  • Experience Level: {self.profile.experience_level}

Next Steps:
  • Write: ./run.sh write "Your prompt here"
  • Interactive: ./run.sh interactive
  • GUI: ./run.sh gui

For help: ./run.sh --help
""")
    
    def save_profile(self, profile: UserProfile):
        config_dir = os.path.expanduser("~/.ai-writing-agent")
        os.makedirs(config_dir, exist_ok=True)
        
        import json
        profile_data = {
            "writer_type": profile.writer_type.value,
            "preferred_styles": profile.preferred_styles,
            "experience_level": profile.experience_level,
        }
        
        with open(f"{config_dir}/profile.json", "w") as f:
            json.dump(profile_data, f, indent=2)


def run_onboarding():
    wizard = OnboardingWizard()
    profile = wizard.run()
    wizard.save_profile(profile)
    return profile


if __name__ == "__main__":
    run_onboarding()
