import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores/job'
import i18n from './i18n'

// Initialize anonymous user id for tracking jobs across sessions
const USER_ID_KEY = 'sports2d_user_id'
let userId = localStorage.getItem(USER_ID_KEY)
if (!userId) {
  userId = crypto.randomUUID()
  localStorage.setItem(USER_ID_KEY, userId)
}

const app = createApp(App)
app.use(pinia)
app.use(router)
app.use(i18n)
app.mount('#app')
