# Historias de Usuario — Aplicación Comunidad de Mujeres

## Contexto del Proyecto

Aplicación web exclusiva para mujeres, orientada a crear comunidad segura. Permite participar en foros temáticos, organizar planes y quedadas, consultar noticias relevantes y conectar con otras usuarias según intereses, edad, situación vital y ubicación.

**Stack técnico:** Vue 3 · Python (FastAPI) · PostgreSQL · Docker Compose · JWT · Pytest

---

## ÉPICA 1 — Registro e Inicio de Sesión

### HU-01 — Registro de nueva usuaria
**Como** mujer que quiere unirse a la comunidad,  
**quiero** poder registrarme en la aplicación,  
**para** acceder a todos los espacios y funcionalidades de forma segura.

**Criterios de aceptación:**
- El formulario solicita: nombre de usuario, email, contraseña y confirmación de contraseña.
- La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número.
- El email debe ser único en el sistema.
- Tras el registro exitoso, se redirige al proceso de personalización del perfil (HU-02).
- Se genera un token JWT al completar el registro.
- Solo se permite el acceso a mujeres (se incluye declaración de honor en el formulario).

---

### HU-02 — Personalización del perfil en el registro
**Como** nueva usuaria,  
**quiero** poder indicar mis intereses, rango de edad, situación vital y ubicación durante el registro,  
**para** que la aplicación me muestre contenido y comunidades relevantes para mí.

**Criterios de aceptación:**
- Paso 1 — Aficiones (selección múltiple): viajar, actividades al aire libre, lectura, cine, pintura, manualidades, otras.
- Paso 2 — Rango de edad (selección única): 18-25, 26-35, 36-45, 46-55, 56-65, +65.
- Paso 3 — Situación vital (selección múltiple): madre primeriza, divorciada/separada, nido vacío, viuda, buscando nuevas amistades, nueva en la ciudad/pueblo, otras.
- Paso 4 — Ubicación: provincia/ciudad y radio de acción (opcional).
- Todos los pasos son opcionales pero recomendados; se pueden editar después desde el perfil.
- El perfil queda guardado en base de datos asociado a la usuaria.

---

### HU-03 — Inicio de sesión
**Como** usuaria registrada,  
**quiero** poder iniciar sesión con mi email y contraseña,  
**para** acceder a mi cuenta y al contenido de la aplicación.

**Criterios de aceptación:**
- Formulario con email y contraseña.
- Se devuelve un token JWT válido al autenticarse correctamente.
- Si las credenciales son incorrectas, se muestra mensaje de error claro.
- Opción de "recordarme" para mantener la sesión activa.
- Sin sesión activa, cualquier ruta protegida redirige al login.

---

### HU-04 — Cierre de sesión
**Como** usuaria autenticada,  
**quiero** poder cerrar sesión,  
**para** proteger mi cuenta cuando no esté usando la aplicación.

**Criterios de aceptación:**
- Botón de cerrar sesión visible en la navegación principal.
- Al cerrar sesión se invalida el token y se redirige al inicio público.

---

### HU-05 — Recuperación de contraseña
**Como** usuaria que ha olvidado su contraseña,  
**quiero** poder recuperarla mediante mi email,  
**para** volver a acceder a mi cuenta.

**Criterios de aceptación:**
- Formulario de recuperación con campo de email.
- Se envía un enlace de restablecimiento al email indicado.
- El enlace expira en 24 horas.
- La nueva contraseña debe cumplir los mismos requisitos que en el registro.

---

## ÉPICA 2 — Perfil de Usuaria

### HU-06 — Ver y editar perfil
**Como** usuaria registrada,  
**quiero** poder ver y editar mi perfil,  
**para** mantener mi información actualizada y personalizada.

**Criterios de aceptación:**
- Sección de perfil con: foto de avatar, nombre de usuario, bio corta, aficiones, situación vital, rango de edad y ubicación.
- Posibilidad de subir o cambiar foto de perfil.
- Los cambios se guardan en base de datos al confirmar.
- El perfil público muestra solo la información que la usuaria decide hacer visible.

---

## ÉPICA 3 — Foros

### HU-07 — Ver listado de foros y subforos
**Como** usuaria autenticada,  
**quiero** ver todos los foros disponibles organizados por categoría,  
**para** encontrar fácilmente el espacio donde quiero participar.

**Criterios de aceptación:**
- Listado de foros principales con su descripción e icono representativo.
- Foros disponibles:
  - **Maternidad** (subforos: Embarazo, Muerte perinatal y duelo, Postparto, Niños 0-2 años, Niños 3-6 años, Adolescencia)
  - **Viajes**
  - **Chismes y cotilleos**
  - **Divorciadas y separadas**
  - **Mayores de 60 y jubilación**
  - **Menopausia**
  - **No maternidad**
  - **Desahogo y violencia recibida**
