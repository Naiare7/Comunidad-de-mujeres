<template>
  <!-- Vista contenedor del formulario de login.
       Centra el formulario en pantalla y limita su ancho máximo. -->
  <div class="login-view">
    <div class="login-view__container">
      <LoginForm />
    </div>
  </div>
</template>

<script setup>
// LoginForm contiene toda la lógica del formulario (validación, envío, errores)
import LoginForm from '../components/LoginForm.vue'
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background-color: var(--blanco-calido);
}

.login-view__container {
  width: 100%;
  max-width: 420px;
}

@media (max-width: 767px) {
  .login-view {
    padding: var(--space-4);
    align-items: flex-start;
    padding-top: var(--space-12);
  }
}
</style>
