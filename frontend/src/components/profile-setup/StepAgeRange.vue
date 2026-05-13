<template>
  <div class="step-content">
    <h3 class="step-content__title">¿Cuál es tu edad?</h3>
    <p class="step-content__desc">
      Indica tu rango de edad para conectar con mujeres en tu misma etapa
    </p>

    <div class="age-grid">
      <button
        v-for="range in ageRanges"
        :key="range.value"
        type="button"
        class="age-chip"
        :class="{ selected: profileStore.ageRange === range.value }"
        @click="profileStore.ageRange = range.value"
      >
        <div class="age-chip-radio">
          <div v-if="profileStore.ageRange === range.value" class="age-chip-dot" />
        </div>
        <span class="age-chip-text">{{ range.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useProfileStore } from '../../stores/profile'

const profileStore = useProfileStore()

const ageRanges = [
  { value: '18-25', label: '18 — 25 años' },
  { value: '26-35', label: '26 — 35 años' },
  { value: '36-45', label: '36 — 45 años' },
  { value: '46-55', label: '46 — 55 años' },
  { value: '56-65', label: '56 — 65 años' },
  { value: '65+', label: 'Más de 65 años' },
]
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

.age-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.age-chip {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  width: 100%;
  padding: 14px 16px;
  font-family: var(--font-body);
  font-size: 1rem;
  font-weight: 400;
  color: var(--marron-cacao);
  background-color: var(--blanco-calido);
  border: 1.5px solid var(--lila-suave);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 150ms ease;
  text-align: left;
  -webkit-tap-highlight-color: transparent;
}

.age-chip:hover {
  border-color: var(--rosa-coral);
  background-color: var(--melocoton);
}

.age-chip.selected {
  border-color: var(--rosa-coral);
  border-width: 2px;
  background-color: var(--melocoton);
  box-shadow: 0 0 0 3px rgba(244, 132, 95, 0.12);
}

.age-chip-radio {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid var(--lila-suave);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: border-color 150ms ease;
}

.age-chip.selected .age-chip-radio {
  border-color: var(--rosa-coral);
}

.age-chip-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: var(--rosa-coral);
  transition: background-color 150ms ease;
}
</style>
