<template>
  <div class="app-container">
    <!-- Header -->
    <header class="app-header">
      <div class="logo">
        <span class="logo-icon">✍️</span>
        <span class="logo-text">AI Writing Agent</span>
      </div>
      
      <!-- Mode Toggle -->
      <div class="mode-toggle">
        <button 
          :class="{ active: currentMode === 'thinking' }"
          @click="setMode('thinking')"
        >
          🧠 Thinking
        </button>
        <button 
          :class="{ active: currentMode === 'writing' }"
          @click="setMode('writing')"
        >
          ✏️ Writing
        </button>
      </div>
      
      <!-- Model Selector -->
      <div class="model-selector">
        <select v-model="selectedModel" @change="onModelChange">
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
      : '/api/v1/write'
    
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
    
    const response = await axios.post(endpoint, payload)
    
    outputContent.value = response.data.content
    
    if (response.data.reasoning) {
      reasoningSteps.value = response.data.reasoning.steps || []
    }
    
    if (response.data.show_reasoning && reasoningSteps.value.length > 0) {
      showReasoning.value = true
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
/* Global Styles */
:root {
  --bg-primary: #0f0f0f;
  --bg-secondary: #1a1a1a;
  --bg-tertiary: #252525;
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
  --accent: #6366f1;
  --accent-hover: #818cf8;
  --success: #22c55e;
  --warning: #f59e0b;
  --error: #ef4444;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--bg-tertiary);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.mode-toggle {
  display: flex;
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 4px;
}

.mode-toggle button {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.mode-toggle button.active {
  background: var(--accent);
  color: white;
}

.model-selector select {
  padding: 0.5rem 1rem;
  background: var(--bg-tertiary);
  border: 1px solid var(--bg-tertiary);
  border-radius: 6px;
  color: var(--text-primary);
  cursor: pointer;
}

/* Main Layout */
.app-main {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 1rem;
  padding: 1rem 2rem;
}

/* Panels */
.input-panel,
.output-panel,
.context-panel {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-header h2 {
  font-size: 1rem;
  font-weight: 600;
}

/* Input Area */
.input-area textarea {
  flex: 1;
  width: 100%;
  padding: 1rem;
  background: var(--bg-tertiary);
  border: 1px solid transparent;
  border-radius: 8px;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.95rem;
  resize: none;
  min-height: 200px;
}

.input-area textarea:focus {
  outline: none;
  border-color: var(--accent);
}

.control-group {
  margin-bottom: 1rem;
}

.control-group label {
  display: block;
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.control-group select {
  width: 100%;
  padding: 0.5rem;
  background: var(--bg-tertiary);
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-primary);
}

.generate-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.generate-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Output Area */
.output-area {
  flex: 1;
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
  min-height: 400px;
  overflow-y: auto;
}

.output-actions button {
  padding: 0.5rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 4px;
}

.output-actions button:hover {
  background: var(--bg-tertiary);
}

.placeholder {
  color: var(--text-secondary);
  font-style: italic;
}

.cursor {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Context Panel */
.context-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.context-tabs button {
  flex: 1;
  padding: 0.5rem;
  background: var(--bg-tertiary);
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px;
  font-size: 0.85rem;
}

.context-tabs button.active {
  background: var(--accent);
  color: white;
}

.context-card {
  padding: 1rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.add-btn {
  width: 100%;
  padding: 0.75rem;
  background: transparent;
  border: 1px dashed var(--text-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 8px;
}

.add-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-secondary);
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--bg-tertiary);
}

.modal-content {
  padding: 1rem;
  max-height: 60vh;
  overflow-y: auto;
}

.reasoning-step {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.step-number {
  width: 24px;
  height: 24px;
  background: var(--accent);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

/* Markdown Styles */
.content h1, .content h2, .content h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.content p {
  margin-bottom: 1rem;
  line-height: 1.7;
}

.content code {
  background: var(--bg-tertiary);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
}

.content pre {
  background: var(--bg-tertiary);
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
}
</style>
