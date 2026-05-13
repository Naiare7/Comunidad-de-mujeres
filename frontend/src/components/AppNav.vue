<template>
  <!-- Barra de navegación principal. Solo se muestra si la usuaria ha iniciado sesión. -->
  <nav v-if="authStore.isAuthenticated" class="app-nav">
    <div class="app-nav__inner">

      <!-- Logo / nombre de la aplicación -->
      <router-link to="/forums" class="app-nav__logo">
        <span class="app-nav__logo-icon">&#9790;</span>
        <span class="app-nav__logo-text">Comunidad de Mujeres</span>
      </router-link>

      <!-- Enlaces de navegación -->
      <div class="app-nav__links">
        <router-link to="/forums" class="app-nav__link">
          <MessageSquareIcon :size="20" />
          <span>Foros</span>
        </router-link>
        <router-link to="/plans" class="app-nav__link">
          <CalendarIcon :size="20" />
          <span>Planes</span>
        </router-link>
        <router-link to="/news" class="app-nav__link">
          <NewspaperIcon :size="20" />
          <span>Noticias</span>
        </router-link>
        <router-link to="/profile" class="app-nav__link">
          <UserIcon :size="20" />
          <span>Perfil</span>
        </router-link>
      </div>

      <!-- Botón de cerrar sesión (solo visible cuando está logueada) -->
      <button class="app-nav__logout" @click="handleLogout" title="Cerrar sesión">
        <LogOutIcon :size="20" />
        <span>Cerrar sesión</span>
      </button>

    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  MessageSquareIcon,
  CalendarIcon,
  NewspaperIcon,
  UserIcon,
  LogOutIcon,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

// Al hacer clic en "Cerrar sesión": limpia el token, los datos de la usuaria
// y redirige a la página de inicio de sesión
function handleLogout() {
  authStore.logout()     // Elimina el token de memoria y del storage
  router.push('/login')  // Redirige al login
}
</script>

<style scoped>
.app-nav {
  background-color: var(--blanco-calido);
  border-bottom: 1.5px solid var(--melocoton);
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-nav__inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  gap: var(--space-4);
}

.app-nav__logo {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  flex-shrink: 0;
}

.app-nav__logo-icon {
  font-size: 1.5rem;
  color: var(--rosa-coral);
}

.app-nav__logo-text {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--rosa-coral);
  white-space: nowrap;
}

.app-nav__links {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.app-nav__link {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  text-decoration: none;
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--marron-cacao);
  transition: all 150ms ease;
}

.app-nav__link:hover {
  background-color: var(--melocoton);
  color: var(--rosa-coral);
}

/* Ruta activa: se ilumina cuando coincides con la URL actual */
.app-nav__link.router-link-exact-active {
  color: var(--rosa-coral);
  background-color: var(--melocoton);
}

.app-nav__logout {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  border: 2px solid var(--rosa-coral);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--rosa-coral);
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 150ms ease;
  white-space: nowrap;
}

.app-nav__logout:hover {
  background-color: var(--melocoton);
}

/* En móvil: ocultamos el texto de los enlaces y solo mostramos iconos */
@media (max-width: 767px) {
  .app-nav__inner {
    gap: var(--space-2);
  }

  .app-nav__logo-text {
    display: none;
  }

  .app-nav__link span {
    display: none;
  }

  .app-nav__logout span {
    display: none;
  }
}
</style>
