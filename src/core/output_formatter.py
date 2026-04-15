"""Output Formatters - Predefined formats for different content types"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class OutputFormat(Enum):
    BLOG_POST = "blog_post"
    LINKEDIN_POST = "linkedin_post"
    EMAIL = "email"
    TWITTER_THREAD = "twitter_thread"
    LANDING_PAGE = "landing_page"
    PRODUCT_DESC = "product_desc"
    PRESS_RELEASE = "press_release"
    NEWSLETTER = "newsletter"
    CASE_STUDY = "case_study"
    HOW_TO_GUIDE = "how_to_guide"
    FAQ = "faq"
    RAW = "raw"


@dataclass
class FormatSpec:
    """Specification for an output format"""
    name: str
    description: str
    word_count: tuple[int, int]
    tone: str
    structure: List[str]
    elements: List[str]
    seo_keywords: Optional[bool] = None
    cta: Optional[bool] = None
    hooks: Optional[List[str]] = None


class OutputFormatter:
    """Formats AI output for specific content types"""
    
    FORMAT_SPECS: Dict[OutputFormat, FormatSpec] = {
        OutputFormat.BLOG_POST: FormatSpec(
            name="Blog Post",
            description="SEO-optimized article with intro, body, conclusion",
            word_count=(800, 2000),
            tone="professional yet engaging",
            structure=["Hook", "Introduction", "Main Points", "Conclusion", "CTA"],
            elements=["H1 Title", "Meta Description", "Subheadings", "Bullet Points"],
            seo_keywords=True,
            cta=True,
            hooks=["Surprising statistic", "Question", "Bold claim"],
        ),
        
        OutputFormat.LINKEDIN_POST: FormatSpec(
            name="LinkedIn Post",
            description="Professional post optimized for engagement",
            word_count=(500, 1500),
            tone="professional but personal",
            structure=["Hook", "Story/Insight", "Value", "Call to action"],
            elements=["Emoji usage", "Line breaks", "Hashtags"],
            seo_keywords=False,
            cta=True,
            hooks=["Personal story", "Result number", "Contrarian take"],
        ),
        
        OutputFormat.EMAIL: FormatSpec(
            name="Email",
            description="Professional email with clear purpose",
            word_count=(100, 500),
            tone="professional, friendly",
            structure=["Subject Line", "Greeting", "Body", "Closing"],
            elements=["Subject line", "Preview text", "Signature"],
            seo_keywords=False,
            cta=True,
        ),
        
        OutputFormat.TWITTER_THREAD: FormatSpec(
            name="Twitter Thread",
            description="Engaging thread of tweets",
            word_count=(1000, 3000),
            tone="conversational, punchy",
            structure=["Hook Tweet", "Value Tweets", "Summary Tweet"],
            elements=["Tweet formatting", "Hashtags", "Engagement hooks"],
            seo_keywords=False,
            cta=True,
        ),
        
        OutputFormat.LANDING_PAGE: FormatSpec(
            name="Landing Page",
            description="Conversion-focused landing page copy",
            word_count=(500, 1500),
            tone="persuasive",
            structure=["Headline", "Subheadline", "Problem", "Solution", "Social Proof", "CTA"],
            elements=["Hero section", "Features", "Benefits", "Testimonials", "FAQ"],
            seo_keywords=True,
            cta=True,
        ),
        
        OutputFormat.PRODUCT_DESC: FormatSpec(
            name="Product Description",
            description="E-commerce product description",
            word_count=(100, 300),
            tone="persuasive, descriptive",
            structure=["Title", "Overview", "Features", "Benefits"],
            elements=["Bullet points", "Keywords"],
            seo_keywords=True,
            cta=False,
        ),
        
        OutputFormat.PRESS_RELEASE: FormatSpec(
            name="Press Release",
            description="News-style announcement",
            word_count=(400, 800),
            tone="formal, authoritative",
            structure=["Headline", "Subheadline", "Dateline", "Body", "Quote", "Boilerplate"],
            elements=["Quote", "Contact info"],
            seo_keywords=False,
            cta=False,
        ),
        
        OutputFormat.NEWSLETTER: FormatSpec(
            name="Newsletter",
            description="Email newsletter content",
            word_count=(500, 1500),
            tone="friendly, informative",
            structure=["Subject", "Greeting", "Main Content", "P.S.", "Unsubscribe"],
            elements=["Sections", "Links", "Images placeholder"],
            seo_keywords=False,
            cta=True,
        ),
        
        OutputFormat.CASE_STUDY: FormatSpec(
            name="Case Study",
            description="Customer success story",
            word_count=(800, 2000),
            tone="professional, data-driven",
            structure=["Title", "Challenge", "Solution", "Results", "Quote", "CTA"],
            elements=["Metrics", "Testimonial", "Screenshots placeholder"],
            seo_keywords=True,
            cta=True,
        ),
        
        OutputFormat.HOW_TO_GUIDE: FormatSpec(
            name="How-To Guide",
            description="Step-by-step tutorial",
            word_count=(500, 2000),
            tone="clear, instructional",
            structure=["Overview", "Prerequisites", "Steps", "Conclusion"],
            elements=["Numbered steps", "Tips", "Warnings"],
            seo_keywords=True,
            cta=False,
        ),
        
        OutputFormat.FAQ: FormatSpec(
            name="FAQ",
            description="Frequently asked questions",
            word_count=(200, 800),
            tone="clear, concise",
            structure=["Question", "Answer"],
            elements=["Q&A pairs", "Keywords"],
            seo_keywords=True,
            cta=False,
        ),
        
        OutputFormat.RAW: FormatSpec(
            name="Raw",
            description="No formatting - plain text output",
            word_count=(0, 10000),
            tone="neutral",
            structure=[],
            elements=[],
            seo_keywords=False,
            cta=False,
        ),
    }
    
    @classmethod
    def get_spec(cls, format: OutputFormat) -> FormatSpec:
        return cls.FORMAT_SPECS.get(format, cls.FORMAT_SPECS[OutputFormat.RAW])
    
    @classmethod
    def format_prompt(
        cls,
        prompt: str,
        format: OutputFormat,
        style: Optional[str] = None,
    ) -> str:
        """Enhance prompt with format requirements"""
        spec = cls.get_spec(format)
        
        format_instructions = f"""
Write in the following format: {spec.name}
- Target word count: {spec.word_count[0]}-{spec.word_count[1]} words
- Tone: {spec.tone}
- Structure: {' → '.join(spec.structure)}

"""
        
        if spec.seo_keywords:
            format_instructions += "- Include relevant SEO keywords naturally\n"
        
        if spec.cta:
            format_instructions += "- Include a clear call-to-action at the end\n"
        
        if spec.hooks:
            format_instructions += f"- Start with one of these hooks: {', '.join(spec.hooks)}\n"
        
        format_instructions += f"\nOriginal request: {prompt}"
        
        return format_instructions
    
    @classmethod
    def list_formats(cls) -> List[Dict[str, str]]:
        """List all available formats"""
        return [
            {
                "id": f.value,
                "name": spec.name,
                "description": spec.description,
                "word_count": f"{spec.word_count[0]}-{spec.word_count[1]}",
            }
            for f, spec in cls.FORMAT_SPECS.items()
        ]


def format_prompt(prompt: str, format_name: str) -> str:
    """Quick format prompt helper"""
    try:
        format = OutputFormat(format_name)
        return OutputFormatter.format_prompt(prompt, format)
    except ValueError:
        return prompt
