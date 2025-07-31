<template>
  <div class="chat-container">
    <header class="chat-header">
      <h1>🏃‍♂️ Fuelyt</h1>
      <p>Your AI Nutrition & Performance Coach</p>
    </header>
    
    <div class="chat-messages" ref="messagesContainer">
      <div class="message system">
        Welcome! I'm Fuelyt, your AI nutrition coach. Tell me about your fitness goals, log your workouts, or ask for meal recommendations.
      </div>
      
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', message.type]"
      >
        <div v-if="message.type === 'assistant' && message.recommendations?.length">
          <div v-html="message.content"></div>
          <div class="recommendations">
            <h4>📋 Recommendations:</h4>
            <ul>
              <li v-for="rec in message.recommendations" :key="rec.title">
                <strong>{{ rec.title }}:</strong> {{ rec.message }}
              </li>
            </ul>
          </div>
        </div>
        <div v-else v-html="message.content"></div>
      </div>
      
      <div v-if="isTyping" class="typing-indicator">
        <span>Fuelyt is thinking</span>
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
    
    <div class="chat-input">
      <input
        v-model="userId"
        type="text"
        placeholder="Enter your user ID (e.g., athlete_123)"
        class="user-id-input"
      />
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <div class="input-container">
        <textarea
          v-model="currentMessage"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.enter.shift.exact="addNewLine"
          placeholder="Ask about nutrition, log a workout, or request meal recommendations..."
          rows="1"
          ref="messageInput"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!currentMessage.trim() || isTyping || !userId.trim()"
          class="send-button"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'FuelytChat',
  data() {
    return {
      messages: [],
      currentMessage: '',
      userId: 'demo_athlete',
      isTyping: false,
      error: null,
      messageIdCounter: 1
    }
  },
  methods: {
    async sendMessage() {
      if (!this.currentMessage.trim() || !this.userId.trim()) return
      
      const userMessage = this.currentMessage.trim()
      this.currentMessage = ''
      this.error = null
      
      // Add user message to chat
      this.addMessage('user', userMessage)
      
      // Show typing indicator
      this.isTyping = true
      
      try {
        // Send message to backend
        const response = await axios.post('/api/chat', {
          user_id: this.userId,
          message: userMessage,
          context: {
            timestamp: new Date().toISOString(),
            source: 'web_interface'
          }
        })
        
        const data = response.data
        
        // Add assistant response
        this.addMessage('assistant', data.response, data.recommendations)
        
        // Show any actions taken
        if (data.actions_taken && data.actions_taken.length > 0) {
          this.addMessage('system', `Actions completed: ${data.actions_taken.join(', ')}`)
        }
        
      } catch (error) {
        console.error('Error sending message:', error)
        this.error = error.response?.data?.detail || 'Failed to send message. Please try again.'
        this.addMessage('system', 'Sorry, I encountered an error. Please try again.')
      } finally {
        this.isTyping = false
        this.scrollToBottom()
      }
    },
    
    addMessage(type, content, recommendations = null) {
      this.messages.push({
        id: this.messageIdCounter++,
        type,
        content: this.formatMessage(content),
        recommendations,
        timestamp: new Date()
      })
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },
    
    formatMessage(content) {
      // Basic markdown-like formatting
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>')
    },
    
    addNewLine() {
      this.currentMessage += '\n'
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },
    
    // Auto-resize textarea
    autoResize() {
      const textarea = this.$refs.messageInput
      if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
      }
    }
  },
  
  watch: {
    currentMessage() {
      this.$nextTick(() => {
        this.autoResize()
      })
    }
  },
  
  mounted() {
    // Focus on message input
    this.$nextTick(() => {
      if (this.$refs.messageInput) {
        this.$refs.messageInput.focus()
      }
    })
    
    // Test connection on mount
    this.testConnection()
  },
  
  methods: {
    ...this.methods,
    
    async testConnection() {
      try {
        const response = await axios.get('/api/')
        if (response.data.status === 'healthy') {
          this.addMessage('system', 'Connected to Fuelyt AI successfully! 🚀')
        }
      } catch (error) {
        this.error = 'Unable to connect to Fuelyt backend. Make sure the server is running on port 8000.'
        console.error('Connection test failed:', error)
      }
    }
  }
}
</script>