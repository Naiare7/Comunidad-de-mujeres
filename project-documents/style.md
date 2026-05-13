# Guía de Estilo — Comunidad de Mujeres

Referencia de diseño para mantener coherencia visual en toda la aplicación. Consultar este archivo antes de implementar cualquier componente o pantalla.

---

## Personalidad visual

Alegre, cálido, femenino sin ser estereotipado, con clase e intuitivo. Los colores deben transmitir energía positiva sin cansar la vista. Nada de grises apagados ni difuminados. Todo tiene presencia y claridad.

---

## Paleta de colores

### Colores principales
| Nombre | Hex | Uso |
|--------|-----|-----|
| Rosa coral | `#F4845F` | Color de acción principal, botones primarios, enlaces activos |
| Lila suave | `#C9B8E8` | Fondos de secciones, badges, highlights |
| Melocotón | `#FDDCB5` | Fondos de tarjetas, áreas de contenido secundario |
| Verde menta | `#A8D5BA` | Confirmaciones, estados positivos, etiquetas de éxito |
| Amarillo mantequilla | `#FFF0A0` | Alertas suaves, destacados, notificaciones |

### Colores de soporte
| Nombre | Hex | Uso |
|--------|-----|-----|
| Blanco cálido | `#FFFAF5` | Fondo general de la aplicación |
| Marrón cacao | `#5C3D2E` | Texto principal, títulos |
| Rosa oscuro | `#C0566B` | Hover de botones primarios, énfasis |
| Lila oscuro | `#8B6BAE` | Texto sobre fondos lila, iconos activos |

### Colores de estado
| Estado | Hex | Uso |
|--------|-----|-----|
| Error | `#E05C5C` | Mensajes de error, validaciones fallidas |
| Éxito | `#5BAD7F` | Confirmaciones, acciones completadas |
| Advertencia | `#F0A500` | Alertas, avisos importantes |
| Info | `#5B9BD5` | Mensajes informativos, tooltips |

