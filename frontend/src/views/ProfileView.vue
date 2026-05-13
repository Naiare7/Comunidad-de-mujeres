<template>
  <div class="profile-view">

    <div v-if="isLoading" class="profile-view__loading">
      <LoaderIcon :size="32" class="spin" />
      <p>Cargando perfil…</p>
    </div>

    <div v-else-if="error" class="profile-view__error" role="alert">
      <AlertCircleIcon :size="24" />
      <p>{{ error }}</p>
    </div>

    <template v-else-if="profile">

      <div class="card profile-view__card">

        <!-- Cabecera: avatar + nombre -->
        <div class="profile-view__header">
          <div class="profile-view__avatar-wrapper">
            <div class="profile-view__avatar" :style="{ backgroundColor: avatarColor }" @click="triggerFileInput">
              <img v-if="avatarSrc" :src="avatarSrc" :alt="'Avatar de ' + profile.username" class="profile-view__avatar-img" />
              <span v-else class="profile-view__initials">{{ initials }}</span>
              <div class="profile-view__avatar-overlay">
                <CameraIcon :size="22" />
              </div>
            </div>
            <button class="profile-view__avatar-btn" @click="triggerFileInput">
              <CameraIcon :size="14" />
              {{ profile.avatar_url ? 'Cambiar foto' : 'Añadir foto' }}
            </button>
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              class="profile-view__file-input"
              @change="handleFileChange"
            />
            <p v-if="uploadError" class="profile-view__upload-error" role="alert">
              {{ uploadError }}
            </p>
            <p v-if="isUploading" class="profile-view__uploading">
              <LoaderIcon :size="14" class="spin" /> Subiendo…
            </p>
          </div>
          <h2>{{ profile.username }}</h2>
          <p class="profile-view__email">{{ profile.email }}</p>
        </div>

        <!-- Bio -->
        <div class="profile-view__section">
          <div class="profile-view__section-title">
            <FileTextIcon :size="18" />
            <span>Sobre mí</span>
            <span class="profile-view__vis-badge" :title="visibilityLabel('bio')">
              <GlobeIcon v-if="getVisibility('bio') === 'public'" :size="14" />
              <LockIcon v-else :size="14" />
            </span>
            <button v-if="editing !== 'bio'" class="profile-view__edit-btn" @click="startEdit('bio')">
              <EditIcon :size="14" /> Editar
            </button>
          </div>
          <template v-if="editing !== 'bio'">
            <p v-if="profile.bio" class="profile-view__bio">{{ profile.bio }}</p>
            <p v-else class="profile-view__empty">Añade una biografía para que otras mujeres te conozcan</p>
          </template>
          <template v-else>
            <textarea v-model="draftBio" class="profile-view__textarea" rows="4" placeholder="Cuéntanos sobre ti…"></textarea>
            <div class="profile-view__vis-toggle">
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.bio === 'public' }" @click="draftVisibility.bio = 'public'">
                <GlobeIcon :size="14" /> Visible
              </button>
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.bio === 'private' }" @click="draftVisibility.bio = 'private'">
                <LockIcon :size="14" /> Solo yo
              </button>
            </div>
            <div class="profile-view__edit-actions">
              <p v-if="saveError" class="profile-view__edit-error" role="alert">{{ saveError }}</p>
              <button class="btn-primary btn-small" @click="saveEdit" :disabled="isSaving">
                <LoaderIcon v-if="isSaving" :size="14" class="spin" />
                Guardar
              </button>
              <button class="btn-secondary btn-small" @click="cancelEdit">Cancelar</button>
            </div>
          </template>
        </div>

        <!-- Aficiones -->
        <div class="profile-view__section">
          <div class="profile-view__section-title">
            <HeartIcon :size="18" />
            <span>Aficiones</span>
            <span class="profile-view__vis-badge" :title="visibilityLabel('hobbies')">
              <GlobeIcon v-if="getVisibility('hobbies') === 'public'" :size="14" />
              <LockIcon v-else :size="14" />
            </span>
            <button v-if="editing !== 'hobbies'" class="profile-view__edit-btn" @click="startEdit('hobbies')">
              <EditIcon :size="14" /> Editar
            </button>
          </div>
          <template v-if="editing !== 'hobbies'">
            <div v-if="profile.hobbies && profile.hobbies.length > 0" class="profile-view__chips">
              <span v-for="hobby in profile.hobbies" :key="hobby" class="chip">{{ getHobbyLabel(hobby) }}</span>
            </div>
            <p v-else class="profile-view__empty">Selecciona tus aficiones para conectar con otras mujeres</p>
          </template>
          <template v-else>
            <div class="profile-view__chip-group">
              <button
                v-for="opt in HOBBY_OPTIONS"
                :key="opt.value"
                type="button"
                class="chip chip--toggle"
                :class="{ 'chip--selected': draftHobbies.includes(opt.value) }"
                @click="toggleDraftHobby(opt.value)"
              >
                {{ opt.label }}
              </button>
            </div>
            <div class="profile-view__vis-toggle">
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.hobbies === 'public' }" @click="draftVisibility.hobbies = 'public'">
                <GlobeIcon :size="14" /> Visible
              </button>
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.hobbies === 'private' }" @click="draftVisibility.hobbies = 'private'">
                <LockIcon :size="14" /> Solo yo
              </button>
            </div>
            <div class="profile-view__edit-actions">
              <p v-if="saveError" class="profile-view__edit-error" role="alert">{{ saveError }}</p>
              <button class="btn-primary btn-small" @click="saveEdit" :disabled="isSaving">
                <LoaderIcon v-if="isSaving" :size="14" class="spin" />
                Guardar
              </button>
              <button class="btn-secondary btn-small" @click="cancelEdit">Cancelar</button>
            </div>
          </template>
        </div>

        <!-- Rango de edad -->
        <div class="profile-view__section">
          <div class="profile-view__section-title">
            <CalendarIcon :size="18" />
            <span>Edad</span>
            <span class="profile-view__vis-badge" :title="visibilityLabel('age_range')">
              <GlobeIcon v-if="getVisibility('age_range') === 'public'" :size="14" />
              <LockIcon v-else :size="14" />
            </span>
            <button v-if="editing !== 'age'" class="profile-view__edit-btn" @click="startEdit('age')">
              <EditIcon :size="14" /> Editar
            </button>
          </div>
          <template v-if="editing !== 'age'">
            <p v-if="profile.age_range" class="profile-view__text">{{ getAgeLabel(profile.age_range) }}</p>
            <p v-else class="profile-view__empty">Indica tu rango de edad</p>
          </template>
          <template v-else>
            <div class="profile-view__radio-group">
              <button
                v-for="r in AGE_RANGES"
                :key="r.value"
                type="button"
                class="profile-view__radio-chip"
                :class="{ selected: draftAgeRange === r.value }"
                @click="draftAgeRange = r.value"
              >
                <span class="profile-view__radio-circle">
                  <span v-if="draftAgeRange === r.value" class="profile-view__radio-dot"></span>
                </span>
                <span>{{ r.label }}</span>
              </button>
            </div>
            <div class="profile-view__vis-toggle">
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.age_range === 'public' }" @click="draftVisibility.age_range = 'public'">
                <GlobeIcon :size="14" /> Visible
              </button>
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.age_range === 'private' }" @click="draftVisibility.age_range = 'private'">
                <LockIcon :size="14" /> Solo yo
              </button>
            </div>
            <div class="profile-view__edit-actions">
              <p v-if="saveError" class="profile-view__edit-error" role="alert">{{ saveError }}</p>
              <button class="btn-primary btn-small" @click="saveEdit" :disabled="isSaving">
                <LoaderIcon v-if="isSaving" :size="14" class="spin" />
                Guardar
              </button>
              <button class="btn-secondary btn-small" @click="cancelEdit">Cancelar</button>
            </div>
          </template>
        </div>

        <!-- Situación vital -->
        <div class="profile-view__section">
          <div class="profile-view__section-title">
            <UsersIcon :size="18" />
            <span>Situación vital</span>
            <span class="profile-view__vis-badge" :title="visibilityLabel('life_situations')">
              <GlobeIcon v-if="getVisibility('life_situations') === 'public'" :size="14" />
              <LockIcon v-else :size="14" />
            </span>
            <button v-if="editing !== 'situation'" class="profile-view__edit-btn" @click="startEdit('situation')">
              <EditIcon :size="14" /> Editar
            </button>
          </div>
          <template v-if="editing !== 'situation'">
            <div v-if="profile.life_situations && profile.life_situations.length > 0" class="profile-view__chips">
              <span v-for="s in profile.life_situations" :key="s" class="chip">{{ getSituationLabel(s) }}</span>
            </div>
            <p v-else class="profile-view__empty">Cuéntanos tu momento actual</p>
          </template>
          <template v-else>
            <div class="profile-view__chip-group">
              <button
                v-for="s in SITUATION_OPTIONS"
                :key="s.value"
                type="button"
                class="chip chip--toggle"
                :class="{ 'chip--selected': draftLifeSituations.includes(s.value) }"
                @click="toggleDraftSituation(s.value)"
              >
                <span v-if="draftLifeSituations.includes(s.value)" class="chip__check">
                  <CheckIcon :size="12" />
                </span>
                {{ s.label }}
              </button>
            </div>
            <div class="profile-view__vis-toggle">
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.life_situations === 'public' }" @click="draftVisibility.life_situations = 'public'">
                <GlobeIcon :size="14" /> Visible
              </button>
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.life_situations === 'private' }" @click="draftVisibility.life_situations = 'private'">
                <LockIcon :size="14" /> Solo yo
              </button>
            </div>
            <div class="profile-view__edit-actions">
              <p v-if="saveError" class="profile-view__edit-error" role="alert">{{ saveError }}</p>
              <button class="btn-primary btn-small" @click="saveEdit" :disabled="isSaving">
                <LoaderIcon v-if="isSaving" :size="14" class="spin" />
                Guardar
              </button>
              <button class="btn-secondary btn-small" @click="cancelEdit">Cancelar</button>
            </div>
          </template>
        </div>

        <!-- Ubicación -->
        <div class="profile-view__section">
          <div class="profile-view__section-title">
            <MapPinIcon :size="18" />
            <span>Ubicación</span>
            <span class="profile-view__vis-badge" :title="visibilityLabel('location')">
              <GlobeIcon v-if="getVisibility('location') === 'public'" :size="14" />
              <LockIcon v-else :size="14" />
            </span>
            <button v-if="editing !== 'location'" class="profile-view__edit-btn" @click="startEdit('location')">
              <EditIcon :size="14" /> Editar
            </button>
          </div>
          <template v-if="editing !== 'location'">
            <p v-if="profile.city || profile.province" class="profile-view__text">
              {{ [profile.city, profile.province].filter(Boolean).join(', ') }}
            </p>
            <p v-else class="profile-view__empty">Añade tu ubicación para descubrir planes cerca de ti</p>
          </template>
          <template v-else>
            <div class="profile-view__location-fields">
              <div class="input-group">
                <label class="input-label" for="edit-city">Ciudad</label>
                <div class="input-wrapper">
                  <MapPinIcon class="input-icon" :size="20" />
                  <input
                    id="edit-city"
                    v-model="draftCity"
                    type="text"
                    class="input-field"
                    list="city-suggestions"
                    placeholder="Ej: Madrid, Barcelona…"
                    autocomplete="off"
                  />
                </div>
                <datalist id="city-suggestions">
                  <option v-for="c in CITY_OPTIONS" :key="c" :value="c" />
                </datalist>
              </div>
              <div class="input-group">
                <label class="input-label" for="edit-province">Provincia</label>
                <div class="input-wrapper input-wrapper--select">
                  <MapPinIcon class="input-icon" :size="20" />
                  <select id="edit-province" v-model="draftProvince" class="input-field input-select">
                    <option value="" disabled selected>Selecciona una provincia</option>
                    <option v-for="p in PROVINCES" :key="p" :value="p">{{ p }}</option>
                  </select>
                  <ChevronDownIcon class="input-chevron" :size="20" />
                </div>
              </div>
            </div>
            <div class="profile-view__vis-toggle">
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.location === 'public' }" @click="draftVisibility.location = 'public'">
                <GlobeIcon :size="14" /> Visible
              </button>
              <button type="button" class="vis-btn" :class="{ active: draftVisibility.location === 'private' }" @click="draftVisibility.location = 'private'">
                <LockIcon :size="14" /> Solo yo
              </button>
            </div>
            <div class="profile-view__edit-actions">
              <p v-if="saveError" class="profile-view__edit-error" role="alert">{{ saveError }}</p>
              <button class="btn-primary btn-small" @click="saveEdit" :disabled="isSaving">
                <LoaderIcon v-if="isSaving" :size="14" class="spin" />
                Guardar
              </button>
              <button class="btn-secondary btn-small" @click="cancelEdit">Cancelar</button>
            </div>
          </template>
        </div>

      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { apiFetchJson, apiFetch } from '../services/http'
