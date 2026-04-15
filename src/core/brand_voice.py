"""Brand Voice DNA - Analyze and replicate brand voice"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path


@dataclass
class VoiceDNA:
    """Brand voice profile"""
    name: str
    vocabulary_profile: Dict[str, Any] = field(default_factory=dict)
    sentence_patterns: Dict[str, Any] = field(default_factory=dict)
    tone_markers: List[str] = field(default_factory=list)
    common_phrases: List[str] = field(default_factory=list)
    style_flags: Dict[str, bool] = field(default_factory=dict)
    example_excerpts: List[str] = field(default_factory=list)


class BrandVoiceAnalyzer:
    """Analyze samples to extract brand voice DNA"""
    
    def __init__(self):
        self.voices: Dict[str, VoiceDNA] = {}
        self._load_saved_voices()
    
    def analyze(
        self,
        samples: List[str],
        name: str = "default",
    ) -> VoiceDNA:
        """Analyze samples and extract voice DNA"""
        if not samples:
            raise ValueError("No samples provided")
        
        combined = " ".join(samples)
        
        vocabulary = self._analyze_vocabulary(combined)
        sentences = self._analyze_sentences(combined)
        tone = self._analyze_tone(combined)
        phrases = self._extract_phrases(samples)
        style = self._analyze_style(samples)
        
        voice = VoiceDNA(
            name=name,
            vocabulary_profile=vocabulary,
            sentence_patterns=sentences,
            tone_markers=tone,
            common_phrases=phrases,
            style_flags=style,
            example_excerpts=samples[:5],
        )
        
        self.voices[name] = voice
        self._save_voice(voice)
        
        return voice
    
    def _analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary patterns"""
        words = text.lower().split()
        word_counts: Dict[str, int] = {}
        
        for word in words:
            clean = ''.join(c for c in word if c.isalpha())
            if len(clean) > 3:
                word_counts[clean] = word_counts.get(clean, 0) + 1
        
        unique_words = len(set(words))
        total_words = len(words)
        
        return {
            "unique_ratio": unique_words / total_words if total_words else 0,
            "top_words": sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:20],
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "vocabulary_richness": "high" if unique_words / total_words > 0.6 else "moderate",
        }
    
    def _analyze_sentences(self, text: str) -> Dict[str, Any]:
        """Analyze sentence patterns"""
        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {"avg_length": 0, "pattern": "short"}
        
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        
        pattern = "short" if avg_length < 15 else "medium" if avg_length < 25 else "long"
        
        return {
            "avg_length": avg_length,
            "min_length": min(lengths),
            "max_length": max(lengths),
            "pattern": pattern,
            "sentence_count": len(sentences),
        }
    
    def _analyze_tone(self, text: str) -> List[str]:
        """Analyze tone markers"""
        text_lower = text.lower()
        markers = []
        
        tone_indicators = {
            "professional": ["therefore", "furthermore", "additionally", "consequently"],
            "casual": ["hey", "awesome", "cool", "pretty", "super", "like"],
            "friendly": ["great", "wonderful", "excited", "happy", "love"],
            "authoritative": ["must", "should", "need to", "essential", "crucial"],
            "empathetic": ["understand", "feel", "believe", "imagine", "know"],
            "urgent": ["now", "today", "immediately", "hurry", "limited"],
            "confident": ["definitely", "certainly", "absolutely", "guarantee"],
        }
        
        for tone, indicators in tone_indicators.items():
            if any(ind in text_lower for ind in indicators):
                markers.append(tone)
        
        return markers
    
    def _extract_phrases(self, samples: List[str]) -> List[str]:
        """Extract common phrases (2-4 word sequences)"""
        import re
        from collections import Counter
        
        phrases = []
        for sample in samples:
            words = sample.split()
            for n in range(2, 5):
                for i in range(len(words) - n + 1):
                    phrase = " ".join(words[i:i+n])
                    if len(phrase) > 6:
                        phrases.append(phrase)
        
        common = Counter(phrases).most_common(15)
        return [p[0] for p in common]
    
    def _analyze_style(self, samples: List[str]) -> Dict[str, bool]:
        """Analyze stylistic choices"""
        text = " ".join(samples).lower()
        
        return {
            "uses_questions": "?" in text,
            "uses_exclamations": "!" in text,
            "uses_emoji": any(ord(c) > 127000 for c in text),
            "uses_first_person": any(p in text for p in [" i ", " we ", " our "]),
            "uses_second_person": " you " in text,
            "uses_numbers": any(c.isdigit() for c in text),
            "uses_bullet_points": "•" in text or "- " in text,
            "uses_hashes": "#" in text,
            "paragraphs_long": len([s for s in text.split('\n\n') if s]) > 2,
        }
    
    def get_voice(self, name: str = "default") -> Optional[VoiceDNA]:
        """Get saved voice profile"""
        return self.voices.get(name)
    
    def list_voices(self) -> List[str]:
        """List all saved voices"""
        return list(self.voices.keys())
    
    def delete_voice(self, name: str):
        """Delete a voice profile"""
        if name in self.voices:
            del self.voices[name]
            self._delete_voice_file(name)
    
    def _save_voice(self, voice: VoiceDNA):
        """Save voice to disk"""
        config_dir = Path.home() / ".ai-writing-agent" / "voices"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        data = {
            "name": voice.name,
            "vocabulary_profile": voice.vocabulary_profile,
            "sentence_patterns": voice.sentence_patterns,
            "tone_markers": voice.tone_markers,
            "common_phrases": voice.common_phrases,
            "style_flags": voice.style_flags,
            "example_excerpts": voice.example_excerpts,
        }
        
        with open(config_dir / f"{voice.name}.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def _load_saved_voices(self):
        """Load saved voices from disk"""
        config_dir = Path.home() / ".ai-writing-agent" / "voices"
        if not config_dir.exists():
            return
        
        for file in config_dir.glob("*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    self.voices[data["name"]] = VoiceDNA(
                        name=data["name"],
                        vocabulary_profile=data.get("vocabulary_profile", {}),
                        sentence_patterns=data.get("sentence_patterns", {}),
                        tone_markers=data.get("tone_markers", []),
                        common_phrases=data.get("common_phrases", []),
                        style_flags=data.get("style_flags", {}),
                        example_excerpts=data.get("example_excerpts", []),
                    )
            except Exception:
                continue
    
    def _delete_voice_file(self, name: str):
        """Delete voice file from disk"""
        config_dir = Path.home() / ".ai-writing-agent" / "voices"
        file_path = config_dir / f"{name}.json"
        if file_path.exists():
            file_path.unlink()
    
    def generate_system_prompt(self, voice: VoiceDNA) -> str:
        """Generate system prompt to replicate voice"""
        prompts = [
            f"You are writing in the voice of '{voice.name}'.",
        ]
        
        if voice.tone_markers:
            prompts.append(f"Tone: {', '.join(voice.tone_markers)}.")
        
        patterns = voice.sentence_patterns
        if patterns:
            prompts.append(f"Write {patterns.get('pattern', 'medium')}-length sentences.")
        
        if voice.common_phrases:
            phrases = ", ".join(voice.common_phrases[:5])
            prompts.append(f"Use natural phrases like: {phrases}.")
        
        flags = voice.style_flags
        if flags.get("uses_questions"):
            prompts.append("You ask questions to engage the reader.")
        if flags.get("uses_first_person"):
            prompts.append("Use first person ('I', 'we') when appropriate.")
        if flags.get("uses_second_person"):
            prompts.append("Address the reader directly as 'you'.")
        
        return " ".join(prompts)


def create_voice_from_samples(samples: List[str], name: str = "default") -> VoiceDNA:
    """Quick helper to create voice profile"""
    analyzer = BrandVoiceAnalyzer()
    return analyzer.analyze(samples, name)
