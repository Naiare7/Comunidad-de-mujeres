<template>
  <!-- Componente raíz de la aplicación. Todo lo demás se renderiza dentro de aquí. -->
  <div class="app">
    <!-- Barra de navegación: solo visible cuando la usuaria ha iniciado sesión (v-if en AppNav) -->
    <AppNav />
    <!-- router-view es el "hueco" donde Vue Router pinta la página de la ruta actual -->
    <main class="app__main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
// Importamos la barra de navegación para que esté disponible en el template
import AppNav from './components/AppNav.vue'
</script>

<style scoped>
/* El contenido principal ocupa al menos toda la pantalla menos la altura del nav (60px) */
.app__main {
  min-height: calc(100vh - 60px);
}
</style>
