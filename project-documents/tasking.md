# Tasking — Comunidad de Mujeres

---

## HU-01 — Registro de nueva usuaria

- **Tarea 1** — Crear el formulario de registro con los campos: nombre de usuario, email, contraseña y confirmación de contraseña.
- **Tarea 2** — Añadir validaciones de frontend: email con formato válido, contraseña mínimo 8 caracteres con al menos una mayúscula y un número, confirmación de contraseña coincidente.
- **Tarea 3** — Añadir checkbox de declaración de honor ("Declaro que soy mujer") obligatorio para continuar.
- **Tarea 4** — Crear el endpoint POST `/auth/register` en el backend que reciba los datos, valide unicidad de email y guarde la usuaria en base de datos con contraseña hasheada (bcrypt).
- **Tarea 5** — Generar y devolver un token JWT al completar el registro correctamente.
- **Tarea 6** — Mostrar mensajes de error claros en el formulario cuando la validación falle (email ya en uso, contraseña débil, etc.).
- **Tarea 7** — Redirigir a la pantalla de personalización de perfil (HU-02) tras registro exitoso.
- **Tarea 8** — Escribir tests con Pytest para el endpoint de registro (caso éxito, email duplicado, datos inválidos).

---

## HU-02 — Personalización del perfil en el registro

- **Tarea 1** — Crear el flujo de 4 pasos (stepper) en el frontend tras el registro.
- **Tarea 2** — Paso 1: componente de selección múltiple de aficiones (viajar, aire libre, lectura, cine, pintura, manualidades, otras).
- **Tarea 3** — Paso 2: componente de selección única de rango de edad (18-25, 26-35, 36-45, 46-55, 56-65, +65).
- **Tarea 4** — Paso 3: componente de selección múltiple de situación vital (madre primeriza, divorciada/separada, nido vacío, viuda, buscando amistades, nueva en la ciudad, otras).
- **Tarea 5** — Paso 4: campo de ubicación (provincia/ciudad) con autocompletado y radio de acción opcional.
- **Tarea 6** — Crear el endpoint PATCH `/users/me/profile` para guardar las preferencias en base de datos.
- **Tarea 7** — Permitir omitir cada paso con botón "Saltar" y completar el flujo igualmente.
- **Tarea 8** — Escribir tests con Pytest para el endpoint de actualización de perfil.

---

## HU-03 — Inicio de sesión

- **Tarea 1** — Crear el formulario de login con campos email, contraseña y checkbox "Recordarme".
- **Tarea 2** — Crear el endpoint POST `/auth/login` que valide credenciales y devuelva token JWT.
- **Tarea 3** — Almacenar el token en el cliente (localStorage o cookie segura según "Recordarme").
- **Tarea 4** — Configurar el interceptor de Axios/Fetch para incluir el token en cada petición autenticada.
- **Tarea 5** — Mostrar mensaje de error si las credenciales son incorrectas.
- **Tarea 6** — Crear guard de rutas en Vue Router que redirija al login si no hay sesión activa.
- **Tarea 7** — Escribir tests con Pytest para el endpoint de login (éxito, credenciales incorrectas).

---

## HU-04 — Cierre de sesión

- **Tarea 1** — Añadir botón de cerrar sesión en la barra de navegación principal.
- **Tarea 2** — Al hacer clic, eliminar el token del cliente y limpiar el estado de la store (Pinia).
- **Tarea 3** — Redirigir a la página de inicio público tras cerrar sesión.

---

## HU-05 — Recuperación de contraseña

- **Tarea 1** — Crear formulario de "¿Olvidaste tu contraseña?" con campo de email.
- **Tarea 2** — Crear endpoint POST `/auth/forgot-password` que genere un token de recuperación y lo envíe por email.
- **Tarea 3** — Crear página de restablecimiento de contraseña que reciba el token por URL.
- **Tarea 4** — Crear endpoint POST `/auth/reset-password` que valide el token (expiración 24h) y actualice la contraseña.
- **Tarea 5** — Mostrar mensajes de confirmación y error en cada paso del flujo.
- **Tarea 6** — Escribir tests con Pytest para ambos endpoints.

---

## HU-06 — Ver y editar perfil

- **Tarea 1** — Crear la página de perfil con: avatar, nombre de usuario, bio, aficiones, situación vital, rango de edad y ubicación.
- **Tarea 2** — Añadir funcionalidad de subida y cambio de foto de avatar (con previsualización).
- **Tarea 3** — Crear modo edición inline o modal para cada sección del perfil.
- **Tarea 4** — Crear endpoint PATCH `/users/me` para guardar los cambios.
- **Tarea 5** — Añadir control de visibilidad por campo (público / solo yo).
- **Tarea 6** — Escribir tests con Pytest para el endpoint de edición de perfil.

---

## HU-07 — Ver listado de foros y subforos

