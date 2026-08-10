# private-doc-agent

Private Doc Agent es una API *local-first* para leer, buscar, indexar y consultar documentos privados. El procesamiento de documentos, el almacenamiento vectorial, los embeddings y la inferencia del modelo se ejecutan localmente mediante FastAPI, ChromaDB y Ollama.

## Versión actual

`v0.8.0`

La documentación en inglés está disponible en [README.md](README.md).

## Funcionalidades implementadas

- Lectura y extracción de texto de archivos `.txt`, `.md`, `.pdf` y `.docx`.
- Búsqueda literal, resumen local, embeddings, indexación y recuperación semántica.
- RAG local con respuestas fundamentadas y fuentes trazables.
- Agente local de un solo paso con herramientas permitidas y argumentos validados.
- Métrica vectorial configurable: `cosine`, `l2` o `ip`.
- Reinicio seguro de la colección vectorial con confirmación explícita.
- Indexación masiva resiliente: los documentos inválidos se mueven a `data/invalid/` y los válidos continúan procesándose.
- Detección y cuarentena de formatos no soportados durante la indexación masiva.
- Reindexación segura que reemplaza chunks modificados y elimina únicamente los obsoletos.
- Reintentos configurables para fallos transitorios de Ollama y diagnóstico de dependencias en `/health`.
- Preservación exacta del nombre físico de cada archivo, sin correcciones ni renombrados automáticos.
- Trace estructurado y configurable para depuración, sin exponer solicitudes ni contenido privado.
- Logs operativos y de interacción con el LLM separados.
- Pruebas automatizadas para servicios, API, RAG, agente, configuración, ChromaDB, cuarentena y trace.

La orquestación multiagente, MCP, una interfaz gráfica, OCR y formatos adicionales todavía no están implementados.

## Arquitectura

```text
Cliente / Swagger
       |
       v
    FastAPI
       |
       +----------------+----------------+----------------+
       |                |                |                |
       v                v                v                v
Documentos          Indexación/RAG   Agente local     Administración
listar/leer         fragmentar       planificar       confirmar reset
buscar/resumir      embeddings       elegir tool      recrear colección
cuarentena          ChromaDB          ejecutar una vez métrica configurada
```

## Instalación

```powershell
git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Confirma los modelos locales disponibles:

```powershell
ollama list
```

## Configuración

| Variable | Predeterminado | Propósito |
|---|---:|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL del servicio local de Ollama. |
| `OLLAMA_MODEL` | `qwen3.5:4b` | Modelo local de generación. |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` | Modelo local de embeddings. |
| `OLLAMA_REQUEST_TIMEOUT_SECONDS` | `120` | Duración máxima de cada solicitud a Ollama. |
| `OLLAMA_MAX_RETRIES` | `2` | Reintentos ante fallos transitorios de conexión o servidor. |
| `EMBEDDING_BATCH_SIZE` | `32` | Tamaño máximo de cada lote de embeddings. |
| `CHUNK_SIZE` | `1000` | Longitud de cada fragmento. |
| `CHUNK_OVERLAP` | `200` | Solapamiento entre fragmentos. |
| `CHROMA_COLLECTION_NAME` | `private_documents` | Nombre de la colección local. |
| `VECTOR_DISTANCE_METRIC` | `cosine` | Métrica `cosine`, `l2` o `ip`. |
| `VECTOR_SEARCH_TOP_K` | `5` | Cantidad predeterminada de resultados. |
| `VECTOR_MIN_RELEVANCE_SCORE` | vacío | Umbral opcional de relevancia entre `0` y `1`. |
| `LOG_SENSITIVE_CONTENT` | `false` | Control reservado para contenido sensible en logs. |
| `DETAILED_TRACE_ENABLED` | `false` | Incluye el trace seguro en respuestas exitosas de `/agent`. |

## Ejecución

