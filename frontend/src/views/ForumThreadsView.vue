<template>
  <div class="threads-view">
    <!-- Cabecera con navegación atrás -->
    <div class="threads-view__header">
      <router-link to="/forums" class="threads-view__back">
        <ArrowLeftIcon :size="20" />
        Todos los foros
      </router-link>
      <h1 class="threads-view__title">{{ forumName }}</h1>
    </div>

    <!-- Botones de ordenación -->
    <div class="threads-view__sort">
      <button
        class="threads-view__sort-btn"
        :class="{ active: sort === 'recent' }"
        @click="changeSort('recent')"
      >
        Más recientes
      </button>
      <button
        class="threads-view__sort-btn"
        :class="{ active: sort === 'comments' }"
        @click="changeSort('comments')"
      >
        Más comentados
      </button>
    </div>

    <!-- Total de hilos -->
    <p v-if="!isLoading && !error" class="threads-view__total">
      {{ total }} {{ total === 1 ? 'hilo' : 'hilos' }} en total
    </p>

    <!-- Botón para crear un nuevo hilo (HU-09 Tarea 1) -->
    <div class="threads-view__new-thread">
      <router-link
        :to="{ name: 'CreateThread', params: { id: forumId }, query: { name: forumName } }"
        class="btn-primary threads-view__new-btn"
      >
        <PlusIcon :size="18" />
        Nuevo hilo
      </router-link>
    </div>

    <!-- Spinner de carga -->
    <div v-if="isLoading" class="threads-view__loading">
      <LoaderIcon :size="32" class="spin" />
      <p>Cargando hilos…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="threads-view__error" role="alert">
      <AlertCircleIcon :size="24" />
      <p>{{ error }}</p>
      <button class="btn-primary" @click="loadThreads">Reintentar</button>
    </div>

    <!-- Sin hilos -->
    <div v-else-if="threads.length === 0" class="threads-view__empty">
      <MessageSquareIcon :size="48" />
      <p>Todavía no hay hilos en este foro.</p>
      <p class="threads-view__empty-sub">¡Sé la primera en crear una conversación!</p>
    </div>

    <!-- Listado de hilos -->
    <div v-else class="threads-view__list">
      <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events -->
      <article
        v-for="thread in threads"
        :key="thread.id"
        class="card threads-view__thread"
        role="link"
        tabindex="0"
        @click="goToThread(thread.id)"
        @keydown.enter="goToThread(thread.id)"
      >
        <div class="threads-view__thread-body">
          <!-- Indicador de actividad nueva -->
          <div v-if="thread.has_new_activity" class="threads-view__new-dot" title="Actividad nueva"></div>

          <!-- Título del hilo -->
          <h3 class="threads-view__thread-title">{{ thread.title }}</h3>

          <!-- Metadatos: autora, fecha, respuestas -->
          <div class="threads-view__thread-meta">
            <span class="threads-view__author">
              <span class="threads-view__avatar-init">{{ thread.author_name.charAt(0).toUpperCase() }}</span>
              {{ thread.author_name }}
            </span>
            <span class="threads-view__date">{{ formatDate(thread.created_at) }}</span>
            <span class="threads-view__replies">
              <MessageSquareIcon :size="14" />
              {{ thread.reply_count }}
            </span>
          </div>
        </div>
      </article>

      <!-- Paginación -->
      <div v-if="pages > 1" class="threads-view__pagination">
        <button
          class="threads-view__page-btn"
          :disabled="page <= 1"
          @click="goToPage(page - 1)"
        >
          <ChevronLeftIcon :size="20" />
          Anterior
        </button>

        <!-- Botones de página numerados -->
        <template v-for="p in pageNumbers" :key="p">
          <span v-if="p === '...'" class="threads-view__page-dots">…</span>
          <button
            v-else
            class="threads-view__page-num"
            :class="{ active: p === page }"
            @click="goToPage(p)"
          >
            {{ p }}
          </button>
        </template>

        <button
          class="threads-view__page-btn"
          :disabled="page >= pages"
          @click="goToPage(page + 1)"
        >
          Siguiente
          <ChevronRightIcon :size="20" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetchJson } from '../services/http'
