// Servicio HTTP centralizado.
// apiFetch() envuelve fetch() nativo y añade automáticamente el token JWT
// en el header "Authorization", para que no tengas que escribirlo en cada petición.

// El token se guarda en localStorage (Recordarme activado) o sessionStorage (sin recordar)
const STORAGE_KEY = 'token'

function getToken() {
  // Busca el token primero en localStorage, si no hay busca en sessionStorage
  return localStorage.getItem(STORAGE_KEY) || sessionStorage.getItem(STORAGE_KEY) || null
}

export async function apiFetch(url, options = {}) {
  const token = getToken()

  // Copiamos los headers que nos pasaron (si no hay, empezamos con objeto vacío)
  const headers = { ...(options.headers || {}) }

  // Si hay token guardado, lo añadimos como header de autorización
  // Así el backend sabe qué usuaria está haciendo la petición
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Hacemos la misma petición fetch(), pero con los headers enriquecidos
  const response = await fetch(url, {
    ...options,
    headers,
  })

  // Si el servidor responde 401 (no autorizado), el token expiró o es inválido
  // Lanzamos un evento personalizado para que main.js pueda cerrar la sesión
  if (response.status === 401) {
    window.dispatchEvent(new CustomEvent('auth:unauthorized'))
  }

  return response
}

// Versión cómoda que además de hacer la petición, parsea la respuesta a JSON
// Devuelve un objeto con { response, data } para tener acceso a ambos
export async function apiFetchJson(url, options = {}) {
  const response = await apiFetch(url, options)
  const data = await response.json()
  return { response, data }
}