- **Tarea 1** — Crear el modelo de base de datos para `Forum` y `Subforum` con sus relaciones.
- **Tarea 2** — Poblar la base de datos con los foros y subforos iniciales mediante seeds.
- **Tarea 3** — Crear endpoint GET `/forums` que devuelva todos los foros con sus subforos, número de hilos y última actividad.
- **Tarea 4** — Crear la página de listado de foros en Vue con tarjetas por categoría e icono representativo.
- **Tarea 5** — Implementar el desplegable de subforos al acceder a un foro principal.
- **Tarea 6** — Escribir tests con Pytest para el endpoint de foros.

---

## HU-08 — Ver hilos de un foro

- **Tarea 1** — Crear el modelo de base de datos para `Thread` (hilo) con relación a foro/subforo y usuaria autora.
- **Tarea 2** — Crear endpoint GET `/forums/{forum_id}/threads` con paginación y ordenación (recientes / más comentados).
- **Tarea 3** — Crear la página de listado de hilos con indicador de actividad nueva.
- **Tarea 4** — Implementar paginación o scroll infinito en el frontend.
- **Tarea 5** — Escribir tests con Pytest para el endpoint de hilos.

---

## HU-09 — Crear un hilo en un foro

- **Tarea 1** — Crear el formulario de nuevo hilo con campos: título, contenido (editor de texto enriquecido) e imágenes adjuntas.
- **Tarea 2** — Crear endpoint POST `/forums/{forum_id}/threads` que guarde el hilo en base de datos.
- **Tarea 3** — Gestionar la subida de imágenes adjuntas al servidor.
- **Tarea 4** — Redirigir al hilo recién creado tras el envío exitoso.
- **Tarea 5** — Escribir tests con Pytest para el endpoint de creación de hilo.

---

## HU-10 — Responder en un hilo

- **Tarea 1** — Crear el modelo de base de datos para `Reply` (respuesta) con relación a hilo y usuaria.
- **Tarea 2** — Añadir caja de respuesta al final del hilo con soporte para citar respuestas anteriores.
- **Tarea 3** — Crear endpoint POST `/threads/{thread_id}/replies` para guardar la respuesta.
- **Tarea 4** — Actualizar la vista del hilo en tiempo real (o refresco automático) al añadir una respuesta.
- **Tarea 5** — Gestionar la subida de imágenes en respuestas.
- **Tarea 6** — Escribir tests con Pytest para el endpoint de respuestas.

---

## HU-11 — Editar o eliminar mi publicación

- **Tarea 1** — Mostrar opciones de editar/eliminar solo a la autora del hilo o respuesta.
- **Tarea 2** — Crear endpoint PATCH `/threads/{thread_id}` y PATCH `/replies/{reply_id}` para editar contenido.
- **Tarea 3** — Mostrar marca "editado" con fecha tras una edición.
- **Tarea 4** — Crear endpoint DELETE `/threads/{thread_id}` y DELETE `/replies/{reply_id}` que reemplacen el contenido por "Mensaje eliminado".
- **Tarea 5** — Escribir tests con Pytest para los endpoints de edición y eliminación.

---

## HU-12 — Reportar contenido inapropiado

- **Tarea 1** — Añadir botón de reporte en cada hilo y respuesta.
- **Tarea 2** — Crear modal de reporte con selector de motivo y campo libre opcional.
- **Tarea 3** — Crear endpoint POST `/reports` que guarde el reporte en base de datos.
- **Tarea 4** — Evitar que la usuaria reportada reciba notificación del reporte.
- **Tarea 5** — Escribir tests con Pytest para el endpoint de reportes.

---

## HU-13 — Ver planes disponibles

- **Tarea 1** — Crear el modelo de base de datos para `Plan` con campos: título, descripción, ciudad, dirección, fecha, plazas, categoría e imagen.
- **Tarea 2** — Crear endpoint GET `/plans` con filtros por ciudad, categoría y fecha.
- **Tarea 3** — Crear la página de listado de planes con tarjetas visuales.
- **Tarea 4** — Implementar los filtros de búsqueda en el frontend.
- **Tarea 5** — Escribir tests con Pytest para el endpoint de planes.

---

## HU-14 — Crear un plan

- **Tarea 1** — Crear el formulario de nuevo plan con todos los campos requeridos e imagen opcional.
- **Tarea 2** — Crear endpoint POST `/plans` que guarde el plan y apunte automáticamente a la creadora.
- **Tarea 3** — Gestionar la subida de imagen del plan.
- **Tarea 4** — Redirigir a la ficha del plan recién creado.
- **Tarea 5** — Escribir tests con Pytest para el endpoint de creación de plan.

---

## HU-15 — Apuntarse a un plan

