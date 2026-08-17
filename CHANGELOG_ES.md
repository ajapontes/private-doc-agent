# Registro de cambios

Todos los cambios relevantes de Private Doc Agent se documentan en este archivo.

La versión en inglés está disponible en [CHANGELOG.md](CHANGELOG.md).

## [0.9.0] - 2026-08-16

### Agregado

- Registro de cambios en español en `CHANGELOG_ES.md`, con el historial completo del proyecto.
- Enlaces cruzados entre los registros de cambios en inglés y español.

### Cambiado

- Documentación del repositorio sincronizada en inglés y español para la versión `0.9.0`.
- Versión de la aplicación actualizada a `0.9.0`.

## [0.8.0] - 2026-08-10

### Agregado

- Diagnóstico por componente en `/health` para Ollama y el almacén vectorial local.
- Gestión configurable de reintentos para errores transitorios de conexión y servidor de Ollama.
- Pruebas de regresión para formatos no soportados, fallos de infraestructura, reindexación segura y preservación exacta de nombres de archivo.

### Cambiado

- Los formatos de entrada no soportados, incluido `.xlsx`, se detectan durante la indexación masiva y se mueven a `data/invalid/` sin detener los documentos válidos.
- La reindexación guarda los nuevos chunks antes de eliminar únicamente los obsoletos, preservando el índice anterior si falla la generación o la persistencia.
- Los fallos de Ollama y ChromaDB se clasifican como errores de infraestructura y se exponen como respuestas HTTP `503`.
- Los nombres físicos de archivo se preservan exactamente; la aplicación no intenta corregir ni renombrar nombres que parezcan dañados.
- Versión de la aplicación actualizada a `0.8.0`.

### Corregido

- Los planes del agente sin la propiedad `arguments` se procesan de forma segura.
- Los archivos no soportados ya no se ignoran silenciosamente durante la indexación masiva.

## [0.7.0] - 2026-08-08

### Agregado

- Cuarentena local `data/invalid/` para documentos que no pueden procesarse.
- Movimiento de documentos inválidos sin colisiones y preservando archivos existentes.
- Diagnóstico estructurado configurable con `DETAILED_TRACE_ENABLED` para el agente local.
- Documentación del repositorio en español en `README_ES.md`.
- Archivo `.env.example` con la configuración de ejecución soportada.
- Pruebas automatizadas para cuarentena, indexación masiva resiliente y privacidad del trace.

### Cambiado

- La indexación masiva continúa con los documentos válidos después de un error de documento.
- Las respuestas de indexación masiva incluyen cantidades de documentos inválidos y detalles de procesamiento.
- Versión de la aplicación actualizada a `0.7.0`.

### Seguridad

- Los traces detallados excluyen solicitudes del usuario, contenido de documentos, prompts, valores de argumentos y resultados de herramientas.
- El almacenamiento de documentos inválidos permanece local y excluido de Git.

## [0.6.0]

- Métricas de distancia vectorial, parámetros de recuperación, puntajes de relevancia normalizados y reinicio seguro de la colección configurables.

## [0.5.0]

- Agente local de un solo paso con herramientas permitidas, planificación validada y ejecución controlada.

## [0.4.0]

- Ingesta de PDF y DOCX integrada con el pipeline RAG local.

## [0.3.0]

- Embeddings locales, indexación con ChromaDB, recuperación semántica y RAG fundamentado.

## [0.2.0]

- Resumen local con Ollama y mejoras de logging orientadas a la privacidad.

## [0.1.0]

- Base de FastAPI, descubrimiento y lectura de documentos, y búsqueda por palabras clave.