- Cada foro muestra número de hilos activos y última actividad.
- Los subforos se despliegan al acceder al foro principal.

---

### HU-08 — Ver hilos de un foro
**Como** usuaria autenticada,  
**quiero** ver los hilos de conversación de un foro o subforo,  
**para** leer lo que otras usuarias han compartido.

**Criterios de aceptación:**
- Listado de hilos ordenados por actividad reciente (por defecto).
- Cada hilo muestra: título, autora, fecha, número de respuestas y si tiene actividad nueva.
- Paginación o scroll infinito.
- Opción de filtrar por más recientes o más comentados.

---

### HU-09 — Crear un hilo en un foro
**Como** usuaria autenticada,  
**quiero** poder crear un nuevo hilo en un foro,  
**para** iniciar una conversación sobre un tema que me interesa.

**Criterios de aceptación:**
- Formulario con título (obligatorio) y contenido (obligatorio).
- Posibilidad de adjuntar imágenes.
- El hilo queda asociado al foro/subforo donde se crea.
- Tras crear el hilo, se redirige al hilo recién creado.

---

### HU-10 — Responder en un hilo
**Como** usuaria autenticada,  
**quiero** poder responder en un hilo existente,  
**para** participar en la conversación.

**Criterios de aceptación:**
- Caja de texto al final del hilo para escribir la respuesta.
- Posibilidad de citar una respuesta anterior.
- Posibilidad de adjuntar imágenes.
- La respuesta aparece al instante en el hilo.

---

### HU-11 — Editar o eliminar mi publicación
**Como** autora de un hilo o respuesta,  
**quiero** poder editar o eliminar mi publicación,  
**para** corregir errores o retirar contenido que ya no quiero compartir.

**Criterios de aceptación:**
- Solo la autora puede editar o eliminar su propio contenido.
- Las ediciones muestran una marca de "editado" con la fecha.
- Al eliminar, el contenido se reemplaza por un mensaje neutro ("Mensaje eliminado").

---

### HU-12 — Reportar contenido inapropiado
**Como** usuaria,  
**quiero** poder reportar un hilo o respuesta que considere inapropiado,  
**para** mantener el espacio seguro para todas.

**Criterios de aceptación:**
- Botón de reporte en cada hilo y respuesta.
- Formulario con motivo del reporte (selección + campo libre opcional).
- El reporte queda registrado para revisión de moderación.
- La usuaria reportada no recibe notificación del reporte.

---

## ÉPICA 4 — Planes y Quedadas

### HU-13 — Ver planes disponibles
**Como** usuaria autenticada,  
**quiero** ver los planes y quedadas publicados,  
**para** encontrar actividades que me interesen cerca de mí.

**Criterios de aceptación:**
- Listado de planes con: título, descripción, ciudad, fecha, número de apuntadas y plazas disponibles.
- Filtro por ciudad/provincia.
- Filtro por categoría de plan (cultura, deporte, gastronomía, viajes, etc.).
- Filtro por fecha.

---

### HU-14 — Crear un plan
**Como** usuaria autenticada,  
**quiero** poder crear un plan o quedada,  
**para** proponer una actividad a otras usuarias.

**Criterios de aceptación:**
- Formulario con: título, descripción, ciudad, dirección o punto de encuentro, fecha y hora, número máximo de participantes (opcional), categoría e imagen opcional.
- El plan queda publicado y visible para otras usuarias.
- La creadora queda automáticamente apuntada al plan.

---

### HU-15 — Apuntarse a un plan
**Como** usuaria autenticada,  
**quiero** poder apuntarme a un plan publicado,  
**para** confirmar mi asistencia y quedar con otras mujeres.

**Criterios de aceptación:**
- Botón "Apuntarme" visible en la ficha del plan.
- Si el plan tiene límite de plazas y está lleno, el botón se deshabilita y muestra "Completo".
- Al apuntarse, la usuaria queda registrada como participante del plan.
- La usuaria puede desapuntarse antes de la fecha del plan.
- La creadora recibe notificación cuando alguien se apunta.

---

### HU-16 — Ver el calendario de planes
**Como** usuaria autenticada,  
**quiero** ver los planes en un calendario,  
**para** tener una visión clara de las actividades programadas.

**Criterios de aceptación:**
- Vista de calendario mensual con los planes marcados en sus fechas.
- Al hacer clic en un plan del calendario, se abre su ficha de detalle.
- Se distinguen visualmente los planes en los que estoy apuntada.
- Posibilidad de cambiar entre vista mensual y semanal.

---

### HU-17 — Chat del plan
**Como** participante de un plan,  
**quiero** tener acceso a un chat exclusivo con las demás apuntadas,  
**para** coordinar los detalles de la quedada.