import {
  LoaderIcon,
  AlertCircleIcon,
  FileTextIcon,
  HeartIcon,
  CalendarIcon,
  UsersIcon,
  MapPinIcon,
  CameraIcon,
  EditIcon,
  ChevronDownIcon,
  CheckIcon,
  GlobeIcon,
  LockIcon,
} from 'lucide-vue-next'

// ─── Datos del perfil ─────────────────────────────────────────────────────

const profile = ref(null)
const isLoading = ref(true)
const error = ref(null)

// ─── Avatar ───────────────────────────────────────────────────────────────

const fileInputRef = ref(null)
const avatarPreview = ref(null)
const isUploading = ref(false)
const uploadError = ref(null)

const avatarSrc = computed(() => avatarPreview.value || profile.value?.avatar_url || null)

const initials = computed(() => {
  if (!profile.value) return ''
  const name = profile.value.username
  const parts = name.split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.slice(0, 2).toUpperCase()
})

const AVATAR_COLORS = [
  '#F4845F', '#C9B8E8', '#A8D5BA', '#FDDCB5',
  '#FFF0A0', '#E8B4C8', '#B4D8E8', '#D4A8E8',
]

const avatarColor = computed(() => {
  if (!profile.value) return AVATAR_COLORS[0]
  const sum = profile.value.username.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  return AVATAR_COLORS[sum % AVATAR_COLORS.length]
})

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
  avatarPreview.value = URL.createObjectURL(file)
  isUploading.value = true
  uploadError.value = null
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiFetch('/users/me/avatar', {
      method: 'POST',
      body: formData,
    })
    const data = await response.json()
    if (response.ok) {
      profile.value.avatar_url = data.avatar_url
      avatarPreview.value = null
    } else {
      uploadError.value = data.detail || 'Error al subir la imagen'
      avatarPreview.value = null
    }
  } catch {
    uploadError.value = 'Error de conexión'
    avatarPreview.value = null
  } finally {
    isUploading.value = false
    event.target.value = ''
  }
}

