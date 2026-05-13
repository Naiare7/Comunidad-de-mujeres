<template>
  <!-- novalidate desactiva la validación nativa del navegador para usar la nuestra -->
  <form class="forgot-form" @submit.prevent="handleSubmit" novalidate>

    <div class="forgot-form__header">
      <h2>¿Olvidaste tu contraseña?</h2>
      <p class="forgot-form__subtitle">
        Te enviaremos un enlace para restablecerla
      </p>
    </div>

    <div class="forgot-form__fields">

      <!-- Mensaje de éxito: se muestra después de enviar -->
      <transition name="fade">
        <div v-if="sent" class="forgot-form__success" role="status">
          <CheckCircleIcon :size="24" />
          <p>Si el email está registrado, recibirás un enlace de recuperación</p>
        </div>
      </transition>

      <!-- El formulario solo se muestra si aún no se ha enviado -->
      <template v-if="!sent">

        <!-- Campo: email -->
        <div class="input-group">
          <label class="input-label" for="email">Email</label>
          <div class="input-wrapper">
            <MailIcon class="input-icon" :size="20" />
            <input
              id="email"
              v-model="form.email"
              type="email"
              class="input-field"
              :class="{ 'input-error': errors.email }"
              :aria-invalid="errors.email ? 'true' : 'false'"
              :aria-describedby="errors.email ? 'error-email' : undefined"
              placeholder="tu@email.com"
              autocomplete="email"
              @blur="handleBlur('email')"
              @input="handleInput('email')"
            />
          </div>
          <span v-if="errors.email" id="error-email" class="field-error" role="alert">
            {{ errors.email }}
          </span>
        </div>

        <!-- Error general (error de red, etc.) -->
        <transition name="fade">
          <div v-if="serverError" class="forgot-form__server-error" role="alert">
            <AlertCircleIcon :size="20" />
            <span>{{ serverError }}</span>
          </div>
        </transition>

        <!-- Botón de envío -->
        <button type="submit" class="btn-primary forgot-form__submit" :disabled="isLoading">
          <LoaderIcon v-if="isLoading" :size="20" class="spin" />
          {{ isLoading ? 'Enviando…' : 'Enviar enlace' }}
        </button>

      </template>
    </div>

    <!-- Enlace para volver al login -->
    <p class="forgot-form__footer">
      <router-link to="/login">&larr; Volver a iniciar sesión</router-link>
    </p>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { apiFetchJson } from '../services/http'
import { MailIcon, AlertCircleIcon, CheckCircleIcon, LoaderIcon } from 'lucide-vue-next'

// reactive() crea un objeto reactivo: Vue actualiza la vista cuando cambia alguna propiedad
const form = reactive({
  email: '',
})

// Mensajes de error por campo (null = sin error)
const errors = reactive({
  email: null,
})

// Registra si la usuaria ya tocó cada campo (para no mostrar errores antes de interactuar)
const touched = reactive({
  email: false,
})

const sent = ref(false)       // true después de enviar el formulario correctamente
const isLoading = ref(false)  // true mientras se envía la petición al servidor
const serverError = ref(null) // Mensaje de error del servidor (si lo hubiera)

// Se llama cuando la usuaria sale de un campo (pierde el foco)
function handleBlur(field) {
  touched[field] = true
  validateField(field)
}

// Se llama mientras la usuaria escribe en un campo
function handleInput(field) {
  if (touched[field]) validateField(field)
}

// Valida un campo concreto y actualiza su mensaje de error
function validateField(field) {
  switch (field) {
    case 'email':
      errors.email = !form.email.trim() ? 'El email es obligatorio'
        : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) ? 'Introduce un email válido'
        : null
      break
  }
}

// Valida todos los campos a la vez y devuelve true si no hay errores
function validateAll() {
  Object.keys(touched).forEach((field) => {
    touched[field] = true
    validateField(field)
  })
  return !Object.values(errors).some(Boolean)
}

// Se ejecuta al enviar el formulario
async function handleSubmit() {
  serverError.value = null

  if (!validateAll()) return

  isLoading.value = true

  try {
    // Enviamos el email al backend para que genere el token de recuperación
    const { response } = await apiFetchJson('/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: form.email.trim() }),
    })

    if (response.ok) {
      // Mostramos mensaje de éxito aunque el email no exista
      // (el backend responde igual por seguridad, para no revelar emails registrados)
      sent.value = true
    } else {
      // Si el servidor devuelve un error inesperado, lo mostramos
      serverError.value = 'Error al procesar la solicitud. Inténtalo de nuevo.'
    }
  } catch {
    // Error de red (servidor caído, sin conexión, etc.)
    serverError.value = 'Error de conexión. Comprueba tu conexión a internet.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.forgot-form {
  width: 100%;
  max-width: 420px;
  background-color: var(--blanco-calido);
  border: 1.5px solid var(--melocoton);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  padding: var(--space-6);
}

.forgot-form__header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.forgot-form__header h2 {
  margin-bottom: var(--space-1);
}

.forgot-form__subtitle {
  color: var(--texto-secundario);
  font-size: 0.875rem;
}

.forgot-form__fields {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--lila-oscuro);
  pointer-events: none;
}

.input-wrapper .input-field {
  padding-left: 44px;
}

.forgot-form__submit {
  width: 100%;
  margin-top: var(--space-2);
}

.forgot-form__success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6);
  text-align: center;
  color: var(--exito);
  font-size: 0.9375rem;
  font-weight: 600;
}

.forgot-form__server-error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background-color: rgba(224, 92, 92, 0.1);
  border: 1px solid var(--error);
  border-radius: var(--radius-sm);
  color: var(--error);
  font-size: 0.875rem;
}

.forgot-form__footer {
  text-align: center;
  margin-top: var(--space-6);
  font-size: 0.875rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
