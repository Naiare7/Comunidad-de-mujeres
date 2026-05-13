<template>
  <!-- Vista contenedor del formulario de recuperación de contraseña.
       Centra el formulario en pantalla y limita su ancho máximo. -->
  <div class="forgot-view">
    <div class="forgot-view__container">
      <ForgotPasswordForm />
    </div>
  </div>
</template>

<script setup>
// ForgotPasswordForm gestiona el envío del email de recuperación
import ForgotPasswordForm from '../components/ForgotPasswordForm.vue'
</script>

<style scoped>
.forgot-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background-color: var(--blanco-calido);
}

.forgot-view__container {
  width: 100%;
  max-width: 420px;
}

@media (max-width: 767px) {
  .forgot-view {
    padding: var(--space-4);
    align-items: flex-start;
    padding-top: var(--space-12);
  }
}
</style>
