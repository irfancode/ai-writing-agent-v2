# API Key Setup Guide

## Quick Setup (5 Minutes)

### Step 1: Get Free API Keys

#### Option A: Groq (Fastest, Recommended)

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up with Google or GitHub
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `gsk_`)

**Free Tier Limits:**
- 30 requests per minute
- 14,400 requests per day
- Models: Llama 3.3 70B, Mixtral 8x7B, Gemma 2

#### Option B: Together AI (Best Variety)

1. Visit [api.together.xyz](https://api.together.xyz)
2. Sign up with email or GitHub
3. Navigate to **Settings** → **API Keys**
4. Click **Create API Key**
5. Copy the key (starts with `tk_`)

**Free Tier Limits:**
- 5 million tokens per month
- Models: Qwen3 32B, DeepSeek-R1 32B, Llama 3.3 70B

#### Option C: HuggingFace (Alternative)

1. Visit [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create new token with **"Make requests to the inference API"** permission
3. Copy the token (starts with `hf_`)

**Free Tier Limits:**
- Rate limited
- Best for light usage

---

### Step 2: Configure Environment

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)

# Option 1: Groq only (recommended for speed)
export GROQ_API_KEY="gsk_your_key_here"

# Option 2: Together AI only (recommended for variety)
export TOGETHER_API_KEY="tk_your_key_here"

# Option 3: Both (recommended for reliability)
export GROQ_API_KEY="gsk_your_key_here"
export TOGETHER_API_KEY="tk_your_key_here"

# Option 4: All three
export GROQ_API_KEY="gsk_your_key_here"
export TOGETHER_API_KEY="tk_your_key_here"
export HF_API_KEY="hf_your_key_here"
```

```bash
# Reload shell
source ~/.zshrc
```

---

### Step 3: Verify Setup

```bash
cd /Users/irfan/ai-writing-agent
source venv/bin/activate

# Test with a simple prompt
python -c "
import os
from src.core.providers.free import FreeProvider

provider = FreeProvider()
models = provider.list_registered_models()
print('Registered models:', len(models))
for m in models[:3]:
    print(f'  - {m.id}')
"
```

Expected output:
```
Registered models: 5
  - groq/llama-3.3-70b-versatile
  - groq/mixtral-8x7b-32768
  - groq/llama-3.1-8b-instant
```

---

## Usage Examples

### Basic Write Command
```bash
python -m src.cli.main write "Write a haiku about coding"
```

### With Thinking Mode
```bash
python -m src.cli.main think "Outline a mystery novel chapter"
```

### Interactive Mode
```bash
python -m src.cli.main interactive
```

---

## Troubleshooting

### "Provider not found" Error

**Cause:** API key not set or not recognized.

**Fix:**
```bash
# Verify key is set
echo $GROQ_API_KEY

# If empty, add to profile
echo 'export GROQ_API_KEY="gsk_your_key"' >> ~/.zshrc
source ~/.zshrc
```

### Rate Limiting Error

**Cause:** Too many requests to free tier.

**Fix:**
- Wait 1 minute and retry
- Use Together AI as fallback
- Implement request throttling

### 401 Unauthorized

**Cause:** Invalid or expired API key.

**Fix:**
1. Go to provider dashboard
2. Generate new API key
3. Update environment variable
4. Restart terminal

---

## Cost Comparison

| Provider | Free Tier | Cost per 1M tokens |
|----------|-----------|---------------------|
| Groq | 14,400 req/day | $0 (free) |
| Together AI | 5M tokens/mo | $0 (free) |
| HuggingFace | Rate limited | $0 (free) |
| OpenAI GPT-4 | None | $15 |
| Anthropic Claude | None | $15 |

**Conclusion:** AI Writing Agent can run entirely on free tiers!

---

## Security Notes

1. **Never commit API keys** to version control
2. **Use environment variables** instead of hardcoding
3. **Rotate keys periodically** for security
4. **Monitor usage** in provider dashboards

```bash
# Add to .gitignore
*.env
.env
```

---

## Next Steps

1. [x] Get API keys
2. [x] Configure environment
3. [x] Verify setup
4. [ ] Run first production task
5. [ ] Set up monitoring (optional)
