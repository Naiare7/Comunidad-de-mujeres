<template>
  <!--
    Página de detalle de un hilo.
    Muestra el título, la autora, la fecha, el contenido, las imágenes adjuntas,
    las respuestas existentes y una caja para escribir una nueva respuesta.
  -->
  <div class="thread-detail">
    <!-- Cabecera con navegación atrás -->
    <div class="thread-detail__header">
      <router-link to="/forums" class="thread-detail__back">
        <ArrowLeftIcon :size="20" />
        Todos los foros
      </router-link>
    </div>

    <!-- Spinner de carga -->
    <div v-if="isLoading" class="thread-detail__loading">
      <LoaderIcon :size="32" class="spin" />
      <p>Cargando hilo…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="thread-detail__error" role="alert">
      <AlertCircleIcon :size="24" />
      <p>{{ error }}</p>
      <button class="btn-primary" @click="loadThread">Reintentar</button>
    </div>

    <!-- Contenido del hilo -->
    <template v-else-if="thread">
      <article class="card thread-detail__card">
        <!-- Título del hilo -->
        <h1 class="thread-detail__title">{{ thread.title }}</h1>

        <!-- Metadatos: autora y fecha -->
        <div class="thread-detail__meta">
          <span class="thread-detail__author">
            <span class="thread-detail__avatar-init">
              {{ thread.author_name.charAt(0).toUpperCase() }}
            </span>
            {{ thread.author_name }}
          </span>
          <span class="thread-detail__date">{{ formatDate(thread.created_at) }}</span>
        </div>

        <!-- Contenido del hilo (preservamos saltos de línea) -->
        <div class="thread-detail__content" v-html="renderedContent"></div>

        <!-- Imágenes adjuntas -->
        <div v-if="thread.image_urls && thread.image_urls.length > 0" class="thread-detail__images">
          <h2 class="thread-detail__images-title">Imágenes adjuntas</h2>
          <div class="thread-detail__gallery">
            <img
              v-for="(imgUrl, index) in thread.image_urls"
              :key="index"
              :src="imgUrl"
              :alt="'Imagen ' + (index + 1)"
              class="thread-detail__image"
              @click="openImage(imgUrl)"
            />
          </div>
        </div>
      </article>

      <!-- ─── Sección de respuestas ─────────────────────────────────────── -->
      <section class="thread-detail__replies">
        <h2 class="thread-detail__replies-title">
          Respuestas
          <span v-if="thread.replies && thread.replies.length" class="thread-detail__replies-count">
            ({{ thread.replies.length }})
          </span>
        </h2>

        <!-- Cuando aún no hay respuestas -->
        <div v-if="!thread.replies || thread.replies.length === 0" class="thread-detail__replies-empty">
          <MessageSquareIcon :size="24" />
          <p>No hay respuestas aún. ¡Sé la primera en responder!</p>
        </div>

        <!-- Lista de respuestas -->
        <div v-else class="thread-detail__replies-list">
          <article
            v-for="reply in thread.replies"
            :key="reply.id"
            class="card thread-detail__reply-card"
          >
            <!-- Metadatos de la respuesta -->
            <div class="thread-detail__reply-meta">
              <span class="thread-detail__reply-author">
                <span class="thread-detail__avatar-init thread-detail__avatar-init--small">
                  {{ reply.author_name.charAt(0).toUpperCase() }}
                </span>
                {{ reply.author_name }}
              </span>
              <span class="thread-detail__reply-date">{{ formatDate(reply.created_at) }}</span>
            </div>

            <!-- Contenido de la respuesta -->
            <div class="thread-detail__reply-content" v-html="renderContent(reply.content)"></div>

            <!-- Botón para citar esta respuesta -->
            <button
              type="button"
              class="thread-detail__quote-btn"
              title="Citar esta respuesta"
              @click="quoteReply(reply)"
            >
              <MessageSquareQuoteIcon :size="14" />
              Citar
            </button>
          </article>
        </div>
      </section>

      <!-- ─── Caja de respuesta ─────────────────────────────────────────── -->
      <div class="card thread-detail__reply-box">
        <h3 class="thread-detail__reply-box-title">Escribe tu respuesta</h3>

        <!-- Indicador de que está citando una respuesta -->
        <div v-if="replyingTo" class="thread-detail__quote-indicator">
          <span class="thread-detail__quote-indicator-text">
            <MessageSquareQuoteIcon :size="14" />
            Citando a <strong>{{ replyingTo.author_name }}</strong>
          </span>
          <button
            type="button"
            class="thread-detail__quote-cancel"
            title="Cancelar cita"
            @click="cancelQuote"
          >
            <XIcon :size="16" />
          </button>
        </div>

        <!-- Barra de herramientas de formato -->
        <div class="thread-detail__toolbar" role="toolbar" aria-label="Formato de texto">
          <button
            type="button"
            class="thread-detail__toolbar-btn"
            title="Negrita"
            @click="insertFormat('bold')"
          >
            <BoldIcon :size="18" />
          </button>
          <button
            type="button"
            class="thread-detail__toolbar-btn"
            title="Cursiva"
            @click="insertFormat('italic')"
          >
            <ItalicIcon :size="18" />
          </button>
          <button
            type="button"
            class="thread-detail__toolbar-btn"
            title="Insertar enlace"
            @click="insertFormat('link')"
          >
            <LinkIcon :size="18" />
          </button>
        </div>

        <!-- Área de texto para escribir la respuesta -->
        <textarea
          ref="contentTextarea"
          v-model="replyContent"
          class="input-field thread-detail__reply-textarea"
          :class="{ 'input-error': submitError }"
          placeholder="Escribe tu respuesta… (puedes usar **negrita**, *cursiva* y [enlaces](url))"
          rows="5"
        ></textarea>

        <!-- Subida de imágenes (opcional) -->
        <div class="thread-detail__reply-images">
          <!-- Previews de las imágenes seleccionadas -->
          <div v-for="(img, index) in replyImages" :key="index" class="thread-detail__reply-image-preview">
            <img :src="img.url" :alt="'Imagen ' + (index + 1)" class="thread-detail__reply-preview-img" />
            <button
              type="button"
              class="thread-detail__reply-remove-image"
              @click="removeReplyImage(index)"
              :aria-label="'Eliminar imagen ' + (index + 1)"
            >
              <XIcon :size="16" />
            </button>
          </div>
          <!-- Botón para añadir imágenes (solo si no hay 5 ya) -->
          <button
            v-if="replyImages.length < 5"
            type="button"
            class="thread-detail__reply-add-image"
            @click="triggerReplyImageInput"
          >
            <ImageIcon :size="20" />
            <span>Añadir imagen</span>
          </button>
        </div>
        <!-- Input oculto para seleccionar archivos -->
        <input
          ref="replyImageInput"
          type="file"
          accept="image/*"
          multiple
          class="thread-detail__reply-file-input"
          @change="handleReplyImagesChange"
        />

        <!-- Mensaje de error al enviar -->
        <span v-if="submitError" class="field-error" role="alert">
          {{ submitError }}
        </span>

        <!-- Botón para enviar la respuesta -->
        <div class="thread-detail__reply-actions">
          <button
            type="button"
            class="btn-primary"
            :disabled="isSubmitting || !replyContent.trim()"
            @click="handleReplySubmit"
          >
            <SendIcon :size="16" />
            {{ isSubmitting ? 'Enviando…' : 'Responder' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiFetchJson, apiFetch } from '../services/http'
import {
  LoaderIcon,
  AlertCircleIcon,
  ArrowLeftIcon,
  MessageSquareIcon,
  MessageSquareQuoteIcon,
  BoldIcon,
  ItalicIcon,
  LinkIcon,
  SendIcon,
  ImageIcon,
  XIcon,
} from 'lucide-vue-next'

const route = useRoute()

// El ID del hilo viene en la URL (/threads/:id)
const threadId = route.params.id

// ─── Estado ───────────────────────────────────────────────────────────────

const thread = ref(null)
const isLoading = ref(true)
const error = ref(null)

// Contenido de la nueva respuesta (textarea)
const replyContent = ref('')

// Respuesta que se está citando (null = no se está citando ninguna)
const replyingTo = ref(null)

// Referencia al textarea para poder insertar formato
const contentTextarea = ref(null)

// Indica si se está enviando la respuesta al servidor
const isSubmitting = ref(false)

// Mensaje de error al enviar la respuesta
const submitError = ref(null)

// ─── Imágenes adjuntas a la respuesta ─────────────────────────────────────

// Input oculto para seleccionar archivos de imagen
const replyImageInput = ref(null)

// Lista de imágenes seleccionadas para adjuntar a la respuesta
// Cada elemento es { file: File, url: string (URL temporal de previsualización) }
const replyImages = ref([])

function triggerReplyImageInput() {
  // Abre el selector de archivos del sistema
  replyImageInput.value?.click()
}

function handleReplyImagesChange(event) {
  const files = Array.from(event.target.files)

  // Validamos que no haya más de 5 imágenes en total
  if (replyImages.value.length + files.length > 5) {
    submitError.value = 'Máximo 5 imágenes permitidas'
    event.target.value = ''
    return
  }

  // Agregamos cada archivo a la lista de previsualizaciones
  files.forEach((file) => {
    // Comprobamos que sea una imagen
    if (!file.type.startsWith('image/')) return
    // Creamos una URL temporal para mostrar la previsualización
    replyImages.value.push({
      file,
      url: URL.createObjectURL(file),
    })
  })

  // Limpiamos el input para poder seleccionar el mismo archivo de nuevo
  event.target.value = ''
}

function removeReplyImage(index) {
  // Liberamos la URL temporal para evitar fugas de memoria
  URL.revokeObjectURL(replyImages.value[index].url)
  // Eliminamos la imagen del array
  replyImages.value.splice(index, 1)
}

// Limpiamos todas las URLs temporales cuando el componente se destruye
onUnmounted(() => {
  replyImages.value.forEach((img) => URL.revokeObjectURL(img.url))
})

// ─── Renderizar contenido con saltos de línea ───────────────────────────

// Convertimos el texto plano a HTML reemplazando los saltos de línea por <br>
// y envolviendo los enlaces en <a> para que se vean como links clicables.
const renderedContent = computed(() => {
  if (!thread.value) return ''
  return renderContent(thread.value.content)
})

// Función reutilizable para renderizar cualquier texto (hilo o respuesta)
function renderContent(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
  // Convertimos markdown básico: **negrita**, *cursiva*, [texto](url)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
  return html
}

// ─── Formatear fecha ─────────────────────────────────────────────────────

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
  }
  if (diffDays === 1) {
    return 'Ayer'
  }
  if (diffDays < 7) {
    return `Hace ${diffDays} días`
  }
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

