<template>
  <div class="step-content">
    <h3 class="step-content__title">¿Dónde te encuentras?</h3>
    <p class="step-content__desc">
      Indica tu ubicación para descubrir planes y mujeres cerca de ti
    </p>

    <div class="location-fields">
      <div class="input-group">
        <label class="input-label" for="city">Ciudad</label>
        <div class="input-wrapper">
          <MapPinIcon class="input-icon" :size="20" />
          <input
            id="city"
            v-model="profileStore.location.city"
            type="text"
            class="input-field"
            list="city-suggestions"
            placeholder="Ej: Madrid, Barcelona, Sevilla..."
            autocomplete="off"
          />
        </div>
        <datalist id="city-suggestions">
          <option v-for="city in cityOptions" :key="city" :value="city" />
        </datalist>
      </div>

      <div class="input-group">
        <label class="input-label" for="province">Provincia</label>
        <div class="input-wrapper input-wrapper--select">
          <MapPinIcon class="input-icon" :size="20" />
          <select
            id="province"
            v-model="profileStore.location.province"
            class="input-field input-select"
          >
            <option value="" disabled selected>Selecciona una provincia</option>
            <option v-for="p in provinces" :key="p" :value="p">{{ p }}</option>
          </select>
          <ChevronDownIcon class="input-chevron" :size="20" />
        </div>
      </div>

      <div class="input-group">
        <label class="input-label" for="radius">Radio de acción <span class="label-optional">(opcional)</span></label>
        <div class="input-wrapper">
          <NavigationIcon class="input-icon" :size="20" />
          <input
            id="radius"
            v-model.number="profileStore.location.radius"
            type="number"
            class="input-field"
            placeholder="Distancia en km"
            min="0"
            max="500"
          />
          <span class="input-suffix">km</span>
        </div>
        <div class="radius-hint">
          ¿Hasta qué distancia te gustaría desplazarte para conocer a otras mujeres?
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useProfileStore } from '../../stores/profile'
import { MapPinIcon, NavigationIcon, ChevronDownIcon } from 'lucide-vue-next'

const profileStore = useProfileStore()

const provinces = [
  'Álava', 'Albacete', 'Alicante', 'Almería', 'Asturias', 'Ávila', 'Badajoz',
  'Barcelona', 'Burgos', 'Cáceres', 'Cádiz', 'Cantabria', 'Castellón',
  'Ciudad Real', 'Córdoba', 'A Coruña', 'Cuenca', 'Girona', 'Granada',
  'Guadalajara', 'Guipúzcoa', 'Huelva', 'Huesca', 'Illes Balears', 'Jaén',
  'León', 'Lleida', 'Lugo', 'Madrid', 'Málaga', 'Murcia', 'Navarra',
  'Ourense', 'Palencia', 'Las Palmas', 'Pontevedra', 'La Rioja', 'Salamanca',
  'Santa Cruz de Tenerife', 'Segovia', 'Sevilla', 'Soria', 'Tarragona',
  'Teruel', 'Toledo', 'Valencia', 'Valladolid', 'Vizcaya', 'Zamora', 'Zaragoza',
]

const cityOptions = [
  'A Coruña', 'Albacete', 'Alicante', 'Almería', 'Badalona', 'Barcelona',
  'Bilbao', 'Burgos', 'Cáceres', 'Cádiz', 'Cartagena', 'Castellón de la Plana',
  'Ciudad Real', 'Córdoba', 'Cuenca', 'Donostia-San Sebastián', 'Elche',
  'Gijón', 'Girona', 'Granada', 'Guadalajara', 'Huelva', 'Huesca',
  'Jaén', 'Jerez de la Frontera', 'Las Palmas de Gran Canaria', 'León',
  'Lleida', 'Logroño', 'Lugo', 'Madrid', 'Málaga', 'Marbella', 'Murcia',
  'Ourense', 'Oviedo', 'Palencia', 'Palma', 'Pamplona', 'Pontevedra',
  'Salamanca', 'San Cristóbal de La Laguna', 'Santander', 'Santiago de Compostela',
  'Segovia', 'Sevilla', 'Soria', 'Tarragona', 'Terrassa', 'Teruel',
  'Toledo', 'Valencia', 'Valladolid', 'Vigo', 'Vitoria-Gasteiz', 'Zamora',
  'Zaragoza',
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

.location-fields {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
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

.input-field.input-select {
  appearance: none;
  padding-right: 44px;
  cursor: pointer;
}

.input-chevron {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--lila-oscuro);
  pointer-events: none;
}

.input-suffix {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.875rem;
  color: var(--texto-secundario);
  pointer-events: none;
}

.label-optional {
  font-weight: 400;
  color: var(--texto-secundario);
}

.radius-hint {
  margin-top: var(--space-1);
  font-size: 0.75rem;
  color: var(--texto-secundario);
}
</style>
