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
export default {
  name: 'FuelytChat',
  data() {
    return {
      messages: [],
      currentMessage: '',
      userId: 'demo_athlete',
      isTyping: false,
      error: null,
      messageIdCounter: 1,
      assistantMessageId: null,
    };
  },
  methods: {
    async sendMessage() {
      if (!this.currentMessage.trim() || !this.userId.trim()) return;

      const userMessage = this.currentMessage.trim();
      this.addMessage('user', userMessage);
      this.currentMessage = '';
      this.isTyping = true;
      this.error = null;

      try {
        const response = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
          },
          body: JSON.stringify({
            user_id: this.userId,
            message: userMessage,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        this.assistantMessageId = this.messageIdCounter++;
        this.addMessage('assistant', '', null, this.assistantMessageId);

        let buffer = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split('\n\n');
          
          parts.slice(0, -1).forEach(part => {
            if (part.startsWith('data: ')) {
              const dataContent = part.substring(6);
              this.updateAssistantMessage(dataContent);
            }
          });

          buffer = parts[parts.length - 1];
        }
      } catch (error) {
        console.error('Error sending message:', error);
        this.error = 'Failed to send message. Please try again.';
        this.addMessage('system', 'Sorry, I encountered an error.');
      } finally {
        this.isTyping = false;
        this.scrollToBottom();
      }
    },

    addMessage(type, content, recommendations = null, id = null) {
      const messageId = id || this.messageIdCounter++;
      this.messages.push({
        id: messageId,
        type,
        content: this.formatMessage(content),
        recommendations,
        timestamp: new Date(),
      });
      this.$nextTick(this.scrollToBottom);
    },

    updateAssistantMessage(chunk) {
      const assistantMessage = this.messages.find(m => m.id === this.assistantMessageId);
      if (assistantMessage) {
        assistantMessage.content += this.formatMessage(chunk);
        this.$nextTick(this.scrollToBottom);
      }
    },

    formatMessage(content) {
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    },

    addNewLine() {
      this.currentMessage += '\n';
    },

    scrollToBottom() {
      this.$nextTick(() => {
        if (this.$refs.messagesContainer) {
          this.$refs.messagesContainer.scrollTop = this.$refs.messagesContainer.scrollHeight;
        }
      });
    },

    autoResize() {
      const textarea = this.$refs.messageInput;
      if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
      }
    },
  },
  watch: {
    currentMessage() {
      this.$nextTick(this.autoResize);
    },
  },
  mounted() {
    this.$nextTick(() => {
      if (this.$refs.messageInput) {
        this.$refs.messageInput.focus();
      }
    });
  },
};
</script>