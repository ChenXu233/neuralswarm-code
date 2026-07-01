import { createApp } from 'vue'
import App from './App.vue'
import i18n from './locales/i18n'
import './styles/tailwind.css'
import './styles/variables.css'
import './styles/base.css'
import './styles/transitions.css'

// 初始化所有内置插件（导入即执行 registerPlugin）
import './plugins/chat-panel'
import './plugins/file-tree'
import './plugins/memory-panel'
import './plugins/plugins-panel'
import './plugins/settings'
import './plugins/status-bar'
import './plugins/conflict-dialog'

createApp(App).use(i18n).mount('#app')
