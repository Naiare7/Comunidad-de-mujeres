<template>
  <!-- Vista contenedor del formulario de registro.
       Centra el formulario en pantalla y limita su ancho máximo. -->
  <div class="register-view">
    <div class="register-view__container">
      <RegisterForm />
    </div>
  </div>
</template>

<script setup>
// RegisterForm contiene toda la lógica del formulario (validación, envío, errores)
import RegisterForm from '../components/RegisterForm.vue'
</script>

<style scoped>
.register-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background-color: var(--blanco-calido);
}

.register-view__container {
  width: 100%;
  max-width: 420px;
}

@media (max-width: 767px) {
  .register-view {
    padding: var(--space-4);
    align-items: flex-start;
    padding-top: var(--space-12);
  }
}
</style>
