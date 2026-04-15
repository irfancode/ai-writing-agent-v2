"""Quality Scorer - Analyzes and scores output quality"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class QualityGrade(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    NEEDS_IMPROVEMENT = "needs_improvement"


@dataclass
class QualityScore:
    """Overall quality score breakdown"""
    grade: QualityGrade
    readability: float
    engagement: float
    seo_score: float
    overall: float
    suggestions: List[str]
    metrics: Dict[str, any]


class QualityScorer:
    """Scores and analyzes writing quality"""
    
    def __init__(self):
        self.weights = {
            "readability": 0.4,
            "engagement": 0.3,
            "seo": 0.3,
        }
    
    def score(self, text: str, check_seo: bool = False) -> QualityScore:
        """Score the quality of text"""
        readability = self._readability_score(text)
        engagement = self._engagement_score(text)
        
        seo_score = 0.0
        if check_seo:
            seo_score = self._seo_score(text)
        
        overall = (
            readability * self.weights["readability"] +
            engagement * self.weights["engagement"] +
            seo_score * self.weights["seo"]
        )
        
        if overall >= 80:
            grade = QualityGrade.EXCELLENT
        elif overall >= 60:
            grade = QualityGrade.GOOD
        elif overall >= 40:
            grade = QualityGrade.FAIR
        else:
            grade = QualityGrade.NEEDS_IMPROVEMENT
        
        suggestions = self._generate_suggestions(text, readability, engagement, seo_score)
        
        metrics = {
            "word_count": len(text.split()),
            "sentence_count": self._count_sentences(text),
            "avg_sentence_length": self._avg_sentence_length(text),
            "avg_word_length": self._avg_word_length(text),
            "paragraph_count": self._count_paragraphs(text),
            "has_cta": bool(re.search(r'\b(click|sign up|get|download|learn more|contact|buy)\b', text.lower())),
            "has_numbers": bool(re.search(r'\d+', text)),
        }
        
        return QualityScore(
            grade=grade,
            readability=readability,
            engagement=engagement,
            seo_score=seo_score,
            overall=overall,
            suggestions=suggestions,
            metrics=metrics,
        )
    
    def _readability_score(self, text: str) -> float:
        """Calculate Flesch-Kincaid readability score"""
        words = text.split()
        sentences = self._count_sentences(text)
        
        if not words or not sentences:
            return 0.0
        
        avg_sentence_length = len(words) / sentences
        avg_syllables_per_word = self._count_syllables(text) / len(words)
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return min(100, max(0, score))
    
    def _engagement_score(self, text: str) -> float:
        """Score engagement factors"""
        score = 50.0
        
        words = text.split()
        text_lower = text.lower()
        
        if re.search(r'\?|!', text):
            score += 10
        
        if len(words) > 50 and len(words) < 1500:
            score += 10
        
        engagement_words = ['you', 'your', 'actually', 'really', 'literally', 'imagine', 'think']
        engagement_count = sum(1 for w in engagement_words if w in text_lower)
        score += min(15, engagement_count * 3)
        
        if re.search(r'\d+', text):
            score += 10
        
        personal_pronouns = ['i', 'we', 'they', 'he', 'she']
        if any(p in text_lower.split() for p in personal_pronouns):
            score += 5
        
        return min(100, max(0, score))
    
    def _seo_score(self, text: str) -> float:
        """Score SEO factors"""
        score = 50.0
        text_lower = text.lower()
        words = text.split()
        
        if len(words) < 50:
            return 20.0
        
        if len(words) > 300:
            score += 15
        
        has_subheadings = bool(re.search(r'^#{1,3}\s', text, re.MULTILINE))
        if has_subheadings:
            score += 15
        
        keyword_density = self._keyword_density(text, self._extract_main_keyword(text))
        if 0.01 <= keyword_density <= 0.03:
            score += 20
        
        if re.search(r'\b(summary|conclusion|final|finally)\b', text_lower):
            score += 10
        
        return min(100, max(0, score))
    
    def _keyword_density(self, text: str, keyword: str) -> float:
        """Calculate keyword density"""
        if not keyword:
            return 0.0
        words = text.lower().split()
        if not words:
            return 0.0
        return words.count(keyword.lower()) / len(words)
    
    def _extract_main_keyword(self, text: str) -> str:
        """Extract main keyword from text (simplified)"""
        words = text.split()
        if len(words) > 3:
            return ' '.join(words[:2])
        return words[0] if words else ""
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        return len(re.findall(r'[.!?]+', text)) or 1
    
    def _count_syllables(self, text: str) -> int:
        """Estimate syllable count"""
        words = text.lower().split()
        count = 0
        for word in words:
            vowels = "aeiouy"
            word = re.sub(r'[^a-z]', '', word)
            if not word:
                continue
            count += max(1, sum(1 for i in range(len(word)) if word[i] in vowels and (i == 0 or word[i-1] not in vowels)))
        return count
    
    def _avg_sentence_length(self, text: str) -> float:
        """Average sentence length in words"""
        sentences = self._count_sentences(text)
        words = len(text.split())
        return words / sentences if sentences else 0
    
    def _avg_word_length(self, text: str) -> float:
        """Average word length in characters"""
        words = text.split()
        if not words:
            return 0.0
        return sum(len(w) for w in words) / len(words)
    
    def _count_paragraphs(self, text: str) -> int:
        """Count paragraphs"""
        return len([p for p in text.split('\n\n') if p.strip()])
    
    def _generate_suggestions(
        self,
        text: str,
        readability: float,
        engagement: float,
        seo_score: float,
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if readability < 60:
            suggestions.append("Simplify sentences - aim for 15-20 words average")
            suggestions.append("Use shorter, common words where possible")
        
        if engagement < 50:
            suggestions.append("Add more engaging hooks at the start")
            suggestions.append("Include specific numbers and data")
            suggestions.append("Use second-person perspective ('you')")
        
        if seo_score < 50 and len(text.split()) > 200:
            suggestions.append("Add subheadings (## Heading) for structure")
            suggestions.append("Include a clear conclusion/summary section")
            suggestions.append("Consider adding a call-to-action")
        
        if self._count_sentences(text) < 3:
            suggestions.append("Content is very short - consider adding more detail")
        
        if not suggestions:
            suggestions.append("Great work! Your content looks solid.")
        
        return suggestions
    
    def format_report(self, score: QualityScore) -> str:
        """Format score as human-readable report"""
        grade_emoji = {
            QualityGrade.EXCELLENT: "🌟",
            QualityGrade.GOOD: "✓",
            QualityGrade.FAIR: "⚠",
            QualityGrade.NEEDS_IMPROVEMENT: "✗",
        }
        
        report = f"""
{grade_emoji[score.grade]} Quality Grade: {score.grade.value.upper()}

📊 Overall Score: {score.overall:.0f}/100

Breakdown:
  • Readability: {score.readability:.0f}/100
  • Engagement: {score.engagement:.0f}/100
  • SEO: {score.seo_score:.0f}/100

📝 Metrics:
  • Words: {score.metrics['word_count']}
  • Sentences: {score.metrics['sentence_count']}
  • Avg Sentence: {score.metrics['avg_sentence_length']:.1f} words
  • Paragraphs: {score.metrics['paragraph_count']}

💡 Suggestions:
"""
        for suggestion in score.suggestions:
            report += f"  • {suggestion}\n"
        
        return report


def analyze_quality(text: str, check_seo: bool = False) -> QualityScore:
    """Quick quality analysis helper"""
    scorer = QualityScorer()
    return scorer.score(text, check_seo)
