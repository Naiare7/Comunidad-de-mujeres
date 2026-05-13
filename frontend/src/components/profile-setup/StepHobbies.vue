<template>
  <div class="step-content">
    <h3 class="step-content__title">¿Qué te gusta hacer?</h3>
    <p class="step-content__desc">
      Selecciona tus aficiones para encontrar mujeres con intereses similares
    </p>

    <div class="hobbies-grid">
      <button
        v-for="hobby in hobbyOptions"
        :key="hobby.value"
        type="button"
        class="hobby-chip"
        :class="{ selected: isSelected(hobby.value) }"
        @click="toggle(hobby.value)"
      >
        <component :is="hobby.icon" :size="18" />
        <span>{{ hobby.label }}</span>
      </button>
    </div>

    <div v-if="isSelected('otras')" class="hobby-other-input">
      <label class="input-label" for="custom-hobby">¿Qué otra afición tienes?</label>
      <input
        id="custom-hobby"
        v-model="customHobby"
        type="text"
        class="input-field"
        placeholder="Ej: yoga, cocina, fotografía..."
      />
    </div>

    <div class="hobbies-count">
      <span v-if="profileStore.hobbies.length === 0">Ninguna seleccionada</span>
      <span v-else>{{ profileStore.hobbies.length }} seleccionada{{ profileStore.hobbies.length !== 1 ? 's' : '' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useProfileStore } from '../../stores/profile'
import {
  PlaneIcon,
  SunIcon,
  BookIcon,
  ClapperboardIcon,
  PaintbrushIcon,
  ScissorsIcon,
  PlusIcon,
} from 'lucide-vue-next'

const profileStore = useProfileStore()
const customHobby = ref('')

const hobbyOptions = [
  { value: 'viajar', label: 'Viajar', icon: PlaneIcon },
  { value: 'aire_libre', label: 'Aire libre', icon: SunIcon },
  { value: 'lectura', label: 'Lectura', icon: BookIcon },
  { value: 'cine', label: 'Cine', icon: ClapperboardIcon },
  { value: 'pintura', label: 'Pintura', icon: PaintbrushIcon },
  { value: 'manualidades', label: 'Manualidades', icon: ScissorsIcon },
  { value: 'otras', label: 'Otras', icon: PlusIcon },
]

function isSelected(value) {
  return profileStore.hobbies.includes(value)
}

function toggle(value) {
  const idx = profileStore.hobbies.indexOf(value)
  if (idx === -1) {
    profileStore.hobbies.push(value)
  } else {
    profileStore.hobbies.splice(idx, 1)
    if (value === 'otras') {
      customHobby.value = ''
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

.hobbies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-3);
}

.hobby-chip {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 10px 16px;
  font-family: var(--font-body);
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--marron-cacao);
  background-color: var(--lila-suave);
  border: 2px solid transparent;
  border-radius: var(--radius-pill);
  cursor: pointer;
  transition: all 150ms ease;
  -webkit-tap-highlight-color: transparent;
}

.hobby-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(92, 61, 46, 0.12);
}

.hobby-chip.selected {
  color: var(--blanco-calido);
  background-color: var(--rosa-coral);
  border-color: var(--rosa-coral);
}

.hobby-chip.selected:hover {
  background-color: var(--rosa-oscuro);
  border-color: var(--rosa-oscuro);
}

.hobby-other-input {
  margin-top: var(--space-4);
}

.hobby-other-input .input-label {
  display: block;
  margin-bottom: var(--space-2);
}

.hobbies-count {
  text-align: center;
  margin-top: var(--space-3);
  font-size: 0.75rem;
  color: var(--texto-secundario);
}

@media (max-width: 767px) {
  .hobbies-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
