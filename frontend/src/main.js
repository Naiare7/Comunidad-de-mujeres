// Punto de entrada de la aplicación Vue.
// Aquí se monta la app y se registran los plugins globales.

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './assets/styles/main.css'       // Variables CSS, tipografía y estilos base
import './assets/styles/components.css' // Clases reutilizables: botones, inputs, tarjetas...

const app = createApp(App)

app.use(createPinia()) // Pinia es el gestor de estado global (guarda datos entre componentes)
app.use(router)        // Vue Router gestiona la navegación entre páginas

// Escuchamos el evento "auth:unauthorized" que lanza apiFetch cuando el servidor
// responde con 401. Al recibirlo, cerramos la sesión automáticamente.
// Así no hace falta comprobar manualmente en cada store si el token expiró.
window.addEventListener('auth:unauthorized', () => {
  const authStore = useAuthStore()
  authStore.logout()
  router.push('/login')
})

app.mount('#app')      // Conecta la app Vue al elemento <div id="app"> del index.html