onUnmounted(() => {
  if (avatarPreview.value) URL.revokeObjectURL(avatarPreview.value)
})

// ─── Edición inline ───────────────────────────────────────────────────────

const editing = ref(null)           // null | 'bio' | 'hobbies' | 'age' | 'situation' | 'location'
const isSaving = ref(false)
const saveError = ref(null)

// Valores temporales mientras se edita
const draftBio = ref('')
const draftHobbies = ref([])
const draftAgeRange = ref('')
const draftLifeSituations = ref([])
const draftCity = ref('')
const draftProvince = ref('')
const draftVisibility = ref({})    // Configuración de visibilidad temporal

// Opciones para los selectores
const HOBBY_OPTIONS = [
  { value: 'viajar', label: 'Viajar' },
  { value: 'aire_libre', label: 'Aire libre' },
  { value: 'lectura', label: 'Lectura' },
  { value: 'cine', label: 'Cine' },
  { value: 'pintura', label: 'Pintura' },
  { value: 'manualidades', label: 'Manualidades' },
  { value: 'otras', label: 'Otras' },
]

const AGE_RANGES = [
  { value: '18-25', label: '18 — 25 años' },
  { value: '26-35', label: '26 — 35 años' },
  { value: '36-45', label: '36 — 45 años' },
  { value: '46-55', label: '46 — 55 años' },
  { value: '56-65', label: '56 — 65 años' },
  { value: '65+', label: 'Más de 65 años' },
]