import {
  LoaderIcon,
  AlertCircleIcon,
  MessageSquareIcon,
  ArrowLeftIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  PlusIcon,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// ─── Datos del foro ──────────────────────────────────────────────────────

const forumId = route.params.id                     // ID del foro desde la URL
const forumName = ref(route.query.name || 'Foro')    // Nombre desde query param

// ─── Estado de los hilos ─────────────────────────────────────────────────

const threads = ref([])
const isLoading = ref(true)
const error = ref(null)

// ─── Paginación y ordenación ─────────────────────────────────────────────

const page = ref(1)
const perPage = 20
const pages = ref(1)
const total = ref(0)

// Genera la lista de botones de página para mostrar (con ... en los saltos)
const pageNumbers = computed(() => {
  const totalPages = pages.value
  const current = page.value
  const result = []

  // Siempre mostramos la primera página
  result.push(1)

  // Rango de páginas visibles alrededor de la actual (2 vecinos a cada lado)
  const start = Math.max(2, current - 2)
  const end = Math.min(totalPages - 1, current + 2)

  // Si hay salto después de la página 1, añadimos "..."
  if (start > 2) {
    result.push('...')
  }

  // Páginas intermedias
  for (let i = start; i <= end; i++) {
    result.push(i)
  }

  // Si hay salto antes de la última página, añadimos "..."
  if (end < totalPages - 1) {
    result.push('...')
  }

  // Siempre mostramos la última página (si es distinta de la primera)
  if (totalPages > 1) {
    result.push(totalPages)
  }

  return result
})
const sort = ref('recent')       // 'recent' o 'comments'

function changeSort(value) {
  sort.value = value
  page.value = 1
  loadThreads()
}

function goToPage(newPage) {
  page.value = newPage
  loadThreads()
  // Al cambiar de página, volvemos al inicio para ver el primer resultado
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToThread(threadId) {
  // Navega al detalle del hilo
  router.push({ name: 'ThreadDetail', params: { id: threadId } })
}

// ─── Formatear fecha ─────────────────────────────────────────────────────

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    // Hoy: mostrar solo la hora
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
  }
  if (diffDays === 1) {
    return 'Ayer'
  }
  if (diffDays < 7) {
    return `Hace ${diffDays} días`
  }
  // Fecha completa
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

// ─── Cargar hilos desde el backend ──────────────────────────────────────

async function loadThreads() {
  isLoading.value = true
  error.value = null

  try {
    // Llamamos al endpoint con paginación y ordenación
    const url = `/forums/${forumId}/threads?page=${page.value}&per_page=${perPage}&sort=${sort.value}`
    const { response, data } = await apiFetchJson(url)

    if (response.ok) {
      threads.value = data.items
      total.value = data.total
      pages.value = data.pages
      page.value = data.page
    } else {
      error.value = data.detail || 'Error al cargar los hilos'
    }
  } catch {
    error.value = 'Error de conexión. Comprueba tu conexión a internet.'
  } finally {
    isLoading.value = false
  }
}

// Si el nombre del foro no se pasó en la URL, lo obtenemos de la lista de foros
async function ensureForumName() {
  if (route.query.name) return

  try {
    const { response, data } = await apiFetchJson('/forums/')
    if (response.ok) {
      const forum = data.find(f => f.id === forumId)
      if (forum) forumName.value = forum.name
    }
  } catch {
    // Si falla, usamos "Foro" como nombre por defecto
  }
}

onMounted(() => {
  ensureForumName()
  loadThreads()
})
</script>

<style scoped>
.threads-view {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-4);
  background-color: var(--blanco-calido);
  min-height: 100vh;
}

/* ─── Cabecera ─────────────────────────────────────────────────────────── */

.threads-view__header {
  margin-bottom: var(--space-6);
}

.threads-view__back {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--lila-oscuro);
  text-decoration: none;
  margin-bottom: var(--space-2);
  transition: color 150ms ease;
}

.threads-view__back:hover {
  color: var(--rosa-coral);
}

