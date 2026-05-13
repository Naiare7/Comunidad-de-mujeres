// Configuración del enrutador: define qué componente se muestra en cada URL.
// Las rutas usan importación dinámica (() => import(...)) para cargar cada página
// solo cuando se necesita, mejorando el rendimiento inicial.

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    // Redirige la raíz al registro. Si ya tiene sesión, el guard la llevará a su destino.
    path: '/',
    redirect: '/register',
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'), // Página de registro (pública)
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'), // Página de login (pública)
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPasswordView.vue'), // Recuperación de contraseña (pública)
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('../views/ResetPasswordView.vue'), // Restablecer contraseña con token (pública)
  },
  {
    path: '/profile/setup',
    name: 'ProfileSetup',
    component: () => import('../views/ProfileSetupView.vue'), // Personalización del perfil (requiere login)
    meta: { requiresAuth: true }, // Marca esta ruta como protegida
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'), // Página de perfil (requiere login)
    meta: { requiresAuth: true },
  },
  {
    path: '/forums',
    name: 'Forums',
    component: () => import('../views/ForumsView.vue'), // Listado de foros (requiere login)
    meta: { requiresAuth: true },
  },
  {
    path: '/forums/:id',
    name: 'ForumThreads',
    component: () => import('../views/ForumThreadsView.vue'), // Hilos de un foro (requiere login)
    meta: { requiresAuth: true },
  },
  {
    path: '/forums/:id/threads/new',
    name: 'CreateThread',
    component: () => import('../views/CreateThreadView.vue'), // Crear nuevo hilo (requiere login)
    meta: { requiresAuth: true },
  },
  {
    path: '/threads/:id',
    name: 'ThreadDetail',
    component: () => import('../views/ThreadDetailView.vue'), // Detalle de un hilo (requiere login)
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(), // Usa URLs limpias (/register) en lugar de hash (#/register)
  routes,
})

// Guard de navegación: se ejecuta antes de cada cambio de ruta.
// Si la ruta marcada como "requiresAuth" y la usuaria no ha iniciado sesión,
// la redirige automáticamente al login.
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // to.meta.requiresAuth → la ruta a la que intenta ir necesita estar logueada
  // authStore.isAuthenticated → true si hay un token guardado
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login') // No está logueada → la enviamos al login
  } else {
    next() // Está logueada o la ruta es pública → la dejamos pasar
  }
})

export default router
