<template>
  <div class="forums-view">
    <h1 class="forums-view__title">Foros</h1>
    <p class="forums-view__subtitle">Encuentra tu espacio y participa en las conversaciones</p>

    <!-- Mientras se cargan los datos mostramos un spinner -->
    <div v-if="isLoading" class="forums-view__loading">
      <LoaderIcon :size="32" class="spin" />
      <p>Cargando foros…</p>
    </div>

    <!-- Si hay error al cargar mostramos el mensaje -->
    <div v-else-if="error" class="forums-view__error" role="alert">
      <AlertCircleIcon :size="24" />
      <p>{{ error }}</p>
      <button class="btn-primary" @click="loadForums">Reintentar</button>
    </div>

    <!-- Listado de foros -->
    <div v-else class="forums-view__grid">
      <article
        v-for="forum in forums"
        :key="forum.id"
        class="card forums-view__card"
        :class="{ 'forums-view__card--expanded': expandedForums.has(forum.id) }"
        @click="toggleForum(forum.id)"
      >
        <!-- Cabecera de la tarjeta: icono + nombre + contador + flecha -->
        <div class="forums-view__card-header">
          <div class="forums-view__icon-wrapper">
            <component :is="getIcon(forum.icon)" :size="28" />
          </div>
          <!-- El nombre del foro es un enlace a la página de hilos -->
          <router-link
            :to="{ name: 'ForumThreads', params: { id: forum.id }, query: { name: forum.name } }"
            class="forums-view__card-info"
            @click.stop
          >
            <h2 class="forums-view__card-title">{{ forum.name }}</h2>
            <span class="forums-view__thread-count">
              <MessageSquareIcon :size="14" />
              {{ forum.thread_count }} hilos
            </span>
          </router-link>
          <!-- Flecha que gira cuando el foro está expandido -->
          <ChevronDownIcon
            :size="20"
            class="forums-view__chevron"
            :class="{ 'forums-view__chevron--open': expandedForums.has(forum.id) }"
          />
        </div>

        <!-- Descripción del foro -->
        <p class="forums-view__card-desc">{{ forum.description }}</p>

        <!-- Subforos: solo se ven cuando la tarjeta está expandida -->
        <Transition name="slide">
          <div v-if="expandedForums.has(forum.id)" class="forums-view__subforums">
            <span
              v-for="sub in forum.subforums"
              :key="sub.id"
              class="badge forums-view__subforum-badge"
            >
              {{ sub.name }}
            </span>
          </div>
        </Transition>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetchJson } from '../services/http'
import {
  LoaderIcon,
  AlertCircleIcon,
  MessageSquareIcon,
  ChevronDownIcon,
  Baby,
  Plane,
  MessageCircle,
  HeartCrack,
  Sun,
  Thermometer,
  Heart,
  Shield,
} from 'lucide-vue-next'

const forums = ref([])
const isLoading = ref(true)
const error = ref(null)

// Set de IDs de foros que están expandidos (subforos visibles)
const expandedForums = ref(new Set())

// Abre o cierra el acordeón de subforos de un foro
function toggleForum(id) {
  const newSet = new Set(expandedForums.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  expandedForums.value = newSet
}

// Mapa: nombre del icono (desde el backend) → componente de Lucide
const ICON_MAP = {
  baby: Baby,
  plane: Plane,
  'message-circle': MessageCircle,
  'heart-crack': HeartCrack,
  sun: Sun,
  thermometer: Thermometer,
  heart: Heart,
  shield: Shield,
}

// Función que dado un nombre de icono devuelve el componente.
// Si no lo encuentra, usa MessageCircle como fallback.
function getIcon(iconName) {
  return ICON_MAP[iconName] || MessageCircle
}

async function loadForums() {
  isLoading.value = true
  error.value = null

  try {
    const { response, data } = await apiFetchJson('/forums/')

    if (response.ok) {
      forums.value = data
    } else {
      error.value = data.detail || 'Error al cargar los foros'
    }
  } catch {
    error.value = 'Error de conexión. Comprueba tu conexión a internet.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadForums)
</script>

<style scoped>
.forums-view {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-4);
  background-color: var(--blanco-calido);
  min-height: 100vh;
}

.forums-view__title {
  font-size: var(--h2-size, 1.75rem);
  margin-bottom: var(--space-1);
}

.forums-view__subtitle {
  color: var(--texto-secundario);
  font-size: 0.9375rem;
  margin-bottom: var(--space-8);
}

/* ─── Loading / Error ─────────────────────────────────────────────────── */

.forums-view__loading,
.forums-view__error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding-top: var(--space-16);
  color: var(--lila-oscuro);
  font-size: 0.9375rem;
  text-align: center;
}

.forums-view__error {
  color: var(--error);
}

/* ─── Grid de tarjetas ────────────────────────────────────────────────── */

.forums-view__grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.forums-view__card {
  padding: var(--space-6);
  cursor: pointer;                     /* Indica que se puede hacer clic */
  transition: box-shadow 200ms ease;   /* Suaviza el hover */
}

.forums-view__card:hover {
  box-shadow: 0 6px 20px rgba(92, 61, 46, 0.12);  /* Sombra más intensa al pasar el ratón */
}

.forums-view__card-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.forums-view__icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  background-color: var(--lila-suave);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--lila-oscuro);
  flex-shrink: 0;
}

.forums-view__card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;      /* Ocupa el espacio disponible para empujar la flecha a la derecha */
  min-width: 0;
}

.forums-view__card-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--marron-cacao);
  margin: 0;
}

.forums-view__thread-count {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.8125rem;
  color: var(--texto-secundario);
}

/* ─── Flecha de acordeón ─────────────────────────────────────────────── */

.forums-view__chevron {
  color: var(--lila-oscuro);
  flex-shrink: 0;
  transition: transform 200ms ease;  /* Gira suavemente al abrir/cerrar */
}

.forums-view__chevron--open {
  transform: rotate(180deg);          /* Apunta hacia arriba cuando está abierto */
}

.forums-view__card-desc {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--marron-cacao);
  margin-top: var(--space-3);        /* Separación del header */
  margin-bottom: var(--space-4);
}

/* ─── Subforos ────────────────────────────────────────────────────────── */

.forums-view__subforums {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.forums-view__subforum-badge {
  font-size: 0.75rem;
  cursor: default;
}

/* ─── Animación de aparición de subforos ──────────────────────────────── */

.slide-enter-active {
  transition: all 200ms ease-out;
}

.slide-leave-active {
  transition: all 150ms ease-in;
}

.slide-enter-from {
  opacity: 0;
  transform: translateY(-8px);       /* Viene desde arriba */
}

.slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);       /* Se va hacia arriba */
}

/* ─── Animación spinner ───────────────────────────────────────────────── */

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
