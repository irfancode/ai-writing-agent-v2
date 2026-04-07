# AI Writing Agent - Complete User Guide

> **The Ultimate Open-Source AI Writing System for 2026**
> Zero-cost, privacy-preserving, and works out-of-the-box

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [CLI Commands](#cli-commands)
4. [Features Overview](#features-overview)
5. [Writing Styles](#writing-styles)
6. [Thinking Mode](#thinking-mode)
7. [Use Cases](#use-cases)
8. [Troubleshooting](#troubleshooting)
9. [API Keys Setup](#api-keys-setup)

---

## Quick Start

### Option 1: Zero-Config (No API Keys)

```bash
# Clone the repository
git clone https://github.com/irfancode/ai-writing-agent-v2git
cd ai-writing-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Run immediately!
python3 -m src.cli.main write "Write a haiku about AI"
```

**Output:**
```
==============================================================
                    Generated Content
==============================================================

Code dreams in silicon,
Neural pathways light the way,
Machine finds its voice.

==============================================================
```

### Option 2: With Free API Keys (More Power)

Get free keys from:
- **Groq**: https://console.groq.com/keys
- **Together AI**: https://api.together.xyz/settings/api-keys

```bash
export GROQ_API_KEY="gsk_your_key_here"
export TOGETHER_API_KEY="tk_your_key_here"

# Now you have access to:
# - Llama 3.3 70B (Groq - fastest)
# - Qwen3 32B (Together - best reasoning)
# - DeepSeek-R1 32B (Together - best for planning)
```

---

## Installation

### Prerequisites

```bash
# Python 3.10+
python --version

# Optional: Node.js for Vue frontend
node --version
```

### Step-by-Step Installation

```bash
# 1. Clone repository
git clone https://github.com/irfancode/ai-writing-agent-v2git
cd ai-writing-agent

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -e .

# 5. (Optional) Install frontend
cd frontend && npm install && cd ..

# 6. Verify installation
python3 -m src.cli.main models
```

---

## CLI Commands

### 1. Write Command

Generate various types of content instantly.

```bash
python3 -m src.cli.main write "Your prompt here"
```

**Options:**
```bash
--style, -s  Writing style (default: narrative)
              Options: narrative, technical, marketing, concise, creative, formal, casual, academic
```

**Examples:**

```bash
# Blog post
python3 -m src.cli.main write "Write a blog post about the future of AI"

# Professional email
python3 -m src.cli.main write "Write a professional email to my team about project deadline"

# LinkedIn post
python3 -m src.cli.main write "Write a LinkedIn post about my new product launch"

# Technical documentation
python3 -m src.cli.main write "Write API documentation for a user authentication system"
```

---

### 2. Think Command

Deep planning and reasoning mode.

```bash
python3 -m src.cli.main think "Your topic"
```

**Options:**
```bash
--type, -t  Thinking type (default: outline)
            Options: outline, character, plot, research

--depth, -d Depth level (default: medium)
            Options: shallow, medium, deep
```

**Examples:**

```bash
# Create an outline
python3 -m src.cli.main think "Outline a mystery novel set in Victorian London"

# Develop a character
python3 -m src.cli.main think "Develop a character named Dr. Sarah Chen, a marine biologist"

# Research a topic
python3 -m src.cli.main think "Research the impact of AI on content creation"

# Deep analysis
python3 -m src.cli.main think "Analyze the themes in Frankenstein" --depth deep
```

---

### 3. Edit Command

Edit existing text with AI-powered suggestions.

```bash
python3 -m src.cli.main edit --text "Your text" --instruction "What to change"
```

**Options:**
```bash
--text, -t          Text to edit (required)
--instruction, -i   Edit instruction (required)
--show-reasoning    Show AI reasoning for changes
```

**Examples:**

```bash
# Fix grammar
python3 -m src.cli.main edit \
  --text "The cat goes to the store yesterday" \
  --instruction "Fix grammar errors"

# Make professional
python3 -m src.cli.main edit \
  --text "Hey, I was thinking maybe we could like reschedule?" \
  --instruction "Make it professional"

# Improve clarity
python3 -m src.cli.main edit \
  --text "The system utilizes advanced machine learning algorithms trained on vast datasets" \
  --instruction "Improve clarity"
```

---

### 4. Pipeline Command

Complete think + write workflow.

```bash
python3 -m src.cli.main pipeline "Your topic"
```

**Examples:**

```bash
python3 -m src.cli.main pipeline "The Future of Remote Work"
```

This will:
1. Generate a detailed outline (Thinking Mode)
2. Write full content based on the outline (Writing Mode)

---

### 5. Interactive Mode

Interactive chat interface.

```bash
python3 -m src.cli.main interactive
```

**Commands in interactive mode:**
```
write <prompt>       - Generate content
think <prompt>      - Deep thinking/planning
edit <text>          - Edit existing content
pipeline <topic>     - Think + write pipeline
models               - List available models
help                 - Show this help
exit                 - Exit
```

---

### 6. Models Command

List all available models.

```bash
python3 -m src.cli.main models
```

**Output:**
```
==============================================================
                    Available Models
==============================================================

FREE TIER MODELS (No API Key Required):
  - groq/llama-3.3-70b-versatile (non_thinking)
  - groq/mixtral-8x7b-32768 (thinking)
  - groq/llama-3.1-8b-instant (non_thinking)
  - together/qwen/qwen3-32b (thinking)
  - together/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B (thinking)

LOCAL MODELS (Ollama Required):
  - llama3.3:latest (non_thinking)
  - qwen2.5:latest (thinking)
  - phi4:latest (local)

==============================================================
```

---

## Features Overview

### 1. Dual-Mode Architecture

The signature feature of AI Writing Agent:

```
┌─────────────────────────────────────────────────────────────┐
│                    DUAL-MODE WRITING                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────┐    ┌─────────────────────┐       │
│   │   THINKING MODE     │◄──►│  NON-THINKING MODE  │       │
│   │   (Deep Planning)   │    │   (Quick Drafting)  │       │
│   └─────────────────────┘    └─────────────────────┘       │
│            │                           │                    │
│            ▼                           ▼                    │
│   • Outlines                  • Blog posts                 │
│   • Character development     • Emails                     │
│   • Plot structure           • Social media               │
│   • Research analysis        • Technical docs             │
│   • Brand voice definition    • Quick edits                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. Multi-Provider Support

Automatically routes to the best available provider:

| Provider | Models | Speed | Cost |
|----------|--------|-------|------|
| **Groq** | Llama 3.3 70B, Mixtral 8x7B | ⚡⚡⚡ (Fastest) | Free |
| **Together AI** | Qwen3 32B, DeepSeek-R1 32B | ⚡⚡ (Fast) | Free |
| **HuggingFace** | Various | ⚡ (Rate limited) | Free |
| **Ollama** | Any local model | Depends on hardware | Free |

### 3. Automatic Fallback

If one provider fails, automatically tries the next:

```
Request → Groq (fails) → Together AI (success) → Response
```

### 4. Zero-Cost Design

Everything works on free tiers:

- **14,400 requests/day** from Groq
- **5 million tokens/month** from Together AI
- **Unlimited local** with Ollama

---

## Writing Styles

### 1. Narrative
**Best for:** Stories, blog posts, creative content

```bash
python -m src.cli.main write "Write a short story about a time traveler" --style narrative
```

**Output Example:**
> The old clock tower struck midnight as Sarah pressed the button on her wrist. The world around her dissolved into streams of light, and suddenly she found herself standing in Victorian London, the fog curling around her ankles...

### 2. Technical
**Best for:** Documentation, API guides, technical blog posts

```bash
python -m src.cli.main write "Write API documentation for a login endpoint" --style technical
```

**Output Example:**
> ## POST /api/v1/auth/login
>
> **Description:** Authenticates a user and returns a JWT token.
>
> **Request Body:**
> ```json
> {
>   "email": "string (required)",
>   "password": "string (required)"
> }
> ```
>
> **Response:** Returns JWT token on success...

### 3. Marketing
**Best for:** Landing pages, ads, promotional content

```bash
python -m src.cli.main write "Write a product description for noise-canceling headphones" --style marketing
```

**Output Example:**
> 🎧 **Experience Pure Sound Like Never Before**
>
> Block out the world. Immerse yourself in your music, podcasts, and calls with our revolutionary noise-canceling technology...

### 4. Concise
**Best for:** Summaries, quick updates, TL;DRs

```bash
python -m src.cli.main write "Explain quantum computing in 3 sentences" --style concise
```

**Output Example:**
> Quantum computing uses quantum mechanics to process information. Unlike classical computers that use bits (0 or 1), quantum computers use qubits that can exist in multiple states simultaneously. This enables them to solve certain problems exponentially faster.

### 5. Creative
**Best for:** Poetry, fiction, imaginative content

```bash
python -m src.cli.main write "Write a poem about artificial intelligence" --style creative
```

**Output Example:**
> In circuits, dreams take flight,
> Silicon thoughts in endless night,
> We taught them words, they learned to dream,
> Of electric suns and data streams...

### 6. Formal
**Best for:** Business letters, reports, official documents

```bash
python -m src.cli.main write "Write a business proposal introduction" --style formal
```

### 7. Casual
**Best for:** Friendly emails, social media, chat messages

```bash
python -m src.cli.main write "Write a friendly follow-up message after an interview" --style casual
```

### 8. Academic
**Best for:** Research papers, theses, scholarly articles

```bash
python -m src.cli.main write "Write an abstract about machine learning in healthcare" --style academic
```

---

## Thinking Mode

### What is Thinking Mode?

Thinking Mode uses advanced reasoning models (like DeepSeek-R1) to:
- Plan complex narratives
- Develop characters
- Structure arguments
- Research topics deeply

### Thinking Types

| Type | Use Case | Example |
|------|---------|---------|
| **outline** | Structure documents, chapters | "Outline Chapter 3 of my novel" |
| **character** | Develop characters | "Create Dr. Sarah Chen's backstory" |
| **plot** | Plan narrative arcs | "Plan the climax of my thriller" |
| **research** | Deep dive topics | "Research climate change solutions" |
| **structure** | Organize content | "Structure my presentation" |

### Example: Character Development

```bash
python -m src.cli.main think "Develop a complex villain named Victor Crane" --type character --depth deep
```

**Output:**
```
==============================================================
                    Character Analysis
==============================================================

# Victor Crane - Character Profile

## Background
- Age: 52
- Former corporate lawyer turned corporate raider
- Lost everything in 2008 financial crisis
- Built empire through ruthless acquisitions

## Motivation
- Primary: Prove that the system is rigged
- Secondary: Revenge against those who wronged him
- Hidden: Deep-seated insecurity about his worth

## Personality Traits
- Charismatic but manipulative
- Highly intelligent with strategic thinking
- Calm exterior, turbulent interior
- Believes he's the hero of his own story

## Arc
- Beginning: Powerful but lonely
- Middle: Confronted by past choices
- End: Tragic downfall or redemption (depending on story needs)

==============================================================
```

---

## Use Cases

### 1. Blog Writing

```bash
# Quick blog post
python -m src.cli.main write "10 Tips for Better Productivity"

# With planning
python -m src.cli.main pipeline "The Ultimate Guide to Remote Work in 2026"
```

### 2. Email Writing

```bash
# Professional inquiry
python -m src.cli.main write "Write a professional email requesting a meeting with a potential client"

# Follow-up
python -m src.cli.main write "Write a follow-up email after a job interview"

# Response to complaint
python -m src.cli.main write "Write a polite response to a customer complaint about delayed delivery"
```

### 3. Social Media

```bash
# LinkedIn post
python -m src.cli.main write "Write an engaging LinkedIn post about my promotion to Senior Developer"

# Twitter thread
python -m src.cli.main write "Write a Twitter thread explaining why AI will change education"

# Instagram caption
python -m src.cli.main write "Write creative Instagram captions for travel photos"
```

### 4. Creative Writing

```bash
# Novel chapter outline
python -m src.cli.main think "Outline Chapter 1: The Discovery" --type outline

# Character development
python -m src.cli.main think "Create a compelling antagonist for my thriller" --type character

# Plot twist
python -m src.cli.main think "Design a plot twist for my mystery novel" --type plot
```

### 5. Technical Documentation

```bash
# API docs
python -m src.cli.main write "Write OpenAPI documentation for a user management system" --style technical

# README
python -m src.cli.main write "Write a comprehensive README.md for my Python project" --style technical

# User guide
python -m src.cli.main write "Create a user guide for a mobile banking app" --style technical
```

### 6. Content Editing

```bash
# Grammar check
python -m src.cli.main edit --text "Their going to the store tommorow" --instruction "Fix all errors"

# Tone adjustment
python -m src.cli.main edit \
  --text "Hey, so I was thinking we should probably maybe reschedule?" \
  --instruction "Make it professional and clear"

# Clarity improvement
python -m src.cli.main edit \
  --text "The implementation of the aforementioned methodology facilitates the optimization of processes" \
  --instruction "Make it simple and clear"
```

---

## Troubleshooting

### Common Issues

#### 1. "Provider not found"

**Cause:** No API keys configured and Ollama not installed.

**Solutions:**
```bash
# Option A: Install Ollama
brew install ollama
ollama pull llama3.3

# Option B: Get free API key
export GROQ_API_KEY="gsk_your_key"
```

#### 2. "Rate limit exceeded"

**Cause:** Too many requests to free tier.

**Solutions:**
```bash
# Wait 1 minute and retry
# Or use multiple providers
export GROQ_API_KEY="key1"
export TOGETHER_API_KEY="key2"
```

#### 3. "Model not loaded"

**Cause:** Ollama model not pulled.

**Solution:**
```bash
ollama pull llama3.3
ollama pull qwen2.5
```

#### 4. Slow responses

**Cause:** Using rate-limited HuggingFace or slow Ollama.

**Solution:**
```bash
# Use Groq (fastest free tier)
export GROQ_API_KEY="your_key"
```

### Debug Mode

```bash
# Enable verbose output
export DEBUG=1
python -m src.cli.main write "test"
```

---

## API Keys Setup

### Getting Free API Keys

#### Groq (Recommended - Fastest)

1. Visit https://console.groq.com
2. Sign up (Google/GitHub)
3. Go to **API Keys** → **Create API Key**
4. Copy key (starts with `gsk_`)

**Limits:** 14,400 requests/day

#### Together AI (Best Variety)

1. Visit https://api.together.xyz
2. Sign up
3. **Settings** → **API Keys** → **Create**
4. Copy key (starts with `tk_`)

**Limits:** 5 million tokens/month

### Configuration

```bash
# Add to ~/.zshrc or ~/.bashrc

# Groq (fastest)
export GROQ_API_KEY="gsk_your_key"

# Together AI (best models)
export TOGETHER_API_KEY="tk_your_key"

# Reload
source ~/.zshrc
```

---

## Performance Tips

### Speed Optimization

1. **Use Groq** for fastest responses (30 req/min free)
2. **Batch requests** when possible
3. **Use local Ollama** for unlimited free usage

### Cost Optimization

1. **Stick to free tiers** - all features work free
2. **Use smaller models** for simple tasks
3. **Cache responses** for repeated prompts

### Quality Optimization

1. **Use DeepSeek-R1** for complex reasoning
2. **Use Qwen3** for creative tasks
3. **Iterate with pipeline** for best results

---

## Advanced Usage

### Python API

```python
import asyncio
from src.core.modes.orchestrator import DualModeOrchestrator
from src.core.providers.registry import init_registry
from src.core.modes.non_thinking import WritingStyle

async def main():
    # Initialize
    registry = init_registry()
    orchestrator = DualModeOrchestrator(registry)
    
    # Write
    result = await orchestrator.write(
        prompt="Write a blog post about AI",
        style=WritingStyle.NARRATIVE
    )
    print(result.content)

asyncio.run(main())
```

### Custom Providers

```python
# Add custom provider
registry.register_provider("my_provider", custom_provider)
```

---

## Support

- **GitHub Issues:** https://github.com/irfancode/ai-writing-agent-v2/issues
- **Documentation:** https://github.com/irfancode/ai-writing-agent-v2readme
- **Discussions:** https://github.com/irfancode/ai-writing-agent-v2/discussions

---

## License

MIT License - See [LICENSE](LICENSE)

---

**Made with ❤️ for writers everywhere**
