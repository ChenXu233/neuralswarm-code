<script setup lang="ts">
import { ref } from 'vue'
import { useServerConnection } from '../composables/useServerConnection'

const emit = defineEmits<{
  (e: 'connected'): void
}>()

const { addServer, connectServer } = useServerConnection()

const url = ref('http://localhost:8000')
const token = ref('')
const name = ref('')
const error = ref('')
const loading = ref(false)
const step = ref<'form' | 'connecting' | 'success'>('form')

async function handleConnect() {
  if (!url.value) {
    error.value = '请输入服务器地址'
    return
  }

  if (!token.value) {
    error.value = '请输入认证Token'
    return
  }

  loading.value = true
  error.value = ''
  step.value = 'connecting'

  try {
    const server = await addServer({
      name: name.value || `Server ${Date.now()}`,
      url: url.value,
      token: token.value
    })

    const success = await connectServer(server.id)
    if (success) {
      step.value = 'success'
      setTimeout(() => {
        emit('connected')
      }, 1000)
    } else {
      error.value = '连接失败，请检查服务器地址和Token'
      step.value = 'form'
    }
  } catch (e) {
    error.value = `连接错误: ${e instanceof Error ? e.message : '未知错误'}`
    step.value = 'form'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="server-setup-overlay">
    <div class="server-setup-dialog">
      <div class="dialog-header">
        <h2>连接服务器</h2>
        <p class="subtitle">NeuralSwarm需要连接到服务器才能正常工作</p>
      </div>

      <div class="dialog-content">
        <form @submit.prevent="handleConnect" class="manual-form">
          <div class="form-group">
            <label for="url">服务器地址 *</label>
            <input
              id="url"
              v-model="url"
              type="url"
              placeholder="http://localhost:8000"
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label for="token">认证Token *</label>
            <input
              id="token"
              v-model="token"
              type="password"
              placeholder="输入认证Token"
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label for="name">服务器名称</label>
            <input
              id="name"
              v-model="name"
              type="text"
              placeholder="可选，用于显示"
              :disabled="loading"
            />
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="loading"
            >
              <span v-if="loading && step === 'connecting'" class="loading-spinner"></span>
              连接
            </button>
          </div>
        </form>
      </div>

      <!-- 成功状态 -->
      <div v-if="step === 'success'" class="success-overlay">
        <div class="success-icon">✓</div>
        <p>连接成功！</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.server-setup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}

.server-setup-dialog {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  width: 100%;
  max-width: 480px;
  box-shadow: var(--shadow-xl);
  position: relative;
}

.dialog-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.dialog-header h2 {
  margin: 0 0 var(--space-2) 0;
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--color-text);
}

.dialog-header .subtitle {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.manual-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.form-group label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text);
}

.form-group input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  background: var(--color-surface);
  color: var(--color-text);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-focus-ring);
}

.form-group input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: var(--color-error);
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-3);
  background: var(--color-error-soft);
  border-radius: var(--radius-md);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: var(--space-2) var(--space-5);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-bg);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin-right: var(--space-2);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.success-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-surface);
  opacity: 0.95;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  gap: var(--space-4);
}

.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-success);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
}

.success-overlay p {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: var(--font-medium);
  color: var(--color-success);
}
</style>