// ─── Abrir imagen en una nueva pestaña ───────────────────────────────────

function openImage(url) {
  window.open(url, '_blank')
}

// ─── Mecanismo para citar una respuesta ──────────────────────────────────

function quoteReply(reply) {
  // Guardamos la respuesta que se está citando
  replyingTo.value = reply

  // Construimos el texto citado con formato markdown de blockquote
  const quotedText = reply.content
    .split('\n')                    // Dividimos en líneas
    .map(line => `> ${line}`)       // Cada línea empieza con >
    .join('\n')                     // Volvemos a unir

  // Preparamos el texto que se insertará
  const quote = `> **${reply.author_name}** escribió:\n${quotedText}\n\n`

  // Si ya hay algo escrito, añadimos la cita al principio
  if (replyContent.value.trim()) {
    replyContent.value = quote + replyContent.value
  } else {
    replyContent.value = quote
  }

  // Enfocamos el textarea y movemos el cursor al final
  setTimeout(() => {
    contentTextarea.value?.focus()
    contentTextarea.value?.setSelectionRange(
      replyContent.value.length,
      replyContent.value.length
    )
  }, 0)
}

function cancelQuote() {
  // Limpiamos la respuesta citada
  replyingTo.value = null

  // Quitamos la cita del textarea (todo lo que empiece por > al inicio)
  const lines = replyContent.value.split('\n')
  const withoutQuote = lines.filter(line => !line.startsWith('> ')).join('\n').trim()
  replyContent.value = withoutQuote
}