```powershell
python -m uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Endpoints

| Método | Endpoint | Propósito |
|---|---|---|
| `GET` | `/health` | Estado y versión de la aplicación. |
| `GET` | `/documents` | Lista los documentos soportados. |
| `GET` | `/documents/{filename}` | Lee un documento. |
| `POST` | `/documents/index` | Indexa todos los documentos y pone en cuarentena los inválidos. |
| `POST` | `/documents/{filename}/index` | Indexa un documento. |
| `POST` | `/search` | Búsqueda literal. |
| `POST` | `/retrieve` | Recuperación semántica. |
| `POST` | `/summarize` | Resumen local. |
| `POST` | `/ask` | Respuesta RAG con fuentes. |
| `POST` | `/agent` | Planifica y ejecuta una herramienta permitida. |
| `POST` | `/admin/vector-store/reset` | Reinicia la colección con confirmación. |

## Ingesta resiliente

Los documentos se colocan en `data/input/`. Durante la indexación masiva, un archivo ilegible, dañado, cifrado o sin texto indexable se mueve a:

```text
data/invalid/
```

El proceso continúa con los demás documentos. Si ya existe un archivo con el mismo nombre, se agrega un sufijo numérico y no se sobrescribe el anterior. Los fallos de infraestructura, como Ollama o ChromaDB no disponibles, siguen deteniendo la operación para evitar clasificar un documento válido como inválido.

Los formatos no soportados, como `.xlsx`, también se detectan y trasladan a cuarentena. Los nombres se conservan exactamente como existen en disco, incluso si contienen Unicode, errores ortográficos o texto aparentemente dañado; la aplicación no intenta adivinar ni aplicar correcciones.

## Trace detallado

Para habilitarlo en `.env`:

```text
DETAILED_TRACE_ENABLED=true
```

Las respuestas exitosas de `/agent` incluyen las etapas de validación, planificación, decisión, ejecución y resultado, junto con la función responsable, herramienta seleccionada, nombres de argumentos y tipo de resultado. El trace no contiene la solicitud del usuario, contenido documental, prompts, valores de argumentos ni resultados de herramientas.

## Reinicio de la base vectorial

```http
POST /admin/vector-store/reset
Content-Type: application/json

{
  "confirm": true
}
```

El endpoint elimina únicamente la colección configurada y la recrea con la métrica actual. Después se deben indexar nuevamente los documentos.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

La versión `v0.8.0` contiene 160 pruebas. La suite cubre carga de documentos, PDF/DOCX, nombres Unicode, fragmentación, embeddings, reintentos de Ollama, ChromaDB, métricas, reinicio, reindexación segura, errores de infraestructura, health check, cuarentena, recuperación, RAG, agente, API, configuración, privacidad del trace y logging.

## Privacidad

- Los documentos, embeddings, índices y modelos permanecen en el equipo local.
- `data/input/`, `data/invalid/`, `data/chroma/`, `.env` y los logs privados se excluyen de Git.
- Los logs operativos no almacenan documentos completos.
- `logs/llm_io.log` puede contener prompts, respuestas y fragmentos recuperados; debe permanecer local.
- Revisa los nombres de archivos, logs y respuestas antes de compartir información de diagnóstico.

## Historial resumido

| Versión | Evolución principal |
|---|---|
| `v0.1.0` | API, carga, lectura y búsqueda literal. |
| `v0.2.x` | Resumen con Ollama y logging local. |
| `v0.3.0` | RAG básico, embeddings y ChromaDB. |
| `v0.4.0` | Ingesta PDF y DOCX. |
| `v0.5.0` | Agente local con herramientas permitidas. |
| `v0.6.0` | Métrica configurable y reinicio seguro. |
| `v0.7.0` | Ingesta resiliente, cuarentena, trace detallado y documentación bilingüe. |
| `v0.8.0` | Estabilidad, formatos no soportados, reintentos, reindexación segura y health ampliado. |

## Repositorio

[github.com/ajapontes/private-doc-agent](https://github.com/ajapontes/private-doc-agent)
