// Store de autenticación con Pinia.
// Guarda el estado de la sesión (token y datos de la usuaria) y expone
// las acciones de registro y cierre de sesión.

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetchJson } from '../services/http'

export const useAuthStore = defineStore('auth', () => {
  // Estado inicial: primero busca en localStorage, si no hay busca en sessionStorage
  const token = ref(localStorage.getItem('token') || sessionStorage.getItem('token') || null)
  const user = ref(JSON.parse(
    localStorage.getItem('user') || sessionStorage.getItem('user') || 'null'
  ))
  const isLoading = ref(false) // true mientras esperamos respuesta del servidor
  const error = ref(null)

  // Computed: devuelve true si hay un token activo (la usuaria está logueada)
  const isAuthenticated = computed(() => !!token.value)

  // Mapa para traducir los nombres de campo del backend al formato del formulario
  const FIELD_MAP = {
    password: 'password',
    email: 'email',
    username: 'username',
    confirm_password: 'confirmPassword',
  }

  async function register(payload) {
    isLoading.value = true
    error.value = null

    try {
      const { response, data } = await apiFetchJson('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      // Si la respuesta no es exitosa, procesamos el error
      if (!response.ok) {
        // Error 422: validación fallida (Pydantic devuelve un array de errores)
        if (response.status === 422 && Array.isArray(data.detail)) {
          const firstError = data.detail[0]
          const fieldName = firstError.loc?.at(-1) // Último elemento de la ruta del error
          return {
            success: false,
            field: FIELD_MAP[fieldName] || null,
            message: firstError.msg || 'Error de validación',
          }
        }

        // Error 409: conflicto (email o usuario ya en uso)
        if (res.status === 409) {
          const msg = data.detail || ''
          const field = msg.toLowerCase().includes('email') ? 'email'
            : msg.toLowerCase().includes('usuario') ? 'username'
            : null
          return { success: false, field, message: msg }
        }

        return { success: false, field: null, message: data.detail || 'Error al registrarse' }
      }

      // Registro exitoso: guardamos token y usuaria en memoria y en localStorage
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      return { success: true, field: null, message: null }

    } catch (err) {
      // Error de red (sin conexión, servidor caído...)
      error.value = err.message
      return { success: false, field: null, message: err.message || 'Error de conexión' }
    } finally {
      isLoading.value = false // Siempre desactivamos el loading al terminar
    }
  }

  async function login(payload) {
    isLoading.value = true
    error.value = null

    try {
      const { response, data } = await apiFetchJson('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: payload.email, password: payload.password }),
      })

      // Si el servidor devuelve error (credenciales incorrectas)
      if (!response.ok) {
        // El backend devuelve 401 con "Email o contraseña incorrectos"
        return { success: false, field: null, message: data.detail || 'Error al iniciar sesión' }
      }

      // Login exitoso: guardamos token y usuaria
      token.value = data.access_token
      user.value = data.user

      // "Recordarme": si está marcado guardamos en localStorage (persiste),
      // si no, en sessionStorage (se borra al cerrar el navegador)
      if (payload.remember) {
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
      } else {
        sessionStorage.setItem('token', data.access_token)
        sessionStorage.setItem('user', JSON.stringify(data.user))
      }

      return { success: true, field: null, message: null }

    } catch (err) {
      error.value = err.message
      return { success: false, field: null, message: err.message || 'Error de conexión' }
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    // Limpiamos todo el estado y ambos storages por si acaso
    token.value = null
    user.value = null
    error.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('user')
  }

  return { token, user, isLoading, error, isAuthenticated, register, login, logout }
})