const SITUATION_OPTIONS = [
  { value: 'madre_primeriza', label: 'Madre primeriza' },
  { value: 'divorciada_separada', label: 'Divorciada / Separada' },
  { value: 'nido_vacio', label: 'Nido vacío' },
  { value: 'viuda', label: 'Viuda' },
  { value: 'buscando_amistades', label: 'Buscando nuevas amistades' },
  { value: 'nueva_ciudad', label: 'Nueva en la ciudad / pueblo' },
  { value: 'otras', label: 'Otras' },
]

const PROVINCES = [
  'Álava', 'Albacete', 'Alicante', 'Almería', 'Asturias', 'Ávila', 'Badajoz',
  'Barcelona', 'Burgos', 'Cáceres', 'Cádiz', 'Cantabria', 'Castellón',
  'Ciudad Real', 'Córdoba', 'A Coruña', 'Cuenca', 'Girona', 'Granada',
  'Guadalajara', 'Guipúzcoa', 'Huelva', 'Huesca', 'Illes Balears', 'Jaén',
  'León', 'Lleida', 'Lugo', 'Madrid', 'Málaga', 'Murcia', 'Navarra',
  'Ourense', 'Palencia', 'Las Palmas', 'Pontevedra', 'La Rioja', 'Salamanca',
  'Santa Cruz de Tenerife', 'Segovia', 'Sevilla', 'Soria', 'Tarragona',
  'Teruel', 'Toledo', 'Valencia', 'Valladolid', 'Vizcaya', 'Zamora', 'Zaragoza',
]

