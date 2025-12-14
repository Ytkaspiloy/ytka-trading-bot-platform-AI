import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/components/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chart/:symbol?',
    name: 'Chart',
    component: () => import('@/components/Chart.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/signals',
    name: 'Signals',
    component: () => import('@/components/Signals.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/components/Statistics.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/components/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/components/Auth.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Навигационная защита
router.beforeEach((to, from, next) => {
  const store = useTradingStore()
  
  if (to.meta.requiresAuth && !store.isAuthenticated) {
    next('/auth')
  } else {
    next()
  }
})

export default router