**Criterios de aceptación:**
- El chat se crea automáticamente cuando se crea el plan.
- Solo las usuarias apuntadas al plan tienen acceso al chat.
- Mensajes en tiempo real (o con refresco automático).
- Al desapuntarse del plan, se pierde el acceso al chat.
- El chat muestra el nombre y avatar de cada participante.

---

## ÉPICA 5 — Noticias

### HU-18 — Ver noticias relevantes
**Como** usuaria autenticada,  
**quiero** ver noticias actualizadas relacionadas con temas de interés para mujeres,  
**para** estar informada sobre lo que me importa.

**Criterios de aceptación:**
- Sección de noticias con artículos ordenados por fecha (más recientes primero).
- Cada noticia muestra: imagen, titular, resumen, fuente y fecha.
- Categorías de noticias: salud femenina, sociedad, cultura, derechos, bienestar, otras.
- Posibilidad de filtrar por categoría.
- Las noticias pueden ser externas (enlace) o internas (redactadas en la plataforma).

---

## ÉPICA 6 — Notificaciones

### HU-19 — Recibir notificaciones
**Como** usuaria,  
**quiero** recibir notificaciones sobre actividad relevante para mí,  
**para** estar al tanto sin tener que revisar constantemente la aplicación.

**Criterios de aceptación:**
- Notificaciones para: respuestas en mis hilos, menciones, nuevas apuntadas a mis planes, mensajes en chats de planes donde participo, y nuevos planes en mi ciudad.
- Icono de notificaciones en la barra de navegación con contador de no leídas.
- Al hacer clic, se muestra el listado de notificaciones recientes.
- Posibilidad de marcar como leídas individualmente o todas a la vez.

---

## ÉPICA 7 — Moderación y Seguridad

### HU-20 — Panel de moderación (rol moderadora)
**Como** moderadora de la plataforma,  
**quiero** tener acceso a un panel de moderación,  
**para** gestionar los reportes y mantener el espacio seguro.

**Criterios de aceptación:**
- Listado de reportes pendientes con contenido reportado y motivo.
- Acciones disponibles: eliminar contenido, advertir a la usuaria, suspender cuenta temporalmente.
- Registro de acciones tomadas con fecha y moderadora responsable.
- Solo usuarias con rol "moderadora" o "admin" tienen acceso.

---

## ÉPICA 8 — Diseño y Experiencia de Usuario

### HU-21 — Diseño responsive
**Como** usuaria,  
**quiero** poder usar la aplicación desde mi móvil o tablet,  
**para** acceder cómodamente desde cualquier dispositivo.

**Criterios de aceptación:**
- La interfaz se adapta correctamente a pantallas de móvil (≥320px), tablet (≥768px) y escritorio (≥1280px).
- La navegación en móvil usa un menú hamburguesa o barra inferior.
- Los formularios, botones y textos son usables en pantalla táctil.

---

### HU-22 — Estilo visual alegre e intuitivo
**Como** usuaria,  
**quiero** que la aplicación tenga un diseño atractivo, alegre y fácil de usar,  
**para** sentirme cómoda y con ganas de volver.

**Criterios de aceptación:**
- Paleta de colores alegres y suaves (sin grises ni difuminados).
- Tipografía legible y amigable.
- Iconografía clara e intuitiva.
- Las imágenes tienen espacio reservado y se cargan con lazy loading.
- Transiciones y animaciones suaves que no distraigan.
- Consistencia visual en todos los componentes (botones, tarjetas, formularios).

---

## Resumen de Historias

| ID | Épica | Historia |
|----|-------|----------|
| HU-01 | Registro | Registro de nueva usuaria |
| HU-02 | Registro | Personalización del perfil |
| HU-03 | Registro | Inicio de sesión |
| HU-04 | Registro | Cierre de sesión |
| HU-05 | Registro | Recuperación de contraseña |
| HU-06 | Perfil | Ver y editar perfil |
| HU-07 | Foros | Ver listado de foros y subforos |
| HU-08 | Foros | Ver hilos de un foro |
| HU-09 | Foros | Crear un hilo |
| HU-10 | Foros | Responder en un hilo |
| HU-11 | Foros | Editar o eliminar publicación |
| HU-12 | Foros | Reportar contenido |
| HU-13 | Planes | Ver planes disponibles |
| HU-14 | Planes | Crear un plan |
| HU-15 | Planes | Apuntarse a un plan |
| HU-16 | Planes | Calendario de planes |
| HU-17 | Planes | Chat del plan |
| HU-18 | Noticias | Ver noticias relevantes |
| HU-19 | Notificaciones | Recibir notificaciones |
| HU-20 | Moderación | Panel de moderación |
| HU-21 | UX | Diseño responsive |
| HU-22 | UX | Estilo visual alegre e intuitivo |