const CITY_OPTIONS = [
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

// Visibilidad por defecto para cada campo del perfil
const DEFAULT_VISIBILITY = {
  bio: 'public',
  hobbies: 'public',
  age_range: 'public',
  life_situations: 'public',
  location: 'public',
}

// Devuelve la visibilidad de un campo (con fallback a 'public' si no está configurado)
function getVisibility(field) {
  return profile.value?.visibility?.[field] || 'public'
}

// Texto descriptivo para el tooltip del badge de visibilidad
function visibilityLabel(field) {
  return getVisibility(field) === 'public'
    ? 'Visible para otras mujeres'
    : 'Solo visible para ti'
}

// Convierte valor almacenado a label para mostrar
function getHobbyLabel(value) {
  return HOBBY_OPTIONS.find(o => o.value === value)?.label || value
}

function getAgeLabel(value) {
  return AGE_RANGES.find(r => r.value === value)?.label || value
}

function getSituationLabel(value) {
  return SITUATION_OPTIONS.find(s => s.value === value)?.label || value
}

// Alterna un valor en un array del draft (para hobbies, life_situations)
function toggleDraftHobby(value) {
  const idx = draftHobbies.value.indexOf(value)
  if (idx === -1) draftHobbies.value.push(value)
  else draftHobbies.value.splice(idx, 1)
}

function toggleDraftSituation(value) {
  const idx = draftLifeSituations.value.indexOf(value)
  if (idx === -1) draftLifeSituations.value.push(value)
  else draftLifeSituations.value.splice(idx, 1)
}

// Inicia la edición de una sección: copia los valores actuales a los drafts
function startEdit(section) {
  draftBio.value = profile.value.bio || ''
  draftHobbies.value = [...(profile.value.hobbies || [])]
  draftAgeRange.value = profile.value.age_range || ''
  draftLifeSituations.value = [...(profile.value.life_situations || [])]
  draftCity.value = profile.value.city || ''
  draftProvince.value = profile.value.province || ''
  // Copiamos la visibilidad actual (o los defaults si no existe)
  draftVisibility.value = { ...DEFAULT_VISIBILITY, ...(profile.value.visibility || {}) }
  saveError.value = null
  editing.value = section
}

// Cancela la edición sin guardar
function cancelEdit() {
  editing.value = null
  saveError.value = null
}

// Guarda los cambios de la sección que se está editando
async function saveEdit() {
  isSaving.value = true
  saveError.value = null

  // Construimos el payload según qué sección estamos editando
  let payload = {}
  switch (editing.value) {
    case 'bio':
      payload = { bio: draftBio.value }
      break
    case 'hobbies':
      payload = { hobbies: draftHobbies.value }
      break
    case 'age':
      payload = { age_range: draftAgeRange.value }
      break
    case 'situation':
      payload = { life_situations: draftLifeSituations.value }
      break
    case 'location':
      payload = { city: draftCity.value, province: draftProvince.value }
      break
  }

  // Incluimos la configuración de visibilidad completa (se actualiza con cada guardado)
  payload.visibility = { ...draftVisibility.value }

  try {
    const { response, data } = await apiFetchJson('/users/me/profile', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (response.ok) {
      // Actualizamos el perfil con los datos que devuelve el backend
      profile.value = data
      editing.value = null
    } else {
      saveError.value = data.detail || 'Error al guardar los cambios'
    }
  } catch {
    saveError.value = 'Error de conexión. Comprueba tu conexión a internet.'
  } finally {
    isSaving.value = false
  }
}

// ─── Carga inicial ────────────────────────────────────────────────────────

onMounted(async () => {
  try {
    const { response, data } = await apiFetchJson('/users/me/profile')
    if (response.ok) {
      profile.value = data
    } else {
      error.value = data.detail || 'Error al cargar el perfil'
    }
  } catch {
    error.value = 'Error de conexión. Comprueba tu conexión a internet.'
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--space-6) var(--space-4);
  background-color: var(--blanco-calido);
}

.profile-view__card {
  width: 100%;
  max-width: 560px;
  padding: var(--space-8);
}

/* ─── Cabecera ─────────────────────────────────────────────────────────── */

.profile-view__header {
  text-align: center;
  margin-bottom: var(--space-8);
  padding-bottom: var(--space-6);
  border-bottom: 1.5px solid var(--melocoton);
}

.profile-view__avatar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--space-4);
}

.profile-view__avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.profile-view__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.profile-view__avatar-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 150ms ease;
  border-radius: 50%;
}

