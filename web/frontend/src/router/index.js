import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import JobView from '../views/JobView.vue'
import CreditsView from '../views/CreditsView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/job/:jobId', name: 'job', component: JobView, props: true },
  { path: '/credits', name: 'credits', component: CreditsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
