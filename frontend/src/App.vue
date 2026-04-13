<template>
  <div class="app-container theme-glass">
    <!-- Background elements for glassmorphism -->
    <div class="glass-orb orb-1"></div>
    <div class="glass-orb orb-2"></div>
    <div class="glass-orb orb-3"></div>

    <!-- Header -->
    <header class="app-header glass-panel">
      <div class="logo">
        <div class="logo-icon-bg"><span class="logo-icon">✨</span></div>
        <div class="logo-text-group">
          <span class="logo-text">Agentic.AI</span>
          <span class="version-badge">Enterprise v2</span>
        </div>
      </div>
      
      <!-- Mode Toggle -->
      <div class="mode-toggle glass-pill">
        <button 
          :class="{ active: currentMode === 'thinking' }"
          @click="setMode('thinking')"
        >
          <span class="icon">🧠</span> Plan
        </button>
        <button 
          :class="{ active: currentMode === 'writing' }"
          @click="setMode('writing')"
        >
          <span class="icon">⚡</span> Draft
        </button>
      </div>
      
      <!-- Right Side Header -->
      <div class="header-actions">
        <!-- Auth / SSO -->
        <div class="auth-section">
          <div v-if="userRole === 'anonymous'" class="login-inputs">
            <input v-model="loginUser" placeholder="admin/pro/user" class="glass-input-sm" @keyup.enter="handleLogin" />
            <button @click="handleLogin" class="glass-btn primary btn-sm">SSO Login</button>
          </div>
          <div v-else class="user-badge" :class="userRole">
            <span class="role-dot"></span> {{ userRole.toUpperCase() }}
            <button @click="logout" class="icon-btn logout-btn" title="Sign Out">➜</button>
          </div>
        </div>

        <!-- Model Selector -->
        <div class="model-selector">
          <select v-model="selectedModel" @change="onModelChange" class="glass-select">
            <optgroup label="Thinking Models">
              <option value="deepseek-ai/DeepSeek-R1">DeepSeek-R1 (Reasoning)</option>
              <option value="Qwen/Qwen3-235B-A22B">Qwen3-235B (Creative)</option>
            </optgroup>
            <optgroup label="Fast Models">
              <option value="MiniMaxAI/MiniMax-M2">MiniMax-M2 (Fast)</option>
              <option value="mistralai/Mistral-Small-3.1">Mistral Small</option>
            </optgroup>
            <optgroup label="Local Models">
              <option value="gemma3:12b">Gemma 3 12B (Local)</option>
              <option value="phi4:latest">Phi-4 (Local)</option>
            </optgroup>
          </select>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="app-main">
      <!-- Left Panel: Input -->
      <aside class="input-panel">
        <div class="panel-header">
          <h2>{{ currentMode === 'thinking' ? 'Plan & Think' : 'Write & Create' }}</h2>
        </div>
        
        <!-- Thinking Mode -->
        <div v-if="currentMode === 'thinking'" class="thinking-controls">
          <div class="control-group">
            <label>Thinking Type</label>
            <select v-model="thinkingType">
              <option value="outline">Outline & Structure</option>
              <option value="character">Character Development</option>
              <option value="plot">Plot Planning</option>
              <option value="research">Research & Analysis</option>
              <option value="structure">Document Structure</option>
            </select>
          </div>
          
          <div class="control-group">
            <label>Depth</label>
            <select v-model="thinkingDepth">
              <option value="shallow">Shallow</option>
              <option value="medium">Medium</option>
              <option value="deep">Deep</option>
            </select>
          </div>
        </div>
        
        <!-- Writing Mode -->
        <div v-if="currentMode === 'writing'" class="writing-controls">
          <div class="control-group">
            <label>Style</label>
            <select v-model="writingStyle">
              <option value="narrative">Narrative</option>
              <option value="technical">Technical</option>
              <option value="marketing">Marketing</option>
              <option value="concise">Concise</option>
              <option value="creative">Creative</option>
              <option value="formal">Formal</option>
              <option value="casual">Casual</option>
            </select>
          </div>
          
          <div class="control-group">
            <label>Task</label>
            <select v-model="writingTask">
              <option value="draft">Draft</option>
              <option value="edit">Edit</option>
              <option value="rephrase">Rephrase</option>
              <option value="expand">Expand</option>
              <option value="condense">Condense</option>
            </select>
          </div>
        </div>
        
        <!-- Input Area -->
        <div class="input-area">
          <textarea 
            v-model="inputText"
            :placeholder="inputPlaceholder"
            rows="10"
            @keydown.ctrl.enter="generate"
          ></textarea>
        </div>
        
        <!-- Generate Button -->
        <button 
          class="generate-btn"
          @click="generate"
          :disabled="isGenerating || !inputText.trim()"
        >
          {{ isGenerating ? '⏳ Generating...' : '🚀 Generate' }}
        </button>
      </aside>

      <!-- Center Panel: Output -->
      <section class="output-panel">
        <div class="panel-header">
          <h2>Output</h2>
          <div class="output-actions">
            <button @click="copyOutput" title="Copy">📋</button>
            <button @click="exportOutput" title="Export">💾</button>
            <button @click="clearOutput" title="Clear">🗑️</button>
          </div>
        </div>
        
        <!-- Streaming Output -->
        <div class="output-area">
          <div v-if="isGenerating && streamingContent" class="streaming-content">
            <div v-html="renderedStreaming"></div>
            <span class="cursor">▋</span>
          </div>
          
          <div v-else-if="outputContent" class="content">
            <div v-html="renderedOutput"></div>
          </div>
          
          <div v-else class="placeholder">
            Your generated content will appear here...
          </div>
        </div>
      </section>

      <!-- Right Panel: Context/Memory -->
      <aside class="context-panel">
        <div class="panel-header">
          <h2>Memory & Context</h2>
        </div>
        
        <!-- Tabs -->
        <div class="context-tabs">
          <button 
            :class="{ active: contextTab === 'characters' }"
            @click="contextTab = 'characters'"
          >Characters</button>
          <button 
            :class="{ active: contextTab === 'plot' }"
            @click="contextTab = 'plot'"
          >Plot</button>
          <button 
            :class="{ active: contextTab === 'style' }"
            @click="contextTab = 'style'"
          >Style</button>
        </div>
        
        <!-- Characters -->
        <div v-if="contextTab === 'characters'" class="context-content">
          <div 
            v-for="char in characters" 
            :key="char.name"
            class="context-card character"
          >
            <h4>{{ char.name }}</h4>
            <p class="traits">{{ char.traits.join(', ') }}</p>
          </div>
          
          <button class="add-btn" @click="showAddCharacter = true">
            + Add Character
          </button>
        </div>
        
        <!-- Plot -->
        <div v-if="contextTab === 'plot'" class="context-content">
          <div 
            v-for="point in plotPoints" 
            :key="point.chapter"
            class="context-card plot-point"
          >
            <span class="chapter">Ch. {{ point.chapter }}</span>
            <span class="title">{{ point.title }}</span>
          </div>
          
          <button class="add-btn" @click="showAddPlotPoint = true">
            + Add Plot Point
          </button>
        </div>
        
        <!-- Style -->
        <div v-if="contextTab === 'style'" class="context-content">
          <div class="context-card style-guide">
            <h4>Style Guide</h4>
            <p v-if="styleGuide.tone">Tone: {{ styleGuide.tone }}</p>
            <p v-if="styleGuide.format">Format: {{ styleGuide.format }}</p>
          </div>
          
          <button class="add-btn" @click="uploadStyleGuide">
            📄 Upload Style Guide
          </button>
        </div>
      </aside>
    </main>

    <!-- Reasoning Trace Modal -->
    <div v-if="showReasoning" class="modal-overlay" @click.self="showReasoning = false">
      <div class="modal reasoning-modal">
        <div class="modal-header">
          <h3>🧠 Reasoning Trace</h3>
          <button @click="showReasoning = false">✕</button>
        </div>
        <div class="modal-content">
          <div 
            v-for="(step, index) in reasoningSteps" 
            :key="index"
            class="reasoning-step"
          >
            <span class="step-number">{{ index + 1 }}</span>
            <span class="step-content">{{ step.thought }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import axios from 'axios'

// State
const currentMode = ref<'thinking' | 'writing'>('writing')
const selectedModel = ref('MiniMaxAI/MiniMax-M2')
const inputText = ref('')
const outputContent = ref('')
const streamingContent = ref('')
const isGenerating = ref(false)

// Auth State
const loginUser = ref('')
const userRole = ref('anonymous')
const authToken = ref('')

async function handleLogin() {
  if (!loginUser.value.trim()) return
  try {
    const res = await axios.post('/api/v1/auth/login', { username: loginUser.value, password: 'pw' })
    authToken.value = res.data.token
    userRole.value = res.data.role
    loginUser.value = ''
  } catch(e) {
    console.error("Login failed", e)
  }
}

function logout() {
  authToken.value = ''
  userRole.value = 'anonymous'
}

// Thinking Mode
const thinkingType = ref('outline')
const thinkingDepth = ref('medium')
const reasoningSteps = ref<Array<{thought: string}>>([])
const showReasoning = ref(false)

// Writing Mode
const writingStyle = ref('narrative')
const writingTask = ref('draft')

// Context
const contextTab = ref('characters')
const characters = ref([
  { name: 'Alice', traits: ['brave', 'curious', 'determined'] },
])
const plotPoints = ref([
  { chapter: 1, title: 'The Beginning' },
])
const styleGuide = ref({})

// Computed
const inputPlaceholder = computed(() => {
  if (currentMode.value === 'thinking') {
    return 'Enter your topic or problem to think through...'
  }
  return 'Enter your writing prompt, topic, or content to work with...'
})

const renderedOutput = computed(() => {
  return marked.parse(outputContent.value)
})

const renderedStreaming = computed(() => {
  return marked.parse(streamingContent.value)
})

// Methods
function setMode(mode: 'thinking' | 'writing') {
  currentMode.value = mode
}

async function generate() {
  if (!inputText.value.trim() || isGenerating.value) return
  
  isGenerating.value = true
  streamingContent.value = ''
  outputContent.value = ''
  reasoningSteps.value = []
  
  try {
    const endpoint = currentMode.value === 'thinking' 
      ? '/api/v1/think'
      : '/api/v1/write/stream'
    
    const payload = currentMode.value === 'thinking' 
      ? {
          prompt: inputText.value,
          thinking_type: thinkingType.value,
          depth: thinkingDepth.value,
          model: selectedModel.value,
        }
      : {
          prompt: inputText.value,
          style: writingStyle.value,
          task: writingTask.value,
          model: selectedModel.value,
        }
        
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (authToken.value) {
      headers['Authorization'] = `Bearer ${authToken.value}`
    }
    
    if (currentMode.value === 'writing') {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
      })

      if (!response.ok) throw new Error("Network response was not ok")
      if (!response.body) throw new Error("No response body")

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      while (true) {
        const { value, done } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.content) {
                // Remove some specific fastAPI SSE bugs or formats if needed
                streamingContent.value += data.content
                outputContent.value = streamingContent.value
              }
            } catch (e) {}
          }
        }
      }
    } else {
      const response = await axios.post(endpoint, payload, { headers })
      
      outputContent.value = response.data.content
      
      if (response.data.reasoning) {
        reasoningSteps.value = response.data.reasoning.steps || []
      }
      
      if (response.data.show_reasoning && reasoningSteps.value.length > 0) {
        showReasoning.value = true
      }
    }
    
  } catch (error) {
    console.error('Generation error:', error)
    outputContent.value = 'Error generating content. Please try again.'
  } finally {
    isGenerating.value = false
  }
}