.profile-view__avatar:hover .profile-view__avatar-overlay {
  opacity: 1;
}

.profile-view__avatar-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  margin-top: var(--space-2);
  background: none;
  border: none;
  color: var(--lila-oscuro);
  font-family: var(--font-body);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  transition: all 150ms ease;
}

.profile-view__avatar-btn:hover {
  background-color: var(--melocoton);
  color: var(--rosa-coral);
}

.profile-view__file-input {
  display: none;
}

.profile-view__upload-error {
  color: var(--error);
  font-size: 0.8125rem;
  margin-top: var(--space-1);
}

.profile-view__uploading {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--lila-oscuro);
  font-size: 0.8125rem;
  margin-top: var(--space-1);
}

.profile-view__initials {
  font-family: var(--font-display);
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--blanco-calido);
}

.profile-view__header h2 {
  margin-bottom: var(--space-1);
}

.profile-view__email {
  color: var(--texto-secundario);
  font-size: 0.875rem;
}

/* ─── Secciones ────────────────────────────────────────────────────────── */

.profile-view__section {
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-5);
  border-bottom: 1px solid var(--melocoton);
}

.profile-view__section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.profile-view__section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--lila-oscuro);
  margin-bottom: var(--space-3);
}

/* ─── Badge de visibilidad (en view mode) ─────────────────────────────── */

.profile-view__vis-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--melocoton);
  color: var(--lila-oscuro);
  cursor: help;
}

/* ─── Toggle de visibilidad (en edit mode) ───────────────────────────── */

.profile-view__vis-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  padding: var(--space-2);
  background-color: var(--melocoton);
  border-radius: var(--radius-sm);
}

.vis-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 600;
  border: 2px solid transparent;
  border-radius: var(--radius-pill);
  cursor: pointer;
  transition: all 150ms ease;
  background-color: transparent;
  color: var(--marron-cacao);
}

.vis-btn.active {
  background-color: var(--blanco-calido);
  border-color: var(--lila-suave);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.vis-btn:hover:not(.active) {
  color: var(--rosa-coral);
}

/* ─── Botón de editar ─────────────────────────────────────────────────── */

.profile-view__edit-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  background: none;
  border: none;
  color: var(--lila-oscuro);
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  transition: all 150ms ease;
}

