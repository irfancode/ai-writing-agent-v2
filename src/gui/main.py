"""GUI - Desktop GUI for AI Writing Agent using CustomTkinter"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

try:
    import customtkinter as ctk
    from tkinter import messagebox as tk_messagebox
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False
    ctk = None
    tk_messagebox = None

from ..core.providers.registry import init_registry
from ..core.modes.orchestrator import DualModeOrchestrator
from ..core.modes.thinking import ThinkingType
from ..core.modes.non_thinking import WritingStyle
from ..core.memory.context import HighContextMemory


class WritingMode:
    WRITE = "write"
    THINK = "think"
    EDIT = "edit"
    PIPELINE = "pipeline"


class AIGUI:
    """AI Writing Agent Desktop GUI"""
    
    def __init__(self):
        if not CTK_AVAILABLE:
            raise ImportError("tkinter/customtkinter not available. Install with: brew install python-tk")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("AI Writing Agent")
        self.root.geometry("1200x800")
        
        self.registry = None
        self.orchestrator = None
        self.current_mode = WritingMode.WRITE
        self.current_style = WritingStyle.NARRATIVE
        self.generated_content = ""
        self.sessions = {}
        self.current_session_id = None
        self.is_generating = False
        
        self.app_data_dir = Path.home() / ".ai-writing-agent"
        self.sessions_dir = self.app_data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_ui()
        self.load_sessions()
        self.bind_keys()
    
    def setup_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="✍️ AI Writing Agent",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_write = ctk.CTkButton(
            self.sidebar, 
            text="📝 Write",
            command=lambda: self.set_mode(WritingMode.WRITE),
            fg_color="transparent",
            border_width=2,
            anchor="w"
        )
        self.btn_write.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_think = ctk.CTkButton(
            self.sidebar, 
            text="🧠 Think",
            command=lambda: self.set_mode(WritingMode.THINK),
            fg_color="transparent",
            border_width=2,
            anchor="w"
        )
        self.btn_think.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_edit = ctk.CTkButton(
            self.sidebar, 
            text="✏️ Edit",
            command=lambda: self.set_mode(WritingMode.EDIT),
            fg_color="transparent",
            border_width=2,
            anchor="w"
        )
        self.btn_edit.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_pipeline = ctk.CTkButton(
            self.sidebar, 
            text="🔄 Pipeline",
            command=lambda: self.set_mode(WritingMode.PIPELINE),
            fg_color="transparent",
            border_width=2,
            anchor="w"
        )
        self.btn_pipeline.grid(row=4, column=0, padx=20, pady=10)
        
        sessions_label = ctk.CTkLabel(self.sidebar, text="💾 Sessions", font=ctk.CTkFont(weight="bold"))
        sessions_label.grid(row=5, column=0, padx=20, pady=(20, 5))
        
        self.sessions_frame = ctk.CTkScrollableFrame(self.sidebar, label_text="Sessions")
        self.sessions_frame.grid(row=6, column=0, padx=20, pady=10, sticky="nsew")
        
        self.btn_settings = ctk.CTkButton(
            self.sidebar,
            text="⚙️ Settings",
            command=self.open_settings,
            fg_color="transparent"
        )
        self.btn_settings.grid(row=7, column=0, padx=20, pady=10)
        
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.main_content.grid_rowconfigure(2, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        options_bar = ctk.CTkFrame(self.main_content, fg_color="transparent")
        options_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        options_bar.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(options_bar, text="Style:").grid(row=0, column=0, padx=5)
        
        self.style_var = ctk.StringVar(value="narrative")
        self.style_combo = ctk.CTkComboBox(
            options_bar,
            values=["narrative", "technical", "marketing", "concise", "creative", "formal", "casual", "academic"],
            variable=self.style_var,
            command=self.on_style_changed
        )
        self.style_combo.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.btn_new_session = ctk.CTkButton(
            options_bar,
            text="📄 New Session",
            command=self.new_session,
            width=120
        )
        self.btn_new_session.grid(row=0, column=2, padx=10)
        
        self.prompt_input = ctk.CTkTextbox(self.main_content, height=120)
        self.prompt_input.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.prompt_input.insert("1.0", "Enter your writing prompt here...")
        
        self.btn_generate = ctk.CTkButton(
            self.main_content,
            text="✨ Generate",
            command=self.generate_content,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.btn_generate.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        output_label = ctk.CTkLabel(self.main_content, text="📄 Generated Content", font=ctk.CTkFont(weight="bold"))
        output_label.grid(row=3, column=0, padx=10, pady=(10, 0))
        
        self.output_area = ctk.CTkTextbox(self.main_content, wrap="word")
        self.output_area.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        
        self.status_bar = ctk.CTkLabel(
            self.main_content,
            text="Ready",
            text_color="gray"
        )
        self.status_bar.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        
        self.set_mode(WritingMode.WRITE)
    
    def bind_keys(self):
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-n>", lambda e: self.new_session())
        self.root.bind("<Return>", lambda e: self.generate_content() if not self.is_generating else None)
    
    def set_mode(self, mode: str):
        self.current_mode = mode
        
        for btn in [self.btn_write, self.btn_think, self.btn_edit, self.btn_pipeline]:
            btn.configure(fg_color="transparent")
        
        mode_buttons = {
            WritingMode.WRITE: self.btn_write,
            WritingMode.THINK: self.btn_think,
            WritingMode.EDIT: self.btn_edit,
            WritingMode.PIPELINE: self.btn_pipeline,
        }
        mode_buttons[mode].configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        
        prompts = {
            WritingMode.WRITE: "What would you like to write about?",
            WritingMode.THINK: "What would you like to plan or think about?",
            WritingMode.EDIT: "Paste the text you want to edit...",
            WritingMode.PIPELINE: "What topic would you like to plan and draft?",
        }
        self.prompt_input.delete("1.0", "end")
        self.prompt_input.insert("1.0", prompts.get(mode, ""))
        
        self.update_status(f"Mode: {mode.title()}")
    
    def on_style_changed(self, choice: str):
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
        self.current_style = style_map.get(choice, WritingStyle.NARRATIVE)
    
    def new_session(self):
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_id = session_id
        self.sessions[session_id] = {
            "created": datetime.now().isoformat(),
            "mode": self.current_mode,
            "history": []
        }
        self.output_area.delete("1.0", "end")
        self.prompt_input.delete("1.0", "end")
        self.save_sessions()
        self.load_sessions()
        self.update_status(f"New session: {session_id}")
    
    def load_sessions(self):
        for widget in self.sessions_frame.winfo_children():
            widget.destroy()
        
        sessions_file = self.sessions_dir / "sessions.json"
        if sessions_file.exists():
            with open(sessions_file, 'r') as f:
                self.sessions = json.load(f)
        
        for session_id in self.sessions.get(self.current_session_id, {}).get("history", []):
            btn = ctk.CTkButton(
                self.sessions_frame,
                text=f"Session {session_id[:8]}...",
                command=lambda s=session_id: self.load_session(s)
            )
            btn.pack(pady=2, fill="x")
    
    def save_sessions(self):
        sessions_file = self.sessions_dir / "sessions.json"
        with open(sessions_file, 'w') as f:
            json.dump(self.sessions, f)
    
    def load_session(self, session_id: str):
        if session_id in self.sessions:
            self.current_session_id = session_id
            self.update_status(f"Loaded session: {session_id[:8]}...")
    
    def open_settings(self):
        settings_win = ctk.CTkToplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x400")
        
        ctk.CTkLabel(settings_win, text="API Keys", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        ctk.CTkLabel(settings_win, text="GROQ API Key:").pack(anchor="w", padx=20)
        groq_entry = ctk.CTkEntry(settings_win, width=350)
        groq_entry.pack(padx=20, pady=5)
        
        ctk.CTkLabel(settings_win, text="Ollama URL:").pack(anchor="w", padx=20)
        ollama_entry = ctk.CTkEntry(settings_win, width=350)
        ollama_entry.insert(0, "http://localhost:11434")
        ollama_entry.pack(padx=20, pady=5)
        
        btn_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Save", command=settings_win.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=settings_win.destroy).pack(side="left", padx=10)
    
    def update_status(self, message: str):
        self.status_bar.configure(text=message)
    
    def generate_content(self):
        if self.is_generating:
            return
        
        prompt = self.prompt_input.get("1.0", "end-1c").strip()
        if not prompt:
            if tk_messagebox:
                tk_messagebox.showwarning("Warning", "Please enter a prompt!")
            return
        
        self.is_generating = True
        self.btn_generate.configure(text="⏳ Generating...")
        self.update_status("Generating content...")
        
        asyncio.create_task(self._generate_async(prompt))
    
    async def _generate_async(self, prompt: str):
        try:
            if not self.registry:
                self.registry = init_registry()
                memory = HighContextMemory()
                self.orchestrator = DualModeOrchestrator(self.registry, memory)
            
            result = None
            
            if self.current_mode == WritingMode.WRITE:
                result = await self.orchestrator.write(
                    prompt=prompt,
                    style=self.current_style,
                )
                self.generated_content = result.content
                
            elif self.current_mode == WritingMode.THINK:
                result = await self.orchestrator.think(
                    prompt=prompt,
                    thinking_type=ThinkingType.OUTLINE,
                )
                self.generated_content = result.content
                
            elif self.current_mode == WritingMode.EDIT:
                result = await self.orchestrator.edit(
                    text=prompt,
                    instruction="Improve this text",
                )
                self.generated_content = result.content
                
            elif self.current_mode == WritingMode.PIPELINE:
                thinking_result, draft_result = await self.orchestrator.plan_and_draft(
                    topic=prompt,
                    draft_style=self.current_style,
                )
                self.generated_content = f"=== OUTLINE ===\n{thinking_result.content}\n\n=== DRAFT ===\n{draft_result.content}"
            
            self.output_area.delete("1.0", "end")
            self.output_area.insert("1.0", self.generated_content)
            self.update_status("Content generated!")
            
        except Exception as e:
            if tk_messagebox:
                tk_messagebox.showerror("Error", f"Generation failed: {str(e)}")
            self.update_status(f"Error: {str(e)}")
        
        finally:
            self.is_generating = False
            self.btn_generate.configure(text="✨ Generate")
    
    def run(self):
        self.root.mainloop()


def run_gui():
    """Run the GUI application"""
    app = AIGUI()
    app.run()


if __name__ == "__main__":
    run_gui()
