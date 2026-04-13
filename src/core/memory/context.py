"""High-Context Memory - Long document memory for character traits, plot points, brand voice"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class MemoryEntry:
    """A single entry in memory"""
    key: str
    value: Any
    category: str
    importance: float = 1.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class CharacterProfile:
    """Character in a story or brand voice"""
    name: str
    traits: List[str] = field(default_factory=list)
    voice_patterns: List[str] = field(default_factory=list)
    backstory: Optional[str] = None
    relationships: Dict[str, str] = field(default_factory=dict)
    arc: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlotPoint:
    """A point in a narrative"""
    chapter: int
    title: str
    description: str
    characters: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    notes: Optional[str] = None


class HighContextMemory:
    """
    High-context memory for long documents.
    
    Maintains:
    - Character profiles
    - Plot points and timeline
    - Brand voice guidelines
    - Writing style preferences
    - Document-specific context
    
    Supports 128K-256K token context windows.
    """
    
    def __init__(
        self,
        max_entries: int = 10000,
        context_window: int = 128000,
    ):
        self.max_entries = max_entries
        self.context_window = context_window
        
        # Core memory store
        self._entries: Dict[str, MemoryEntry] = {}
        
        # Specialized stores
        self._characters: Dict[str, CharacterProfile] = {}
        self._plot_points: List[PlotPoint] = []
        self._brand_voice: Dict[str, Any] = {}
        self._style_guide: Dict[str, Any] = {}
        
        # Session memories (temporary)
        self._session_memories: Dict[str, List[MemoryEntry]] = defaultdict(list)
        
        # Index for fast retrieval
        self._category_index: Dict[str, List[str]] = defaultdict(list)
    
    def create_session(self, session_id: str) -> "HighContextMemory":
        """Create a session-scoped memory view"""
        session_memory = HighContextMemory(
            max_entries=self.max_entries,
            context_window=self.context_window,
        )
        session_memory._entries = self._entries.copy()
        session_memory._characters = self._characters.copy()
        session_memory._plot_points = self._plot_points.copy()
        session_memory._brand_voice = self._brand_voice.copy()
        session_memory._style_guide = self._style_guide.copy()
        
        return session_memory
    
    def add(
        self,
        key: str,
        value: Any,
        category: str = "general",
        importance: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add an entry to memory"""
        entry = MemoryEntry(
            key=key,
            value=value,
            category=category,
            importance=importance,
            metadata=metadata or {},
        )
        
        self._entries[key] = entry
        self._category_index[category].append(key)
        
        # Prune if needed
        if len(self._entries) > self.max_entries:
            self._prune_low_importance()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        entry = self._entries.get(key)
        return entry.value if entry else None
    
    def get_by_category(self, category: str) -> List[MemoryEntry]:
        """Get all entries in a category"""
        keys = self._category_index.get(category, [])
        return [self._entries[k] for k in keys if k in self._entries]
    
    def add_character(self, character: CharacterProfile):
        """Add a character profile"""
        self._characters[character.name] = character
        self.add(
            key=f"character:{character.name}",
            value=character,
            category="characters",
            importance=1.0,
        )
    
    def get_character(self, name: str) -> Optional[CharacterProfile]:
        """Get a character profile"""
        return self._characters.get(name)
    
    def get_all_characters(self) -> List[CharacterProfile]:
        """Get all character profiles"""
        return list(self._characters.values())
    
    def add_plot_point(self, point: PlotPoint):
        """Add a plot point"""
        self._plot_points.append(point)
        self._plot_points.sort(key=lambda p: p.chapter)
        
        self.add(
            key=f"plot:{point.chapter}",
            value=point,
            category="plot",
            importance=0.8,
        )
    
    def get_plot_timeline(self) -> List[PlotPoint]:
        """Get plot points in order"""
        return self._plot_points.copy()
    
    def set_brand_voice(self, guidelines: Dict[str, Any]):
        """Set brand voice guidelines"""
        self._brand_voice = guidelines
        self.add(
            key="brand_voice",
            value=guidelines,
            category="brand",
            importance=1.0,
        )
    
    def get_brand_voice(self) -> Dict[str, Any]:
        """Get brand voice guidelines"""
        return self._brand_voice.copy()
    
    def set_style_guide(self, guide: Dict[str, Any]):
        """Set writing style guide"""
        self._style_guide = guide
        self.add(
            key="style_guide",
            value=guide,
            category="style",
            importance=0.9,
        )
    
    def get_style_guide(self) -> Dict[str, Any]:
        """Get writing style guide"""
        return self._style_guide.copy()
    
    def add_to_context(self, key: str, value: Any):
        """Add context entry (alias for add with default category)"""
        self.add(key, value, category="context")
    
    def get_context_summary(self) -> str:
        """Get a summary of all context for prompt injection"""
        lines = ["# Context Summary\n"]
        
        # Characters
        if self._characters:
            lines.append("\n## Characters\n")
            for char in self._characters.values():
                lines.append(f"- **{char.name}**: {', '.join(char.traits[:3])}")
        
        # Plot points
        if self._plot_points:
            lines.append("\n## Plot Timeline\n")
            for point in self._plot_points[-5:]:  # Last 5
                lines.append(f"- Chapter {point.chapter}: {point.title}")
        
        # Brand voice
        if self._brand_voice:
            lines.append("\n## Brand Voice\n")
            lines.append(f"- Tone: {self._brand_voice.get('tone', 'N/A')}")
            lines.append(f"- Values: {', '.join(self._brand_voice.get('values', [])[:3])}")
        
        # Style guide
        if self._style_guide:
            lines.append("\n## Style\n")
            lines.append(f"- Format: {self._style_guide.get('format', 'N/A')}")
        
        return "\n".join(lines)
    
    def get_full_context(self) -> Dict[str, Any]:
        """Get full context as dictionary"""
        return {
            "characters": [c.__dict__ for c in self._characters.values()],
            "plot_points": [p.__dict__ for p in self._plot_points],
            "brand_voice": self._brand_voice,
            "style_guide": self._style_guide,
            "entries": {k: v.to_dict() for k, v in self._entries.items()},
        }
    
    def get_for_prompt(
        self,
        max_tokens: int = 32000,
        prioritize: Optional[List[str]] = None,
    ) -> str:
        """
        Get context formatted for prompt injection.
        
        Args:
            max_tokens: Maximum tokens to include
            prioritize: Categories to prioritize
        """
        context = []
        
        # Priority categories first
        priority_order = prioritize or ["characters", "plot", "brand", "style", "context"]
        
        for category in priority_order:
            if category == "characters":
                for char in self._characters.values():
                    char_text = self._format_character(char)
                    context.append(char_text)
            
            elif category == "plot":
                for point in self._plot_points:
                    context.append(f"Plot: Ch.{point.chapter} - {point.title}: {point.description}")
            
            elif category == "brand":
                if self._brand_voice:
                    context.append(f"Brand Voice: {json.dumps(self._brand_voice)}")
            
            elif category == "style":
                if self._style_guide:
                    context.append(f"Style Guide: {json.dumps(self._style_guide)}")
        
        # Add general entries by importance
        sorted_entries = sorted(
            self._entries.values(),
            key=lambda e: e.importance,
            reverse=True
        )
        
        for entry in sorted_entries:
            if entry.category not in priority_order:
                context.append(f"{entry.key}: {entry.value}")
        
        # Combine and truncate
        full_context = "\n\n".join(context)
        
        # Rough token estimate (4 chars per token)
        if len(full_context) > max_tokens * 4:
            full_context = full_context[:max_tokens * 4] + "\n\n[Truncated...]"
        
        return full_context
    
    def _format_character(self, char: CharacterProfile) -> str:
        """Format a character for context"""
        parts = [
            f"Character: {char.name}",
            f"Traits: {', '.join(char.traits)}",
        ]
        
        if char.voice_patterns:
            parts.append(f"Voice: {', '.join(char.voice_patterns)}")
        
        if char.backstory:
            parts.append(f"Backstory: {char.backstory}")
        
        if char.relationships:
            rels = [f"{name} ({rel})" for name, rel in char.relationships.items()]
            parts.append(f"Relationships: {', '.join(rels)}")
        
        if char.arc:
            parts.append(f"Arc: {char.arc}")
        
        return "\n".join(parts)
    
    def _prune_low_importance(self):
        """Remove low importance entries when at max"""
        sorted_entries = sorted(
            self._entries.items(),
            key=lambda x: x[1].importance
        )
        
        # Remove bottom 10%
        to_remove = len(sorted_entries) // 10
        for key, _ in sorted_entries[:to_remove]:
            entry = self._entries.pop(key, None)
            if entry:
                self._category_index[entry.category].remove(key)
    
    def clear(self):
        """Clear all memory"""
        self._entries.clear()
        self._characters.clear()
        self._plot_points.clear()
        self._brand_voice.clear()
        self._style_guide.clear()
        self._category_index.clear()
    
    def save(self, path: str):
        """Save memory to file"""
        data = {
            "entries": {k: v.to_dict() for k, v in self._entries.items()},
            "characters": {
                name: char.__dict__
                for name, char in self._characters.items()
            },
            "plot_points": [p.__dict__ for p in self._plot_points],
            "brand_voice": self._brand_voice,
            "style_guide": self._style_guide,
        }
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self, path: str):
        """Load memory from file"""
        with open(path, "r") as f:
            data = json.load(f)
        
        self._entries = {
            k: MemoryEntry(**v)
            for k, v in data.get("entries", {}).items()
        }
        
        self._characters = {
            k: CharacterProfile(**v)
            for k, v in data.get("characters", {}).items()
        }
        
        self._plot_points = [
            PlotPoint(**p)
            for p in data.get("plot_points", [])
        ]
        
        self._brand_voice = data.get("brand_voice", {})
        self._style_guide = data.get("style_guide", {})
        
        # Rebuild index
        self._category_index.clear()
        for entry in self._entries.values():
            self._category_index[entry.category].append(entry.key)
