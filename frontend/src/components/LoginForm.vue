<template>
  <!-- novalidate desactiva la validación nativa del navegador para usar la nuestra -->
  <form class="login-form" @submit.prevent="handleSubmit" novalidate>

    <div class="login-form__header">
      <h2>Iniciar sesión</h2>
      <p class="login-form__subtitle">Bienvenida de nuevo</p>
    </div>

    <div class="login-form__fields">

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

      <!-- Campo: contraseña -->
      <div class="input-group">
        <label class="input-label" for="password">Contraseña</label>
        <div class="input-wrapper">
          <LockIcon class="input-icon" :size="20" />
          <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            class="input-field"
            :class="{ 'input-error': errors.password }"
            :aria-invalid="errors.password ? 'true' : 'false'"
            :aria-describedby="errors.password ? 'error-password' : undefined"
            placeholder="Tu contraseña"
            autocomplete="current-password"
            @blur="handleBlur('password')"
            @input="handleInput('password')"
          />
          <!-- Botón para mostrar/ocultar la contraseña -->
          <button
            type="button"
            class="input-toggle"
            @click="showPassword = !showPassword"
            :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
          >
            <EyeIcon v-if="!showPassword" :size="20" />
            <EyeOffIcon v-else :size="20" />
          </button>
        </div>
        <span v-if="errors.password" id="error-password" class="field-error" role="alert">
          {{ errors.password }}
        </span>
      </div>

      <!-- Checkbox: Recordarme -->
      <div class="input-group">
        <label class="checkbox-label" for="remember">
          <!-- El input real está oculto; el span.checkbox-custom es el visual -->
          <input
            id="remember"
            v-model="form.remember"
            type="checkbox"
            class="checkbox-input"
          />
          <span class="checkbox-custom">
            <CheckIcon v-if="form.remember" :size="14" />
          </span>
          <span class="checkbox-text">Recordarme</span>
        </label>
      </div>

      <!-- Error general: credenciales incorrectas o error de red -->
      <transition name="fade">
        <div v-if="serverError" class="login-form__server-error" role="alert">
          <AlertCircleIcon :size="20" />
          <span>{{ serverError }}</span>
        </div>
      </transition>

      <!-- Botón de envío: muestra spinner mientras carga -->
      <button type="submit" class="btn-primary login-form__submit" :disabled="authStore.isLoading">
        <LoaderIcon v-if="authStore.isLoading" class="spin" :size="20" />
        <span v-else>Iniciar sesión</span>
      </button>
    </div>

    <p class="login-form__footer">
      ¿No tienes cuenta?
      <router-link to="/register">Regístrate</router-link>
    </p>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  MailIcon, LockIcon,
  EyeIcon, EyeOffIcon,
  AlertCircleIcon, LoaderIcon,
  CheckIcon,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

// reactive() crea un objeto reactivo: Vue actualiza la vista cuando cambia alguna propiedad
const form = reactive({
  email: '',
  password: '',
  remember: false,     // Checkbox "Recordarme": false = no recordar
})

// Mensajes de error por campo (null = sin error)
const errors = reactive({
  email: null,
  password: null,
})

// Registra si la usuaria ya tocó cada campo (para no mostrar errores antes de interactuar)
const touched = reactive({
  email: false,
  password: false,
})

const serverError = ref(null)
const showPassword = ref(false)

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

    case 'password':
      errors.password = !form.password ? 'La contraseña es obligatoria'
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

  // Llamamos al store para hacer la petición al backend
  const result = await authStore.login({
    email: form.email.trim(),
    password: form.password,
    remember: form.remember,
  })

  if (result.success) {
    // Login exitoso: redirigimos a la página principal (foros)
    router.push('/forums')
  } else {
    // Error: lo mostramos como banner general
    serverError.value = result.message
  }
}
</script>

<style scoped>
.login-form {
  width: 100%;
  max-width: 420px;
  background-color: var(--blanco-calido);
  border: 1.5px solid var(--melocoton);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  padding: var(--space-6);
}

.login-form__header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.login-form__header h2 {
  margin-bottom: var(--space-1);
}

.login-form__subtitle {
  color: var(--texto-secundario);
  font-size: 0.875rem;
}

.login-form__fields {
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
  padding-right: 44px;
}

.input-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--texto-secundario);
  cursor: pointer;
  padding: var(--space-1);
  display: flex;
  align-items: center;
}

.input-toggle:hover {
  color: var(--marron-cacao);
}

.login-form__submit {
  width: 100%;
  margin-top: var(--space-2);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
}

.checkbox-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid var(--lila-suave);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 150ms ease;
  background-color: var(--blanco-calido);
  color: var(--blanco-calido);
}

.checkbox-input:focus + .checkbox-custom {
  box-shadow: 0 0 0 3px rgba(244, 132, 95, 0.2);
  border-color: var(--rosa-coral);
}

.checkbox-input:hover + .checkbox-custom {
  border-color: var(--rosa-oscuro);
}

.checkbox-input:checked + .checkbox-custom {
  background-color: var(--rosa-coral);
  border-color: var(--rosa-coral);
}

.checkbox-input:checked:hover + .checkbox-custom {
  background-color: var(--rosa-oscuro);
  border-color: var(--rosa-oscuro);
}

.checkbox-text {
  font-size: 0.875rem;
  color: var(--marron-cacao);
  user-select: none;
}

.login-form__server-error {
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

.login-form__footer {
  text-align: center;
  margin-top: var(--space-6);
  font-size: 0.875rem;
  color: var(--texto-secundario);
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
