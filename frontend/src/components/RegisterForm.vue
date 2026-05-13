<template>
  <!-- novalidate desactiva la validación nativa del navegador para usar la nuestra -->
  <form class="register-form" @submit.prevent="handleSubmit" novalidate>

    <div class="register-form__header">
      <h2>Crear tu cuenta</h2>
      <p class="register-form__subtitle">Únete a la comunidad</p>
    </div>

    <div class="register-form__fields">

      <!-- Campo: nombre de usuario -->
      <div class="input-group">
        <label class="input-label" for="username">Nombre de usuario</label>
        <div class="input-wrapper">
          <UserIcon class="input-icon" :size="20" />
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="input-field"
            :class="{ 'input-error': errors.username }"
            :aria-invalid="errors.username ? 'true' : 'false'"
            :aria-describedby="errors.username ? 'error-username' : undefined"
            placeholder="Tu nombre de usuario"
            autocomplete="username"
            @blur="handleBlur('username')"
            @input="handleInput('username')"
          />
        </div>
        <span v-if="errors.username" id="error-username" class="field-error" role="alert">
          {{ errors.username }}
        </span>
      </div>

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

      <!-- Campo: contraseña con indicador de fortaleza -->
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
            placeholder="Mínimo 8 caracteres"
            autocomplete="new-password"
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

        <!-- Indicador de fortaleza: aparece cuando la usuaria empieza a escribir -->
        <div
          v-if="touched.password || form.password.length > 0"
          class="password-feedback"
          role="status"
          aria-live="polite"
        >
          <!-- Barra de progreso que cambia de color según la fortaleza -->
          <div class="password-strength-bar" :class="'strength-' + strengthLevel">
            <div class="password-strength-fill" :style="{ width: strengthPercent + '%' }"></div>
          </div>
          <!-- Lista de requisitos con check/x según se cumplan -->
          <ul class="password-checklist">
            <li :class="{ met: passwordChecks.minLength }">
              <CheckIcon v-if="passwordChecks.minLength" :size="14" />
              <XIcon v-else :size="14" />
              Mínimo 8 caracteres
            </li>
            <li :class="{ met: passwordChecks.hasUppercase }">
              <CheckIcon v-if="passwordChecks.hasUppercase" :size="14" />
              <XIcon v-else :size="14" />
              Una mayúscula
            </li>
            <li :class="{ met: passwordChecks.hasNumber }">
              <CheckIcon v-if="passwordChecks.hasNumber" :size="14" />
              <XIcon v-else :size="14" />
              Un número
            </li>
          </ul>
        </div>

        <span v-if="errors.password" id="error-password" class="field-error" role="alert">
          {{ errors.password }}
        </span>
      </div>

      <!-- Campo: confirmar contraseña -->
      <div class="input-group">
        <label class="input-label" for="confirmPassword">Confirmar contraseña</label>
        <div class="input-wrapper">
          <LockIcon class="input-icon" :size="20" />
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            class="input-field"
            :class="{ 'input-error': errors.confirmPassword }"
            :aria-invalid="errors.confirmPassword ? 'true' : 'false'"
            :aria-describedby="errors.confirmPassword ? 'error-confirmPassword' : undefined"
            placeholder="Repite la contraseña"
            autocomplete="new-password"
            @blur="handleBlur('confirmPassword')"
            @input="handleInput('confirmPassword')"
          />
          <button
            type="button"
            class="input-toggle"
            @click="showConfirmPassword = !showConfirmPassword"
            :aria-label="showConfirmPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
          >
            <EyeIcon v-if="!showConfirmPassword" :size="20" />
            <EyeOffIcon v-else :size="20" />
          </button>
        </div>
        <span v-if="errors.confirmPassword" id="error-confirmPassword" class="field-error" role="alert">
          {{ errors.confirmPassword }}
        </span>
      </div>

      <!-- Checkbox: declaración de honor -->
      <div class="input-group">
        <label class="checkbox-label" for="honorDeclaration">
          <!-- El input real está oculto; el span.checkbox-custom es el visual -->
          <input
            id="honorDeclaration"
            v-model="form.honorDeclaration"
            type="checkbox"
            class="checkbox-input"
            :class="{ 'checkbox-error': errors.honorDeclaration }"
            :aria-invalid="errors.honorDeclaration ? 'true' : 'false'"
            :aria-describedby="errors.honorDeclaration ? 'error-honorDeclaration' : undefined"
            @blur="handleBlur('honorDeclaration')"
            @change="handleInput('honorDeclaration')"
          />
          <span class="checkbox-custom">
            <CheckIcon v-if="form.honorDeclaration" :size="14" />
          </span>
          <span class="checkbox-text">Declaro que soy mujer</span>
        </label>
        <span v-if="errors.honorDeclaration" id="error-honorDeclaration" class="field-error" role="alert">
          {{ errors.honorDeclaration }}
        </span>
      </div>

      <!-- Error general del servidor (ej: error de red) -->
      <transition name="fade">
        <div v-if="serverError" class="register-form__server-error" role="alert">
          <AlertCircleIcon :size="20" />
          <span>{{ serverError }}</span>
        </div>
      </transition>

      <!-- Botón de envío: muestra spinner mientras carga -->
      <button type="submit" class="btn-primary register-form__submit" :disabled="authStore.isLoading">
        <LoaderIcon v-if="authStore.isLoading" class="spin" :size="20" />
        <span v-else>Crear cuenta</span>
      </button>
    </div>

    <p class="register-form__footer">
      ¿Ya tienes cuenta?
      <router-link to="/login">Inicia sesión</router-link>
    </p>
  </form>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  UserIcon, MailIcon, LockIcon,
  EyeIcon, EyeOffIcon,
  AlertCircleIcon, LoaderIcon,
  CheckIcon, XIcon,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

