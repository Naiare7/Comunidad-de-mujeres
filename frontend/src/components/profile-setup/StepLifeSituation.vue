<template>
  <div class="step-content">
    <h3 class="step-content__title">¿Cuál es tu situación vital?</h3>
    <p class="step-content__desc">
      Cuéntanos tu momento actual para ofrecerte contenido relevante
    </p>

    <div class="situation-list">
      <button
        v-for="s in situations"
        :key="s.value"
        type="button"
        class="situation-chip"
        :class="{ selected: isSelected(s.value) }"
        @click="toggle(s.value)"
      >
        <span class="situation-checkbox">
          <CheckIcon v-if="isSelected(s.value)" :size="14" />
        </span>
        <span>{{ s.label }}</span>
      </button>
    </div>

    <div v-if="isSelected('otras')" class="situation-other">
      <label class="input-label" for="custom-situation">Cuéntanos más</label>
      <input
        id="custom-situation"
        v-model="customSituation"
        type="text"
        class="input-field"
        placeholder="Describe tu situación..."
      />
    </div>

    <div class="situation-count">
      <span v-if="profileStore.lifeSituations.length === 0">Ninguna seleccionada</span>
      <span v-else>{{ profileStore.lifeSituations.length }} seleccionada{{ profileStore.lifeSituations.length !== 1 ? 's' : '' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useProfileStore } from '../../stores/profile'
import { CheckIcon } from 'lucide-vue-next'

const profileStore = useProfileStore()
const customSituation = ref('')

const situations = [
  { value: 'madre_primeriza', label: 'Madre primeriza' },
  { value: 'divorciada_separada', label: 'Divorciada / Separada' },
  { value: 'nido_vacio', label: 'Nido vacío' },
  { value: 'viuda', label: 'Viuda' },
  { value: 'buscando_amistades', label: 'Buscando nuevas amistades' },
  { value: 'nueva_ciudad', label: 'Nueva en la ciudad / pueblo' },
  { value: 'otras', label: 'Otras' },
]

function isSelected(value) {
  return profileStore.lifeSituations.includes(value)
}

function toggle(value) {
  const idx = profileStore.lifeSituations.indexOf(value)
  if (idx === -1) {
    profileStore.lifeSituations.push(value)
  } else {
    profileStore.lifeSituations.splice(idx, 1)
    if (value === 'otras') {
      customSituation.value = ''
    }
  }
}
</script>

<style scoped>
.step-content {
  padding: var(--space-4) 0;
}

.step-content__title {
  margin-bottom: var(--space-2);
}

.step-content__desc {
  color: var(--texto-secundario);
  font-size: 0.875rem;
  margin-bottom: var(--space-6);
}

.situation-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.situation-chip {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: 12px 16px;
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--marron-cacao);
  background-color: var(--lila-suave);
  border: 2px solid transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 150ms ease;
  text-align: left;
  -webkit-tap-highlight-color: transparent;
}

.situation-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(92, 61, 46, 0.12);
}

.situation-chip.selected {
  color: var(--blanco-calido);
  background-color: var(--rosa-coral);
  border-color: var(--rosa-coral);
}

.situation-chip.selected:hover {
  background-color: var(--rosa-oscuro);
  border-color: var(--rosa-oscuro);
}

.situation-checkbox {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 2px solid rgba(92, 61, 46, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 150ms ease;
  background-color: transparent;
  color: transparent;
}

.situation-chip.selected .situation-checkbox {
  background-color: var(--blanco-calido);
  border-color: var(--blanco-calido);
  color: var(--rosa-coral);
}

.situation-other {
  margin-top: var(--space-4);
}

.situation-other .input-label {
  display: block;
  margin-bottom: var(--space-2);
}

.situation-count {
  text-align: center;
  margin-top: var(--space-3);
  font-size: 0.75rem;
  color: var(--texto-secundario);
}
</style>
