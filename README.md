# AI Writing Agent - Enterprise Open-Source Edition

<div align="center">

![AI Writing Agent](docs/assets/banner.png)

**The Ultimate Open-Source AI Writing System for 2026**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-42b883.svg)](https://vuejs.org)
[![vLLM](https://img.shields.io/badge/vLLM-Optimized-green.svg)](https://docs.vllm.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/irfancode/ai-writing-agent?style=social)](https://github.com/irfancode/ai-writing-agent-v2
[![Pages](https://img.shields.io/badge/GitHub%20Pages-Live-blue.svg)](https://irfancode.github.io)

**Dual-Mode | Multi-Agent | High-Context | Open-Source | Zero-Cost**

</div>

---

## 🎥 See it in Action
![Setup Showcase](demo.gif)

---

## 🌐 Live Demo

**Visit our website:** https://irfancode.github.io

---

## 🎯 Overview

AI Writing Agent is a **production-grade, open-source writing system** that combines the best of 2026's open-source AI models with enterprise features. **Works out-of-the-box with zero API keys** using Ollama local models or free cloud tiers:

| Feature | Description |
|---------|-------------|
| 🧠 **Dual-Mode Writing** | Switch between "Thinking Mode" (planning/structure) and "Non-Thinking Mode" (quick drafting) |
| 🔄 **Model Agnostic** | Use any model: Qwen3, DeepSeek-R1, Gemma, Phi-4, Llama, Mistral |
| 💰 **Zero-Cost Mode** | Works without API keys using Ollama (local) or free cloud tiers |
| 📚 **High-Context Memory** | 128K-256K token context for long documents |
| ✏️ **Real-Time Editing** | Inline suggestions with reasoning traces |
| 🤖 **Multi-Agent** | Drafting + Editing sub-agents collaborate |
| 🔄 **Automatic Fallback** | Switches providers automatically if one fails |

---

## 🔥 Best Use Cases

| Persona | Why AI Writing Agent is a Hit | Key Feature Used |
|---------|-------------------------------|------------------|
| **🖋️ The Fiction Novelist** | Keeps track of sprawling lore without AI hallucinating off-book facts. | **Local RAG System** + `think --type character` |
| **📈 The Technical Blogger** | Blasts out technical drafts fast and uses Polish agent to meet strict SEO constraints. | **Multi-Agent Collaboration** (Draft -> Polish) |
| **🏢 Enterprise Content Team** | Scales content generation at exactly zero cost, keeping internal docs perfectly private. | **Ollama Offline Mode** (Model Agnostic Backend) |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [🚀 Quick Start](docs/USER_GUIDE.md#quick-start) | Get running in 5 minutes |
| [📖 Complete User Guide](docs/USER_GUIDE.md) | All commands and features |
| [✨ Feature Showcase](docs/FEATURE_SHOWCASE.md) | Visual examples with outputs |
| [📝 Marketing Blog](docs/BLOG_POST.md) | Why AI Writing Agent changes everything |
| [🔑 API Keys Setup](docs/API_KEYS.md) | Free API configuration |
| [🧪 Test Report](docs/TEST_REPORT.md) | 33 tests, 100% passing |

---

## 🏆 2026 Best Open-Source Models

Based on latest benchmarks, we support these models optimally:

| Model | Provider | Best For | Speed | Cost |
|-------|----------|----------|-------|------|
| **Llama 3.3 70B** | Groq | General Writing | ⚡⚡⚡ | Free |
| **Mixtral 8x7B** | Groq | Thinking/Planning | ⚡⚡⚡ | Free |
| **Qwen3 32B** | Together AI | Creative | ⚡⚡ | Free |
| **DeepSeek-R1 32B** | Together AI | Reasoning | ⚡⚡ | Free |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI Writing Agent System                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │   Vue.js    │  │   CLI       │  │   API       │                │
│  │   Frontend  │  │   Interface  │  │   Server    │                │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                │
│         └────────────────┼────────────────┘                         │
│                          │                                          │
│  ┌───────────────────────▼────────────────────────────────────┐  │
│  │              Dual-Mode Orchestrator                           │  │
│  │  ┌─────────────────┐    ┌─────────────────┐                 │  │
│  │  │  Thinking Mode   │◄──►│ Non-Thinking Mode│                │  │
│  │  │  (Planning)     │    │ (Quick Drafting) │                │  │
│  │  └─────────────────┘    └─────────────────┘                 │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│  ┌───────────────────────▼────────────────────────────────────┐  │
│  │                    Multi-Agent System                         │  │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐               │  │
│  │  │  Draft   │──►│  Edit    │──►│  Polish  │               │  │
│  │  │  Agent   │    │  Agent   │    │  Agent   │               │  │
│  │  └──────────┘    └──────────┘    └──────────┘               │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│  ┌───────────────────────▼────────────────────────────────────┐  │
│  │              Model Provider Layer (Model Agnostic)             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │  │
│  │  │ HuggingFace│  │  Ollama  │  │  vLLM    │  │  OpenAI  │    │  │
│  │  │   API     │  │  Local   │  │  Server  │  │ 兼容     │    │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│  ┌───────────────────────▼────────────────────────────────────┐  │
│  │              High-Context Memory + RAG                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐           │  │
│  │  │  Document  │  │  Character │  │   Style    │           │  │
│  │  │  Memory    │  │   Bank     │  │   Guide    │           │  │
│  │  └────────────┘  └────────────┘  └────────────┘           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Zero-Cost Mode)

### Zero-Config (No API Keys Required)

```bash
# Install Ollama (truly free, runs locally)
brew install ollama  # macOS
curl -fsSL https://ollama.com/install.sh | sh  # Linux

# Pull a model
ollama pull llama3.3

# Clone and run
git clone https://github.com/irfancode/ai-writing-agent-v2git
cd ai-writing-agent
python -m venv venv && source venv/bin/activate
pip install -e .

# Run CLI (works immediately!)
python -m src.cli.main write "Write a haiku about AI"
```

### With Free Cloud APIs (More Power)

```bash
# Get free API keys:
# - Groq: https://console.groq.com/keys (free tier)
# - Together AI: https://api.together.xyz/settings/api-keys (free tier)
# - HuggingFace: https://huggingface.co/settings/tokens (free tier)

export GROQ_API_KEY="gsk_..."
export TOGETHER_API_KEY="..."

# Now you have access to:
# - Llama 3.3 70B (Groq - fastest free tier)
# - Qwen3 32B (Together AI)
# - DeepSeek-R1 32B (Together AI)
```

### Full Installation (Docker & UV)

We use modern dependency management (`pyproject.toml`) and offer instant dockerization.

```bash
git clone https://github.com/irfancode/ai-writing-agent-v2git
cd ai-writing-agent

# Option A: Universal "Zero-Config" Docker approach
# Starts the API Server on port 8000 and Vue frontend on port 5173
docker-compose up -d

# Option B: Manual uv installation
python -m venv venv
source venv/bin/activate
pip install uv
uv pip install -e .[dev]

# Run CLI Interactive Mode
python -m src.cli.main interactive
```

---

## 🎮 Dual-Mode Writing

The signature feature: seamlessly switch between two modes:

### Thinking Mode (Deep Planning)
- Outlining and structure
- Character development
- Plot point tracking
- Brand voice definition
- Uses reasoning-heavy models (DeepSeek-R1)

### Non-Thinking Mode (Fast Drafting)
- Quick content generation
- Editing and rephrasing
- Format conversion
- Uses speed-optimized models (MiMo-V2)

```python
# Example: Switching modes
agent = DualModeWriter()

# Thinking: Plan a novel chapter
plan = await agent.think(
    prompt="Outline Chapter 3: The Discovery",
    mode="creative_outline"
)

# Non-Thinking: Quick draft
draft = await agent.write(
    outline=plan,
    mode="fast_draft"
)
```

---

## 🤖 Multi-Agent Collaboration

Three specialized agents work together:

```python
# Draft Agent - Generates initial content
draft = await drafting_agent.write(
    topic="AI in Healthcare",
    style="technical_blog"
)

# Edit Agent - Improves structure and clarity
edited = await editing_agent.revise(
    content=draft,
    focus="clarity_coherence"
)

# Polish Agent - Final refinement
polished = await polish_agent.finalize(
    content=edited,
    constraints=["seo_optimized", "engaging"]
)
```

---

## 📚 Local RAG System

Load your documents for style-consistent writing:

```bash
# Add style guides and reference documents
python -m src.rag.ingest \
    --path ./my-style-guide.md \
    --type style_guide

python -m src.rag.ingest \
    --path ./character-bibles/ \
    --type character_bank
```

The agent will use these documents to maintain consistency.

---

## 🔍 Real-Time Editing

See the AI's reasoning as it edits:

```
Original:  "The cat go to the store."

Reasoning: "Subject-verb agreement error. 'cat' is singular, 'go' should be 'goes'. 
            Also, missing preposition. 'to' works but 'went to' implies past tense."

Suggestion: "The cat went to the store."
Confidence: 95%
```

---

## 🛠️ Configuration

### config/models.yaml

```yaml
providers:
  - name: huggingface
    type: huggingface
    api_key: ${HF_API_KEY}
    models:
      - id: Qwen/Qwen3-235B-A22B
        mode: thinking
        context: 128000
      - id: deepseek-ai/DeepSeek-R1
        mode: thinking
        context: 256000
      - id: MiniMax/MiniMax-M2
        mode: non_thinking
        context: 128000

  - name: ollama
    type: ollama
    base_url: http://localhost:11434
    models:
      - id: gemma3:12b
        mode: local
        context: 128000
      - id: phi4:latest
        mode: local
        context: 128000
```

### config/agents.yaml

```yaml
agents:
  drafting:
    provider: huggingface
    model: MiniMax-M2-Flash
    temperature: 0.8
    
  editing:
    provider: huggingface
    model: Qwen3-235B-A22B
    temperature: 0.5
    
  polish:
    provider: ollama
    model: phi4:latest
    temperature: 0.3
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Test specific module
pytest tests/test_modes.py -v
pytest tests/test_agents.py -v
pytest tests/test_rag.py -v

# Run integration tests
pytest tests/integration/ -v
```

---

## 📦 API Reference

### POST /api/v1/generate

```json
{
  "mode": "thinking",
  "prompt": "Outline a mystery novel set in Victorian London",
  "context": {
    "characters": ["Sherlock Holmes", "Dr. Watson"],
    "genre": "mystery"
  },
  "model": "deepseek-ai/DeepSeek-R1",
  "stream": false
}
```

### POST /api/v1/edit

```json
{
  "content": "The quick brown fox jumps over the lazy dog",
  "instruction": "Make this more engaging",
  "show_reasoning": true,
  "model": "Qwen3-235B-A22B"
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing`
5. Open PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co) - Model Hub
- [vLLM Team](https://docs.vllm.ai) - Serving Optimization
- [LangChain](https://langchain.dev) - Agent Framework
- [Qwen Team](https://qwenlm.ai) - Qwen3 Models
- [DeepSeek](https://deepseek.com) - DeepSeek-R1
- [Vue.js](https://vuejs.org) - Frontend Framework

---

<div align="center">

**Star us** ⭐ | **Fork us** 🍴 | **Join Discord** 💬

</div>