function onModelChange() {
  localStorage.setItem('selectedModel', selectedModel.value)
}

function copyOutput() {
  navigator.clipboard.writeText(outputContent.value)
}

function exportOutput() {
  const blob = new Blob([outputContent.value], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'generated-content.md'
  a.click()
}

function clearOutput() {
  outputContent.value = ''
  streamingContent.value = ''
  reasoningSteps.value = []
}

function showAddCharacter() {
  // Implementation for adding characters
}

function showAddPlotPoint() {
  // Implementation for adding plot points
}

function uploadStyleGuide() {
  // Implementation for uploading style guides
}
</script>

<style>
/* Glassmorphism Premium Enterprise Theme */
:root {
  --bg-dark: #0a0a0f;
  --glass-bg: rgba(255, 255, 255, 0.03);
  --glass-border: rgba(255, 255, 255, 0.08);
  --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --accent-primary: #8b5cf6;
  --accent-secondary: #ec4899;
  --accent-gradient: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: var(--bg-dark);
  color: var(--text-primary);
  min-height: 100vh;
  overflow-x: hidden;
}

.theme-glass {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Background elements for glassmorphism */
.glass-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: -1;
  opacity: 0.5;
}

.orb-1 {
  top: -10%; left: -5%; width: 40vw; height: 40vw;
  background: radial-gradient(circle, rgba(139,92,246,0.3) 0%, rgba(0,0,0,0) 70%);
}

.orb-2 {
  bottom: -10%; right: -5%; width: 50vw; height: 50vw;
  background: radial-gradient(circle, rgba(236,72,153,0.2) 0%, rgba(0,0,0,0) 70%);
}

.orb-3 {
  top: 40%; left: 40%; width: 30vw; height: 30vw;
  background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, rgba(0,0,0,0) 70%);
}