.threads-view__title {
  font-size: 1.75rem;
  margin: 0;
}

/* ─── Botones de ordenación ────────────────────────────────────────────── */

.threads-view__sort {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
}

.threads-view__sort-btn {
  font-family: var(--font-body);
  font-size: 0.8125rem;
  font-weight: 600;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-pill);
  border: 2px solid var(--lila-suave);
  background-color: transparent;
  color: var(--marron-cacao);
  cursor: pointer;
  transition: all 150ms ease;
}

.threads-view__sort-btn:hover {
  border-color: var(--rosa-coral);
  color: var(--rosa-coral);
}

.threads-view__sort-btn.active {
  background-color: var(--lila-suave);
  border-color: var(--lila-suave);
  color: var(--lila-oscuro);
}

/* ─── Botón "Nuevo hilo" ──────────────────────────────────────────────── */

.threads-view__new-thread {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--space-4);
}

.threads-view__new-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.875rem;
  padding: var(--space-2) var(--space-4);
  text-decoration: none;
}

/* ─── Loading / Error / Empty ──────────────────────────────────────────── */

.threads-view__loading,
.threads-view__error,
.threads-view__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding-top: var(--space-12);
  color: var(--lila-oscuro);
  font-size: 0.9375rem;
  text-align: center;
}

.threads-view__error {
  color: var(--error);
}

.threads-view__empty {
  color: var(--texto-secundario);
}

.threads-view__empty-sub {
  font-size: 0.875rem;
  color: var(--texto-secundario);
}

/* ─── Lista de hilos ───────────────────────────────────────────────────── */

.threads-view__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.threads-view__thread {
  padding: var(--space-4) var(--space-6);
  cursor: pointer;
  transition: box-shadow 200ms ease;
  position: relative;
}

.threads-view__thread:hover {
  box-shadow: 0 6px 20px rgba(92, 61, 46, 0.12);
}

.threads-view__new-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--rosa-coral);
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
}

.threads-view__thread-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--marron-cacao);
  margin: 0 0 var(--space-2) 0;
  line-height: 1.4;
}

/* ─── Metadatos del hilo ───────────────────────────────────────────────── */

.threads-view__thread-meta {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-size: 0.8125rem;
  color: var(--texto-secundario);
  flex-wrap: wrap;
}

.threads-view__author {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-weight: 600;
  color: var(--marron-cacao);
}

.threads-view__avatar-init {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background-color: var(--lila-suave);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--lila-oscuro);
}

.threads-view__date {
  color: var(--texto-secundario);
}

.threads-view__replies {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--texto-secundario);
  margin-left: auto;
}

/* ─── Paginación ───────────────────────────────────────────────────────── */

.threads-view__pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  margin-top: var(--space-8);
  padding-top: var(--space-6);
  border-top: 1.5px solid var(--melocoton);
}

.threads-view__page-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--lila-oscuro);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  transition: all 150ms ease;
}

.threads-view__page-btn:hover:not(:disabled) {
  background-color: var(--melocoton);
  color: var(--rosa-coral);
}

.threads-view__page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.threads-view__page-info {
  font-size: 0.875rem;
  color: var(--texto-secundario);
  font-weight: 600;
}

/* ─── Botones de página numerados ─────────────────────────────────────── */

.threads-view__page-dots {
  font-size: 0.875rem;
  color: var(--texto-secundario);
  padding: 0 var(--space-1);
}

.threads-view__page-num {
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--lila-oscuro);
  background: none;
  border: none;
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  transition: all 150ms ease;
}

.threads-view__page-num:hover {
  background-color: var(--melocoton);
  color: var(--rosa-coral);
}

.threads-view__page-num.active {
  background-color: var(--lila-suave);
  color: var(--lila-oscuro);
  font-weight: 700;
}

/* ─── Total de hilos ──────────────────────────────────────────────────── */

.threads-view__total {
  font-size: 0.8125rem;
  color: var(--texto-secundario);
  margin-bottom: var(--space-4);
}

/* ─── Spinner ──────────────────────────────────────────────────────────── */

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
