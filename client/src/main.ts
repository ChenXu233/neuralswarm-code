import { createApp } from 'vue'
import App from './App.vue'
import i18n from './locales/i18n'
import './styles/tailwind.css'
import './styles/variables.css'
import './styles/base.css'
import './styles/transitions.css'

createApp(App).use(i18n).mount('#app')