.profile-view__edit-btn:hover {
  background-color: var(--melocoton);
  color: var(--rosa-coral);
}

/* ─── Estado vacío ─────────────────────────────────────────────────────── */

.profile-view__empty {
  color: var(--texto-secundario);
  font-size: 0.875rem;
  font-style: italic;
}

/* ─── Texto de visualización ───────────────────────────────────────────── */

.profile-view__bio {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--marron-cacao);
}

.profile-view__text {
  font-size: 0.9375rem;
  color: var(--marron-cacao);
}

/* ─── Chips ────────────────────────────────────────────────────────────── */

.profile-view__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  background-color: var(--melocoton);
  color: var(--marron-cacao);
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: var(--radius-pill);
  cursor: default;
}

.chip--toggle {
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 150ms ease;
}

.chip--toggle:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(92, 61, 46, 0.12);
}

.chip--selected {
  background-color: var(--rosa-coral);
  color: var(--blanco-calido);
  border-color: var(--rosa-coral);
}

.chip__check {
  display: inline-flex;
}

/* ─── Grupo de chips en edición ────────────────────────────────────────── */

.profile-view__chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

/* ─── Radio group (edad) ───────────────────────────────────────────────── */

.profile-view__radio-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.profile-view__radio-chip {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: 12px 16px;
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--marron-cacao);
  background-color: var(--blanco-calido);
  border: 1.5px solid var(--lila-suave);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 150ms ease;
  text-align: left;
}

.profile-view__radio-chip:hover {
  border-color: var(--rosa-coral);
  background-color: var(--melocoton);
}

.profile-view__radio-chip.selected {
  border-color: var(--rosa-coral);
  border-width: 2px;
  background-color: var(--melocoton);
  box-shadow: 0 0 0 3px rgba(244, 132, 95, 0.12);
}

.profile-view__radio-circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--lila-suave);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: border-color 150ms ease;
}

.profile-view__radio-chip.selected .profile-view__radio-circle {
  border-color: var(--rosa-coral);
}

.profile-view__radio-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: var(--rosa-coral);
}

/* ─── Campos de ubicación en edición ───────────────────────────────────── */

.profile-view__location-fields {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

/* ─── Textarea ─────────────────────────────────────────────────────────── */

.profile-view__textarea {
  width: 100%;
  padding: var(--space-3);
  font-family: var(--font-body);
  font-size: 0.875rem;
  color: var(--marron-cacao);
  background-color: var(--blanco-calido);
  border: 1.5px solid var(--melocoton);
  border-radius: var(--radius-sm);
  resize: vertical;
  min-height: 80px;
  transition: border-color 150ms ease;
  box-sizing: border-box;
  margin-bottom: var(--space-4);
}

.profile-view__textarea:focus {
  outline: none;
  border-color: var(--rosa-coral);
  box-shadow: 0 0 0 3px rgba(244, 132, 95, 0.12);
}

/* ─── Acciones de edición ──────────────────────────────────────────────── */

.profile-view__edit-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.profile-view__edit-error {
  flex-basis: 100%;
  color: var(--error);
  font-size: 0.8125rem;
  margin-bottom: var(--space-1);
}

/* Botones pequeños para edición inline */
.btn-small {
  padding: var(--space-1) var(--space-4);
  font-size: 0.8125rem;
  border-radius: var(--radius-sm);
}

/* ─── Loading / Error ──────────────────────────────────────────────────── */

.profile-view__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding-top: var(--space-16);
  color: var(--lila-oscuro);
  font-size: 0.9375rem;
}

.profile-view__error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding-top: var(--space-16);
  color: var(--error);
  font-size: 0.9375rem;
  text-align: center;
}

/* ─── Responsive ───────────────────────────────────────────────────────── */

@media (max-width: 767px) {
  .profile-view {
    padding: var(--space-4);
    padding-top: var(--space-6);
  }

  .profile-view__card {
    padding: var(--space-6);
  }
}
</style>