/* Utility Glass Panel */
.glass-panel, .input-panel, .output-panel, .context-panel, .modal, .context-card {
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  border-radius: 16px;
}

/* Header */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  margin: 1rem 2rem;
  border-radius: 20px;
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon-bg {
  background: var(--accent-gradient);
  border-radius: 12px;
  width: 40px; height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.logo-text-group {
  display: flex;
  flex-direction: column;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(to right, #fff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.version-badge {
  font-size: 0.65rem;
  color: var(--accent-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

/* Mode Toggle */
.mode-toggle.glass-pill {
  display: flex;
  background: rgba(0,0,0,0.3);
  border-radius: 100px;
  padding: 4px;
  border: 1px solid var(--glass-border);
}

.mode-toggle button {
  padding: 0.5rem 1.5rem;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 100px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 6px;
}

.mode-toggle button.active {
  background: var(--glass-bg);
  color: var(--text-primary);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  border: 1px solid rgba(255,255,255,0.1);
}

/* Auth / SSO */
.header-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.auth-section {
  display: flex;
  align-items: center;
}

.login-inputs {
  display: flex;
  gap: 0.5rem;
}

.glass-input-sm {
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--glass-border);
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-size: 0.85rem;
  outline: none;
  width: 130px;
}
.glass-input-sm:focus {
  border-color: var(--accent-primary);
}

.btn-sm {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  border-radius: 8px;
}

.glass-btn {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--glass-border);
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}
.glass-btn.primary {
  background: var(--accent-gradient);
  border: none;
  font-weight: 600;
}
.glass-btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 1rem;
  background: rgba(255,255,255,0.05);
  border-radius: 20px;
  border: 1px solid var(--glass-border);
  font-size: 0.85rem;
  font-weight: 600;
}
.role-dot {
  width: 8px; height: 8px; border-radius: 50%;
}
.user-badge.admin .role-dot { background: var(--error); box-shadow: 0 0 8px var(--error); }
.user-badge.pro .role-dot { background: var(--accent-primary); box-shadow: 0 0 8px var(--accent-primary); }
.user-badge.user .role-dot { background: var(--success); box-shadow: 0 0 8px var(--success); }

.icon-btn {
  background: none; border: none; color: var(--text-secondary); cursor: pointer;
}
.icon-btn:hover { color: white; }

.glass-select {
  padding: 0.5rem 1rem;
  background: rgba(0,0,0,0.3);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.9rem;
  outline: none;
  cursor: pointer;
}

/* Main Layout */
.app-main {
  flex: 1;
  display: grid;
  grid-template-columns: 320px 1fr 300px;
  gap: 1.5rem;
  padding: 0 2rem 2rem 2rem;
  z-index: 5;
}

/* Panels */
.input-panel, .output-panel, .context-panel {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* Add a subtle highlight to top edge of panels for extreme glass effect */
.glass-panel::before, .input-panel::before, .output-panel::before, .context-panel::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.panel-header h2 {
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: -0.3px;
}

/* Input Area */
.input-area textarea {
  flex: 1;
  width: 100%;
  padding: 1rem;
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.6;
  resize: none;
  min-height: 250px;
  transition: all 0.3s;
}

.input-area textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(139,92,246,0.1);
}

.control-group {
  margin-bottom: 1.25rem;
}

.control-group label {
  display: block;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.control-group select {
  width: 100%;
  padding: 0.6rem;
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.2s;
}
.control-group select:focus {
  border-color: var(--accent-primary);
}

.generate-btn {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--accent-gradient);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(139,92,246,0.3);
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139,92,246,0.4);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* Output Area */
.output-area {
  flex: 1;
  padding: 1.5rem;
  background: rgba(0,0,0,0.15);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  min-height: 400px;
  overflow-y: auto;
}

.output-actions button {
  padding: 0.5rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--glass-border);
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.output-actions button:hover {
  background: rgba(255,255,255,0.1);
  color: white;
}

.placeholder {
  color: var(--text-secondary);
  font-style: italic;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  opacity: 0.7;
}

.cursor {
  display: inline-block;
  width: 8px;
  height: 1.2em;
  background: var(--accent-primary);
  vertical-align: text-bottom;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* Context Panel */
.context-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: rgba(0,0,0,0.2);
  padding: 4px;
  border-radius: 8px;
}

.context-tabs button {
  flex: 1;
  padding: 0.5rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
}

.context-tabs button.active {
  background: var(--glass-bg);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.context-card {
  margin-bottom: 0.75rem;
}
.context-card h4 { font-weight: 600; margin-bottom: 0.25rem; }
.context-card .traits { font-size: 0.85rem; color: var(--text-secondary); }

.add-btn {
  width: 100%;
  padding: 0.75rem;
  background: rgba(0,0,0,0.1);
  border: 1px dashed rgba(255,255,255,0.2);
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.add-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  background: rgba(139,92,246,0.05);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: 90%;
  max-width: 650px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
}

.modal-content {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.reasoning-step {
  display: flex;
  gap: 1.25rem;
  padding: 1rem;
  background: rgba(0,0,0,0.2);
  border-radius: 12px;
  margin-bottom: 0.75rem;
  border: 1px solid rgba(255,255,255,0.05);
}

.step-number {
  width: 28px; height: 28px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--accent-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content {
  line-height: 1.6;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

/* Markdown Styles */
.content h1, .content h2, .content h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: white;
}

.content p {
  margin-bottom: 1.25rem;
  line-height: 1.7;
  color: #e2e8f0;
}

.content code {
  background: rgba(0,0,0,0.3);
  padding: 0.2em 0.4em;
  border-radius: 6px;
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
  border: 1px solid var(--glass-border);
}

.content pre {
  background: #0f111a;
  padding: 1.25rem;
  border-radius: 12px;
  overflow-x: auto;
  border: 1px solid var(--glass-border);
  margin-bottom: 1.25rem;
}
</style>
