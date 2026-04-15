"""Template Library - Pre-built writing templates"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum


class TemplateCategory(Enum):
    MARKETING = "marketing"
    FICTION = "fiction"
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    SOCIAL = "social"
    BUSINESS = "business"
    EMAIL = "email"


@dataclass
class Template:
    """A writing template"""
    id: str
    name: str
    description: str
    category: TemplateCategory
    prompt_template: str
    variables: List[str]
    style: str
    пример: Optional[str] = None


class TemplateLibrary:
    """Library of pre-built templates"""
    
    TEMPLATES: List[Template] = [
        Template(
            id="blog-outline",
            name="Blog Post Outline",
            description="Generate a detailed blog post outline",
            category=TemplateCategory.MARKETING,
            prompt_template="""Create a detailed outline for a blog post about {topic}.

Include:
- Attention-grabbing introduction points
- {num_sections} main sections with key points
- Supporting arguments for each section
- Transition ideas between sections
- Compelling conclusion

Target audience: {audience}
Tone: {tone}""",
            variables=["topic", "num_sections", "audience", "tone"],
            style="narrative",
            пример="Topic: AI in Healthcare, Sections: 5, Audience: Medical professionals",
        ),
        
        Template(
            id="product-launch",
            name="Product Launch Email",
            description="Announce a new product to your audience",
            category=TemplateCategory.EMAIL,
            prompt_template="""Write an exciting product launch email for {product_name}.

Include:
- Subject line (compelling)
- Opening hook (exciting news)
- Product description (key benefits)
- Social proof or launch details
- Clear call-to-action

Product: {product_description}
Launch date: {launch_date}
CTA: {cta}""",
            variables=["product_name", "product_description", "launch_date", "cta"],
            style="marketing",
        ),
        
        Template(
            id="linkedin-story",
            name="LinkedIn Story Post",
            description="Share a professional story on LinkedIn",
            category=TemplateCategory.SOCIAL,
            prompt_template="""Write a LinkedIn post that tells a story about {topic}.

Structure:
- Hook (attention-grabbing first line)
- The situation/challenge
- What happened/learned
- The outcome/result
- Question or CTA for engagement

Topic: {topic}
Tone: {tone}
Length: {length}""",
            variables=["topic", "tone", "length"],
            style="narrative",
        ),
        
        Template(
            id="seo-article",
            name="SEO Article",
            description="Write an SEO-optimized article",
            category=TemplateCategory.TECHNICAL,
            prompt_template="""Write an SEO-optimized article about {keyword}.

Requirements:
- Include keyword in title, first paragraph, and subheadings
- {word_count} words minimum
- Use H2 and H3 subheadings
- Include bullet points for key information
- End with actionable conclusion

Primary keyword: {keyword}
Secondary keywords: {secondary_keywords}
Target audience: {audience}""",
            variables=["keyword", "secondary_keywords", "word_count", "audience"],
            style="technical",
        ),
        
        Template(
            id="case-study",
            name="Case Study",
            description="Write a customer success story",
            category=TemplateCategory.MARKETING,
            prompt_template="""Write a case study for {client_name}.

Structure:
- Executive summary
- The challenge they faced
- The solution provided
- Results (use specific numbers)
- Client testimonial quote
- Call to action

Client: {client_name}
Industry: {industry}
Results: {results}""",
            variables=["client_name", "industry", "results"],
            style="formal",
        ),
        
        Template(
            id="character-profile",
            name="Character Profile",
            description="Develop a fictional character",
            category=TemplateCategory.FICTION,
            prompt_template="""Create a detailed character profile for {character_name}.

Include:
- Physical description
- Background story
- Personality traits (strengths and flaws)
- Motivations and goals
- Relationships with other characters
- Character arc potential
- Speech patterns/voice

Character: {character_name}
Role: {role}
Genre: {genre}""",
            variables=["character_name", "role", "genre"],
            style="creative",
        ),
        
        Template(
            id="video-script",
            name="Video Script",
            description="Write a script for video content",
            category=TemplateCategory.TECHNICAL,
            prompt_template="""Write a video script for {video_title}.

Duration: {duration}
Type: {video_type}

Include:
- Attention-grabbing intro ({intro_length})
- Main content points ({num_points} key points)
- Visual suggestions
- Transitions
- Strong closing with CTA

Topic: {topic}
Tone: {tone}""",
            variables=["video_title", "duration", "video_type", "topic", "tone", "intro_length", "num_points"],
            style="concise",
        ),
        
        Template(
            id="cold-email",
            name="Cold Outreach Email",
            description="Write a cold email for outreach",
            category=TemplateCategory.EMAIL,
            prompt_template="""Write a cold outreach email to {recipient_role}.

Goal: {goal}
Recipient: {recipient_role} at {company_type}

Structure:
- Personalized opening (reference their work)
- Value proposition
- Specific reason to connect
- Low-friction CTA

Tone: {tone}
Research: {research}""",
            variables=["recipient_role", "company_type", "goal", "tone", "research"],
            style="concise",
        ),
        
        Template(
            id="twitter-thread",
            name="Twitter Thread",
            description="Create an engaging Twitter thread",
            category=TemplateCategory.SOCIAL,
            prompt_template="""Create a Twitter thread about {topic}.

Format:
- Hook tweet (attention grabber)
- {num_tweets} value tweets
- Summary tweet with CTA

Content summary: {summary}
Tone: {tone}
Include: {include}""",
            variables=["topic", "num_tweets", "summary", "tone", "include"],
            style="concise",
        ),
        
        Template(
            id="faq-section",
            name="FAQ Section",
            description="Generate FAQ content",
            category=TemplateCategory.TECHNICAL,
            prompt_template="""Write FAQ content for {product_service}.

Generate {num_questions} frequently asked questions with answers.

Questions should cover:
- Pricing/plans
- How it works
- Common objections
- Support/contact

Product: {product_service}
Audience: {audience}""",
            variables=["product_service", "num_questions", "audience"],
            style="technical",
        ),
    ]
    
    @classmethod
    def get_by_category(cls, category: TemplateCategory) -> List[Template]:
        return [t for t in cls.TEMPLATES if t.category == category]
    
    @classmethod
    def get_by_id(cls, template_id: str) -> Optional[Template]:
        for t in cls.TEMPLATES:
            if t.id == template_id:
                return t
        return None
    
    @classmethod
    def search(cls, query: str) -> List[Template]:
        query_lower = query.lower()
        return [
            t for t in cls.TEMPLATES
            if query_lower in t.name.lower() or query_lower in t.description.lower()
        ]
    
    @classmethod
    def apply_template(cls, template_id: str, variables: Dict[str, str]) -> str:
        template = cls.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        prompt = template.prompt_template
        for var in template.variables:
            value = variables.get(var, f"[{var}]")
            prompt = prompt.replace(f"{{{var}}}", value)
        
        return prompt
    
    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "variables": t.variables,
                "пример": t.пример,
            }
            for t in cls.TEMPLATES
        ]
    
    @classmethod
    def list_categories(cls) -> List[str]:
        return [c.value for c in TemplateCategory]


def get_template(template_id: str, **kwargs) -> str:
    """Quick helper to apply a template"""
    return TemplateLibrary.apply_template(template_id, kwargs)
