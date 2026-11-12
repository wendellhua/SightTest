import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/projects' },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/index.vue'),
    meta: { public: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/register/index.vue'),
    meta: { public: true },
  },
  {
    path: '/projects',
    name: 'projects',
    component: () => import('@/views/projects/index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/create-project',
    name: 'create-project',
    component: () => import('@/views/create-project/index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/project/:id',
    name: 'project-detail',
    component: () => import('@/views/project/detail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/project/:id/cases',
    name: 'project-cases',
    component: () => import('@/views/case/index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/project/:id/executions',
    name: 'project-executions',
    component: () => import('@/views/execution/index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/project/:id/execution/:executionId',
    name: 'execution-detail',
    component: () => import('@/views/execution/detail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/project/:id/reports',
    name: 'project-reports',
    component: () => import('@/views/report/index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/project/:id/report/:reportId',
    name: 'report-detail',
    component: () => import('@/views/report/detail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/models',
    name: 'models',
    component: () => import('@/views/model/index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/usage',
    name: 'usage',
    component: () => import('@/views/usage/index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/admin/index.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/settings/index.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if ((to.name === 'login' || to.name === 'register') && token) {
    return { path: '/projects' }
  }
  return true
})

export default router
