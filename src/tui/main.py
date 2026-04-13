"""TUI - Terminal User Interface for AI Writing Agent"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Button, Input, TextArea, Static, ListView, Select
from textual.screen import Screen
from textual import work
from textual.binding import Binding

from ..core.providers.registry import init_registry
from ..core.modes.orchestrator import DualModeOrchestrator
from ..core.modes.thinking import ThinkingType
from ..core.modes.non_thinking import WritingStyle
from ..core.memory.context import HighContextMemory


class Mode:
    WRITE = "write"
    THINK = "think"
    EDIT = "edit"
    PIPELINE = "pipeline"


class WritingScreen(Screen):
    CSS = """
    Screen { background: $surface; }
    
    # main-container {
        height: 100%;
        layout: vertical;
    }
    
    # toolbar {
        height: 3;
        background: $primary;
        dock: top;
    }
    
    # mode-selector {
        height: 100%;
        layout: horizontal;
    }
    
    .toolbar-btn {
        background: transparent;
        color: white;
        margin: 0 1;
    }
    
    .toolbar-btn.active {
        background: $accent;
    }
    
    # prompt-area {
        height: 6;
        border: solid $primary;
        margin: 1 2;
    }
    
    # output-area {
        height: 1fr;
        border: solid $accent;
        margin: 1 2;
    }
    
    # input-prompt {
        border: solid $success;
        margin: 1 2;
        height: 3;
    }
    
    # sidebar {
        width: 25;
        border: solid $surface-darken-1;
        dock: right;
    }
    
    # sessions-panel, # history-panel {
        height: 50%;
    }
    
    # output-label {
        text-style: bold;
        color: $text;
        padding: 0 1;
    }
    
    # status-bar {
        height: 3;
        dock: bottom;
        background: $primary-darken-1;
    }
    
    LoadingIndicator {
        dock: center;
    }
    
    .generated-text {
        color: $text;
        padding: 0 1;
    }
    
    ListView {
        height: 100%;
    }
    """
    
    def __init__(self, orchestrator, **kwargs):
        super().__init__(**kwargs)
        self.orchestrator = orchestrator
        self.current_mode = Mode.WRITE
        self.current_style = WritingStyle.NARRATIVE
        self.generated_content = ""
        self.is_generating = False
        self.sessions = []
        self.history = []
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, clock_format="%-I:%M %p")
        
        with Container(id="main-container"):
            # Toolbar
            with Horizontal(id="toolbar"):
                yield Button("Write", variant="primary", id="btn-write", classes="toolbar-btn active")
                yield Button("Think", variant="default", id="btn-think", classes="toolbar-btn")
                yield Button("Edit", variant="default", id="btn-edit", classes="toolbar-btn")
                yield Button("Pipeline", variant="default", id="btn-pipeline", classes="toolbar-btn")
            
            # Mode selector
            with Horizontal(id="mode-selector"):
                with Vertical(id="prompt-area"):
                    yield Static("📝 Enter your writing prompt:", id="prompt-label")
                    yield TextArea(id="prompt-input", placeholder="What would you like to write about?")
                
                with Vertical(id="input-prompt"):
                    yield Static("⚙️ Options:", id="options-label")
                    yield Select(
                        [
                            ("narrative", "📖 Narrative"),
                            ("technical", "⚡ Technical"),
                            ("marketing", "📢 Marketing"),
                            ("concise", "✂️ Concise"),
                            ("creative", "🎨 Creative"),
                            ("formal", "👔 Formal"),
                            ("casual", "😊 Casual"),
                            ("academic", "🎓 Academic"),
                        ],
                        value="narrative",
                        id="style-select",
                    )
                    yield Button("✨ Generate", variant="success", id="btn-generate")
            
            # Output area
            with Vertical(id="output-area"):
                yield Static("📄 Generated Content:", id="output-label")
                yield TextArea(id="output", readonly=True, show_line_numbers=True)
            
            # Sidebar
            with Vertical(id="sidebar"):
                with ScrollableContainer(id="sessions-panel"):
                    yield Static("💾 Sessions", id="sessions-label")
                    yield ListView(id="sessions-list")
                
                with ScrollableContainer(id="history-panel"):
                    yield Static("📜 History", id="history-label")
                    yield ListView(id="history-list")
        
        yield Footer()
    
    def on_mount(self) -> None:
        self.query_one("#btn-write", Button).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        
        # Update active button
        for btn in self.query(".toolbar-btn"):
            btn.variant = "default"
            btn.remove_class("active")
        
        event.button.variant = "primary"
        event.button.add_class("active")
        
        if btn_id == "btn-write":
            self.current_mode = Mode.WRITE
        elif btn_id == "btn-think":
            self.current_mode = Mode.THINK
        elif btn_id == "btn-edit":
            self.current_mode = Mode.EDIT
        elif btn_id == "btn-pipeline":
            self.current_mode = Mode.PIPELINE
        elif btn_id == "btn-generate":
            self.generate_content()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        style_map = {
            "narrative": WritingStyle.NARRATIVE,
            "technical": WritingStyle.TECHNICAL,
            "marketing": WritingStyle.MARKETING,
            "concise": WritingStyle.CONCISE,
            "creative": WritingStyle.CREATIVE,
            "formal": WritingStyle.FORMAL,
            "casual": WritingStyle.CASUAL,
            "academic": WritingStyle.ACADEMIC,
        }
        self.current_style = style_map.get(event.value, WritingStyle.NARRATIVE)
    
    @work
    async def generate_content(self) -> None:
        prompt_input = self.query_one("#prompt-input", TextArea)
        output = self.query_one("#output", TextArea)
        
        prompt = prompt_input.text.strip()
        if not prompt:
            self.app.notify("Please enter a prompt!", severity="warning")
            return
        
        self.is_generating = True
        output.text = "⏳ Generating..."
        
        try:
            if self.current_mode == Mode.WRITE:
                result = await self.orchestrator.write(
                    prompt=prompt,
                    style=self.current_style,
                )
                self.generated_content = result.content
                output.text = result.content
                
            elif self.current_mode == Mode.THINK:
                result = await self.orchestrator.think(
                    prompt=prompt,
                    thinking_type=ThinkingType.OUTLINE,
                )
                self.generated_content = result.content
                output.text = result.content
                
            elif self.current_mode == Mode.EDIT:
                result = await self.orchestrator.edit(
                    text=prompt,
                    instruction="Improve this text",
                )
                self.generated_content = result.content
                output.text = result.content
                
            elif self.current_mode == Mode.PIPELINE:
                thinking_result, draft_result = await self.orchestrator.plan_and_draft(
                    topic=prompt,
                    draft_style=self.current_style,
                )
                self.generated_content = f"=== OUTLINE ===\n{thinking_result.content}\n\n=== DRAFT ===\n{draft_result.content}"
                output.text = self.generated_content
            
            self.app.notify("Content generated!", severity="information")
            
        except Exception as e:
            output.text = f"Error: {str(e)}"
            self.app.notify(f"Error: {str(e)}", severity="error")
        
        self.is_generating = False


class SettingsScreen(Screen):
    CSS = """
    Screen { background: $surface; }
    Vertical { padding: 2; }
    Input { margin: 1 0; }
    Button { margin: 1 2 1 0; }
    """
    
    def __init__(self, orchestrator, **kwargs):
        super().__init__(**kwargs)
        self.orchestrator = orchestrator
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Vertical():
            yield Static("⚙️ Settings", id="settings-title")
            yield Input(placeholder="GROQ_API_KEY", id="groq-key")
            yield Input(placeholder="TOGETHER_API_KEY", id="together-key")
            yield Input(placeholder="HF_API_KEY", id="hf-key")
            yield Input(placeholder="OLLAMA_BASE_URL", value="http://localhost:11434", id="ollama-url")
            
            with Horizontal():
                yield Button("Save", variant="success", id="btn-save")
                yield Button("Back", variant="default", id="btn-back")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-save":
            self.app.notify("Settings saved!", severity="information")


class AITuiApp(App):
    """AI Writing Agent Terminal User Interface"""
    
    CSS_PATH = None
    TITLE = "AI Writing Agent - TUI"
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+s", "push_screen('settings')", "Settings", show=True),
        Binding("ctrl+n", "new_session", "New Session", show=True),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orchestrator = None
        self.current_session = None
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, clock_format="%-I:%M %p")
        yield Footer()
    
    async def on_mount(self) -> None:
        self.title = "🤖 AI Writing Agent"
        
        # Initialize registry and orchestrator
        self.registry = init_registry()
        memory = HighContextMemory()
        self.orchestrator = DualModeOrchestrator(self.registry, memory)
        
        # Push main writing screen
        self.push_screen(WritingScreen(self.orchestrator))
    
    def action_push_screen(self, screen_name: str) -> None:
        if screen_name == "settings":
            self.push_screen(SettingsScreen(self.orchestrator))
    
    def action_quit(self) -> None:
        self.exit()
    
    def action_new_session(self) -> None:
        self.app.notify("New session created!", severity="information")


def run_tui():
    """Run the TUI application"""
    app = AITuiApp()
    app.run()


if __name__ == "__main__":
    run_tui()