// reactive() crea un objeto reactivo: Vue actualiza la vista cuando cambia cualquier propiedad
const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  honorDeclaration: false,
})

// Mensajes de error por campo (null = sin error)
const errors = reactive({
  username: null,
  email: null,
  password: null,
  confirmPassword: null,
  honorDeclaration: null,
})

// Registra si la usuaria ya tocó cada campo (para no mostrar errores antes de interactuar)
const touched = reactive({
  username: false,
  email: false,
  password: false,
  confirmPassword: false,
  honorDeclaration: false,
})

const serverError = ref(null)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Comprueba cada requisito de la contraseña en tiempo real
const passwordChecks = computed(() => ({
  minLength: form.password.length >= 8,
  hasUppercase: /[A-Z]/.test(form.password),
  hasNumber: /\d/.test(form.password),
}))

// Cuenta cuántos requisitos se cumplen (0, 1, 2 o 3)
const checksMet = computed(() =>
  Object.values(passwordChecks.value).filter(Boolean).length
)

// Nivel de fortaleza según los requisitos cumplidos
const strengthLevel = computed(() => {
  const levels = ['none', 'weak', 'medium', 'strong']
  return levels[checksMet.value]
})

// Porcentaje para la barra de progreso (0%, 33%, 66%, 100%)
const strengthPercent = computed(() => (checksMet.value / 3) * 100)

// Se llama cuando la usuaria sale de un campo (pierde el foco)
function handleBlur(field) {
  touched[field] = true
  validateField(field)
}

// Se llama mientras la usuaria escribe en un campo
function handleInput(field) {
  if (touched[field]) validateField(field)
  // Caso especial: si cambia la contraseña, revalidamos la confirmación
  if (field === 'password' && touched.confirmPassword && form.confirmPassword) {
    validateField('confirmPassword')
  }
}

// Valida un campo concreto y actualiza su mensaje de error
function validateField(field) {
  switch (field) {
    case 'username':
      errors.username = !form.username.trim() ? 'El nombre de usuario es obligatorio'
        : form.username.trim().length < 3 ? 'El nombre de usuario debe tener al menos 3 caracteres'
        : null
      break

    case 'email':
      errors.email = !form.email.trim() ? 'El email es obligatorio'
        : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) ? 'Introduce un email válido'
        : null
      break

    case 'password':
      errors.password = !form.password ? 'La contraseña es obligatoria'
        : !passwordChecks.value.minLength ? 'La contraseña debe tener mínimo 8 caracteres'
        : !passwordChecks.value.hasUppercase ? 'Debe contener al menos una mayúscula'
        : !passwordChecks.value.hasNumber ? 'Debe contener al menos un número'
        : null
      break

    case 'confirmPassword':
      errors.confirmPassword = !form.confirmPassword ? 'Confirma tu contraseña'
        : form.password !== form.confirmPassword ? 'Las contraseñas no coinciden'
        : null
      break

    case 'honorDeclaration':
      errors.honorDeclaration = !form.honorDeclaration
        ? 'Debes aceptar la declaración para registrarte'
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

  const result = await authStore.register({
    username: form.username.trim(),
    email: form.email.trim(),
    password: form.password,
    confirm_password: form.confirmPassword,
  })

  if (result.success) {
    router.push('/profile/setup')
  } else if (result.field) {
    errors[result.field] = result.message
    document.getElementById(result.field)?.focus()
  } else {
    serverError.value = result.message
  }
}
</script>

<style scoped>
.register-form {
  width: 100%;
  max-width: 420px;
  background-color: var(--blanco-calido);
  border: 1.5px solid var(--melocoton);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  padding: var(--space-6);
}

.register-form__header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.register-form__header h2 {
  margin-bottom: var(--space-1);
}

.register-form__subtitle {
  color: var(--texto-secundario);
  font-size: 0.875rem;
}

.register-form__fields {
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

.password-feedback {
  margin-top: var(--space-2);
}

.password-strength-bar {
  height: 4px;
  background-color: var(--melocoton);
  border-radius: var(--radius-pill);
  overflow: hidden;
  margin-bottom: var(--space-2);
}

.password-strength-fill {
  height: 100%;
  border-radius: var(--radius-pill);
  transition: width 200ms ease, background-color 200ms ease;
}

.strength-none .password-strength-fill  { width: 0% !important; }
.strength-weak .password-strength-fill  { background-color: var(--error); }
.strength-medium .password-strength-fill { background-color: var(--advertencia); }
.strength-strong .password-strength-fill { background-color: var(--exito); }

.password-checklist {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.password-checklist li {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.75rem;
  color: var(--error);
  transition: color 200ms ease;
}

.password-checklist li.met {
  color: var(--exito);
}

.register-form__submit {
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

.checkbox-input.checkbox-error + .checkbox-custom {
  border-color: var(--error);
}

.checkbox-input.checkbox-error:focus + .checkbox-custom {
  box-shadow: 0 0 0 3px rgba(224, 92, 92, 0.2);
}

.checkbox-text {
  font-size: 0.875rem;
  color: var(--marron-cacao);
  user-select: none;
}

.register-form__server-error {
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

.register-form__footer {
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
