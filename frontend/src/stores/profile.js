// Store del flujo de personalización de perfil con Pinia.
// Guarda las selecciones de la usuaria mientras avanza por los 4 pasos.

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProfileStore = defineStore('profile', () => {
  // Paso actual (0 = Aficiones, 1 = Edad, 2 = Situación vital, 3 = Ubicación)
  const currentStep = ref(0)

  // Lista de pasos que ya han sido completados o saltados
  const completedSteps = ref([])

  // Datos que la usuaria va rellenando en cada paso
  const hobbies = ref([])           // Aficiones seleccionadas (array, selección múltiple)
  const ageRange = ref(null)        // Rango de edad (string, selección única)
  const lifeSituations = ref([])    // Situaciones vitales (array, selección múltiple)
  const location = ref({ city: '', province: '', radius: '' }) // Ubicación

  // Devuelve true si un paso concreto ya fue completado o saltado
  const isStepComplete = (step) => completedSteps.value.includes(step)

  // Devuelve true cuando los 4 pasos han sido completados o saltados
  const isAllComplete = computed(() => completedSteps.value.length === 4)

  function markStepDone(step) {
    // Añade el paso a la lista de completados si no estaba ya
    if (!completedSteps.value.includes(step)) {
      completedSteps.value.push(step)
    }
    // Avanza al siguiente paso si no estamos en el último
    if (currentStep.value < 4) {
      currentStep.value++
    }
  }

  function goToStep(step) {
    // Solo permite ir a pasos válidos (entre 0 y 4)
    if (step >= 0 && step <= 4) {
      currentStep.value = step
    }
  }

  function reset() {
    // Vuelve todo al estado inicial (útil al cerrar sesión o empezar de nuevo)
    currentStep.value = 0
    completedSteps.value = []
    hobbies.value = []
    ageRange.value = null
    lifeSituations.value = []
    location.value = { city: '', province: '', radius: '' }
  }

  return {
    currentStep,
    completedSteps,
    hobbies,
    ageRange,
    lifeSituations,
    location,
    isStepComplete,
    isAllComplete,
    // Exponemos markStepDone con los dos nombres que usa la vista (saltar y completar hacen lo mismo)
    skipStep: markStepDone,
    completeStep: markStepDone,
    goToStep,
    reset,
  }
})