- **Tarea 1** — Crear el modelo de base de datos para `PlanParticipant` (relación usuaria-plan).
- **Tarea 2** — Añadir botón "Apuntarme" / "Desapuntarme" en la ficha del plan.
- **Tarea 3** — Crear endpoint POST `/plans/{plan_id}/join` y DELETE `/plans/{plan_id}/leave`.
- **Tarea 4** — Deshabilitar el botón y mostrar "Completo" cuando se alcance el límite de plazas.
- **Tarea 5** — Enviar notificación a la creadora cuando alguien se apunte.
- **Tarea 6** — Escribir tests con Pytest para los endpoints de apuntarse y desapuntarse.

---

## HU-16 — Calendario de planes

- **Tarea 1** — Integrar un componente de calendario en Vue (por ejemplo, vue-cal o similar).
- **Tarea 2** — Crear endpoint GET `/plans/calendar` que devuelva los planes del mes seleccionado.
- **Tarea 3** — Marcar visualmente los planes en los que la usuaria está apuntada.
- **Tarea 4** — Implementar navegación entre vista mensual y semanal.
- **Tarea 5** — Al hacer clic en un plan del calendario, abrir su ficha de detalle.

---

## HU-17 — Chat del plan

- **Tarea 1** — Crear el modelo de base de datos para `PlanMessage` con relación a plan y usuaria.
- **Tarea 2** — Crear el chat automáticamente al crear un plan.
- **Tarea 3** — Crear endpoint GET `/plans/{plan_id}/messages` y POST `/plans/{plan_id}/messages`.
- **Tarea 4** — Restringir el acceso al chat solo a las participantes apuntadas al plan.
- **Tarea 5** — Implementar refresco automático de mensajes en el frontend (polling o WebSocket).
- **Tarea 6** — Mostrar nombre y avatar de cada participante en el chat.
- **Tarea 7** — Revocar acceso al chat cuando una usuaria se desapunte del plan.
- **Tarea 8** — Escribir tests con Pytest para los endpoints del chat.

---

## HU-18 — Ver noticias relevantes

- **Tarea 1** — Crear el modelo de base de datos para `News` con campos: título, resumen, imagen, fuente, URL externa, categoría y fecha.
- **Tarea 2** — Poblar noticias iniciales mediante seeds.
- **Tarea 3** — Crear endpoint GET `/news` con filtro por categoría y paginación.
- **Tarea 4** — Crear la página de noticias con tarjetas visuales ordenadas por fecha.
- **Tarea 5** — Implementar filtro por categoría en el frontend.
- **Tarea 6** — Escribir tests con Pytest para el endpoint de noticias.

---

## HU-19 — Notificaciones

- **Tarea 1** — Crear el modelo de base de datos para `Notification` con tipo, mensaje, leída/no leída y usuaria destinataria.
- **Tarea 2** — Crear endpoint GET `/notifications` para listar las notificaciones de la usuaria autenticada.
- **Tarea 3** — Crear endpoint PATCH `/notifications/{id}/read` y PATCH `/notifications/read-all`.
- **Tarea 4** — Añadir icono de notificaciones en la barra de navegación con contador de no leídas.
- **Tarea 5** — Disparar notificaciones automáticas en los eventos correspondientes (respuesta en hilo, apuntada a plan, mensaje en chat).
- **Tarea 6** — Escribir tests con Pytest para los endpoints de notificaciones.

---

## HU-20 — Panel de moderación

- **Tarea 1** — Crear roles de usuaria en base de datos: `user`, `moderator`, `admin`.
- **Tarea 2** — Crear el panel de moderación accesible solo para roles `moderator` y `admin`.
- **Tarea 3** — Crear endpoint GET `/admin/reports` para listar reportes pendientes.
- **Tarea 4** — Implementar acciones: eliminar contenido, advertir a usuaria, suspender cuenta.
- **Tarea 5** — Crear endpoint PATCH `/admin/reports/{id}` para registrar la acción tomada.
- **Tarea 6** — Guardar log de acciones con fecha y moderadora responsable.
- **Tarea 7** — Escribir tests con Pytest para los endpoints de moderación.

---

## HU-21 — Diseño responsive

- **Tarea 1** — Definir los breakpoints en el sistema de estilos: móvil (≥320px), tablet (≥768px), escritorio (≥1280px).
- **Tarea 2** — Implementar menú hamburguesa o barra de navegación inferior para móvil.
- **Tarea 3** — Revisar y ajustar todos los formularios para que sean usables en pantalla táctil (tamaño de inputs y botones).
- **Tarea 4** — Probar la interfaz en los tres breakpoints y corregir desbordamientos o solapamientos.

---

## HU-22 — Estilo visual

- **Tarea 1** — Aplicar la paleta de colores y tipografía definida en `style.md` a todos los componentes.
- **Tarea 2** — Crear componentes base reutilizables: botón primario, botón secundario, tarjeta, modal, input, badge.
- **Tarea 3** — Implementar lazy loading en todas las imágenes de la aplicación.
- **Tarea 4** — Añadir transiciones suaves en cambios de ruta y apertura de modales.
- **Tarea 5** — Revisar consistencia visual en todos los componentes antes de cada entrega.
