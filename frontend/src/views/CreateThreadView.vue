<template>
  <!--
    Página para crear un nuevo hilo en un foro.
    Por ahora (Tarea 1) solo tiene el formulario frontend con validaciones,
    pero NO envía los datos al servidor. Eso llegará en la Tarea 2.
  -->
  <div class="create-thread">
    <!-- Cabecera con enlace para volver al foro -->
    <div class="create-thread__header">
      <router-link
        :to="{ name: 'ForumThreads', params: { id: forumId }, query: { name: forumName } }"
        class="create-thread__back"
      >
        <ArrowLeftIcon :size="20" />
        Volver al foro
      </router-link>
      <h1 class="create-thread__title">{{ forumName }}</h1>
      <p class="create-thread__subtitle">Crear un nuevo hilo</p>
    </div>

    <!-- El formulario: novalidate desactiva la validación nativa del navegador -->
    <form class="card create-thread__form" @submit.prevent="handleSubmit" novalidate>

      <!-- Campo: título del hilo -->
      <div class="input-group">
        <label class="input-label" for="title">Título del hilo</label>
        <div class="input-wrapper">
          <input
            id="title"
            v-model="form.title"
            type="text"
            class="input-field"
            :class="{ 'input-error': errors.title }"
            :aria-invalid="errors.title ? 'true' : 'false'"
            :aria-describedby="errors.title ? 'error-title' : undefined"
            placeholder="¿De qué quieres hablar?"
            @blur="handleBlur('title')"
            @input="handleInput('title')"
          />
        </div>
        <span v-if="errors.title" id="error-title" class="field-error" role="alert">
          {{ errors.title }}
        </span>
      </div>

      <!-- Campo: contenido del hilo con barra de formato simple -->
      <div class="input-group">
        <label class="input-label" for="content">Contenido</label>

        <!-- Barra de herramientas: botones para dar formato al texto -->
        <div class="create-thread__toolbar" role="toolbar" aria-label="Formato de texto">
          <button
            type="button"
            class="create-thread__toolbar-btn"
            title="Negrita"
            @click="insertFormat('bold')"
          >
            <BoldIcon :size="18" />
          </button>
          <button
            type="button"
            class="create-thread__toolbar-btn"
            title="Cursiva"
            @click="insertFormat('italic')"
          >
            <ItalicIcon :size="18" />
          </button>
          <button
            type="button"
            class="create-thread__toolbar-btn"
            title="Insertar enlace"
            @click="insertFormat('link')"
          >
            <LinkIcon :size="18" />
          </button>
        </div>

        <!-- Área de texto donde se escribe el contenido del hilo -->
        <textarea
          id="content"
          ref="contentTextarea"
          v-model="form.content"
          class="input-field create-thread__textarea"
          :class="{ 'input-error': errors.content }"
          :aria-invalid="errors.content ? 'true' : 'false'"
          :aria-describedby="errors.content ? 'error-content' : undefined"
          placeholder="Escribe tu mensaje… (puedes usar **negrita**, *cursiva* y [enlaces](url))"
          rows="10"
          @blur="handleBlur('content')"
          @input="handleInput('content')"
        ></textarea>
        <span v-if="errors.content" id="error-content" class="field-error" role="alert">
          {{ errors.content }}
        </span>
      </div>

      <!-- Subida de imágenes (igual que en ProfileView) -->
      <div class="input-group">
        <label class="input-label">Imágenes (opcional)</label>
        <div class="create-thread__images-area">
          <!-- Previews de las imágenes seleccionadas -->
          <div v-for="(img, index) in imagePreviews" :key="index" class="create-thread__image-preview">
            <img :src="img.url" :alt="'Imagen ' + (index + 1)" class="create-thread__preview-img" />
            <button
              type="button"
              class="create-thread__remove-image"
              @click="removeImage(index)"
              :aria-label="'Eliminar imagen ' + (index + 1)"
            >
              <XIcon :size="16" />
            </button>
          </div>
          <!-- Botón para añadir imágenes (solo si no hay 5 ya) -->
          <button
            v-if="imagePreviews.length < 5"
            type="button"
            class="create-thread__add-image"
            @click="triggerImageInput"
          >
            <ImageIcon :size="24" />
            <span>Añadir imagen</span>
          </button>
        </div>
        <!-- Input oculto para seleccionar archivos -->
        <input
          ref="imageInputRef"
          type="file"
          accept="image/*"
          multiple
          class="create-thread__file-input"
          @change="handleImagesChange"
        />
        <p v-if="imageError" class="create-thread__image-error" role="alert">
          {{ imageError }}
        </p>
      </div>

      <!-- Error general (por si el envío fallara en el futuro) -->
      <transition name="fade">
        <div v-if="serverError" class="create-thread__server-error" role="alert">
          <AlertCircleIcon :size="20" />
          <span>{{ serverError }}</span>
        </div>
      </transition>

      <!-- Botones de acción -->
      <div class="create-thread__actions">
        <router-link
          :to="{ name: 'ForumThreads', params: { id: forumId }, query: { name: forumName } }"
          class="btn-secondary"
        >
          Cancelar
        </router-link>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            <LoaderIcon v-if="isSubmitting" class="spin" :size="20" />
            <span v-else>Crear hilo</span>
          </button>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetchJson, apiFetch } from '../services/http'
