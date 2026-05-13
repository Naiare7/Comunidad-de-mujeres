<template>
  <!-- novalidate desactiva la validación nativa del navegador para usar la nuestra -->
  <form class="reset-form" @submit.prevent="handleSubmit" novalidate>

    <div class="reset-form__header">
      <h2>Restablecer contraseña</h2>
      <p class="reset-form__subtitle">Escribe tu nueva contraseña</p>
    </div>

    <div class="reset-form__fields">

      <!-- Mensaje de éxito después de restablecer -->
      <transition name="fade">
        <div v-if="success" class="reset-form__success" role="status">
          <CheckCircleIcon :size="28" />
          <p>Contraseña restablecida correctamente</p>
          <router-link to="/login" class="btn-primary reset-form__success-btn">
            Iniciar sesión
          </router-link>
        </div>
      </transition>

      <!-- Si falta el token en la URL -->
      <template v-if="!token">
        <div class="reset-form__error-card" role="alert">
          <AlertCircleIcon :size="24" />
          <p>Enlace de recuperación inválido. Solicita un nuevo enlace.</p>
          <router-link to="/forgot-password" class="btn-primary reset-form__error-btn">
            Solicitar nuevo enlace
          </router-link>
        </div>
      </template>

      <!-- El formulario solo se muestra si hay token y aún no se ha enviado -->
      <template v-if="token && !success">

        <!-- Campo: nueva contraseña -->
        <div class="input-group">
          <label class="input-label" for="password">Nueva contraseña</label>
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

          <!-- Indicador de fortaleza -->
          <div
            v-if="touched.password || form.password.length > 0"
            class="password-feedback"
            role="status"
            aria-live="polite"
          >
            <div class="password-strength-bar" :class="'strength-' + strengthLevel">
              <div class="password-strength-fill" :style="{ width: strengthPercent + '%' }"></div>
            </div>
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

        <!-- Error general -->
        <transition name="fade">
          <div v-if="serverError" class="reset-form__server-error" role="alert">
            <AlertCircleIcon :size="20" />
            <span>{{ serverError }}</span>
          </div>
        </transition>

        <!-- Botón de envío -->
        <button type="submit" class="btn-primary reset-form__submit" :disabled="isLoading">
          <LoaderIcon v-if="isLoading" :size="20" class="spin" />
          {{ isLoading ? 'Restableciendo…' : 'Restablecer contraseña' }}
        </button>

      </template>
    </div>

    <!-- Enlace para volver al login -->
    <p class="reset-form__footer" v-if="!success">
      <router-link to="/login">&larr; Volver a iniciar sesión</router-link>
    </p>
  </form>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetchJson } from '../services/http'
import {
  LockIcon, EyeIcon, EyeOffIcon,
  AlertCircleIcon, CheckCircleIcon, LoaderIcon,
  CheckIcon, XIcon,
} from 'lucide-vue-next'

const route = useRoute()

// Leemos el token de la URL (?token=xxx)
const token = route.query.token || null

const form = reactive({
  password: '',
  confirmPassword: '',
})

const errors = reactive({
  password: null,
  confirmPassword: null,
})

const touched = reactive({
  password: false,
  confirmPassword: false,
})

const success = ref(false)
const isLoading = ref(false)  // true mientras se envía la petición al servidor
const serverError = ref(null)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Comprueba cada requisito de la contraseña en tiempo real
const passwordChecks = computed(() => ({
  minLength: form.password.length >= 8,
  hasUppercase: /[A-Z]/.test(form.password),
  hasNumber: /\d/.test(form.password),
}))

const checksMet = computed(() =>
  Object.values(passwordChecks.value).filter(Boolean).length
)

const strengthLevel = computed(() => {
  const levels = ['none', 'weak', 'medium', 'strong']
  return levels[checksMet.value]
})

const strengthPercent = computed(() => (checksMet.value / 3) * 100)

function handleBlur(field) {
  touched[field] = true
  validateField(field)
}

function handleInput(field) {
  if (touched[field]) validateField(field)
  if (field === 'password' && touched.confirmPassword && form.confirmPassword) {
    validateField('confirmPassword')
  }
}

function validateField(field) {
  switch (field) {
    case 'password':
      errors.password = !form.password ? 'La contraseña es obligatoria'
        : form.password.length < 8 ? 'La contraseña debe tener mínimo 8 caracteres'
        : !/[A-Z]/.test(form.password) ? 'Debe contener al menos una mayúscula'
        : !/\d/.test(form.password) ? 'Debe contener al menos un número'
        : null
      break

    case 'confirmPassword':
      errors.confirmPassword = !form.confirmPassword ? 'Confirma tu contraseña'
        : form.password !== form.confirmPassword ? 'Las contraseñas no coinciden'
        : null
      break
  }
}

function validateAll() {
  Object.keys(touched).forEach((field) => {
    touched[field] = true
    validateField(field)
  })
  return !Object.values(errors).some(Boolean)
}

async function handleSubmit() {
  serverError.value = null

  if (!validateAll()) return

  isLoading.value = true

  try {
    // Llamamos al endpoint de restablecimiento con el token y las nuevas contraseñas
    const { response, data } = await apiFetchJson('/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: token,
        password: form.password,
        confirm_password: form.confirmPassword,
      }),
    })

    if (response.ok) {
      success.value = true
    } else {
      // Mostramos el error que devuelve el backend (token inválido, expirado, etc.)
      serverError.value = data.detail || 'Error al restablecer la contraseña'
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
.reset-form {
  width: 100%;
  max-width: 420px;
  background-color: var(--blanco-calido);
  border: 1.5px solid var(--melocoton);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  padding: var(--space-6);
}

.reset-form__header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.reset-form__header h2 {
  margin-bottom: var(--space-1);
}

.reset-form__subtitle {
  color: var(--texto-secundario);
  font-size: 0.875rem;
}

.reset-form__fields {
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

.reset-form__submit {
  width: 100%;
  margin-top: var(--space-2);
}

.reset-form__success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  text-align: center;
  color: var(--exito);
  font-size: 0.9375rem;
  font-weight: 600;
}

.reset-form__success-btn {
  text-decoration: none;
  width: 100%;
}

.reset-form__error-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6);
  text-align: center;
  color: var(--error);
  font-size: 0.9375rem;
}

.reset-form__error-btn {
  text-decoration: none;
  width: 100%;
}

.reset-form__server-error {
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

.reset-form__footer {
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
