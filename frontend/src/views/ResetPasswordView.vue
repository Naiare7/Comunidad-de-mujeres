<template>
  <!-- Vista contenedor del formulario de restablecimiento de contraseña.
       Recibe el token de recuperación por la URL (?token=xxx) y lo pasa al formulario. -->
  <div class="reset-view">
    <div class="reset-view__container">
      <ResetPasswordForm />
    </div>
  </div>
</template>

<script setup>
// ResetPasswordForm lee el token de la URL y gestiona el cambio de contraseña
import ResetPasswordForm from '../components/ResetPasswordForm.vue'
</script>

<style scoped>
.reset-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background-color: var(--blanco-calido);
}

.reset-view__container {
  width: 100%;
  max-width: 420px;
}

@media (max-width: 767px) {
  .reset-view {
    padding: var(--space-4);
    align-items: flex-start;
    padding-top: var(--space-12);
  }
}
</style>
