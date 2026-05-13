<template>
  <div class="profile-setup">
    <div class="profile-setup__container">
      <div class="card profile-setup__card">
        <div class="profile-setup__header">
          <div class="profile-setup__icon">
            <SparklesIcon :size="32" />
          </div>
          <h2>Personaliza tu perfil</h2>
          <p class="profile-setup__subtitle">
            Cuéntanos sobre ti para que podamos mostrarte contenido relevante
          </p>
        </div>

        <div class="profile-setup__stepper">
          <div class="stepper-line"></div>
          <div
            class="stepper-step"
            v-for="(step, i) in steps"
            :key="i"
            :class="{ clickable: i <= profileStore.completedSteps.length }"
            @click="goToStepIfAllowed(i)"
          >
            <div
              class="step-dot"
              :class="{
                active: i === profileStore.currentStep,
                done: profileStore.isStepComplete(i),
              }"
            >
              <CheckIcon v-if="profileStore.isStepComplete(i)" :size="14" />
              <span v-else>{{ i + 1 }}</span>
            </div>
            <div class="step-info">
              <span class="step-label">{{ step.label }}</span>
              <span class="step-desc">{{ step.desc }}</span>
            </div>
          </div>
        </div>

        <div class="profile-setup__body">
          <transition name="step-fade" mode="out-in">
            <component :is="stepComponent" :key="profileStore.currentStep" />
          </transition>
        </div>

        <div class="profile-setup__actions">
          <button
            v-if="profileStore.currentStep > 0"
            class="btn-secondary"
            @click="prevStep"
          >
            Atrás
          </button>
          <button
            v-else
            class="btn-secondary"
            disabled
            style="visibility: hidden"
          >
            Atrás
          </button>

          <button
            class="btn-secondary"
            @click="skipStep"
            v-if="profileStore.currentStep < 4"
          >
            Saltar
          </button>

          <button
            v-if="profileStore.currentStep < 3"
            class="btn-primary"
            @click="nextStep"
          >
            Siguiente
          </button>
          <button
            v-else-if="profileStore.currentStep === 3"
            class="btn-primary"
            @click="finishSetup"
          >
            Finalizar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { SparklesIcon, CheckIcon } from 'lucide-vue-next'
import { useProfileStore } from '../stores/profile'
import StepHobbies from '../components/profile-setup/StepHobbies.vue'
import StepAgeRange from '../components/profile-setup/StepAgeRange.vue'
import StepLifeSituation from '../components/profile-setup/StepLifeSituation.vue'
import StepLocation from '../components/profile-setup/StepLocation.vue'

const router = useRouter()
const profileStore = useProfileStore()

const steps = [
  { label: 'Aficiones', desc: 'Selecciona tus intereses' },
  { label: 'Edad', desc: 'Rango de edad' },
  { label: 'Situación vital', desc: 'Tu momento actual' },
  { label: 'Ubicación', desc: 'Ciudad y radio de acción' },
]

const stepComponents = [
  StepHobbies,
  StepAgeRange,
  StepLifeSituation,
  StepLocation,
]

const stepComponent = computed(() => stepComponents[profileStore.currentStep])

function goToStepIfAllowed(i) {
  if (i <= profileStore.completedSteps.length) {
    profileStore.goToStep(i)
  }
}

function prevStep() {
  if (profileStore.currentStep > 0) {
    profileStore.goToStep(profileStore.currentStep - 1)
  }
}

function nextStep() {
  if (profileStore.currentStep < 4) {
    profileStore.completeStep(profileStore.currentStep)
  }
}

function skipStep() {
  if (profileStore.currentStep < 4) {
    profileStore.skipStep(profileStore.currentStep)
  }
}

function finishSetup() {
  profileStore.completeStep(3)
  router.push('/forums')
}
</script>

<style scoped>
.profile-setup {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
  background-color: var(--blanco-calido);
}

.profile-setup__container {
  width: 100%;
  max-width: 560px;
}

.profile-setup__card {
  padding: var(--space-8);
}

.profile-setup__header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.profile-setup__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: var(--melocoton);
  color: var(--rosa-coral);
  margin-bottom: var(--space-4);
}

.profile-setup__header h2 {
  margin-bottom: var(--space-2);
}

.profile-setup__subtitle {
  color: var(--texto-secundario);
  font-size: 0.875rem;
  max-width: 360px;
  margin: 0 auto;
}

.profile-setup__stepper {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  position: relative;
  margin-bottom: var(--space-8);
  padding-left: var(--space-4);
}

.stepper-line {
  position: absolute;
  left: 19px;
  top: 10px;
  bottom: 10px;
  width: 2px;
  background-color: var(--lila-suave);
}

.stepper-step {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
}

.stepper-step.clickable {
  cursor: pointer;
}

.stepper-step.clickable:hover .step-label {
  color: var(--rosa-coral);
}

.step-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 700;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
  background-color: var(--blanco-calido);
  border: 2px solid var(--lila-suave);
  color: var(--lila-oscuro);
  transition: all 200ms ease;
}

.step-dot.active {
  border-color: var(--rosa-coral);
  background-color: var(--rosa-coral);
  color: var(--blanco-calido);
}

.step-dot.done {
  border-color: var(--verde-menta);
  background-color: var(--verde-menta);
  color: var(--blanco-calido);
}

.step-info {
  display: flex;
  flex-direction: column;
  padding-top: var(--space-2);
}

.step-label {
  font-family: var(--font-body);
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--marron-cacao);
  transition: color 150ms ease;
}

.step-desc {
  font-size: 0.8125rem;
  color: var(--texto-secundario);
}

.profile-setup__body {
  margin-bottom: var(--space-6);
  min-height: 120px;
}

.profile-setup__actions {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
}

.profile-setup__actions .btn-primary,
.profile-setup__actions .btn-secondary {
  flex: 1;
}

.step-fade-enter-active,
.step-fade-leave-active {
  transition: opacity 200ms ease;
}

.step-fade-enter-from,
.step-fade-leave-to {
  opacity: 0;
}

@media (max-width: 767px) {
  .profile-setup {
    padding: var(--space-4);
    align-items: flex-start;
    padding-top: var(--space-8);
  }

  .profile-setup__card {
    padding: var(--space-6);
  }
}
</style>