import {
  ArrowLeftIcon,
  BoldIcon,
  ItalicIcon,
  LinkIcon,
  ImageIcon,
  XIcon,
  AlertCircleIcon,
  LoaderIcon,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// ─── Datos del foro ──────────────────────────────────────────────────────

// El ID del foro viene en la URL (/forums/:id/threads/new)
const forumId = route.params.id
// El nombre del foro se pasa como query param (?name=...)
const forumName = ref(route.query.name || 'Foro')

// ─── Estado del formulario ──────────────────────────────────────────────

// reactive() crea un objeto reactivo: Vue actualiza la vista cuando cambia
const form = reactive({
  title: '',
  content: '',
})

// Mensajes de error por campo (null = sin error)
const errors = reactive({
  title: null,
  content: null,
})

// Registra si la usuaria ya tocó cada campo (para no mostrar errores antes)
const touched = reactive({
  title: false,
  content: false,
})

const serverError = ref(null)
const isSubmitting = ref(false)  // true mientras se envía el formulario

// ─── Imágenes ────────────────────────────────────────────────────────────

const imageInputRef = ref(null)
const imagePreviews = ref([])   // Array de { file, url } para previsualizar
const imageError = ref(null)

function triggerImageInput() {
  // Abre el selector de archivos del sistema
  imageInputRef.value?.click()
}

function handleImagesChange(event) {
  const files = Array.from(event.target.files)
  imageError.value = null

  // Validamos que no haya más de 5 imágenes en total
  if (imagePreviews.value.length + files.length > 5) {
    imageError.value = 'Máximo 5 imágenes permitidas'
    event.target.value = ''
    return
  }

  // Agregamos cada archivo a la lista de previsualizaciones
  files.forEach((file) => {
    // Comprobamos que sea una imagen
    if (!file.type.startsWith('image/')) return
    // Creamos una URL temporal para mostrar la previsualización
    imagePreviews.value.push({
      file,
      url: URL.createObjectURL(file),
    })
  })

  // Limpiamos el input para poder seleccionar el mismo archivo de nuevo
  event.target.value = ''
}

function removeImage(index) {
  // Liberamos la URL temporal para evitar fugas de memoria
  URL.revokeObjectURL(imagePreviews.value[index].url)
  // Eliminamos la imagen del array
  imagePreviews.value.splice(index, 1)
}

// Limpiamos todas las URLs temporales cuando el componente se destruye
onUnmounted(() => {
  imagePreviews.value.forEach((img) => URL.revokeObjectURL(img.url))
})

// ─── Barra de formato ───────────────────────────────────────────────────

// Referencia al textarea para poder manipular la selección
const contentTextarea = ref(null)

function insertFormat(type) {
  // Obtenemos el textarea del DOM
  const textarea = contentTextarea.value
  if (!textarea) return

  // Guardamos la posición del cursor (inicio y fin de la selección)
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = form.content.substring(start, end)
  let wrapped = ''      // Texto que reemplazará a la selección
  let cursorOffset = 0  // Dónde colocar el cursor después

  switch (type) {
    case 'bold':
      // Envuelve la selección con ** ** (markdown de negrita)
      wrapped = `**${selectedText || 'texto en negrita'}**`
      cursorOffset = selectedText ? 2 : 2  // cursor al inicio del texto
      break
    case 'italic':
      // Envuelve la selección con * * (markdown de cursiva)
      wrapped = `*${selectedText || 'texto en cursiva'}*`
      cursorOffset = selectedText ? 1 : 1
      break
    case 'link':
      // Inserta un enlace en formato markdown [texto](url)
      if (selectedText) {
        // Si hay texto seleccionado, lo usa como texto del enlace
        wrapped = `[${selectedText}](url)`
        cursorOffset = selectedText.length + 3  // selecciona "url"
      } else {
        wrapped = '[texto del enlace](url)'
        cursorOffset = 0  // cursor al principio del placeholder
      }
      break
  }

  // Reemplazamos el texto seleccionado por el texto con formato
  form.content = form.content.substring(0, start) + wrapped + form.content.substring(end)

  // Colocamos el cursor en la posición adecuada
  const newCursorPos = type === 'link'
    ? (selectedText ? start + selectedText.length + 3 : start + 19) // dentro de "url"
    : start + wrapped.length

  // Programamos el foco para después de que Vue actualice el DOM
  requestAnimationFrame(() => {
    textarea.focus()
    textarea.setSelectionRange(newCursorPos, newCursorPos)
  })
}

// ─── Validaciones ───────────────────────────────────────────────────────

// Se llama cuando la usuaria sale de un campo (pierde el foco)
function handleBlur(field) {
  touched[field] = true
  validateField(field)
}

// Se llama mientras la usuaria escribe
function handleInput(field) {
  if (touched[field]) validateField(field)
}

// Valida un campo concreto y actualiza su mensaje de error
function validateField(field) {
  switch (field) {
    case 'title':
      errors.title = !form.title.trim()
        ? 'El título es obligatorio'
        : form.title.trim().length < 3
          ? 'El título debe tener al menos 3 caracteres'
          : form.title.length > 200
            ? 'El título no puede superar los 200 caracteres'
            : null
      break

    case 'content':
      errors.content = !form.content.trim()
        ? 'El contenido es obligatorio'
        : form.content.trim().length < 10
          ? 'El contenido debe tener al menos 10 caracteres'
          : null
      break
  }
}

// Valida todos los campos y devuelve true si no hay errores
function validateAll() {
  Object.keys(touched).forEach((field) => {
    touched[field] = true
    validateField(field)
  })
  return !Object.values(errors).some(Boolean)
}

// ─── Envío del formulario al backend ──────────────────────────────────

async function handleSubmit() {
  serverError.value = null

  // Si la validación falla, no seguimos
  if (!validateAll()) return

  isSubmitting.value = true

  try {
    // Llamamos al endpoint POST /forums/{forum_id}/threads
    const { response, data } = await apiFetchJson(`/forums/${forumId}/threads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: form.title.trim(),
        content: form.content.trim(),
      }),
    })

    if (response.ok) {
      // Éxito: el hilo se creó correctamente
      const threadId = data.id

      // Si hay imágenes seleccionadas, las subimos una por una
      if (imagePreviews.value.length > 0) {
        // isSubmitting se queda en true mientras subimos imágenes
        for (const img of imagePreviews.value) {
          const formData = new FormData()
          formData.append('file', img.file)

          const uploadResponse = await apiFetch(`/threads/${threadId}/images`, {
            method: 'POST',
            body: formData,
          })

          // Si falla la subida de una imagen, mostramos error pero seguimos
          if (!uploadResponse.ok) {
            const errData = await uploadResponse.json().catch(() => ({}))
            serverError.value = errData.detail || 'Error al subir una imagen'
          }
        }
      }

      // Redirigimos al hilo recién creado para verlo
      router.push({
        name: 'ThreadDetail',
        params: { id: threadId },
      })
    } else if (response.status === 422 && Array.isArray(data.detail)) {
      // Error de validación (Pydantic devuelve un array de errores)
      const firstError = data.detail[0]
      const fieldName = firstError.loc?.at(-1)
      if (fieldName === 'title') {
        errors.title = firstError.msg
      } else if (fieldName === 'content') {
        errors.content = firstError.msg
      } else {
        serverError.value = firstError.msg || 'Error de validación'
      }
    } else {
      // Otro error del servidor
      serverError.value = data.detail || 'Error al crear el hilo'
    }
  } catch {
    serverError.value = 'Error de conexión. Comprueba tu conexión a internet.'
  } finally {
    isSubmitting.value = false
  }
}

// ─── Cargar nombre del foro si no se pasó en la URL ────────────────────

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
})
</script>

<style scoped>
.create-thread {
  max-width: 700px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-4);
  background-color: var(--blanco-calido);
  min-height: 100vh;
}

/* ─── Cabecera ─────────────────────────────────────────────────────────── */

.create-thread__header {
  margin-bottom: var(--space-6);
}

.create-thread__back {
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

.create-thread__back:hover {
  color: var(--rosa-coral);
}

.create-thread__title {
  font-size: 1.75rem;
  margin: 0;
}

.create-thread__subtitle {
  color: var(--texto-secundario);
  font-size: 0.9375rem;
  margin-top: var(--space-1);
}

/* ─── Formulario ───────────────────────────────────────────────────────── */

.create-thread__form {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* ─── Barra de herramientas de formato ─────────────────────────────────── */

.create-thread__toolbar {
  display: flex;
  gap: var(--space-1);
  margin-bottom: var(--space-2);
  padding: var(--space-1);
  background-color: var(--melocoton);
  border-radius: var(--radius-sm);
  border: 1px solid var(--melocoton);
}

.create-thread__toolbar-btn {
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

.create-thread__toolbar-btn:hover {
  background-color: var(--blanco-calido);
  color: var(--rosa-coral);
}

/* ─── Área de texto ────────────────────────────────────────────────────── */

.create-thread__textarea {
  width: 100%;
  padding: var(--space-3);
  font-family: var(--font-body);
  font-size: 0.9375rem;
  line-height: 1.7;
  color: var(--marron-cacao);
  background-color: var(--blanco-calido);
  border: 1.5px solid var(--melocoton);
  border-radius: var(--radius-sm);
  resize: vertical;
  min-height: 180px;
  box-sizing: border-box;
  transition: border-color 150ms ease;
}

.create-thread__textarea:focus {
  outline: none;
  border-color: var(--rosa-coral);
  box-shadow: 0 0 0 3px rgba(244, 132, 95, 0.12);
}

/* ─── Subida de imágenes ───────────────────────────────────────────────── */

.create-thread__images-area {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.create-thread__image-preview {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1.5px solid var(--melocoton);
}

.create-thread__preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.create-thread__remove-image {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 150ms ease;
}

.create-thread__remove-image:hover {
  background-color: rgba(0, 0, 0, 0.8);
}

.create-thread__add-image {
  width: 100px;
  height: 100px;
  border: 2px dashed var(--lila-suave);
  border-radius: var(--radius-sm);
  background: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  color: var(--lila-oscuro);
  font-family: var(--font-body);
  font-size: 0.75rem;
  font-weight: 600;
  transition: all 150ms ease;
}

.create-thread__add-image:hover {
  border-color: var(--rosa-coral);
  color: var(--rosa-coral);
  background-color: var(--melocoton);
}

.create-thread__file-input {
  display: none;
}

.create-thread__image-error {
  color: var(--error);
  font-size: 0.8125rem;
  margin-top: var(--space-1);
}

/* ─── Botones de acción ────────────────────────────────────────────────── */

.create-thread__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding-top: var(--space-2);
  border-top: 1px solid var(--melocoton);
}

/* ─── Error del servidor ───────────────────────────────────────────────── */

.create-thread__server-error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3);
  background-color: rgba(224, 92, 92, 0.1);
  border: 1px solid var(--error);
  border-radius: var(--radius-sm);
  color: var(--error);
  font-size: 0.875rem;
}

/* ─── Animación fade ───────────────────────────────────────────────────── */

.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