> Nunca usar grises puros (#808080, #ccc, etc.) ni fondos difuminados. Si se necesita un tono neutro, usar el blanco cálido o el melocotón muy claro.

---

## Tipografía

### Fuentes
- **Títulos y headings:** `Playfair Display` (Google Fonts) — serif elegante, da carácter y clase.
- **Cuerpo y UI:** `Nunito` (Google Fonts) — redondeada, amigable y muy legible.

### Escala tipográfica
| Elemento | Fuente | Tamaño | Peso |
|----------|--------|--------|------|
| H1 | Playfair Display | 2.25rem (36px) | 700 |
| H2 | Playfair Display | 1.75rem (28px) | 700 |
| H3 | Playfair Display | 1.375rem (22px) | 600 |
| Cuerpo | Nunito | 1rem (16px) | 400 |
| Cuerpo pequeño | Nunito | 0.875rem (14px) | 400 |
| Label / Badge | Nunito | 0.75rem (12px) | 600 |
| Botón | Nunito | 0.9375rem (15px) | 700 |

### Color de texto
- Texto principal: `#5C3D2E`
- Texto secundario / placeholder: `#A07860` (marrón claro, nunca gris)
- Texto sobre fondo oscuro o de color: `#FFFAF5`

---

## Espaciado

Sistema basado en múltiplos de 4px.

| Token | Valor | Uso típico |
|-------|-------|------------|
| `space-1` | 4px | Separación mínima entre elementos inline |
| `space-2` | 8px | Padding interno de badges y chips |
| `space-3` | 12px | Gap entre iconos y texto |
| `space-4` | 16px | Padding de inputs, separación entre campos |
| `space-6` | 24px | Padding de tarjetas, separación entre secciones |
| `space-8` | 32px | Margen entre bloques de contenido |
| `space-12` | 48px | Separación entre secciones grandes |
| `space-16` | 64px | Padding de páginas en escritorio |

---

## Bordes y sombras

- **Border radius base:** `12px` para tarjetas, modales y contenedores.
- **Border radius pequeño:** `8px` para inputs, botones y badges.
- **Border radius pill:** `999px` para chips de categoría y avatares pequeños.
- **Borde sutil:** `1.5px solid #FDDCB5` para separar secciones sin usar grises.
- **Sombra tarjeta:** `0 4px 16px rgba(92, 61, 46, 0.08)` — cálida y suave.
- **Sombra modal:** `0 8px 32px rgba(92, 61, 46, 0.16)`.

---

## Componentes base

### Botón primario
- Fondo: `#F4845F`
- Texto: `#FFFAF5`
- Hover: fondo `#C0566B`
- Border radius: `8px`
- Padding: `12px 24px`
- Fuente: Nunito 700, 15px

### Botón secundario
- Fondo: transparente
- Borde: `2px solid #F4845F`
- Texto: `#F4845F`
- Hover: fondo `#FDDCB5`
- Mismas medidas que el primario

### Botón destructivo
- Fondo: `#E05C5C`
- Texto: `#FFFAF5`
- Hover: fondo oscurecido 10%

### Input / Textarea
- Fondo: `#FFFAF5`
- Borde: `1.5px solid #C9B8E8`
- Foco: borde `#F4845F`, sombra `0 0 0 3px rgba(244,132,95,0.2)`
- Border radius: `8px`
- Padding: `12px 16px`
- Placeholder color: `#A07860`

### Tarjeta
- Fondo: `#FFFAF5`
- Borde: `1.5px solid #FDDCB5`
- Border radius: `12px`
- Sombra: `0 4px 16px rgba(92, 61, 46, 0.08)`
- Padding: `24px`

### Badge / Chip de categoría
- Fondo: `#C9B8E8`
- Texto: `#5C3D2E`
- Border radius: `999px`
- Padding: `4px 12px`
- Fuente: Nunito 600, 12px

### Avatar
- Forma circular (`border-radius: 50%`)
- Borde: `2px solid #F4845F`
- Tamaños: 32px (mini), 48px (lista), 80px (perfil), 120px (página de perfil)

---

## Iconografía

- Librería: **Lucide Icons** (consistente, línea limpia, moderna).
- Tamaño base: `20px` en navegación y listas, `24px` en acciones destacadas.
- Color: heredado del contexto (`#5C3D2E` sobre fondo claro, `#FFFAF5` sobre fondo oscuro).
- No mezclar estilos de iconos de distintas librerías.

---

## Imágenes

- Todas las imágenes usan `lazy loading` (`loading="lazy"`).
- Relación de aspecto fija por tipo:
  - Portada de foro: `16:9`
  - Imagen de plan: `3:2`
  - Imagen de noticia: `16:9`
  - Avatar: `1:1`
- Siempre incluir `alt` descriptivo.
- Placeholder mientras carga: fondo `#FDDCB5` con icono de imagen centrado.

---

## Animaciones y transiciones

- Transición de ruta: fade suave, `200ms ease`.
- Apertura de modal: scale de `0.95` a `1` + fade, `180ms ease-out`.
- Hover en tarjetas: `transform: translateY(-2px)`, `200ms ease`.
- Hover en botones: cambio de color, `150ms ease`.
- No usar animaciones que duren más de `300ms` en interacciones de UI.

---

## Responsive — Breakpoints

| Nombre | Ancho mínimo | Descripción |
|--------|-------------|-------------|
| `mobile` | 320px | Móvil pequeño |
| `tablet` | 768px | Tablet y móvil grande |
| `desktop` | 1280px | Escritorio |

### Navegación
- **Escritorio:** barra lateral izquierda o barra superior horizontal.
- **Tablet:** barra superior compacta con iconos y texto corto.
- **Móvil:** barra inferior fija con iconos de las secciones principales + menú hamburguesa para el resto.

### Grid de contenido
- **Escritorio:** máximo 3 columnas en listados de tarjetas.
- **Tablet:** 2 columnas.
- **Móvil:** 1 columna, ancho completo.

---

## Tono visual por sección

| Sección | Color de acento | Notas |
|---------|----------------|-------|
| Foros | Lila suave `#C9B8E8` | Transmite calma y escucha |
| Planes y quedadas | Rosa coral `#F4845F` | Energía y acción |
| Noticias | Verde menta `#A8D5BA` | Frescura e información |
| Perfil | Melocotón `#FDDCB5` | Calidez personal |
| Notificaciones | Amarillo mantequilla `#FFF0A0` | Atención suave |
| Moderación | Rosa oscuro `#C0566B` | Seriedad sin agresividad |