// ─── Barra de formato para el textarea ──────────────────────────────────

function insertFormat(type) {
  const textarea = contentTextarea.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = replyContent.value.substring(start, end)
  let wrapped = ''
  let cursorOffset = 0

  switch (type) {
    case 'bold':
      wrapped = `**${selectedText || 'texto en negrita'}**`
      cursorOffset = selectedText ? 2 : 2
      break
    case 'italic':
      wrapped = `*${selectedText || 'texto en cursiva'}*`
      cursorOffset = selectedText ? 1 : 1
      break
    case 'link':
      if (selectedText) {
        wrapped = `[${selectedText}](url)`
        cursorOffset = selectedText.length + 3
      } else {
        wrapped = '[texto del enlace](url)'
        cursorOffset = 0
      }
      break
  }

  replyContent.value = replyContent.value.substring(0, start) + wrapped + replyContent.value.substring(end)

  const newCursorPos = type === 'link'
    ? (selectedText ? start + selectedText.length + 3 : start + 19)
    : start + wrapped.length

  requestAnimationFrame(() => {
    textarea.focus()
    textarea.setSelectionRange(newCursorPos, newCursorPos)
  })
}

// ─── Enviar respuesta al servidor ──────────────────────────────────────

async function handleReplySubmit() {
  // Validamos que no esté vacío
  if (!replyContent.value.trim()) return

  isSubmitting.value = true
  submitError.value = null

  try {
    // Llamamos al endpoint POST /threads/{thread_id}/replies
    const { response, data } = await apiFetchJson(`/threads/${threadId}/replies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: replyContent.value.trim(),
        // Si está citando una respuesta, enviamos su ID
        parent_reply_id: replyingTo.value ? replyingTo.value.id : null,
      }),
    })

    if (response.ok) {
      // Éxito: obtenemos el ID de la respuesta creada
      const replyId = data.id

      // Si hay imágenes seleccionadas, las subimos una por una
      if (replyImages.value.length > 0) {
        for (const img of replyImages.value) {
          const formData = new FormData()
          formData.append('file', img.file)

          const uploadResponse = await apiFetch(`/threads/${threadId}/replies/${replyId}/images`, {
            method: 'POST',
            body: formData,
          })

          // Si falla la subida de una imagen, mostramos error pero seguimos
          if (!uploadResponse.ok) {
            const errData = await uploadResponse.json().catch(() => ({}))
            submitError.value = errData.detail || 'Error al subir una imagen'
          }
        }
      }

      // Limpiamos el formulario y recargamos el hilo
      replyContent.value = ''
      replyImages.value = []
      replyingTo.value = null
      await loadThread()
    } else {
      // Error del servidor
      submitError.value = data.detail || 'Error al enviar la respuesta'
    }
  } catch {
    submitError.value = 'Error de conexión. Comprueba tu conexión a internet.'
  } finally {
    isSubmitting.value = false
  }
}

// ─── Cargar el hilo desde el backend ────────────────────────────────────

async function loadThread() {
  isLoading.value = true
  error.value = null

  try {
    const { response, data } = await apiFetchJson(`/threads/${threadId}`)

    if (response.ok) {
      thread.value = data
    } else {
      error.value = data.detail || 'Error al cargar el hilo'
    }
  } catch {
    error.value = 'Error de conexión. Comprueba tu conexión a internet.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadThread)
</script>

<style scoped>
.thread-detail {
  max-width: 750px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-4);
  background-color: var(--blanco-calido);
  min-height: 100vh;
}

/* ─── Cabecera ─────────────────────────────────────────────────────────── */

.thread-detail__header {
  margin-bottom: var(--space-6);
}

.thread-detail__back {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--lila-oscuro);
  text-decoration: none;
  transition: color 150ms ease;
}

.thread-detail__back:hover {
  color: var(--rosa-coral);
}

/* ─── Tarjeta del hilo ─────────────────────────────────────────────────── */

.thread-detail__card {
  padding: var(--space-6) var(--space-8);
}

.thread-detail__title {
  font-family: var(--font-display);
  font-size: 1.625rem;
  color: var(--marron-cacao);
  margin: 0 0 var(--space-4) 0;
  line-height: 1.3;
}

.thread-detail__meta {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  font-size: 0.875rem;
  color: var(--texto-secundario);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1.5px solid var(--melocoton);
}

.thread-detail__author {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-weight: 600;
  color: var(--marron-cacao);
}

.thread-detail__avatar-init {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: var(--lila-suave);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--lila-oscuro);
}

.thread-detail__avatar-init--small {
  width: 24px;
  height: 24px;
  font-size: 0.625rem;
}

.thread-detail__date {
  color: var(--texto-secundario);
}

/* ─── Contenido ────────────────────────────────────────────────────────── */

.thread-detail__content {
  font-size: 1rem;
  line-height: 1.8;
  color: var(--marron-cacao);
  margin-bottom: var(--space-6);
}

.thread-detail__content :deep(a) {
  color: var(--rosa-coral);
  text-decoration: underline;
}

/* ─── Imágenes ─────────────────────────────────────────────────────────── */

.thread-detail__images {
  border-top: 1.5px solid var(--melocoton);
  padding-top: var(--space-4);
}

.thread-detail__images-title {
  font-family: var(--font-body);
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--lila-oscuro);
  margin-bottom: var(--space-3);
}

.thread-detail__gallery {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.thread-detail__image {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: 1.5px solid var(--melocoton);
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.thread-detail__image:hover {
  transform: scale(1.03);
  box-shadow: 0 4px 12px rgba(92, 61, 46, 0.15);
}

/* ─── Sección de respuestas ────────────────────────────────────────────── */

.thread-detail__replies {
  margin-top: var(--space-8);
}

.thread-detail__replies-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  color: var(--marron-cacao);
  margin: 0 0 var(--space-4) 0;
}

.thread-detail__replies-count {
  font-size: 0.9375rem;
  color: var(--texto-secundario);
  font-weight: 400;
}

.thread-detail__replies-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-8);
  color: var(--texto-secundario);
  text-align: center;
}

.thread-detail__replies-empty p {
  font-size: 0.9375rem;
  margin: 0;
}

.thread-detail__replies-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.thread-detail__reply-card {
  padding: var(--space-4);
  border-color: var(--lila-suave);
  background-color: rgba(255, 255, 255, 0.6);
}

.thread-detail__reply-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: 0.8125rem;
  color: var(--texto-secundario);
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--melocoton);
}

.thread-detail__reply-author {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-weight: 600;
  color: var(--marron-cacao);
}

.thread-detail__reply-date {
  color: var(--texto-secundario);
}

.thread-detail__reply-content {
  font-size: 0.9375rem;
  line-height: 1.7;
  color: var(--marron-cacao);
  margin-bottom: var(--space-3);
}

.thread-detail__reply-content :deep(a) {
  color: var(--rosa-coral);
  text-decoration: underline;
}

/* ─── Botón de citar ───────────────────────────────────────────────────── */

.thread-detail__quote-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--lila-oscuro);
  background: none;
  border: none;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 150ms ease;
}

.thread-detail__quote-btn:hover {
  background-color: var(--lila-suave);
  color: var(--rosa-coral);
}

/* ─── Caja de respuesta ────────────────────────────────────────────────── */

.thread-detail__reply-box {
  margin-top: var(--space-6);
  padding: var(--space-6);
}

.thread-detail__reply-box-title {
  font-family: var(--font-display);
  font-size: 1.0625rem;
  color: var(--marron-cacao);
  margin: 0 0 var(--space-3) 0;
}

/* ─── Indicador de cita ────────────────────────────────────────────────── */

.thread-detail__quote-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-3);
  background-color: var(--lila-suave);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--lila-oscuro);
}

.thread-detail__quote-indicator-text {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 0.8125rem;
  color: var(--lila-oscuro);
}

.thread-detail__quote-cancel {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  border-radius: 50%;
  color: var(--texto-secundario);
  cursor: pointer;
  transition: all 150ms ease;
}

.thread-detail__quote-cancel:hover {
  background-color: var(--melocoton);
  color: var(--error);
}

/* ─── Barra de herramientas ────────────────────────────────────────────── */

.thread-detail__toolbar {
  display: flex;
  gap: var(--space-1);
  margin-bottom: var(--space-2);
  padding: var(--space-1);
  background-color: var(--melocoton);
  border-radius: var(--radius-sm);
  border: 1px solid var(--melocoton);
}

.thread-detail__toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  border-radius: var(--radius-sm);
  color: var(--marron-cacao);
  cursor: pointer;
  transition: all 150ms ease;
}

.thread-detail__toolbar-btn:hover {
  background-color: var(--blanco-calido);
  color: var(--rosa-coral);
}

/* ─── Textarea de respuesta ────────────────────────────────────────────── */

.thread-detail__reply-textarea {
  width: 100%;
  resize: vertical;
  min-height: 100px;
  font-family: var(--font-body);
  font-size: 0.9375rem;
  line-height: 1.7;
}

/* ─── Subida de imágenes en respuestas ─────────────────────────────────── */

.thread-detail__reply-images {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-3);
}

.thread-detail__reply-image-preview {
  position: relative;
  width: 80px;
  height: 80px;
}

.thread-detail__reply-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-sm);
  border: 1.5px solid var(--melocoton);
}

.thread-detail__reply-remove-image {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 22px;
  height: 22px;
  border: none;
  background-color: var(--error);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: transform 150ms ease;
}

.thread-detail__reply-remove-image:hover {
  transform: scale(1.15);
}

.thread-detail__reply-add-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  width: 80px;
  height: 80px;
  border: 1.5px dashed var(--melocoton);
  border-radius: var(--radius-sm);
  background: none;
  color: var(--texto-secundario);
  font-family: var(--font-body);
  font-size: 0.6875rem;
  cursor: pointer;
  transition: all 150ms ease;
}

.thread-detail__reply-add-image:hover {
  border-color: var(--lila-oscuro);
  color: var(--lila-oscuro);
  background-color: var(--lila-suave);
}

.thread-detail__reply-file-input {
  display: none;
}

/* ─── Acciones de la respuesta ─────────────────────────────────────────── */

.thread-detail__reply-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-3);
}

/* ─── Loading / Error ──────────────────────────────────────────────────── */

.thread-detail__loading,
.thread-detail__error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding-top: var(--space-16);
  color: var(--lila-oscuro);
  font-size: 0.9375rem;
  text-align: center;
}

.thread-detail__error {
  color: var(--error);
}

/* ─── Spinner ──────────────────────────────────────────────────────────── */

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
