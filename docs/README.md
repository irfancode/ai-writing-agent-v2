# AI Writing Agent Documentation

> **Your Complete Guide to the Ultimate Open-Source AI Writing System**

🌐 **Live Website:** https://irfancode.github.io

---

## Quick Links

| Document | Description |
|----------|-------------|
| [🚀 Quick Start](USER_GUIDE.md#quick-start) | Get running in 5 minutes |
| [📖 User Guide](USER_GUIDE.md) | Complete command reference |
| [✨ Feature Showcase](FEATURE_SHOWCASE.md) | Visual examples of all features |
| [📝 Blog Post](BLOG_POST.md) | Why AI Writing Agent changes everything |
| [🔑 API Keys Setup](API_KEYS.md) | Free API configuration guide |
| [🧪 Test Report](TEST_REPORT.md) | 33 tests, 100% passing |
| [🐛 Troubleshooting](USER_GUIDE.md#troubleshooting) | Common issues and solutions |

---

## What is AI Writing Agent?

AI Writing Agent is an **open-source, zero-cost** AI writing system that combines:

- 🧠 **Thinking Mode** - Deep planning and reasoning
- ⚡ **Non-Thinking Mode** - Instant content generation
- 💰 **Free by Design** - Works on free-tier APIs
- 🔒 **Privacy First** - Run locally with Ollama
- 🔄 **Multi-Provider** - Groq, Together AI, HuggingFace, Ollama
- 📊 **8 Writing Styles** - Narrative, Technical, Marketing, and more

---

## Why AI Writing Agent?

### vs. Paid Alternatives

| Feature | AI Writing Agent | Jasper ($49/mo) | Copy.ai ($49/mo) |
|---------|-----------------|-----------------|------------------|
| **Cost** | $0 | $49/mo | $49/mo |
| **Open Source** | ✅ | ❌ | ❌ |
| **Thinking Mode** | ✅ | ❌ | ❌ |
| **Free Tier** | Unlimited | Limited | Limited |
| **Local Models** | ✅ | ❌ | ❌ |
| **Multi-Provider** | ✅ | ❌ | ❌ |

---

## Getting Started

### Option 1: Zero-Config (No API Keys)

```bash
git clone https://github.com/irfancode/ai-writing-agent-v2git
cd ai-writing-agent
python3 -m venv venv && source venv/bin/activate
pip install -e .
python3 -m src.cli.main write "Write a haiku about AI"
```

### Option 2: With Free API Keys (Recommended)

Get free keys:
- **Groq**: https://console.groq.com/keys (14,400 req/day free)
- **Together AI**: https://api.together.xyz (5M tokens/month free)

```bash
export GROQ_API_KEY="your_key"
python3 -m src.cli.main write "Hello world"
```

---

## Feature Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI WRITING AGENT                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   WRITE    │  │   THINK     │  │   EDIT      │        │
│  │  Commands  │  │   Commands  │  │  Commands   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────┐            │
│  │            WRITING STYLES                    │            │
│  │  Narrative | Technical | Marketing | More  │            │
│  └─────────────────────────────────────────────┘            │
│                                                             │
│  ┌─────────────────────────────────────────────┐            │
│  │            FREE PROVIDERS                    │            │
│  │  Groq | Together AI | HuggingFace | Ollama │            │
│  └─────────────────────────────────────────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Documentation by Use Case

### For Bloggers

- [User Guide - Writing Styles](USER_GUIDE.md#writing-styles)
- [Feature Showcase - Blog Examples](FEATURE_SHOWCASE.md#writing-examples)
- [Blog Post - Why It Matters](BLOG_POST.md)

### For Marketers

- [User Guide - Marketing Style](USER_GUIDE.md#writing-styles)
- [Feature Showcase - Marketing](FEATURE_SHOWCASE.md#writing-styles-comparison)
- [Blog Post - Marketing Workflow](BLOG_POST.md)

### For Authors

- [User Guide - Thinking Mode](USER_GUIDE.md#thinking-mode)
- [Feature Showcase - Character Development](FEATURE_SHOWCASE.md#thinking-mode-examples)
- [Feature Showcase - Creative Writing](FEATURE_SHOWCASE.md#writing-styles-comparison)

### For Developers

- [User Guide - Technical Style](USER_GUIDE.md#writing-styles)
- [Feature Showcase - API Documentation](FEATURE_SHOWCASE.md#writing-examples)
- [API Keys Setup](API_KEYS.md)

---

## Test Results

All features tested and working:

| Category | Tests | Status |
|----------|-------|--------|
| Registry & Models | 4 | ✅ |
| Write Command | 5 | ✅ |
| Think Command | 3 | ✅ |
| Edit Command | 3 | ✅ |
| Writing Styles | 8 | ✅ |
| Pipeline | 1 | ✅ |
| Memory | 3 | ✅ |
| Sessions | 2 | ✅ |
| Model Selection | 3 | ✅ |
| Health Checks | 1 | ✅ |
| **TOTAL** | **33** | **✅ 100%** |

[See Full Test Report](TEST_REPORT.md)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI / API                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Dual-Mode Orchestrator                   │  │
│  │  ┌─────────────────┐    ┌─────────────────┐            │  │
│  │  │  Thinking Mode  │◄──►│Non-Thinking Mode│            │  │
│  │  │  (DeepSeek-R1)  │    │ (Llama 3.3 70B) │            │  │
│  │  └─────────────────┘    └─────────────────┘            │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                  Model Registry                      │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │  │
│  │  │   Groq   │ │ Together │ │  Ollama  │          │  │
│  │  └──────────┘ └──────────┘ └──────────┘          │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](../CONTRIBUTING.md).

- ⭐ Star the repo
- 🐛 Report bugs
- 💡 Suggest features  
- 📝 Improve docs
- 🔧 Submit PRs

---

## License

MIT License - See [LICENSE](../LICENSE)

---

## Support

- 📋 [GitHub Issues](https://github.com/irfancode/ai-writing-agent-v2/issues)
- 💬 [Discussions](https://github.com/irfancode/ai-writing-agent-v2/discussions)
- 📖 [Wiki](https://github.com/irfancode/ai-writing-agent-v2/wiki)

---

<div align="center">

**Made with ❤️ for writers everywhere**

[Star on GitHub](https://github.com/irfancode/ai-writing-agent-v2 | [Get Started](USER_GUIDE.md#quick-start)

</div>
