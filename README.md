# private-doc-agent

Private Doc Agent is a local-first AI assistant designed to analyze and interact with private documents.

The project is being built incrementally, starting from deterministic document loading and keyword search, and evolving toward a private AI-powered document agent with local LLM support, RAG, tools, MCP, and multi-agent validation.

## Current Version

v0.2.1

## What it does now

Private Doc Agent currently provides a FastAPI backend that can read local `.txt` and `.md` documents, list available files, retrieve document content, search keywords across documents, and summarize documents using a locally running LLM through Ollama.

The current version includes the first AI-powered capability: local document summarization.

The document content is processed locally and sent to a local model served by Ollama. This keeps the project aligned with a local-first and privacy-oriented architecture.

This version also adds centralized application logging to improve traceability and debugging across the API and internal services.

## Current Features

- FastAPI backend.
- Health check endpoint.
- Local document listing.
- Support for `.txt` and `.md` files.
- Document content retrieval.
- Simple keyword search across supported documents.
- Local LLM integration through Ollama.
- Configurable model using environment variables.
- Prompt template for document summarization.
- Document summarization endpoint.
- Centralized application logging.
- Console and rotating file logging.
- Request-level log separator for better traceability.
- Privacy-aware logs that avoid storing document content, full prompts or generated responses.

## AI Layer Introduced

In version `v0.2.0`, the project introduced a local LLM-based generation layer.

Current AI flow:

```text
Local document
  -> document loader
  -> prompt template
  -> local LLM client
  -> Ollama
  -> local generative model
  -> generated summary
```

At this stage, this is not RAG yet. The application sends the full document content to the local LLM as context.

RAG will be introduced in a future version using chunking, embeddings, vector storage, and context retrieval.

## Project Structure

```text
private-doc-agent/
  app/
    __init__.py
    main.py
    config.py
    logging_config.py
    prompts/
      summarize_prompt.txt
    services/
      __init__.py
      document_loader.py
      simple_search.py
      llm_client.py
      summarizer.py
  data/
    input/
      demo.txt
      demo.md
    processed/
  docs/
    roadmap.md
  logs/
    app.log
  tests/
  README.md
  requirements.txt
  .env.example
  .gitignore
```

Note: `logs/app.log` is generated locally and should not be committed to GitHub.

## Requirements

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- requests
- Ollama installed and running locally

## Setup

Clone the repository:

```bash
git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root based on `.env.example`.

Example:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
```

The `.env` file should not be committed to GitHub.

The `.env.example` file should be committed to document the required configuration.

## Ollama Setup

Make sure Ollama is running locally.

Validate Ollama:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:11434
```

Expected response:

```text
Ollama is running
```

List installed models:

```powershell
ollama list
```

Example model used in this project:

```text
qwen3.5:4b
```

If needed, update `.env` with the model available in your local environment.

## Run the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

```text
http://localhost:8000/docs
```


lun, 6 jul a la(s) 22:35
Dentro de IA, quiero entender el concepto de Agentes, de MCP, y algun otro que consideres que me ayude a poder tener claro esta forma de hablar de ahora

Claro, Alfredo. La forma más simple de verlo es esta:

Antes hablábamos de “un modelo de IA que responde”.
Ahora hablamos de “sistemas de IA que entienden una tarea, consultan información, usan herramientas y ejecutan pasos”.

Ahí entran tres conceptos clave: LLM, agente y MCP.

1. LLM
Un LLM es el modelo de lenguaje: GPT, Claude, Gemini, Llama, etc.

Es el “cerebro lingüístico”. Puede razonar, resumir, escribir código, analizar información y tomar decisiones, pero por sí solo no necesariamente tiene acceso a tus archivos, internet, SAP, bases de datos, correo o sistemas internos.

Ejemplo:

“Explícame qué hace este contrato.”

Si solo le pegas el texto, el LLM responde. Pero no fue a buscar nada ni ejecutó acciones externas.

2. Agente
Un agente es un sistema que usa un modelo, pero además puede planear, decidir pasos, usar herramientas y actuar.

La diferencia práctica:

Concepto	Qué hace
Chatbot	Responde preguntas
Copilot	Te ayuda mientras tú diriges
Agente	Puede ejecutar una tarea con cierto nivel de autonomía
Ejemplo:

“Revisa este repositorio, encuentra el error, corrige el código y ejecuta pruebas.”

Ahí el agente puede:

Leer archivos.

Entender la arquitectura.

Buscar el bug.

Modificar código.

Ejecutar pruebas.

Entregarte el resultado.

Eso ya no es solo “pregunta-respuesta”; es trabajo asistido por IA.

3. Herramientas / Tools
Las herramientas son capacidades externas que el agente puede usar.

Por ejemplo:

Buscar en internet.

Leer archivos.

Consultar una base de datos.

Ejecutar código.

Llamar una API.

Crear una imagen.

Consultar SAP.

Enviar un correo.

Crear un ticket.

El modelo no “hace magia”; decide cuándo llamar una herramienta, recibe el resultado y continúa razonando.

OpenAI describe las tools como mecanismos para que los agentes puedan tomar acciones como consultar datos, ejecutar código o llamar APIs externas (OpenAI Agents SDK - Tools).

4. MCP
MCP significa Model Context Protocol.

Es un protocolo para conectar modelos/agentes con herramientas, datos y sistemas externos de una forma estandarizada. La idea es que, en vez de construir una integración diferente para cada modelo y cada sistema, puedas exponer herramientas mediante un servidor MCP.

Una forma sencilla de decirlo:

MCP es como un “conector universal” para que los agentes puedan descubrir y usar herramientas externas.

Ejemplo:

Agente de IA
   ↓
MCP
   ↓
Herramientas: SAP, GitHub, Gmail, Drive, base de datos, filesystem, APIs
OpenAI ya soporta integraciones MCP dentro de su Agents SDK, incluyendo servidores MCP alojados o locales (OpenAI Agents SDK - MCP).

5. RAG
Otro concepto importante es RAG, Retrieval-Augmented Generation.

RAG significa que el modelo responde usando información recuperada desde documentos, bases vectoriales o knowledge bases.

Ejemplo:

“Responde esta pregunta usando solamente los documentos de políticas internas.”

Flujo típico:

Pregunta del usuario
   ↓
Buscar documentos relevantes
   ↓
Pasar fragmentos al modelo
   ↓
Generar respuesta basada en esa evidencia
En tu caso, cuando hablas de ChromaDB, embeddings y documentos vectorizados, estás hablando de una arquitectura RAG.

6. Embeddings y Vector DB
Los embeddings convierten texto en vectores numéricos para poder buscar por significado, no solo por palabras exactas.

Una base vectorial como ChromaDB, Pinecone, Weaviate o FAISS permite decir:

“Encuéntrame los documentos más parecidos semánticamente a esta pregunta.”

Eso es clave para RAG.

7. Orquestación
La orquestación es la coordinación del flujo.

Por ejemplo:

El usuario pide algo.

El agente decide si necesita buscar documentos.

Consulta una base vectorial.

Llama una API.

Valida el resultado.

Responde.

Si hay error, intenta otra ruta.

Frameworks como LangChain, LlamaIndex, Semantic Kernel, CrewAI o el Agents SDK ayudan con esa orquestación.

8. Multiagente
Un sistema multiagente usa varios agentes especializados.

Ejemplo en SAP:

Agente	Rol
Agente funcional	Entiende requerimientos de negocio
Agente técnico	Revisa ABAP, APIs, BADIs
Agente Clean Core	Evalúa extensibilidad y riesgos
Agente redactor	Genera correo, FS o TS
Agente auditor	Revisa consistencia y riesgos
No siempre necesitas multiagentes. Muchas veces un solo agente bien diseñado con buenas herramientas es mejor.

9. Guardrails
Los guardrails son reglas de control.

Sirven para evitar que el agente:

Invente información.

Ejecute acciones peligrosas.

Acceda a datos que no debe.

Responda fuera de política.

Tome decisiones sin aprobación humana.

En empresas, esto es fundamental.

10. Human-in-the-loop
Significa que el humano aprueba ciertos pasos.

Ejemplo:

El agente puede preparar un correo, pero no enviarlo sin tu aprobación.

O:

El agente puede proponer una corrección ABAP, pero no transportarla a calidad sin autorización.

Resumen Mental
La foto completa sería:

Concepto	Cómo entenderlo
LLM	El modelo que razona y genera lenguaje
Agente	LLM + herramientas + capacidad de actuar
Tool	Acción externa que el agente puede usar
MCP	Protocolo estándar para conectar herramientas al agente
RAG	Buscar información relevante antes de responder
Embeddings	Representación numérica del significado
Vector DB	Base para buscar por similitud semántica
Orquestación	Coordinación de pasos, herramientas y decisiones
Multiagente	Varios agentes especializados colaborando
Guardrails	Controles de seguridad y calidad
Human-in-the-loop	Aprobación humana en pasos sensibles
Mi forma favorita de resumirlo:

Un LLM conversa.
Un RAG conversa con memoria documental.
Un agente conversa y actúa.
MCP le permite conectarse ordenadamente con el mundo externo.


Si voy a describir las partes de un agente, como podria verlo? Un Prompt, mas que cosas?, en esto tambien estoy enredado

Sí, totalmente normal que se enrede, porque “agente” se usa como si fuera una sola cosa, pero en realidad es una arquitectura.

Puedes verlo así:

Un agente = Modelo + instrucciones + contexto + herramientas + memoria + lógica de decisión + controles + salida.

Una forma muy clara de describir sus partes sería esta:

Parte	Qué es	Ejemplo
Modelo	El LLM que razona y genera respuestas	GPT, Claude, Gemini, Llama
Prompt / Instrucciones	Las reglas de comportamiento del agente	“Eres un analista SAP Clean Core…”
Contexto	Información que el agente recibe para resolver la tarea	Documentos, conversación, datos del usuario
Herramientas	Acciones externas que puede ejecutar	Buscar web, leer archivos, consultar SAP, llamar APIs
Memoria	Información persistente que recuerda entre interacciones	Preferencias, proyectos, decisiones previas
Planificación	Capacidad de dividir una tarea en pasos	“Primero leo, luego comparo, luego redacto”
Orquestación	Lógica que decide qué paso o herramienta usar	Si falta información, consulta una fuente
Guardrails	Reglas de seguridad, permisos y límites	No enviar correo sin aprobación
Output	La respuesta o acción final	Informe, código, correo, ticket, análisis
La confusión suele venir porque uno piensa que el agente es solo el prompt. Pero el prompt es apenas una parte.

Una imagen mental sencilla:

Usuario
  ↓
Prompt / Instrucciones
  ↓
Modelo LLM
  ↓
Contexto + Memoria
  ↓
Herramientas / MCP / APIs
  ↓
Planificación y control
  ↓
Respuesta o acción
El prompt
El prompt define la personalidad, el rol, las reglas y el objetivo.

Ejemplo:

Eres un agente experto en SAP Clean Core.
Tu tarea es analizar desarrollos Z, identificar riesgos,
clasificar extensiones y proponer alternativas compatibles con Clean Core.
Pero con solo eso, el agente todavía está “encerrado” en texto.

Las herramientas
Son lo que le permite actuar.

Ejemplo:

Herramientas disponibles:
- Leer documentos técnicos
- Consultar repositorios ABAP
- Buscar APIs liberadas
- Generar matriz de riesgos
- Crear correo de recomendación
Sin herramientas, el agente solo recomienda.
Con herramientas, puede trabajar.

El contexto
Es la información que necesita para no inventar.

Ejemplo:

Contexto:
- Cliente: Banco X
- Sistema: S/4HANA
- Objetivo: evaluar custom code
- Política: solo extensiones Clean Core A/B
- Documentos: matriz WRICEF, reporte ATC, notas SAP
La memoria
Es lo que le permite mantener continuidad.

Ejemplo:

Recuerda que el cliente no acepta excepciones ATC.
Recuerda que el aprobador técnico es X.
Recuerda que la nomenclatura de paquetes debe ser ZC/ZS.
La planificación
Es la capacidad de armar pasos.

Ejemplo:

1. Leer la matriz WRICEF.
2. Identificar objetos críticos.
3. Cruzar contra resultados ATC.
4. Clasificar riesgo.
5. Recomendar acción.
6. Generar resumen ejecutivo.
La orquestación
Es el “director de tráfico”.

Decide cosas como:

Si no tengo evidencia, busco documentos.
Si el usuario pide código, leo el repositorio.
Si hay una acción riesgosa, pido aprobación.
Si la respuesta necesita datos actuales, consulto internet.
MCP
MCP entra especialmente en la parte de herramientas.

Puedes decir:

MCP es la capa estándar que permite que el agente descubra y use herramientas externas.

O sea:

Agente
  ↓
MCP
  ↓
SAP / GitHub / Drive / Base de datos / APIs / Archivos
Una Definición Buena
Si tuvieras que explicarlo en una reunión, podrías decir:

Un agente de IA no es solo un prompt. Es una solución compuesta por un modelo de lenguaje, instrucciones, contexto, herramientas, memoria, lógica de planificación y controles de seguridad, que le permiten no solo responder, sino ejecutar tareas de forma guiada.

Y más corto:

Un agente es un LLM con rol, contexto, herramientas y capacidad de tomar pasos para cumplir un objetivo.

Esa frase es muy buena para no perderte.


y cuando me dicen que es una solucion multiagente? como puedo imaginarlo?

Una solución multiagente la puedes imaginar como un equipo de trabajo, no como una sola IA gigante.

En vez de tener un agente que intenta hacerlo todo, tienes varios agentes con roles específicos, y cada uno aporta una parte del trabajo.

Por ejemplo:

Usuario
  ↓
Agente coordinador
  ↓
Agente investigador
Agente técnico
Agente auditor
Agente redactor
  ↓
Respuesta final
La idea clave es esta:

Multiagente = varios agentes especializados colaborando para resolver una tarea.

Ejemplo Simple
Imagina que pides:

“Analiza este requerimiento SAP y dime si cumple Clean Core.”

Una solución de un solo agente haría todo:

Leer el requerimiento.

Interpretarlo.

Buscar riesgos.

Proponer alternativa.

Redactar respuesta.

Una solución multiagente podría dividirlo así:

Agente	Qué hace
Agente coordinador	Entiende la solicitud y reparte el trabajo
Agente funcional	Interpreta el proceso de negocio
Agente técnico	Evalúa BADIs, APIs, exits, extensiones
Agente Clean Core	Clasifica riesgo y compatibilidad
Agente auditor	Revisa inconsistencias o supuestos débiles
Agente redactor	Prepara la respuesta final para el cliente
La respuesta que tú ves al final puede parecer una sola, pero internamente fue construida por varios “especialistas”.

La Analogía Más Clara
Piensa en un proyecto real:

En un proyecto humano	En solución multiagente
Project Manager	Agente coordinador
Consultor funcional	Agente funcional
Arquitecto técnico	Agente técnico
QA / auditor	Agente revisor
Consultor que arma el correo	Agente redactor
No es que cada agente sea “inteligente independiente” como una persona. Más bien son instancias del modelo con instrucciones, herramientas y responsabilidades diferentes.

Qué Tiene Cada Agente
Cada agente puede tener:

Agente = modelo + prompt propio + herramientas propias + contexto propio + objetivo propio
Ejemplo:

Agente	Prompt	Herramientas
Investigador	“Busca evidencia confiable”	Web, documentos, base vectorial
Técnico	“Evalúa arquitectura y código”	Repositorio, APIs, logs
Auditor	“Detecta riesgos y errores”	Checklist, reglas, políticas
Redactor	“Escribe claro y ejecutivo”	Plantillas, tono corporativo
Por Qué Usar Multiagente
Tiene sentido cuando la tarea tiene varias dimensiones.

Por ejemplo:

Investigación + análisis + redacción.

Código + pruebas + documentación.

Legal + financiero + técnico.

Funcional SAP + ABAP + arquitectura + gestión de riesgos.

No siempre es mejor. Para tareas simples, un solo agente basta. Multiagente agrega complejidad, costo y coordinación.

Cómo Lo Puedes Explicar
Una frase buena sería:

Una solución multiagente es una arquitectura donde varios agentes especializados, cada uno con un rol, instrucciones y herramientas propias, colaboran bajo una coordinación para resolver una tarea compleja.

Y en versión corta:

Es como armar un equipo de especialistas de IA, en lugar de pedirle todo a un solo asistente.

Ejemplo En Tu Mundo SAP
Para Clean Core podrías imaginarlo así:

Agente Orquestador
  ├─ Agente Funcional: entiende el proceso
  ├─ Agente ABAP: revisa custom code
  ├─ Agente Extensibility: busca alternativas clean
  ├─ Agente Riesgos: clasifica impacto
  └─ Agente Redactor: genera informe ejecutivo
La magia no está en “tener muchos agentes”. La magia está en que cada uno tenga un rol claro y que haya una buena coordinación.


sera que en lugar de un unico agente es mejor uno multi, como para delimitar tareas y no "confundir" al agente?

Sí, esa intuición es buena, pero con un matiz importante:

Multiagente puede ayudar a delimitar responsabilidades, pero no siempre es mejor que un solo agente.

La decisión no debería ser “multiagente porque suena más avanzado”, sino: ¿la tarea realmente necesita roles separados?

Cuándo Conviene Un Solo Agente
Un solo agente suele ser mejor cuando la tarea tiene un flujo claro:

Redactar un correo.

Resumir un documento.

Analizar un requerimiento simple.

Consultar una base de conocimiento.

Clasificar un caso.

Generar una respuesta con una plantilla.

Ejemplo:

Agente SAP Clean Core
- Lee el requerimiento
- Clasifica el riesgo
- Sugiere alternativa
- Redacta conclusión
Si el trabajo cabe bien en una cadena de pasos, un solo agente con buenas instrucciones, contexto y herramientas puede ser más simple, barato y fácil de controlar.

Cuándo Conviene Multiagente
Multiagente empieza a tener sentido cuando hay especialidades diferentes o posibles conflictos de criterio.

Por ejemplo:

Agente funcional
  entiende el proceso de negocio

Agente técnico
  revisa código, APIs, BADIs, exits

Agente auditor
  cuestiona supuestos y valida riesgos

Agente redactor
  arma la respuesta ejecutiva
Ahí sí ayuda, porque cada agente tiene una “mirada” distinta.

La Idea Clave
No uses multiagente solo para que “no se confunda”. Para eso muchas veces basta con:

Un prompt más claro.

Mejor contexto.

Menos herramientas disponibles al mismo tiempo.

Un flujo por etapas.

Validaciones antes de responder.

Guardrails.

Muchas confusiones no se resuelven metiendo más agentes; a veces se multiplican.

Mi Recomendación Práctica
Yo lo pensaría por niveles:

Nivel	Arquitectura	Cuándo usar
1	Un agente simple	Tareas claras y repetibles
2	Un agente con herramientas	Necesita consultar datos o ejecutar acciones
3	Un agente con flujo por etapas	Necesita análisis ordenado
4	Multiagente	Necesita varios criterios especializados
5	Multiagente con auditor	Hay riesgo alto, compliance o decisiones sensibles
Para empezar, yo preferiría:

Un solo agente bien diseñado, con etapas internas claras.

Por ejemplo:

Agente Clean Core

Etapa 1: entender requerimiento
Etapa 2: identificar objeto técnico
Etapa 3: evaluar compatibilidad Clean Core
Etapa 4: buscar alternativa
Etapa 5: validar riesgos
Etapa 6: redactar recomendación
Eso ya reduce mucho la confusión sin meter complejidad multiagente.

Cuándo Sí Lo Separaría
Lo separaría si notas que el agente mezcla sombreros. Por ejemplo:

Está redactando bonito, pero no cuestiona técnicamente.

Está buscando solución técnica, pero pierde el contexto funcional.

Está siendo optimista y no detecta riesgos.

Está generando respuestas largas sin validar evidencia.

Necesitas una revisión independiente antes de entregar.

Ahí un agente auditor o revisor sí aporta mucho.

Frase Para Recordarlo
Esta me parece la más útil:

Primero diseña bien el flujo. Después decides si cada etapa necesita ser un agente separado.

O más corto:

Multiagente no es para hacer más inteligente la solución; es para organizar responsabilidades cuando la tarea lo justifica.


Podria ser de entrada que defina las funciones y genere un unico agente, y como resultado de las pruebas se vaya "despedazando" en agentes?

Sí, Alfredo. Esa es probablemente la forma más madura de diseñarlo.

Yo lo vería así:

Empiezas con un solo agente bien definido, observas dónde falla o se sobrecarga, y solo después separas funciones en agentes especializados.

Eso evita caer en “multiagente por moda” y te deja que la arquitectura salga de la evidencia.

Cómo Sería El Camino

Definir la función general del agente

Ejemplo:

“Agente para analizar requerimientos SAP y recomendar alternativas Clean Core.”

Definir sus capacidades internas

- Entender el requerimiento funcional
- Identificar objetos técnicos involucrados
- Consultar documentación o base de conocimiento
- Evaluar cumplimiento Clean Core
- Detectar riesgos
- Recomendar alternativa
- Redactar respuesta ejecutiva
Construirlo como un único agente

Con:

Prompt claro.

Herramientas limitadas.

Contexto bien organizado.

Flujo de pasos.

Criterios de salida.

Probarlo con casos reales

Ahí miras cosas como:

¿Confunde lo funcional con lo técnico?

¿Redacta bien pero analiza débil?

¿No detecta riesgos?

¿Usa mal las herramientas?

¿No sabe cuándo pedir más información?

¿Mezcla fuentes?

¿Responde con demasiada seguridad?

Separar solo lo que lo amerite

Por ejemplo, si notas que el análisis técnico necesita una lógica distinta, separas:

Agente funcional
Agente técnico
Agente auditor
Agente redactor
Pero no lo haces desde el día uno salvo que ya sepas que esos roles son realmente necesarios.

Una Buena Regla
Puedes usar esta regla:

Si una capacidad requiere instrucciones, herramientas, criterios de evaluación o responsabilidades muy diferentes, puede convertirse en agente separado.

Ejemplo:

Capacidad	¿Separarla?	Motivo
Redactar correo final	A veces	Si necesitas tono ejecutivo muy cuidado
Consultar documentos	No necesariamente	Puede ser una herramienta del agente
Auditar riesgos	Sí, muchas veces	Conviene una mirada crítica separada
Clasificar Clean Core	Depende	Si tiene reglas complejas, puede separarse
Ejecutar pruebas técnicas	Sí	Tiene herramientas y criterios propios
Resumir resultados	No necesariamente	Puede ser etapa final del mismo agente
Me Gusta Esta Secuencia
Para tu caso, yo usaría una evolución así:

Versión 1: Un agente
- Analiza requerimiento
- Consulta conocimiento
- Clasifica
- Recomienda
- Redacta

Versión 2: Un agente + auditor
- Agente principal propone
- Agente auditor revisa riesgos y consistencia

Versión 3: Multiagente real
- Funcional
- Técnico
- Clean Core
- Auditor
- Redactor
La versión 2 suele ser el mejor punto intermedio. No complicas demasiado, pero agregas una revisión independiente, que en temas SAP/Clean Core vale oro.

Frase Profesional Para Explicarlo
Podrías decirlo así:

La estrategia inicial será implementar un agente único con responsabilidades claramente definidas y un flujo controlado. A partir de las pruebas, métricas y análisis de errores, se identificarán las capacidades que requieran especialización. Solo aquellas funciones que presenten criterios, herramientas o riesgos diferenciados serán desacopladas en agentes especializados.

Y más sencillo:

Primero validamos el comportamiento con un agente integral; luego, según los errores y la complejidad observada, evolucionamos hacia una arquitectura multiagente.

Esa aproximación está muy bien pensada. Es diseño incremental, no arquitectura inflada.


Como se implementaria este ejemplo que me das? imaginando que tenemos un S4HANA Private Cloud; por otra parte me gustaria tener un modelo LLM local... asi puedo hacer pruebas protengiendo la privacidad de la data?

Sí, y tu intuición de modelo local para proteger datos tiene mucho sentido, especialmente en SAP. La arquitectura podría arrancar muy controlada: S/4HANA Private Cloud + capa de integración + base de conocimiento privada + LLM local + agente.

Lo imaginaría así:

Usuario
  ↓
Aplicación del agente
  ↓
Orquestador / backend
  ↓
LLM local
  ↓
Herramientas privadas
  ├─ Consulta documentos / ChromaDB
  ├─ Consulta APIs S/4HANA
  ├─ Consulta reportes ATC / logs
  └─ Genera análisis / recomendación
Arquitectura Base
Para un primer MVP, yo no arrancaría conectando el agente directo a todo SAP. Haría una arquitectura por capas:

Capa	Función
Interfaz	Chat o formulario donde haces la consulta
Backend del agente	FastAPI, Python, LangGraph, LlamaIndex o similar
LLM local	Modelo corriendo en tu servidor o portátil
RAG privado	ChromaDB/FAISS con documentos, notas, guías, FS, TS, ATC
Tools SAP	Funciones controladas para consultar S/4HANA
Guardrails	Validaciones, permisos, logs, aprobación humana
En S/4HANA Private Cloud, la integración puede hacerse usando servicios OData, APIs, SOAP, RFC o conectividad vía BTP/Cloud Connector según el escenario. SAP documenta escenarios de conexión con S/4HANA Private Cloud usando usuario técnico, Cloud Connector, destinations y activación de servicios OData para integración con BTP (SAP Help Portal).

Punto Importante
Yo separaría dos tipos de datos:

Tipo de dato	Dónde lo pondría
Documentos, FS, TS, guías, notas, políticas Clean Core	Base vectorial privada
Datos vivos de SAP, órdenes, documentos, maestros	Consulta por API/tool controlada
Código ABAP, ATC, SCI, findings	Repositorio o extracción controlada
Decisiones previas del proyecto	Memoria privada / base relacional
Es decir: no metería “todo SAP” en embeddings. Vectorizaría conocimiento documental y usaría tools para consultar datos transaccionales cuando haga falta.

Implementación MVP
Un primer flujo podría ser:

Pregunta:
“Evalúa este requerimiento contra Clean Core.”

1. El agente recibe el requerimiento.
2. Busca contexto en ChromaDB:
   - guías Clean Core
   - matriz WRICEF
   - criterios A/B/C/D
   - notas internas
3. Si necesita datos SAP, llama una tool:
   - get_object_atc_findings()
   - get_released_apis()
   - get_custom_object_metadata()
4. El LLM local analiza.
5. Genera:
   - clasificación
   - riesgos
   - alternativa recomendada
   - evidencia usada
Ejemplo De Tools
No dejaría que el LLM “entre a SAP” libremente. Le daría funciones específicas:

def get_atc_findings(object_name: str):
    """Consulta findings ATC para un objeto Z específico."""

def get_api_catalog(process_area: str):
    """Busca APIs liberadas para un área funcional."""

def get_wrICEF_detail(wricef_id: str):
    """Consulta la descripción funcional y técnica del WRICEF."""

def create_clean_core_assessment(requirement_text: str):
    """Genera evaluación estructurada de Clean Core."""
El agente no debería decidir credenciales, endpoints ni SQL. Solo invoca funciones con parámetros controlados.

LLM Local
Sí, puedes usar un modelo local para pruebas y privacidad. Algunas opciones razonables:

Opción	Uso típico
Ollama	Muy práctico para pruebas locales
LM Studio	Fácil para experimentar en escritorio
vLLM	Mejor para servidor y concurrencia
llama.cpp	Liviano y portable
LocalAI	API compatible estilo OpenAI
Modelos posibles:

Llama 3.x / Llama 4 si está disponible en tu entorno.

Mistral / Mixtral.

Qwen.

DeepSeek coder para código.

Modelos especializados para embeddings como BGE-M3 o E5.

Para documentos SAP y español/inglés, yo probaría algo tipo:

LLM local: Qwen / Llama / Mistral
Embeddings: BGE-M3
Vector DB: ChromaDB
Backend: FastAPI
Orquestación: LangGraph o LlamaIndex
Privacidad
Sí, esto ayuda a proteger la data, pero con una aclaración:

“LLM local” no significa automáticamente “seguro”; significa que los datos no salen hacia un proveedor externo, siempre que toda la arquitectura esté cerrada.

Tendrías que controlar:

Que el modelo corra on-premise o en red privada.

Que no use APIs externas.

Que logs no guarden datos sensibles innecesarios.

Que los embeddings también se generen localmente.

Que ChromaDB esté en infraestructura privada.

Que las tools SAP usen usuarios técnicos con mínimos permisos.

Que haya auditoría de quién preguntó, qué consultó y qué respondió.

Cómo Evolucionaría A Multiagente
Primero haría esto:

Versión 1:
Un agente Clean Core integral
Luego, si las pruebas muestran fallas, lo separaría:

Versión 2:
Agente Principal + Agente Auditor
Después:

Versión 3:
Orquestador
  ├─ Agente Funcional
  ├─ Agente Técnico SAP
  ├─ Agente Clean Core
  ├─ Agente Auditor
  └─ Agente Redactor
Pero mi recomendación práctica: empieza con un agente único + RAG + tools controladas + auditoría. Eso te da valor rápido y evidencia real para decidir qué separar.

La frase arquitectónica sería:

Implementaría inicialmente un agente privado ejecutado sobre un LLM local, conectado a una base vectorial interna y a herramientas controladas de consulta sobre S/4HANA Private Cloud. A partir de las pruebas, las funciones que requieran criterios, permisos o herramientas diferenciadas se desacoplarían progresivamente en agentes especializados.


dame ejemplos de preguntas que le haría a este agente? 

Pensó durante un par de segundos
Sí. Para este agente SAP/Clean Core sobre S/4HANA Private Cloud, las preguntas deberían estar orientadas a analizar, consultar, comparar, auditar y recomendar.

Te las agrupo por tipo de uso.

1. Preguntas para entender requerimientos
Estas son buenas para empezar cuando tienes una necesidad funcional o técnica:

“Analiza este requerimiento y dime si puede implementarse manteniendo principios Clean Core.”

“Con base en esta descripción funcional, identifica qué tipo de extensión SAP podría necesitarse: configuración, extensibilidad in-app, side-by-side, BADI, API o desarrollo clásico.”

“Resume este requerimiento en términos funcionales, técnicos, riesgos y supuestos.”

“Dime qué información falta para poder estimar este WRICEF.”

“Clasifica este requerimiento como bajo, medio o alto en complejidad técnica y justifica la clasificación.”

Ejemplo más concreto:

“El cliente necesita agregar validaciones adicionales al momento de contabilizar pagos automáticos. ¿Qué alternativas existen en S/4HANA Private Cloud y cuál sería la más alineada con Clean Core?”

2. Preguntas sobre Clean Core
Estas serían el corazón del agente:

“Evalúa si este desarrollo Z cumple con lineamientos Clean Core.”

“Clasifica este objeto según el nivel de compatibilidad Clean Core: A, B, C o D, y explica por qué.”

“¿Qué riesgos de upgrade tiene este objeto?”

“¿Este enhancement debería mantenerse, reemplazarse por una API liberada o rediseñarse como extensión side-by-side?”

“Dame una recomendación para modernizar este desarrollo sin modificar el core.”

“Identifica qué partes de este requerimiento podrían resolverse por configuración estándar.”

Ejemplo:

“Tengo un EXIT que modifica información durante la creación de documentos contables. ¿Qué riesgos tiene frente a Clean Core y qué alternativas debería revisar?”

3. Preguntas usando documentación interna o RAG
Aquí el agente consulta tus documentos vectorizados: FS, TS, guías, decisiones, matriz WRICEF, políticas, notas internas.

“Busca en la documentación del proyecto si ya existe una decisión sobre pagos por línea de captura.”

“Según nuestras guías internas, ¿qué criterios usamos para aprobar una excepción Clean Core?”

“Compara este requerimiento con otros WRICEF similares del proyecto.”

“Dame evidencia documental de por qué esta alternativa fue recomendada.”

“¿Qué objetos de la matriz WRICEF están relacionados con tesorería y tienen complejidad alta?”

“Genera un resumen ejecutivo de los desarrollos con mayor riesgo Clean Core.”

Ejemplo:

“Consulta la matriz WRICEF y dime cuáles objetos tienen tipo EXIT, complejidad alta y posible impacto en upgrade.”

4. Preguntas sobre objetos técnicos SAP
Aquí el agente usaría tools controladas para consultar información técnica.

“Consulta los findings ATC del objeto ZFI_PAYMENT_VALIDATION y resume los principales riesgos.”

“¿Este objeto usa APIs no liberadas?”

“¿Qué dependencias tiene este programa Z?”

“Identifica si este objeto tiene sentencias críticas para S/4HANA, como SELECT directo a tablas obsoletas.”

“Revisa los resultados ATC y dime cuáles findings son prioridad alta.”

“Agrupa los hallazgos ATC por tipo de riesgo: sintaxis, performance, uso de tablas, APIs, seguridad.”

Ejemplo:

“Para el objeto ZMM_CREATE_PO_EXT, consulta sus hallazgos ATC y dime si puede pasar a calidad o requiere remediación.”

5. Preguntas sobre alternativas técnicas
Estas son muy útiles para no quedarte solo en “esto está mal”, sino pedir una solución.

“Propón alternativas técnicas para este requerimiento ordenadas de más Clean Core a menos Clean Core.”

“¿Se puede resolver con extensibilidad in-app en lugar de ABAP clásico?”

“¿Qué API liberada podría usarse para este escenario?”

“¿Conviene una extensión side-by-side en BTP para este caso?”

“¿Qué implicaciones tendría usar una BADI clásica frente a una extensión en BTP?”

“Dame una arquitectura recomendada para este desarrollo.”

Ejemplo:

“El cliente quiere enriquecer datos de proveedor antes de la contabilización. ¿Qué opciones existen y cuál recomendarías?”

6. Preguntas para estimación
Muy útiles en preventa, explore o preparación de construcción:

“Estima el esfuerzo de este desarrollo considerando complejidad baja, media o alta.”

“Qué supuestos debo dejar explícitos para esta estimación?”

“Qué dependencias funcionales y técnicas podrían afectar el esfuerzo?”

“Genera una tabla con objeto, tipo, complejidad, riesgos, esfuerzo estimado y observaciones.”

“Revisa si esta estimación es consistente con desarrollos similares.”

Ejemplo:

“Tengo estos cuatro desarrollos: impresión de cheque, anulación de pagos rechazados, pago por línea de captura y contabilización multisociedad. Ayúdame a estimar complejidad, riesgos y supuestos.”

7. Preguntas para auditoría o revisión crítica
Aquí el agente funciona como revisor independiente.

“Audita esta recomendación técnica y dime qué supuestos débiles encuentras.”

“¿Qué riesgos no estoy considerando?”

“¿Qué preguntas debería hacerle al equipo funcional antes de aprobar este diseño?”

“Revisa esta especificación funcional y detecta inconsistencias.”

“Identifica posibles impactos en seguridad, performance, upgrade y operación.”

“Dime si esta solución parece sobreconstruida.”

Ejemplo:

“Revisa esta propuesta de usar un EXIT para modificar datos financieros. ¿Qué riesgos debo advertir antes de aprobarla?”

8. Preguntas para generación de entregables
El agente también puede ayudarte a producir documentos o comunicaciones:

“Genera una ficha técnica para este WRICEF.”

“Redacta una recomendación ejecutiva para el cliente explicando por qué esta opción no es Clean Core.”

“Crea una matriz de riesgos para estos desarrollos.”

“Genera el resumen para comité Clean Core.”

“Convierte este análisis técnico en un correo claro para el equipo funcional.”

“Prepara una sección de supuestos y exclusiones para la estimación.”

Ejemplo:

“Con base en este análisis, redacta un correo para el cliente explicando que recomendamos una extensión side-by-side en BTP y no una modificación directa en S/4HANA.”

9. Preguntas para operación del agente
Estas ayudan a controlar mejor el comportamiento del agente:

“No respondas todavía; primero dime qué información necesitas validar.”

“Responde solo con evidencia encontrada en la documentación cargada.”

“Dame la respuesta en formato tabla.”

“Separa tu respuesta en: hallazgos, riesgos, recomendación y próximos pasos.”

“Indica claramente qué es evidencia y qué es inferencia.”

“Marca con nivel alto, medio o bajo la confianza de tu recomendación.”

Estas preguntas son muy importantes porque reducen alucinaciones.

10. Ejemplo de pregunta completa bien formulada
Una buena pregunta para este agente sería así:

“Analiza el siguiente requerimiento desde una perspectiva Clean Core para S/4HANA Private Cloud. Indica: tipo de extensión recomendada, riesgos técnicos, impacto en upgrade, alternativas disponibles, información faltante y recomendación final. Usa únicamente la documentación interna y, si no hay evidencia suficiente, indícalo explícitamente.”

Ese prompt obliga al agente a:

No inventar.

Consultar evidencia.

Separar riesgos.

Recomendar.

Decir cuándo no sabe.

11. Ejemplo aplicado a tu mundo SAP
“Tenemos un desarrollo para procesar pagos mediante línea de captura y referencia. El desarrollo debe identificar el pago, validarlo, contabilizarlo y luego actualizar el campo asignación con información tomada de ACDOCA. Evalúa este requerimiento para S/4HANA Private Cloud bajo criterios Clean Core. Indica riesgos, alternativas, objetos SAP involucrados, preguntas para funcional y recomendación de arquitectura.”

Ese sería un caso perfecto para el agente.

La respuesta esperada debería venir algo así:

1. Entendimiento del requerimiento
2. Clasificación funcional
3. Tipo de extensión probable
4. Riesgos Clean Core
5. Alternativas técnicas
6. Información faltante
7. Recomendación
8. Nivel de confianza
Fórmula útil para preguntar
Puedes usar esta estructura:

Analiza [requerimiento / objeto / documento]
en el contexto de [S/4HANA Private Cloud / Clean Core / proyecto X].
Consulta [documentación interna / ATC / matriz WRICEF / APIs].
Devuelve [riesgos, alternativas, recomendación, evidencia].
Indica [supuestos, información faltante y nivel de confianza].
Ejemplo:

“Analiza el objeto ZFI_PAYMENTS_EXT en el contexto de S/4HANA Private Cloud y Clean Core. Consulta findings ATC, documentación funcional y matriz WRICEF. Devuelve riesgos, alternativas, recomendación, evidencia, supuestos e información faltante.”

Esa es una manera muy profesional de interactuar con un agente de este tipo.


Ahora, puedes hacer un mapa? 

Pensó durante 4s
Sí. Te dejo un mapa mental / conceptual de cómo imaginar esta arquitectura de agentes para SAP S/4HANA Private Cloud con LLM local.

                         SOLUCIÓN DE IA CON AGENTES
                                  PARA SAP
                                      │
                                      │
        ┌─────────────────────────────┴─────────────────────────────┐
        │                                                           │
   1. Usuario                                                  2. Interfaz
        │                                                           │
        │ Pregunta, requerimiento, archivo, caso SAP                 │ Chat / Web App /
        │                                                           │ Teams / Fiori /
        ▼                                                           │ Portal interno
 "Evalúa este WRICEF contra Clean Core"                             │
                                                                    ▼
                          ┌──────────────────────────┐
                          │  3. Orquestador / Backend │
                          │  FastAPI / LangGraph      │
                          │  LlamaIndex / Python      │
                          └─────────────┬────────────┘
                                        │
                                        │ Decide el flujo:
                                        │ - entender
                                        │ - buscar contexto
                                        │ - usar tools
                                        │ - validar
                                        │ - responder
                                        ▼
                          ┌──────────────────────────┐
                          │  4. Agente Principal      │
                          │  "Agente Clean Core SAP"  │
                          └─────────────┬────────────┘
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          │                             │                             │
          ▼                             ▼                             ▼
 ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
 │ 5. Prompt /      │           │ 6. LLM Local     │           │ 7. Memoria       │
 │ Instrucciones    │           │ Ollama / vLLM    │           │ Historial,       │
 │ Rol, reglas,     │           │ Llama / Qwen /   │           │ decisiones,      │
 │ formato salida   │           │ Mistral          │           │ preferencias     │
 └─────────────────┘           └─────────────────┘           └─────────────────┘
          │                             │                             │
          └─────────────────────────────┼─────────────────────────────┘
                                        │
                                        ▼
                           ┌────────────────────────┐
                           │ 8. Contexto Privado     │
                           │ RAG / ChromaDB          │
                           └────────────┬───────────┘
                                        │
                   ┌────────────────────┼────────────────────┐
                   │                    │                    │
                   ▼                    ▼                    ▼
        ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
        │ Documentos FS/TS │  │ Matriz WRICEF   │  │ Guías Clean Core │
        │ Diseños, actas   │  │ Objetos, tipos  │  │ políticas,       │
        │ decisiones       │  │ complejidad     │  │ criterios A/B/C/D│
        └─────────────────┘  └─────────────────┘  └─────────────────┘


                                        │
                                        ▼
                           ┌────────────────────────┐
                           │ 9. Herramientas / Tools │
                           └────────────┬───────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
              ▼                         ▼                         ▼
   ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
   │ Tool ATC             │   │ Tool SAP APIs        │   │ Tool Repositorio     │
   │ findings, riesgos,   │   │ OData, CDS,          │   │ código ABAP,         │
   │ simplification       │   │ released APIs        │   │ paquetes, objetos    │
   └─────────────────────┘   └─────────────────────┘   └─────────────────────┘
              │                         │                         │
              └─────────────────────────┼─────────────────────────┘
                                        │
                                        ▼
                              ┌────────────────────┐
                              │ 10. S/4HANA Private │
                              │ Cloud               │
                              └──────────┬─────────┘
                                         │
                         ┌───────────────┼───────────────┐
                         │               │               │
                         ▼               ▼               ▼
                 ┌────────────┐  ┌────────────┐  ┌────────────┐
                 │ OData APIs  │  │ CDS Views  │  │ RFC / BAPI  │
                 │ controladas │  │ autorizadas│  │ si aplica   │
                 └────────────┘  └────────────┘  └────────────┘


                                        │
                                        ▼
                           ┌────────────────────────┐
                           │ 11. Guardrails          │
                           │ Seguridad y control     │
                           └────────────┬───────────┘
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          │                             │                             │
          ▼                             ▼                             ▼
 ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
 │ No inventar      │           │ No ejecutar      │           │ Human-in-the-   │
 │ sin evidencia    │           │ cambios sin      │           │ loop            │
 │                  │           │ aprobación       │           │ aprobación      │
 └─────────────────┘           └─────────────────┘           └─────────────────┘


                                        │
                                        ▼
                           ┌────────────────────────┐
                           │ 12. Respuesta Final     │
                           └────────────┬───────────┘
                                        │
                  ┌─────────────────────┼─────────────────────┐
                  │                     │                     │
                  ▼                     ▼                     ▼
        ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
        │ Clasificación    │   │ Riesgos          │   │ Recomendación   │
        │ Clean Core       │   │ técnicos,        │   │ arquitectura,   │
        │ A/B/C/D          │   │ upgrade, datos   │   │ próximos pasos  │
        └─────────────────┘   └─────────────────┘   └─────────────────┘
Mapa más simple
La versión resumida sería:

Usuario
  ↓
Interfaz
  ↓
Orquestador
  ↓
Agente SAP Clean Core
  ↓
LLM local
  ↓
RAG privado + Tools SAP
  ↓
S/4HANA Private Cloud
  ↓
Guardrails
  ↓
Respuesta con evidencia
Y si evoluciona a multiagente
Primero sería así:

Usuario
  ↓
Agente Clean Core integral
  ↓
Respuesta
Después, si las pruebas muestran que se necesita separar responsabilidades:

Usuario
  ↓
Agente Orquestador
  ↓
┌───────────────────────────────┐
│ Agente Funcional              │
│ Entiende proceso de negocio    │
└───────────────────────────────┘
  ↓
┌───────────────────────────────┐
│ Agente Técnico SAP             │
│ Revisa ABAP, APIs, BADIs, ATC  │
└───────────────────────────────┘
  ↓
┌───────────────────────────────┐
│ Agente Clean Core              │
│ Clasifica riesgo y alternativas│
└───────────────────────────────┘
  ↓
┌───────────────────────────────┐
│ Agente Auditor                 │
│ Cuestiona supuestos y evidencia│
└───────────────────────────────┘
  ↓
┌───────────────────────────────┐
│ Agente Redactor                │
│ Genera respuesta ejecutiva     │
└───────────────────────────────┘
El mapa en una frase
La solución sería un agente SAP privado, ejecutado sobre un LLM local, alimentado con documentación interna mediante RAG, conectado a S/4HANA Private Cloud mediante herramientas controladas, protegido por guardrails y con posibilidad de evolucionar a multiagente según los errores observados en las pruebas.

Dónde entra cada concepto
Concepto	Dónde está en el mapa
Prompt	Instrucciones del agente
LLM local	Motor de razonamiento privado
RAG	Consulta de documentos internos
ChromaDB	Base vectorial privada
Tools	Funciones para consultar SAP, ATC, APIs, código
MCP	Capa estándar para exponer esas tools al agente
Orquestador	Decide el flujo de trabajo
Guardrails	Seguridad, permisos y límites
Human-in-the-loop	Aprobación humana antes de acciones sensibles
Multiagente	Separación por roles especializados
La forma más fácil de recordarlo:

LLM = cerebro
Prompt = instrucciones
RAG = conocimiento privado
Tools = manos
MCP = conector estándar
Orquestador = coordinador
Guardrails = controles
Agente = todo lo anterior trabajando junto
Multiagente = varios agentes especializados trabajando como equipo

lunes 23:14
Quiero hacer un proyecto sencillo, que luego por capas lo vayamos escalando, no tienen que ser con SAP, puedes darme varias opciones para escoger, la idea es poder ir publicandolos en mi github a medida que voy avanzando. Cuales opciones podemos manejar? quiero ir de lo mas sencillo a lo mas complejo para afianzar mis conocimientos. Ok?

Perfecto. Te propongo manejarlo como una ruta de aprendizaje por proyectos, donde cada repositorio pueda crecer por capas.

La idea sería que cada proyecto pase, poco a poco, por esta evolución:

Nivel 0: Script simple
Nivel 1: API con FastAPI
Nivel 2: Interfaz web básica
Nivel 3: LLM local
Nivel 4: RAG con documentos propios
Nivel 5: Tools / funciones externas
Nivel 6: Agente con flujo controlado
Nivel 7: MCP
Nivel 8: Multiagente
Nivel 9: Evaluación, métricas, logs y despliegue
Para usar LLM local, Ollama es una buena opción de entrada porque expone una API local por defecto en localhost:11434, lo que facilita integrarlo con Python/FastAPI. 
 Para RAG, LlamaIndex explica el patrón base como cargar datos, indexarlos y luego consultar el índice para recuperar contexto relevante antes de responder. 
 Para agentes más avanzados, LangGraph permite diseñar flujos de agente simples, multiagente o jerárquicos. 
 Y MCP puede entrar después como estándar para conectar agentes con herramientas, datos y sistemas externos. 

Opción 1: Asistente de documentos personales
Este sería mi favorito para empezar.

Idea: subir documentos PDF, TXT o Markdown y hacerles preguntas.

Ejemplos:

“Resume este documento.”

“Extrae los puntos importantes.”

“Dime qué riesgos tiene este contrato.”

“Responde solo usando el documento cargado.”

Capas del proyecto:

Nivel	Qué construirías
0	Script que lee un .txt y lo resume
1	API /summarize con FastAPI
2	Frontend simple para cargar archivo
3	LLM local con Ollama
4	RAG con ChromaDB
5	Tool para buscar dentro de documentos
6	Agente que decide si resumir, buscar o preguntar
7	MCP server para exponer “buscar_documento”
8	Agente auditor que verifica si la respuesta tiene evidencia
9	Métricas: tiempo, fuentes usadas, confianza
Nombre posible en GitHub:

private-doc-agent
Por qué sirve: aprendes LLM local, RAG, embeddings, vector DB, agentes, privacidad y evaluación.

Opción 2: Asistente de correos profesionales
Este conecta mucho con lo que ya haces.

Idea: una app que transforme notas sueltas en correos profesionales en español o inglés.

Ejemplos:

“Mejora este correo.”

“Hazlo más diplomático.”

“Traduce al inglés manteniendo tono corporativo.”

“Genera asunto, cuerpo y próximos pasos.”

Capas del proyecto:

Nivel	Qué construirías
0	Prompt fijo desde consola
1	API /rewrite-email
2	Interfaz web con campos: contexto, tono, idioma
3	Plantillas de tono: formal, ejecutivo, amable
4	LLM local
5	Memoria de preferencias de redacción
6	Agente redactor
7	Agente revisor que detecta ambigüedad o tono riesgoso
8	Multiagente: redactor + traductor + auditor
9	Integración Gmail opcional
Nombre posible:

email-polisher-ai
Por qué sirve: es útil, demostrable y fácil de mostrar en GitHub/LinkedIn.

Opción 3: Analizador de contratos simple
Este también conecta con cosas que ya has trabajado.

Idea: cargar un contrato y pedir riesgos, cláusulas ambiguas, obligaciones, fechas y puntos a negociar.

Ejemplos:

“Identifica cláusulas ambiguas.”

“Extrae obligaciones de cada parte.”

“Qué debería pedir aclarar antes de firmar?”

“Resume riesgos en lenguaje simple.”

Capas del proyecto:

Nivel	Qué construirías
0	Leer texto y extraer bullets
1	API /analyze-contract
2	Frontend para cargar contrato
3	RAG para responder con evidencia
4	Clasificador de riesgos: bajo, medio, alto
5	Tool para extraer fechas, montos y partes
6	Agente analista legal no-abogado
7	Agente auditor de ambigüedad
8	Multiagente: extractor + analista + redactor
9	Reporte PDF/Markdown
Nombre posible:

contract-risk-assistant
Nota importante: debe dejar claro que no reemplaza asesoría legal.

Opción 4: Agente de investigación académica
Muy útil para tus proyectos de maestría.

Idea: ayudar a analizar papers, resumir artículos, comparar enfoques y generar estado del arte.

Ejemplos:

“Resume este paper.”

“Extrae problema, metodología, resultados y limitaciones.”

“Compara estos tres artículos.”

“Genera una matriz de literatura.”

Capas del proyecto:

Nivel	Qué construirías
0	Resumidor de abstracts
1	API /paper-summary
2	Carga de PDFs
3	RAG sobre papers
4	Extracción estructurada
5	Comparador de papers
6	Agente investigador
7	Agente crítico que detecta limitaciones
8	Multiagente: investigador + metodólogo + redactor
9	Exportar matriz a CSV/Excel
Nombre posible:

research-paper-agent
Por qué sirve: te ayuda a construir portafolio académico y técnico.

Opción 5: Agente de tareas personales / productividad
Idea: un asistente que toma una nota desordenada y la convierte en tareas priorizadas.

Ejemplos:

“Organiza estas notas en tareas.”

“Extrae responsables, fechas y riesgos.”

“Crea un plan semanal.”

“Qué está bloqueado?”

Capas del proyecto:

Nivel	Qué construirías
0	Parser simple de notas
1	API /extract-tasks
2	Frontend tipo tablero
3	LLM local para estructurar tareas
4	Base SQLite para guardar tareas
5	Tool para crear, actualizar, cerrar tareas
6	Agente planificador
7	MCP server de tareas
8	Multiagente: planificador + priorizador + auditor
9	Integración calendario opcional
Nombre posible:

task-agent-lab
Por qué sirve: es perfecto para entender tools y memoria.

Opción 6: Analizador de gastos personales
Este es bueno si quieres combinar IA + datos + visualización.

Idea: cargar un CSV de gastos y preguntarle cosas en lenguaje natural.

Ejemplos:

“En qué gasté más este mes?”

“Detecta gastos inusuales.”

“Clasifica mis gastos.”

“Genera recomendaciones de ahorro.”

Capas del proyecto:

Nivel	Qué construirías
0	Leer CSV con pandas
1	Dashboard básico
2	API /analyze-expenses
3	LLM para explicar resultados
4	Tool para consultar datos
5	Agente financiero personal
6	Memoria de categorías
7	MCP server para consultar gastos
8	Multiagente: clasificador + analista + recomendador
9	Métricas y alertas
Nombre posible:

personal-finance-agent
Por qué sirve: aprendes datos estructurados + agente con tools.

Opción 7: Mini agente de código
Idea: una herramienta que revise un proyecto pequeño y explique estructura, errores y mejoras.

Ejemplos:

“Explícame este repositorio.”

“Detecta archivos importantes.”

“Sugiere mejoras al README.”

“Identifica funciones sin documentación.”

Capas del proyecto:

Nivel	Qué construirías
0	Script que lista archivos
1	Resume estructura del repo
2	API para analizar carpeta
3	LLM local para explicación
4	Tool para leer archivos específicos
5	Agente que decide qué archivos revisar
6	Agente revisor de README
7	Agente auditor de calidad
8	Multiagente: lector + analista + documentador
9	GitHub Actions opcional
Nombre posible:

repo-inspector-agent
Por qué sirve: te prepara para agentes tipo coding assistant.

Mi recomendación de ruta
Yo escogería esta secuencia:

Proyecto 1: email-polisher-ai
Porque es fácil, útil y rápido de publicar.

Aprendes:

prompts

API

frontend

LLM local

evaluación básica

Proyecto 2: private-doc-agent
Porque ahí ya entras fuerte en RAG.

Aprendes:

embeddings

ChromaDB

chunks

recuperación de contexto

respuestas con evidencia

Proyecto 3: task-agent-lab
Porque ahí entiendes tools y agente.

Aprendes:

funciones externas

memoria

acciones controladas

MCP

Proyecto 4: contract-risk-assistant
Porque combina RAG + agente + auditor.

Aprendes:

análisis por roles

evidencia

riesgos

multiagente

Proyecto 5: repo-inspector-agent
Porque ahí entras en agentes que leen archivos y ejecutan flujos.

Aprendes:

navegación de repositorios

tools más avanzadas

agentes técnicos

GitHub Actions

La mejor primera opción
Para empezar sin enredarte, yo escogería:

email-polisher-ai
Pero si quieres aprender directamente lo que hemos venido hablando de RAG + privacidad + agente, escogería:

private-doc-agent
Mi recomendación final sería esta:

1. email-polisher-ai
2. private-doc-agent
3. task-agent-lab
4. contract-risk-assistant
5. repo-inspector-agent
Estructura común para todos tus repositorios
Puedes usar siempre esta estructura:

project-name/
  app/
    main.py
    services/
    agents/
    tools/
    prompts/
  data/
    samples/
  notebooks/
  tests/
  docs/
  README.md
  requirements.txt
  .env.example
Y cada README puede mostrar:

# Objetivo
# Arquitectura
# Instalación
# Cómo ejecutar
# Ejemplos de uso
# Roadmap por capas
# Capturas
# Lecciones aprendidas
Para tu perfil, yo lo enfocaría como un portafolio de aprendizaje:

AI Agent Learning Path
├── 01-email-polisher-ai
├── 02-private-doc-agent
├── 03-task-agent-lab
├── 04-contract-risk-assistant
└── 05-repo-inspector-agent
Así se ve ordenado, progresivo y profesional en GitHub.

Mi voto: empecemos con private-doc-agent si quieres aprender bien agentes/RAG/MCP, o con email-polisher-ai si quieres un primer éxito rápido.


Vamos con el private-doc-agent 

Perfecto. El proyecto será:

private-doc-agent
Objetivo del proyecto
Construir un asistente privado para consultar documentos locales.

La idea final:

Usuario carga documentos
        ↓
El sistema los procesa
        ↓
Crea una base de conocimiento privada
        ↓
El agente responde preguntas usando evidencia del documento
        ↓
Todo corre local o controlado, sin exponer información sensible
Qué vamos a aprender
Con este proyecto vas a practicar, por capas:

Capa	Concepto
1	Python básico aplicado a documentos
2	FastAPI
3	Frontend simple
4	LLM local con Ollama
5	RAG
6	Embeddings
7	ChromaDB
8	Tools
9	Agente
10	MCP
11	Multiagente
12	Evaluación y métricas
Roadmap del proyecto
Fase 0 — Repositorio base
Objetivo: tener el proyecto creado y ordenado en GitHub.

Estructura inicial:

private-doc-agent/
  app/
    main.py
    config.py
    services/
      document_loader.py
      text_splitter.py
      simple_qa.py
    prompts/
      system_prompt.txt
  data/
    input/
    processed/
  tests/
  docs/
    roadmap.md
  README.md
  requirements.txt
  .env.example
  .gitignore
Primera meta:

Crear el repositorio y ejecutar una API básica con /health
Fase 1 — Versión sin IA
Objetivo: que el sistema lea documentos y haga búsquedas simples.

Ejemplo:

Pregunta:
"¿Dónde habla el documento de confidencialidad?"

Respuesta:
"Encontré coincidencias en las líneas 25, 48 y 103."
Aquí no hay LLM todavía.

Aprendes:

lectura de archivos

limpieza de texto

búsqueda por palabras clave

API básica

Endpoints:

GET  /health
POST /documents/upload
GET  /documents
POST /search
Fase 2 — Resumen con LLM local
Objetivo: conectar Ollama y pedir resúmenes.

Ejemplo:

"Resume este documento en 5 puntos."
Componentes nuevos:

app/services/llm_client.py
app/prompts/summarize_prompt.txt
Endpoints:

POST /summarize
Aquí todavía no hay RAG; solo mandas texto al modelo.

Fase 3 — RAG básico
Objetivo: dividir documentos en fragmentos, indexarlos y responder usando contexto recuperado.

Flujo:

Documento
  ↓
Chunks
  ↓
Embeddings
  ↓
ChromaDB
  ↓
Pregunta del usuario
  ↓
Buscar fragmentos relevantes
  ↓
LLM responde usando esos fragmentos
Endpoints:

POST /documents/index
POST /ask
Respuesta esperada:

{
  "answer": "El documento indica que...",
  "sources": [
    {
      "document": "contrato_demo.txt",
      "chunk": 3
    }
  ]
}
Fase 4 — Agente simple
Objetivo: que el sistema decida qué hacer según la intención del usuario.

Ejemplos:

Pregunta	Acción
“Resume el documento”	summarize
“Busca cláusulas de pago”	search
“Pregunta sobre terminación”	rag_qa
“Qué riesgos ves?”	risk_analysis
Aquí aparece el concepto de agente:

Agente = instrucciones + LLM + tools + flujo de decisión
Tools iniciales:

search_documents()
summarize_document()
answer_with_rag()
extract_risks()
Fase 5 — Agente auditor
Objetivo: agregar un segundo agente que revise la respuesta antes de entregarla.

Flujo:

Agente principal genera respuesta
        ↓
Agente auditor revisa:
- ¿hay evidencia?
- ¿inventó algo?
- ¿respondió fuera del documento?
- ¿faltan advertencias?
        ↓
Respuesta final corregida
Aquí ya tienes una mini solución multiagente:

Agente principal + agente auditor
Fase 6 — MCP
Objetivo: exponer las tools mediante MCP.

En vez de que el agente tenga funciones internas solamente, las herramientas se exponen como servicios reutilizables.

Ejemplo:

MCP Server
  ├─ search_documents
  ├─ get_document_metadata
  ├─ retrieve_chunks
  └─ analyze_risks
Esto te prepara para conectar después:

documentos locales

Google Drive

repositorios

APIs

sistemas internos

SAP, si algún día lo quieres llevar allá

Primera versión que vamos a construir
Yo arrancaría con algo pequeño y limpio:

Versión 0.1.0
Debe hacer esto:

1. Levantar API FastAPI.
2. Tener endpoint /health.
3. Leer archivos .txt desde data/input.
4. Listar documentos disponibles.
5. Buscar texto por palabra clave.
6. Devolver resultados simples.
Nada de LLM todavía.

Esto es importante porque te deja una base sólida.

Backlog inicial
Sprint 1 — Base del proyecto
Tareas:

TASK-001 Crear estructura del proyecto
TASK-002 Crear entorno virtual
TASK-003 Crear requirements.txt
TASK-004 Crear FastAPI app
TASK-005 Crear endpoint /health
TASK-006 Crear loader de documentos .txt
TASK-007 Crear endpoint /documents
TASK-008 Crear búsqueda simple por keyword
TASK-009 Crear endpoint /search
TASK-010 Crear README inicial
Sprint 2 — LLM local
TASK-011 Instalar Ollama
TASK-012 Crear cliente para Ollama
TASK-013 Crear prompt de resumen
TASK-014 Crear endpoint /summarize
TASK-015 Probar con documento demo
Sprint 3 — RAG
TASK-016 Crear splitter de texto
TASK-017 Crear embeddings locales
TASK-018 Crear índice ChromaDB
TASK-019 Crear endpoint /index
TASK-020 Crear endpoint /ask
TASK-021 Responder con fuentes
Stack recomendado
Para iniciar:

Python 3.11+
FastAPI
Uvicorn
Pydantic
python-dotenv
Luego agregamos:

Ollama
ChromaDB
sentence-transformers o embeddings locales vía Ollama
LangChain o LlamaIndex
Mi recomendación: al principio hacerlo sin LangChain ni LlamaIndex, para que entiendas la mecánica. Después sí metemos framework.

README inicial del proyecto
Podrías describirlo así:

# private-doc-agent

Private Doc Agent is a local-first AI assistant designed to analyze and answer questions over private documents.

The project starts with simple document loading and keyword search, then evolves into a local LLM-powered RAG assistant, and later into an agentic architecture with tools, MCP and multi-agent validation.

## Learning Goals

- Document ingestion
- FastAPI backend
- Local LLM integration
- Retrieval-Augmented Generation
- Vector databases
- Agent tools
- MCP
- Multi-agent validation

## Roadmap

- v0.1: Basic document loader and keyword search
- v0.2: Local LLM summarization
- v0.3: RAG with vector database
- v0.4: Tool-based agent
- v0.5: Auditor agent
- v0.6: MCP server
Primer commit sugerido
Nombre del commit:

chore: initialize private doc agent project
Contenido:

estructura de carpetas

README

requirements

.gitignore

endpoint /health

Siguiente paso
Empecemos por la versión 0.1.0.

La primera entrega debería dejarte esto funcionando:

uvicorn app.main:app --reload
Y luego:

GET http://localhost:8000/health
Respuesta:

{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.1.0"
}
Después agregamos:

GET /documents
POST /search
La forma correcta de avanzar sería:

Paso 1: Crear estructura del proyecto
Paso 2: Crear API mínima
Paso 3: Probar /health
Paso 4: Primer commit
Paso 5: Agregar lectura de documentos
Paso 6: Segundo commit
Paso 7: Agregar búsqueda simple
Paso 8: Tercer commit
Te recomiendo que el primer objetivo sea muy concreto:

private-doc-agent v0.1.0
API local para listar documentos .txt y buscar coincidencias por palabra clave.
Con eso ya tienes un repositorio publicable y una base real para crecer.


cree la carpeta local C:\Proyectos\private-doc-agent, voy a crear el proyecto en github, un cambio para hacerlo mas util, que lea archivo .txt o .md. OK? ==== este es el repositorio ajapontes/private-doc-agent.git

Perfecto, Alfredo. Sí: desde la primera versión hagámoslo más útil leyendo .txt y .md.

Tu proyecto queda:

Repositorio local:
C:\Proyectos\private-doc-agent

Repositorio remoto:
https://github.com/ajapontes/private-doc-agent.git
Versión 0.1.0 ajustada
Objetivo:

API local con FastAPI que:
1. Responde /health
2. Lista documentos .txt y .md desde data/input
3. Permite buscar texto por palabra clave
Estructura inicial recomendada
Dentro de:

C:\Proyectos\private-doc-agent
crea esta estructura:

private-doc-agent/
  app/
    __init__.py
    main.py
    config.py
    services/
      __init__.py
      document_loader.py
      simple_search.py
  data/
    input/
      demo.txt
      demo.md
    processed/
  docs/
    roadmap.md
  tests/
  README.md
  requirements.txt
  .env.example
  .gitignore
Comandos iniciales en Windows PowerShell
Ubícate en la carpeta:

cd C:\Proyectos\private-doc-agent
Crea entorno virtual:

py -3.11 -m venv .venv
Actívalo:

.\.venv\Scripts\Activate.ps1
Actualiza pip:

python -m pip install --upgrade pip
Crea requirements.txt con esto:

fastapi
uvicorn[standard]
pydantic
python-dotenv
Instala dependencias:

pip install -r requirements.txt
Código inicial
app/config.py
from pathlib import Path

APP_NAME = "private-doc-agent"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"

SUPPORTED_EXTENSIONS = {".txt", ".md"}
app/services/document_loader.py
from pathlib import Path
from app.config import INPUT_DIR, SUPPORTED_EXTENSIONS


def list_documents() -> list[dict]:
    """
    Lists supported documents from data/input.
    Currently supports .txt and .md files.
    """
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    documents = []

    for file_path in INPUT_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            documents.append(
                {
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "size_bytes": file_path.stat().st_size,
                    "path": str(file_path.relative_to(INPUT_DIR.parent.parent)),
                }
            )

    return documents


def read_document(filename: str) -> str:
    """
    Reads a supported document by filename from data/input.
    """
    file_path = INPUT_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {filename}")

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {file_path.suffix}")

    return file_path.read_text(encoding="utf-8")
app/services/simple_search.py
from app.services.document_loader import list_documents, read_document


def search_keyword(query: str) -> list[dict]:
    """
    Searches a keyword or phrase across all supported documents.
    Returns matching lines with line numbers.
    """
    if not query or not query.strip():
        return []

    query_normalized = query.strip().lower()
    results = []

    for document in list_documents():
        filename = document["filename"]
        content = read_document(filename)

        for line_number, line in enumerate(content.splitlines(), start=1):
            if query_normalized in line.lower():
                results.append(
                    {
                        "filename": filename,
                        "line_number": line_number,
                        "line": line.strip(),
                    }
                )

    return results
app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import APP_NAME, APP_VERSION
from app.services.document_loader import list_documents, read_document
from app.services.simple_search import search_keyword


app = FastAPI(
    title="Private Doc Agent",
    description="Local-first assistant for private document analysis.",
    version=APP_VERSION,
)


class SearchRequest(BaseModel):
    query: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/documents")
def get_documents():
    return {
        "documents": list_documents(),
        "count": len(list_documents()),
    }


@app.get("/documents/{filename}")
def get_document(filename: str):
    try:
        content = read_document(filename)
        return {
            "filename": filename,
            "content": content,
        }
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/search")
def search_documents(request: SearchRequest):
    results = search_keyword(request.query)

    return {
        "query": request.query,
        "matches": results,
        "count": len(results),
    }
Archivos de prueba
data/input/demo.txt
Private Doc Agent is a local-first assistant.

This project starts with basic document loading and keyword search.

Later, it will include local LLM integration, RAG, tools, MCP and multi-agent validation.
data/input/demo.md
# Private Doc Agent

This is a sample Markdown document.

## Goals

- Read private documents
- Search across .txt and .md files
- Add local LLM support
- Build a RAG pipeline
- Add agent tools
.gitignore
.venv/
__pycache__/
*.pyc
.env

data/processed/
chroma_db/
*.log

.DS_Store
.vscode/
.idea/
Nota: yo sí dejaría data/input/demo.txt y data/input/demo.md en GitHub porque son archivos de ejemplo. Más adelante, cuando uses documentos reales, no los subas.

README.md inicial
# private-doc-agent

Private Doc Agent is a local-first AI assistant designed to analyze and answer questions over private documents.

The project starts with simple document loading and keyword search over `.txt` and `.md` files. Later, it will evolve into a local LLM-powered RAG assistant with tools, MCP and multi-agent validation.

## Current Version

v0.1.0

## Features

- FastAPI backend
- Health check endpoint
- Local document listing
- Support for `.txt` and `.md` files
- Simple keyword search across documents

## Project Structure

```text
private-doc-agent/
  app/
    main.py
    config.py
    services/
      document_loader.py
      simple_search.py
  data/
    input/
    processed/
  docs/
  tests/
  README.md
  requirements.txt
Setup
python -m venv .venv
On Windows PowerShell:

.\.venv\Scripts\Activate.ps1
Install dependencies:

pip install -r requirements.txt
Run the API:

uvicorn app.main:app --reload
Endpoints
Health
GET /health
Expected response:

{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.1.0"
}
List documents
GET /documents
Read document
GET /documents/demo.txt
GET /documents/demo.md
Search
POST /search
Request body:

{
  "query": "RAG"
}
Roadmap
v0.1.0: Basic document loader and keyword search

v0.2.0: Local LLM summarization

v0.3.0: RAG with vector database

v0.4.0: Tool-based agent

v0.5.0: Auditor agent

v0.6.0: MCP server


Ojo: en el README anterior hay bloques de código anidados. Si VS Code se confunde, lo ajustamos después.

---

# `docs/roadmap.md`

```md
# Roadmap

## v0.1.0 - Basic Document Search

- Create FastAPI app
- Add health endpoint
- Read `.txt` and `.md` files from `data/input`
- List available documents
- Search keyword matches across documents

## v0.2.0 - Local LLM Summarization

- Connect to Ollama
- Add summarization endpoint
- Create prompt templates
- Summarize `.txt` and `.md` documents

## v0.3.0 - RAG

- Split documents into chunks
- Generate embeddings locally
- Store vectors in ChromaDB
- Ask questions using retrieved context
- Return sources

## v0.4.0 - Agent Tools

- Add tools for search, summarize and RAG QA
- Create a simple agent router
- Decide action based on user intent

## v0.5.0 - Auditor Agent

- Review answers for evidence and hallucination risk
- Add confidence level
- Add response validation

## v0.6.0 - MCP

- Expose document tools through MCP
- Allow external clients to call the tools
Ejecutar el proyecto
Desde PowerShell:

cd C:\Proyectos\private-doc-agent
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
Abre:

http://localhost:8000/docs
Prueba:

GET /health
GET /documents
GET /documents/demo.md
POST /search
Body para /search:

{
  "query": "RAG"
}
Conectar con GitHub
Si todavía no inicializaste Git:

git init
git branch -M main
git remote add origin https://github.com/ajapontes/private-doc-agent.git
Si ya existe remoto, valida con:

git remote -v
Agrega archivos:

git add .
Primer commit:

git commit -m "chore: initialize private doc agent"
Sube a GitHub:

git push -u origin main
Si GitHub te dice que el remoto ya tiene contenido, por ejemplo porque creaste README desde GitHub, ejecuta primero:

git pull origin main --rebase
Luego:

git push -u origin main
Criterio de aceptación de la v0.1.0
La versión queda lista cuando puedas demostrar esto:

1. /health responde status ok.
2. /documents lista demo.txt y demo.md.
3. /documents/demo.md devuelve el contenido del Markdown.
4. /search encuentra coincidencias en ambos tipos de archivo.
5. El repositorio queda publicado en GitHub.
El primer tag sugerido cuando funcione:

git tag v0.1.0
git push origin v0.1.0
Con eso dejamos una base limpia, útil y publicable.


martes 20:10
Como puedo resumir lo que hace hasta ahora mi proyecto?

Puedes resumirlo así, dependiendo de dónde lo quieras usar.

Versión corta para GitHub
Private Doc Agent is a local-first document assistant.  
In its current version, it provides a FastAPI backend that reads local `.txt` and `.md` files, lists available documents, retrieves their content, and performs simple keyword searches across them.
Versión en español
Private Doc Agent es un asistente local para documentos privados.  
En su versión actual, expone una API con FastAPI que permite leer archivos `.txt` y `.md` desde una carpeta local, listar los documentos disponibles, consultar su contenido y realizar búsquedas simples por palabra clave.
Versión para el README
## Current Functionality

Private Doc Agent currently provides a basic local document search API.

The application can:

- Run a FastAPI backend.
- Check service availability through `/health`.
- Read local `.txt` and `.md` files from `data/input`.
- List available documents through `/documents`.
- Retrieve the content of a specific document through `/documents/{filename}`.
- Search keywords or phrases across all supported documents through `/search`.

This first version does not use an LLM yet. It establishes the foundation for future layers such as local LLM integration, RAG, vector search, tools, agents, MCP and multi-agent validation.
Versión para LinkedIn o portafolio
I started building Private Doc Agent, a local-first assistant for private document analysis.

The first version implements a FastAPI backend capable of reading `.txt` and `.md` files from a local folder, listing available documents, retrieving document content, and performing simple keyword search across all supported files.

This initial layer intentionally avoids using an LLM. The goal is to build the project progressively: first document ingestion and search, then local LLM summarization, RAG, vector databases, agent tools, MCP and eventually multi-agent validation.
Versión más técnica
Private Doc Agent v0.1.0 is a FastAPI-based local document processing API.

Current capabilities include:
- Health check endpoint.
- Local document discovery.
- Support for `.txt` and `.md` files.
- Document content retrieval.
- Case-insensitive keyword search across supported documents.
- Basic project structure prepared for future LLM, RAG and agentic capabilities.

At this stage, the project focuses on deterministic document loading and search before introducing LLM-based reasoning.
Mi recomendación para tu README
Yo usaría esta:

## What it does now

Private Doc Agent is currently a local document search API built with FastAPI.

It can read `.txt` and `.md` files from a local input folder, list the available documents, retrieve the content of a selected document, and search for keywords or phrases across all supported files.

This version does not use an LLM yet. It provides the foundational layer for future capabilities such as local LLM summarization, Retrieval-Augmented Generation, vector databases, tools, MCP and multi-agent validation.
Y una frase muy buena para dejar clara la filosofía del proyecto sería:

The project is being built incrementally, from deterministic document search to a private AI-powered document agent.

Sigamos con la siguiente version del proyecto, indicame que estariamos agregando y y desde el punto de vista de IA a que llegamos?

Perfecto. La siguiente versión natural sería la v0.2.0, y el objetivo sería pasar de un buscador determinístico a un primer asistente con IA.

Hasta ahora tu proyecto hace esto:

v0.1.0
- Lee archivos .txt y .md
- Lista documentos locales
- Permite consultar el contenido
- Busca palabras clave
- No usa IA todavía
La siguiente versión debería agregar:

v0.2.0
- Conexión con un LLM local
- Resumen automático de documentos
- Endpoint para resumir archivos .txt y .md
- Prompt inicial controlado
- Separación entre lógica de documentos y lógica de IA
Qué estaríamos agregando
1. Cliente para LLM local
Agregaríamos un servicio nuevo:

app/services/llm_client.py
Este servicio se encargaría de comunicarse con un modelo local, por ejemplo usando Ollama.

La idea sería que tu proyecto pueda hacer algo como:

response = generate_text(prompt)
Sin que el resto de la aplicación tenga que saber cómo se conecta al modelo.

2. Prompt para resumen
Agregaríamos un prompt inicial:

app/prompts/summarize_prompt.txt
Ejemplo conceptual:

You are a private document assistant.
Summarize the following document clearly and concisely.
Do not invent information.
Use only the document content.
Esto es importante porque aquí ya empiezas a practicar un concepto clave de IA aplicada:

Prompt engineering controlado
No se trata solo de “preguntarle algo al modelo”, sino de darle instrucciones claras, límites y formato esperado.

3. Endpoint /summarize
Agregaríamos un endpoint nuevo:

POST /summarize
Ejemplo de request:

{
  "filename": "demo.md"
}
Ejemplo de response:

{
  "filename": "demo.md",
  "summary": "The document explains that Private Doc Agent is...",
  "model": "llama3.1",
  "version": "0.2.0"
}
4. Configuración del modelo
Agregaríamos variables de entorno:

.env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
Y un ejemplo seguro:

.env.example
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
Esto te prepara para buenas prácticas:

No quemar configuración técnica dentro del código
Qué NO agregaría todavía
Yo todavía no agregaría RAG en esta versión.

No metería todavía:

- ChromaDB
- embeddings
- vector database
- agentes
- MCP
- multiagente
¿Por qué?

Porque primero necesitamos validar que el proyecto ya puede:

leer documento → construir prompt → llamar LLM local → devolver respuesta
Ese es el primer salto real hacia IA.

Desde el punto de vista de IA, ¿a qué llegamos?
Con la v0.2.0 llegamos a esto:

Aplicación tradicional + LLM local
Todavía no es un agente.
Todavía no es RAG.
Todavía no tiene memoria.
Todavía no usa herramientas de forma autónoma.

Pero ya tiene una primera capacidad de IA:

Generación de lenguaje basada en el contenido de un documento local
Visualmente:

Documento local
    ↓
Lectura del contenido
    ↓
Prompt controlado
    ↓
LLM local
    ↓
Resumen generado
En términos de arquitectura de IA:

Concepto	Estado en v0.2.0
LLM	Sí
Prompt	Sí
Contexto	Sí, pero limitado al documento completo
RAG	No todavía
Embeddings	No todavía
Vector DB	No todavía
Tools	No todavía
Agente	No todavía
MCP	No todavía
Multiagente	No todavía
Qué aprende esta versión
Esta versión te ayuda a entender:

1. Diferencia entre búsqueda e IA
Antes:

/search busca coincidencias exactas o parciales.
Ahora:

/summarize interpreta el contenido y genera una síntesis.
2. Qué es contexto
El documento leído se convierte en contexto para el modelo.

Prompt + contenido del documento = entrada del LLM
3. Qué riesgo aparece
Aquí aparece el primer riesgo serio de IA:

El modelo puede inventar.
Por eso desde esta versión debemos incluir una instrucción como:

Use only the provided document content.
If the document does not contain enough information, say so.
4. Qué significa privacidad
Si usamos LLM local:

El documento no se envía a un proveedor externo.
Esto es clave para la filosofía del proyecto:

local-first private document assistant
Nueva estructura para v0.2.0
La estructura crecería así:

private-doc-agent/
  app/
    main.py
    config.py
    services/
      document_loader.py
      simple_search.py
      llm_client.py
      summarizer.py
    prompts/
      summarize_prompt.txt
  data/
    input/
      demo.txt
      demo.md
    processed/
  docs/
    roadmap.md
  tests/
  README.md
  requirements.txt
  .env.example
  .gitignore
Nuevos archivos:

app/services/llm_client.py
app/services/summarizer.py
app/prompts/summarize_prompt.txt
Archivos a modificar:

app/config.py
app/main.py
requirements.txt
.env.example
README.md
docs/roadmap.md
Endpoints al terminar v0.2.0
Tendríamos:

GET  /health
GET  /documents
GET  /documents/{filename}
POST /search
POST /summarize
Criterios de aceptación de v0.2.0
La versión estaría lista cuando puedas demostrar esto:

1. Ollama está corriendo localmente.
2. El proyecto puede llamar al modelo local.
3. /summarize recibe un filename.
4. El sistema lee un .txt o .md.
5. Construye un prompt con el contenido del documento.
6. El LLM devuelve un resumen.
7. La respuesta incluye filename, summary y model.
8. El README explica que esta versión agrega LLM local.
Commit sugerido
Cuando terminemos la implementación:

git add .
git commit -m "feat: add local LLM document summarization"
git push
Tag sugerido:

git tag v0.2.0
git push origin v0.2.0
Resumen ejecutivo de la siguiente versión
La v0.2.0 agrega la primera capa real de IA al proyecto: integración con un LLM local para resumir documentos .txt y .md. Desde el punto de vista de IA, el sistema pasa de ser una API de búsqueda documental a una aplicación local-first capaz de usar contexto privado y generación de lenguaje controlada. Esta versión prepara el camino para RAG, donde ya no enviaremos todo el documento al modelo, sino solo los fragmentos más relevantes.


martes 22:54
Vamos a ir paso a paso

Perfecto. Vamos paso a paso y sin mezclar muchas cosas.

Paso 1 — Preparar la rama para la v0.2.0
Antes de tocar código, crea una rama nueva para esta versión.

En PowerShell:

cd C:\Proyectos\private-doc-agent
Activa el entorno virtual:

.\.venv\Scripts\Activate.ps1
Verifica que estás en el repo correcto:

git status
Luego crea la rama:

git checkout -b feature/local-llm-summarization
Verifica la rama actual:

git branch
Deberías ver algo como:

* feature/local-llm-summarization
  main
Qué estamos haciendo con este paso
Estamos separando el trabajo de la nueva versión:

v0.2.0 = integración con LLM local para resumir documentos
Así, si algo falla, no dañamos la rama principal main.

Resultado esperado
Después de este paso debes tener:

Carpeta local: C:\Proyectos\private-doc-agent
Rama activa: feature/local-llm-summarization
Entorno virtual activo: .venv
No seguimos todavía con IA
En este paso no instalamos Ollama, no creamos prompts y no modificamos código. Solo dejamos el proyecto listo para trabajar ordenadamente.

Cuando tengas esto listo, el siguiente paso será:

Paso 2 — Agregar configuración para Ollama en .env.example y app/config.py

si

Perfecto. Sigamos con el Paso 2 — Agregar configuración para Ollama.

En esta etapa todavía no llamamos al modelo. Solo dejamos preparada la configuración para que el proyecto sepa:

Dónde está Ollama
Qué modelo vamos a usar
Paso 2.1 — Actualizar .env.example
En la raíz del proyecto:

C:\Proyectos\private-doc-agent
crea o actualiza el archivo:

.env.example
Con este contenido:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
Paso 2.2 — Crear tu archivo local .env
Ahora crea un archivo:

.env
Con el mismo contenido:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
Importante: .env no debe subirse a GitHub. Debe estar en .gitignore.

Verifica que tu .gitignore tenga esta línea:

.env
Paso 2.3 — Actualizar app/config.py
Abre:

app/config.py
Déjalo así:

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = "private-doc-agent"
APP_VERSION = "0.2.0"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"

SUPPORTED_EXTENSIONS = {".txt", ".md"}

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
Qué acabamos de agregar
Antes tu aplicación solo tenía configuración de archivos locales.

Ahora también tiene configuración para IA local:

OLLAMA_BASE_URL = dirección donde corre Ollama
OLLAMA_MODEL = modelo local que vamos a usar
Desde el punto de vista de IA, todavía no usamos el modelo, pero dejamos listo el punto de conexión.

Paso 2.4 — Validar que no rompimos nada
Ejecuta:

uvicorn app.main:app --reload
Luego abre:

http://localhost:8000/health
La respuesta esperada ahora debería ser:

{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.2.0"
}
Paso 2.5 — Revisar cambios en Git
En PowerShell:

git status
Deberías ver cambios en:

.env.example
app/config.py
Y posiblemente .gitignore, si lo modificaste.

No hagas commit todavía. Primero vamos a agregar el cliente de Ollama en el siguiente paso.

El siguiente paso será:

Paso 3 — Crear app/services/llm_client.py
Ahí sí construiremos la primera pieza que se comunicará con el LLM local.


Recuerda siempre mantener el codigo documentado, si es posible al inicio indicar para que es el objeto que se esta creando

Memoria actualizada
Perfecto, Alfredo. Lo dejamos como regla del proyecto:

Todo archivo, clase, función o servicio nuevo debe tener documentación clara.
Idealmente, al inicio del archivo debe indicarse su propósito.
Entonces, por ejemplo, el app/config.py que te pasé lo ajustaría así:

"""
Application configuration module.

This module centralizes the main configuration values used by the
Private Doc Agent application, including application metadata,
local document paths, supported file extensions, and local LLM settings.

The values related to Ollama are loaded from environment variables
defined in the .env file.
"""

from pathlib import Path
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()


# Application metadata
APP_NAME = "private-doc-agent"
APP_VERSION = "0.2.0"


# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"


# Supported document types for this version
SUPPORTED_EXTENSIONS = {".txt", ".md"}


# Local LLM configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
Y de aquí en adelante seguiremos este criterio para todos los archivos nuevos.

Por ejemplo, cuando creemos:

app/services/llm_client.py
lo haremos así:

"""
Local LLM client service.

This module provides a small abstraction layer to communicate with
a locally running Ollama server. The rest of the application should
use this service instead of calling Ollama directly.

This keeps the LLM integration isolated and easier to replace later
with another local model provider if needed.
"""
También documentaremos las funciones:

def generate_text(prompt: str) -> str:
    """
    Sends a prompt to the configured local LLM and returns the generated text.

    Args:
        prompt: The complete prompt that will be sent to the model.

    Returns:
        The text generated by the local LLM.
    """
Con esto el proyecto empieza a verse más profesional y más fácil de explicar en GitHub.


Sigamos

Perfecto. Sigamos con el Paso 3 — Crear el cliente local para Ollama.

En esta parte vamos a crear un servicio que se encargue de hablar con el LLM local. Todavía no creamos el endpoint /summarize; primero dejamos lista la capa de comunicación con el modelo.

Paso 3.1 — Actualizar requirements.txt
Abre tu archivo:

requirements.txt
Y asegúrate de tener esto:

fastapi
uvicorn[standard]
pydantic
python-dotenv
requests
Luego instala la nueva dependencia:

pip install -r requirements.txt
Estamos agregando requests para poder hacer llamadas HTTP al servidor local de Ollama.

Paso 3.2 — Crear app/services/llm_client.py
Crea este archivo:

app/services/llm_client.py
Con este contenido:

"""
Local LLM client service.

This module provides a small abstraction layer to communicate with
a locally running Ollama server.

The rest of the application should use this service instead of calling
Ollama directly. This keeps the LLM integration isolated, easier to test,
and easier to replace later with another local model provider if needed.
"""

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL


class LLMClientError(Exception):
    """
    Custom exception for errors related to the local LLM client.

    This exception is raised when the application cannot communicate with
    the local Ollama server or when the server returns an unexpected response.
    """

    pass


def generate_text(prompt: str) -> str:
    """
    Sends a prompt to the configured local LLM and returns the generated text.

    Args:
        prompt: The complete prompt that will be sent to the local model.

    Returns:
        The text generated by the configured local LLM.

    Raises:
        LLMClientError: If the prompt is empty, if Ollama is not reachable,
        or if the response from Ollama is invalid.
    """
    if not prompt or not prompt.strip():
        raise LLMClientError("Prompt cannot be empty.")

    endpoint = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        raise LLMClientError(f"Error communicating with local LLM: {error}") from error

    data = response.json()

    generated_text = data.get("response")

    if generated_text is None:
        raise LLMClientError("Invalid response from local LLM. Missing 'response' field.")

    return generated_text.strip()
Qué estamos creando aquí
Estamos creando esta capa:

FastAPI app
   ↓
llm_client.py
   ↓
Ollama local
   ↓
Modelo local
La ventaja de hacerlo así es que tu aplicación no queda amarrada directamente a Ollama en todos lados.

Más adelante, si quisieras cambiar de Ollama a otra opción local, solo tendrías que modificar este archivo.

Desde el punto de vista de IA, qué logramos
Con este paso ya tenemos la primera pieza técnica para usar IA:

Prompt → LLM local → respuesta generada
Todavía no estamos haciendo resumen de documentos, pero ya tenemos el “puente” hacia el modelo.

En arquitectura:

Concepto	Estado
LLM local	Preparado
Prompt	Se puede enviar
Contexto documental	Todavía no
Resumen	Todavía no
RAG	No
Agente	No
Paso 3.3 — Verificar que Ollama esté instalado y activo
En una terminal aparte, valida:

ollama --version
Luego valida qué modelos tienes:

ollama list
Si no tienes llama3.1, puedes usar el modelo que tengas instalado y actualizar tu .env.

Por ejemplo, si tienes llama3.2, en tu .env pondrías:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
Para descargar un modelo, puedes usar:

ollama pull llama3.1
O, si prefieres uno más liviano para pruebas:

ollama pull llama3.2
Paso 3.4 — Prueba rápida desde Python
Antes de conectar esto a la API, probemos que el cliente funciona.

Desde la raíz del proyecto:

cd C:\Proyectos\private-doc-agent
Con el entorno activo:

.\.venv\Scripts\Activate.ps1
Ejecuta:

python
Dentro de Python:

from app.services.llm_client import generate_text

response = generate_text("Explain in one short sentence what a local document assistant is.")
print(response)
Para salir de Python:

exit()
Resultado esperado
Deberías recibir una respuesta parecida a:

A local document assistant helps users analyze documents on their own machine.
No tiene que ser exactamente igual. Lo importante es que no aparezca error de conexión.

Posibles errores
Error: Connection refused
Significa que Ollama no está corriendo.

Prueba:

ollama serve
En otra terminal, vuelve a ejecutar la prueba.

Error: model not found
Significa que el modelo configurado en .env no existe localmente.

Valida:

ollama list
Y ajusta:

OLLAMA_MODEL=nombre-del-modelo-que-tengas
Error: ModuleNotFoundError: No module named 'requests'
Ejecuta:

pip install -r requirements.txt
Paso 3.5 — Revisar cambios
Ejecuta:

git status
Deberías ver cambios en:

requirements.txt
app/services/llm_client.py
Y posiblemente:

.env.example
app/config.py
Todavía no hagamos commit. El siguiente paso será crear el servicio de resumen:

Paso 4 — Crear app/services/summarizer.py y app/prompts/summarize_prompt.txt

Este es el valor del llm_client.py andes de tu nueva instruccion: debo reemplazarlo todo? """
Application configuration module.

This module centralizes the main configuration values used by the
Private Doc Agent application, including application metadata,
local document paths, supported file extensions, and local LLM settings.

The values related to Ollama are loaded from environment variables
defined in the .env file.
"""

from pathlib import Path
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()


# Application metadata
APP_NAME = "private-doc-agent"
APP_VERSION = "0.2.0"


# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"


# Supported document types for this version
SUPPORTED_EXTENSIONS = {".txt", ".md"}


# Local LLM configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

Sí, Alfredo: ese contenido no debería estar en llm_client.py. Ese código corresponde a:

app/config.py
Entonces:

No lo borres si está en app/config.py. Ahí está bien.

Si lo copiaste por error dentro de app/services/llm_client.py, entonces sí debes reemplazar todo el contenido de llm_client.py por el código del cliente LLM.

La estructura correcta es esta:

app/
  config.py              ← configuración general del proyecto
  services/
    llm_client.py        ← comunicación con Ollama
app/config.py
Este archivo debe quedar con el contenido que pegaste:

"""
Application configuration module.

This module centralizes the main configuration values used by the
Private Doc Agent application, including application metadata,
local document paths, supported file extensions, and local LLM settings.

The values related to Ollama are loaded from environment variables
defined in the .env file.
"""

from pathlib import Path
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()


# Application metadata
APP_NAME = "private-doc-agent"
APP_VERSION = "0.2.0"


# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"


# Supported document types for this version
SUPPORTED_EXTENSIONS = {".txt", ".md"}


# Local LLM configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
app/services/llm_client.py
Este archivo sí debes reemplazarlo completamente por esto:

"""
Local LLM client service.

This module provides a small abstraction layer to communicate with
a locally running Ollama server.

The rest of the application should use this service instead of calling
Ollama directly. This keeps the LLM integration isolated, easier to test,
and easier to replace later with another local model provider if needed.
"""

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL


class LLMClientError(Exception):
    """
    Custom exception for errors related to the local LLM client.

    This exception is raised when the application cannot communicate with
    the local Ollama server or when the server returns an unexpected response.
    """

    pass


def generate_text(prompt: str) -> str:
    """
    Sends a prompt to the configured local LLM and returns the generated text.

    Args:
        prompt: The complete prompt that will be sent to the local model.

    Returns:
        The text generated by the configured local LLM.

    Raises:
        LLMClientError: If the prompt is empty, if Ollama is not reachable,
        or if the response from Ollama is invalid.
    """
    if not prompt or not prompt.strip():
        raise LLMClientError("Prompt cannot be empty.")

    endpoint = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        raise LLMClientError(f"Error communicating with local LLM: {error}") from error

    data = response.json()

    generated_text = data.get("response")

    if generated_text is None:
        raise LLMClientError("Invalid response from local LLM. Missing 'response' field.")

    return generated_text.strip()
Resumen
Debe quedar así:

config.py
  - APP_NAME
  - APP_VERSION
  - INPUT_DIR
  - SUPPORTED_EXTENSIONS
  - OLLAMA_BASE_URL
  - OLLAMA_MODEL

llm_client.py
  - LLMClientError
  - generate_text()
  - llamada HTTP a Ollama
La confusión fue porque el contenido que me muestras tiene este encabezado:

"""
Application configuration module.
"""
Eso confirma que es configuración, no cliente LLM.

Después de corregirlo, ejecuta:

python
Y prueba:

from app.services.llm_client import generate_text

response = generate_text("Explain in one short sentence what a local document assistant is.")
print(response)
Si eso responde, ya tenemos conectada la primera pieza de IA local.


(.venv) (base) PS C:\Proyectos\private-doc-agent> python
Python 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
Ctrl click to launch VS Code Native REPL
>>> from app.services.llm_client import generate_text
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: cannot import name 'generate_text' from 'app.services.llm_client' (C:\Proyectos\private-doc-agent\app\services\llm_client.py)
>>> 
>>> response = generate_text("Explain in one short sentence what a local document assistant is.")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'generate_text' is not defined
>>> print(response)

Ese error indica que Python sí encontró el archivo:

C:\Proyectos\private-doc-agent\app\services\llm_client.py
pero dentro de ese archivo no encontró una función llamada generate_text.

Lo más probable es una de estas tres cosas:

1. El archivo llm_client.py no fue reemplazado completamente.
2. El archivo fue editado pero no guardado en VS Code.
3. La función existe, pero quedó mal escrita, indentada o con otro nombre.
Paso 1 — Sal de Python
En la consola donde estás escribe:

exit()
o presiona:

Ctrl + Z
Enter
Paso 2 — Abre este archivo exacto
Abre en VS Code:

C:\Proyectos\private-doc-agent\app\services\llm_client.py
Y reemplaza todo su contenido por este:

"""
Local LLM client service.

This module provides a small abstraction layer to communicate with
a locally running Ollama server.

The rest of the application should use this service instead of calling
Ollama directly. This keeps the LLM integration isolated, easier to test,
and easier to replace later with another local model provider if needed.
"""

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL


class LLMClientError(Exception):
    """
    Custom exception for errors related to the local LLM client.

    This exception is raised when the application cannot communicate with
    the local Ollama server or when the server returns an unexpected response.
    """

    pass


def generate_text(prompt: str) -> str:
    """
    Sends a prompt to the configured local LLM and returns the generated text.

    Args:
        prompt: The complete prompt that will be sent to the local model.

    Returns:
        The text generated by the configured local LLM.

    Raises:
        LLMClientError: If the prompt is empty, if Ollama is not reachable,
        or if the response from Ollama is invalid.
    """
    if not prompt or not prompt.strip():
        raise LLMClientError("Prompt cannot be empty.")

    endpoint = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        raise LLMClientError(f"Error communicating with local LLM: {error}") from error

    data = response.json()

    generated_text = data.get("response")

    if generated_text is None:
        raise LLMClientError("Invalid response from local LLM. Missing 'response' field.")

    return generated_text.strip()
Guarda el archivo:

Ctrl + S
Paso 3 — Verifica desde PowerShell que la función existe
Desde PowerShell, ejecuta esto:

Get-Content .\app\services\llm_client.py
Confirma visualmente que dentro aparece esta línea:

def generate_text(prompt: str) -> str:
También puedes buscarla así:

Select-String -Path .\app\services\llm_client.py -Pattern "generate_text"
Deberías ver algo como:

def generate_text(prompt: str) -> str:
Paso 4 — Prueba el import sin entrar al modo interactivo
En lugar de entrar con python, prueba directamente así:

python -c "from app.services.llm_client import generate_text; print(generate_text)"
Resultado esperado:

<function generate_text at 0x...>
Si eso funciona, el import ya quedó bien.

Paso 5 — Prueba el llamado al modelo
Ahora sí:

python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
Si todavía falla
Ejecuta este comando:

python -c "import app.services.llm_client as c; print(dir(c))"
Ese comando nos muestra qué objetos está viendo Python dentro de llm_client.py.

En la salida debería aparecer:

generate_text
LLMClientError
Si generate_text no aparece, entonces el archivo aún no quedó guardado con el contenido correcto.



(.venv) (base) PS C:\Proyectos\private-doc-agent> Get-Content .\app\services\llm_client.py
"""
Local LLM client service.

This module provides a small abstraction layer to communicate with
a locally running Ollama server.

The rest of the application should use this service instead of calling
Ollama directly. This keeps the LLM integration isolated, easier to test,
and easier to replace later with another local model provider if needed.
"""

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL


class LLMClientError(Exception):
    """
    Custom exception for errors related to the local LLM client.

    This exception is raised when the application cannot communicate with
    the local Ollama server or when the server returns an unexpected response.
    """

    pass


def generate_text(prompt: str) -> str:
    """
    Sends a prompt to the configured local LLM and returns the generated text.

    Args:
        prompt: The complete prompt that will be sent to the local model.

    Returns:
        The text generated by the configured local LLM.

    Raises:
        LLMClientError: If the prompt is empty, if Ollama is not reachable,
        or if the response from Ollama is invalid.
    """
    if not prompt or not prompt.strip():
        raise LLMClientError("Prompt cannot be empty.")

    endpoint = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        raise LLMClientError(f"Error communicating with local LLM: {error}") from error

    data = response.json()

    generated_text = data.get("response")

    if generated_text is None:
        raise LLMClientError("Invalid response from local LLM. Missing 'response' field.")

    return generated_text.strip()
(.venv) (base) PS C:\Proyectos\private-doc-agent> 

Ahora sí, el archivo se ve correcto. Ya aparece:

def generate_text(prompt: str) -> str:
El error anterior probablemente ocurrió porque estabas dentro de una sesión de Python abierta antes de guardar o corregir el archivo.

Haz la prueba limpia desde PowerShell, sin entrar a python interactivo:

python -c "from app.services.llm_client import generate_text; print(generate_text)"
Resultado esperado:

<function generate_text at 0x...>
Si eso funciona, prueba ya la llamada al modelo:

python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
Si aparece error de conexión
Puede salir algo como:

Error communicating with local LLM
Connection refused
Eso significa que Ollama no está corriendo. En otra terminal ejecuta:

ollama serve
Y vuelve a probar.

Si aparece error de modelo
Puede salir algo como:

model not found
Valida qué modelos tienes instalados:

ollama list
Luego ajusta tu .env:

OLLAMA_MODEL=nombre-del-modelo-que-tengas
Por ejemplo:

OLLAMA_MODEL=llama3.2
Después vuelve a probar el comando.

Si quieres validar qué modelo está leyendo tu app
Ejecuta:

python -c "from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL; print(OLLAMA_BASE_URL); print(OLLAMA_MODEL)"
Debería mostrar algo como:

http://localhost:11434
llama3.1
Cuando esa prueba devuelva una frase del modelo, podemos pasar al Paso 4: crear el servicio de resumen summarizer.py.


<function generate_text at 0x0000026EED0BA3E0>
(.venv) (base) PS C:\Proyectos\private-doc-agent> python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
Traceback (most recent call last):
  File "C:\Proyectos\private-doc-agent\app\services\llm_client.py", line 55, in generate_text
    response.raise_for_status()
  File "C:\Proyectos\private-doc-agent\.venv\Lib\site-packages\requests\models.py", line 1167, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: http://localhost:11434/api/generate

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "C:\Proyectos\private-doc-agent\app\services\llm_client.py", line 57, in generate_text
    raise LLMClientError(f"Error communicating with local LLM: {error}") from error
app.services.llm_client.LLMClientError: Error communicating with local LLM: 404 Client Error: Not Found for url: http://localhost:11434/api/generate
(.venv) (base) PS C:\Proyectos\private-doc-agent> 

Bien, Alfredo. El avance es bueno: el import ya funciona.

Esto confirma que llm_client.py está bien creado:

<function generate_text at 0x0000026EED0BA3E0>
El nuevo error ya no es de Python. Ahora es de conexión con el servicio local:

404 Client Error: Not Found for url: http://localhost:11434/api/generate
Eso significa:

Tu aplicación sí está llegando a http://localhost:11434,
pero en esa dirección no encuentra el endpoint /api/generate.
Las causas más probables son:

1. Ollama no está corriendo realmente en ese puerto.
2. Otro servicio está usando el puerto 11434.
3. La variable OLLAMA_BASE_URL apunta a una dirección incorrecta.
4. Tienes otro servidor compatible con OpenAI, pero no con la API nativa de Ollama.
Paso 1 — Validar qué responde el puerto 11434
Ejecuta en PowerShell:

curl http://localhost:11434
Si es Ollama, normalmente deberías ver algo parecido a:

Ollama is running
Luego prueba:

curl http://localhost:11434/api/tags
Ese endpoint debería devolver la lista de modelos instalados.

Paso 2 — Validar modelos instalados
Ejecuta:

ollama list
Confirma si tienes un modelo como:

llama3.1
llama3.2
mistral
qwen
Si no tienes ninguno, instala uno:

ollama pull llama3.2
Luego ajusta tu .env:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
Paso 3 — Probar Ollama directo sin Python
Ejecuta este comando en PowerShell:

curl http://localhost:11434/api/generate `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{ "model": "llama3.2", "prompt": "Say hello in one sentence.", "stream": false }'
Si tu modelo no es llama3.2, cambia el nombre por el que aparezca en:

ollama list
Paso 4 — Validar qué configuración lee Python
Ejecuta:

python -c "from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL; print(OLLAMA_BASE_URL); print(OLLAMA_MODEL)"
Debería salir algo como:

http://localhost:11434
llama3.2
Si sale otro valor, revisamos tu .env.

Paso 5 — Mejoremos el manejo de errores
El código está funcionando, pero podemos hacerlo más útil para diagnosticar errores. Reemplaza esta parte en llm_client.py:

    try:
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        raise LLMClientError(f"Error communicating with local LLM: {error}") from error
por esta versión más documentada y clara:

    try:
        response = requests.post(endpoint, json=payload, timeout=120)

        if response.status_code == 404:
            raise LLMClientError(
                f"Ollama endpoint not found: {endpoint}. "
                "Verify that Ollama is running and that OLLAMA_BASE_URL points to the correct server."
            )

        response.raise_for_status()

    except requests.exceptions.RequestException as error:
        raise LLMClientError(f"Error communicating with local LLM: {error}") from error
Con esto, si vuelve a pasar, el error será más entendible.

Lo importante
Ya superaste esta parte:

Python → importa generate_text correctamente
Ahora estamos validando esta otra:

generate_text → Ollama local → modelo local
Ejecuta primero estos tres comandos y dime qué sale:

curl http://localhost:11434
curl http://localhost:11434/api/tags
ollama list


(.venv) (base) PS C:\Proyectos\private-doc-agent> curl http://localhost:11434

Advertencia de seguridad: riesgo de ejecución de script
Invoke-WebRequest analiza el contenido de la página web. El código de script de la página web se puede ejecutar 
cuando se analiza la página.
      ACCIÓN RECOMENDADA:
      Usa el modificador -UseBasicParsing para evitar la ejecución de código de script.

      ¿Quieres continuar?
    
[S] Sí  [O] Sí a todo  [N] No  [T] No a todo  [U] Suspender  [?] Ayuda (el valor predeterminado es "N"): S


StatusCode        : 200
StatusDescription : OK
Content           : Ollama is running
RawContent        : HTTP/1.1 200 OK
                    Content-Length: 17
                    Content-Type: text/plain; charset=utf-8
                    Date: Wed, 15 Jul 2026 04:32:21 GMT
                    
                    Ollama is running
Forms             : {}
Headers           : {[Content-Length, 17], [Content-Type, text/plain; charset=utf-8], [Date, Wed, 15 Jul 2026 
                    04:32:21 GMT]}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : mshtml.HTMLDocumentClass
RawContentLength  : 17                                                                                             
                                                                                                                   
                                                                                                                   
                                                                                                                   
(.venv) (base) PS C:\Proyectos\private-doc-agent> curl http://localhost:11434/api/tags

Advertencia de seguridad: riesgo de ejecución de script
Invoke-WebRequest analiza el contenido de la página web. El código de script de la página web se puede ejecutar 
cuando se analiza la página.
      ACCIÓN RECOMENDADA:
      Usa el modificador -UseBasicParsing para evitar la ejecución de código de script.

      ¿Quieres continuar?
    
[S] Sí  [O] Sí a todo  [N] No  [T] No a todo  [U] Suspender  [?] Ayuda (el valor predeterminado es "N"): A
[S] Sí  [O] Sí a todo  [N] No  [T] No a todo  [U] Suspender  [?] Ayuda (el valor predeterminado es "N"): S


StatusCode        : 200
StatusDescription : OK
Content           : {"models":[{"name":"qwen3.5:4b","model":"qwen3.5:4b","modified_at":"2026-03-24T23:17:32.341820
                    1-05:00","size":3389983735,"digest":"2a654d98e6fba55d452b7043684e9b57a947e393bbffa62485a7aac05
                    ee4eefd","de...
RawContent        : HTTP/1.1 200 OK
                    Content-Length: 1884
                    Content-Type: application/json; charset=utf-8
                    Date: Wed, 15 Jul 2026 04:33:05 GMT
                    
                    {"models":[{"name":"qwen3.5:4b","model":"qwen3.5:4b","modified_at":"2026-03...
Forms             : {}
Headers           : {[Content-Length, 1884], [Content-Type, application/json; charset=utf-8], [Date, Wed, 15 Jul 
                    2026 04:33:05 GMT]}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : mshtml.HTMLDocumentClass
RawContentLength  : 1884



(.venv) (base) PS C:\Proyectos\private-doc-agent> ollama list
NAME                              ID              SIZE      MODIFIED     
qwen3.5:4b                        2a654d98e6fb    3.4 GB    3 months ago    
qwen3.5:2b                        324d162be6ca    2.7 GB    3 months ago    
embeddinggemma:latest             85462619ee72    621 MB    3 months ago    
nomic-embed-text-v2-moe:latest    ff9c2f10ef5e    957 MB    3 months ago    
(.venv) (base) PS C:\Proyectos\private-doc-agent> 

Perfecto, Alfredo. La buena noticia es que Ollama sí está corriendo correctamente.

Ya validaste esto:

http://localhost:11434 → Ollama is running
/api/tags → responde modelos instalados
El problema no era el endpoint como tal, sino muy probablemente el modelo configurado.

Tu .env seguramente tiene esto:

OLLAMA_MODEL=llama3.1
Pero en tu máquina no tienes llama3.1. Tus modelos disponibles son:

qwen3.5:4b
qwen3.5:2b
embeddinggemma:latest
nomic-embed-text-v2-moe:latest
Para generación de texto debemos usar uno de estos:

qwen3.5:4b
qwen3.5:2b
Los otros dos son modelos de embeddings, más útiles para RAG después.

Paso 1 — Ajusta tu .env
Abre:

C:\Proyectos\private-doc-agent\.env
Y cámbialo a:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
También actualiza .env.example para que el repo quede consistente:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
Paso 2 — Valida que Python lea el modelo correcto
Ejecuta:

python -c "from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL; print(OLLAMA_BASE_URL); print(OLLAMA_MODEL)"
Resultado esperado:

http://localhost:11434
qwen3.5:4b
Si todavía aparece llama3.1, revisamos ubicación del .env o si quedó guardado.

Paso 3 — Prueba directa desde Python
Ejecuta:

python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
Ahora debería responder algo parecido a:

A local document assistant helps users read, search, and understand private documents on their own computer.
Nota sobre PowerShell y curl
En PowerShell, curl realmente suele comportarse como alias de Invoke-WebRequest, por eso te mostró la advertencia.

Para evitar esa pregunta, puedes usar:

Invoke-WebRequest -UseBasicParsing http://localhost:11434
O más limpio para APIs JSON:

Invoke-RestMethod http://localhost:11434/api/tags
También puedes usar el ejecutable real:

curl.exe http://localhost:11434/api/tags
Desde el punto de vista de IA, qué logramos ahora
Ya tenemos casi completa esta capa:

Aplicación Python
   ↓
Cliente LLM documentado
   ↓
Ollama local
   ↓
Modelo generativo local: qwen3.5:4b
Es decir, ya estamos en:

Prompt → LLM local → respuesta generada
Todavía no estamos usando documentos, pero ya dejamos operativo el motor de IA local.

Cuando esa prueba funcione, seguimos con:

Paso 4 — Crear el servicio de resumen de documentos
Ahí conectaremos:

document_loader.py → summarizer.py → llm_client.py → Ollama

(.venv) (base) PS C:\Proyectos\private-doc-agent> python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
An artificial intelligence tool that processes and organizes your files entirely on your local device rather than in the cloud for privacy.
(.venv) (base) PS C:\Proyectos\private-doc-agent> 


Excelente. Ya tenemos funcionando la primera integración real con IA local.

Lo que acabas de validar es esto:

Prompt desde Python
   ↓
llm_client.py
   ↓
Ollama local
   ↓
qwen3.5:4b
   ↓
Respuesta generada
La respuesta fue correcta:

An artificial intelligence tool that processes and organizes your files entirely on your local device rather than in the cloud for privacy.
Qué significa este hito
Hasta ahora el proyecto ya tiene:

Capa	Estado
API FastAPI	Lista
Lectura .txt y .md	Lista
Búsqueda simple	Lista
Configuración .env	Lista
Cliente LLM local	Listo
Comunicación con Ollama	Lista
Modelo generativo local	Funcionando
Resumen de documentos	Siguiente paso
Desde el punto de vista de IA, ya pasaste de una aplicación tradicional a una aplicación con LLM local integrado.

Paso 4 — Crear el servicio de resumen
Ahora vamos a conectar documentos con IA:

document_loader.py
   ↓
summarizer.py
   ↓
llm_client.py
   ↓
Ollama
Paso 4.1 — Crear carpeta de prompts
Verifica que exista esta carpeta:

app/prompts/
Si no existe, créala.

Dentro crea este archivo:

app/prompts/summarize_prompt.txt
Con este contenido:

You are a private document assistant.

Your task is to summarize the provided document clearly and concisely.

Rules:
- Use only the information contained in the document.
- Do not invent facts.
- If the document does not contain enough information, say so.
- Keep the summary clear and useful.
- Return the answer in English.

Document content:
{document_content}
Por ahora lo dejamos en inglés porque el prompt, la respuesta del modelo y el README técnico quedan consistentes. Más adelante podemos agregar parámetro de idioma.

Paso 4.2 — Crear app/services/summarizer.py
Crea este archivo:

app/services/summarizer.py
Con este contenido:

"""
Document summarization service.

This module provides the logic required to summarize supported local
documents using the configured local LLM.

It connects three parts of the application:
1. The document loader, which reads local .txt and .md files.
2. The prompt template, which defines how the model should summarize.
3. The local LLM client, which sends the prompt to Ollama.
"""

from pathlib import Path

from app.config import BASE_DIR
from app.services.document_loader import read_document
from app.services.llm_client import generate_text


PROMPT_PATH = BASE_DIR / "app" / "prompts" / "summarize_prompt.txt"


class SummarizerError(Exception):
    """
    Custom exception for errors related to document summarization.

    This exception is raised when the prompt template cannot be found,
    when a document cannot be read, or when the local LLM cannot generate
    a valid summary.
    """

    pass


def load_summary_prompt_template() -> str:
    """
    Loads the summary prompt template from the prompts folder.

    Returns:
        The summary prompt template as a string.

    Raises:
        SummarizerError: If the prompt template file does not exist.
    """
    if not PROMPT_PATH.exists():
        raise SummarizerError(f"Summary prompt template not found: {PROMPT_PATH}")

    return PROMPT_PATH.read_text(encoding="utf-8")


def build_summary_prompt(document_content: str) -> str:
    """
    Builds the final prompt used to summarize a document.

    Args:
        document_content: The full content of the document to summarize.

    Returns:
        A complete prompt with the document content injected into the template.

    Raises:
        SummarizerError: If the document content is empty.
    """
    if not document_content or not document_content.strip():
        raise SummarizerError("Document content cannot be empty.")

    template = load_summary_prompt_template()

    return template.replace("{document_content}", document_content)


def summarize_document(filename: str) -> str:
    """
    Summarizes a supported local document using the configured local LLM.

    Args:
        filename: The name of the document located in the data/input folder.

    Returns:
        The summary generated by the local LLM.

    Raises:
        SummarizerError: If the document cannot be summarized.
    """
    try:
        document_content = read_document(filename)
        prompt = build_summary_prompt(document_content)
        summary = generate_text(prompt)
    except Exception as error:
        raise SummarizerError(f"Error summarizing document '{filename}': {error}") from error

    return summary
Paso 4.3 — Probar summarizer.py desde PowerShell
Antes de tocar la API, probemos el servicio directamente.

Ejecuta:

python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.md'))"
Resultado esperado:

The document explains that Private Doc Agent is a sample Markdown document focused on reading private documents, searching across .txt and .md files, adding local LLM support, building a RAG pipeline, and adding agent tools.
No tiene que ser igual palabra por palabra. Lo importante es que resuma el contenido de demo.md.

También prueba:

python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.txt'))"
Qué estamos logrando con este paso
Ahora ya no es solo:

Prompt manual → LLM local
Ahora será:

Documento local → Prompt controlado → LLM local → Resumen
Desde el punto de vista de IA, esto ya es una capacidad funcional:

Generación aumentada por contexto local simple
Todavía no es RAG, porque estamos enviando el documento completo al modelo. Pero ya estás usando el contenido privado como contexto.

Cuando esta prueba funcione, seguimos con el Paso 5: exponer /summarize en FastAPI.


miércoles 0:42
Vamos al paso 5

Perfecto. Vamos con el Paso 5 — Exponer /summarize en FastAPI.

En este paso conectamos el servicio:

summarizer.py
con la API:

app/main.py
Al final podrás llamar:

POST /summarize
y obtener el resumen de un archivo .txt o .md.

Paso 5.1 — Actualizar app/main.py
Abre:

app/main.py
Vamos a agregar:

from app.services.summarizer import summarize_document, SummarizerError
from app.config import OLLAMA_MODEL
También vamos a crear un modelo Pydantic para el request:

class SummarizeRequest(BaseModel):
    filename: str
Tu app/main.py completo debería quedar así:

"""
FastAPI application entry point.

This module defines the HTTP API for Private Doc Agent.

Current capabilities:
1. Health check endpoint.
2. Local document listing.
3. Local document content retrieval.
4. Simple keyword search across .txt and .md files.
5. Local LLM-powered document summarization.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import APP_NAME, APP_VERSION, OLLAMA_MODEL
from app.services.document_loader import list_documents, read_document
from app.services.simple_search import search_keyword
from app.services.summarizer import summarize_document, SummarizerError


app = FastAPI(
    title="Private Doc Agent",
    description="Local-first assistant for private document analysis.",
    version=APP_VERSION,
)


class SearchRequest(BaseModel):
    """
    Request model for keyword search.

    Attributes:
        query: Keyword or phrase to search across supported documents.
    """

    query: str


class SummarizeRequest(BaseModel):
    """
    Request model for document summarization.

    Attributes:
        filename: Name of the local document to summarize.
    """

    filename: str


@app.get("/health")
def health_check():
    """
    Returns the current health status of the API.

    This endpoint is useful to verify that the FastAPI application
    is running correctly.
    """
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/documents")
def get_documents():
    """
    Lists all supported documents available in the local input folder.

    Supported file extensions are defined in app/config.py.
    """
    documents = list_documents()

    return {
        "documents": documents,
        "count": len(documents),
    }


@app.get("/documents/{filename}")
def get_document(filename: str):
    """
    Returns the full content of a specific local document.

    Args:
        filename: Name of the document located in the data/input folder.
    """
    try:
        content = read_document(filename)
        return {
            "filename": filename,
            "content": content,
        }
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/search")
def search_documents(request: SearchRequest):
    """
    Searches a keyword or phrase across all supported local documents.

    Args:
        request: SearchRequest containing the query to search.
    """
    results = search_keyword(request.query)

    return {
        "query": request.query,
        "matches": results,
        "count": len(results),
    }


@app.post("/summarize")
def summarize_local_document(request: SummarizeRequest):
    """
    Summarizes a supported local document using the configured local LLM.

    Args:
        request: SummarizeRequest containing the filename to summarize.
    """
    try:
        summary = summarize_document(request.filename)

        return {
            "filename": request.filename,
            "summary": summary,
            "model": OLLAMA_MODEL,
            "version": APP_VERSION,
        }

    except SummarizerError as error:
        raise HTTPException(status_code=500, detail=str(error))
Paso 5.2 — Ejecutar la API
Desde PowerShell:

cd C:\Proyectos\private-doc-agent
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
Abre en el navegador:

http://localhost:8000/docs
Ahora deberías ver un nuevo endpoint:

POST /summarize
Paso 5.3 — Probar desde Swagger
En:

http://localhost:8000/docs
Busca:

POST /summarize
Haz clic en:

Try it out
Body para probar con Markdown:

{
  "filename": "demo.md"
}
Luego:

Execute
Respuesta esperada:

{
  "filename": "demo.md",
  "summary": "The document explains...",
  "model": "qwen3.5:4b",
  "version": "0.2.0"
}
También prueba:

{
  "filename": "demo.txt"
}
Paso 5.4 — Probar desde PowerShell
Con la API corriendo, abre otra terminal y ejecuta:

Invoke-RestMethod `
  -Uri "http://localhost:8000/summarize" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{ "filename": "demo.md" }'
También puedes usar curl.exe:

curl.exe -X POST "http://localhost:8000/summarize" ^
  -H "Content-Type: application/json" ^
  -d "{ \"filename\": \"demo.md\" }"
En PowerShell, yo prefiero Invoke-RestMethod.

Qué acabamos de agregar
Con este paso ya tienes la funcionalidad completa de la v0.2.0:

Documento .txt/.md
   ↓
FastAPI /summarize
   ↓
summarizer.py
   ↓
prompt template
   ↓
llm_client.py
   ↓
Ollama local
   ↓
respuesta del modelo
Desde el punto de vista de IA, el proyecto ya llegó a:

Aplicación local con LLM integrado y prompt controlado para análisis documental básico.
Todavía no es RAG ni agente, pero ya es una app con IA real.

Paso 5.5 — Validar errores básicos
Prueba con un archivo que no exista:

{
  "filename": "no_existe.md"
}
Hoy devolverá error 500 porque todo se encapsula como SummarizerError.

Más adelante podemos refinarlo para responder:

404 si el archivo no existe
400 si la extensión no está soportada
500 si falla el LLM
Eso podría ser una mejora pequeña antes del commit.

Criterio de aceptación del Paso 5
Este paso queda listo si:

1. /health sigue funcionando.
2. /documents sigue listando demo.txt y demo.md.
3. /search sigue funcionando.
4. /summarize aparece en Swagger.
5. /summarize resume demo.md.
6. /summarize resume demo.txt.
7. La respuesta incluye filename, summary, model y version.
Cuando confirmes que /summarize funciona, hacemos el Paso 6 — mejorar manejo de errores y preparar commit de v0.2.0.


Si funciona

Excelente, Alfredo. Entonces ya completamos la funcionalidad principal de la v0.2.0.

Hasta ahora el proyecto ya hace esto:

v0.1.0
- Lee documentos .txt y .md
- Lista documentos locales
- Permite consultar contenido
- Busca por palabra clave

v0.2.0
- Integra un LLM local vía Ollama
- Usa qwen3.5:4b como modelo generativo local
- Carga un prompt controlado desde archivo
- Resume documentos .txt y .md usando IA local
- Expone el endpoint POST /summarize
Desde el punto de vista de IA, ¿a qué llegamos?
Llegamos a esta capa:

Aplicación documental local + LLM local + prompt controlado
Visualmente:

Documento privado
   ↓
document_loader.py
   ↓
summarizer.py
   ↓
summarize_prompt.txt
   ↓
llm_client.py
   ↓
Ollama local
   ↓
qwen3.5:4b
   ↓
Resumen generado
Esto todavía no es RAG y todavía no es un agente, pero ya es una aplicación con IA real.

La diferencia es:

Antes:
Documento → búsqueda exacta por palabra clave

Ahora:
Documento → contexto para un LLM → resumen generado
Paso 6 — Mejorar manejo de errores antes del commit
Ahora haría una mejora pequeña pero profesional: que /summarize devuelva errores más claros.

Actualmente, si el archivo no existe, probablemente devuelve 500. Mejor sería:

404 → documento no encontrado
400 → extensión no soportada
500 → error del LLM o del resumen
Para eso modifica el endpoint /summarize en app/main.py.

Reemplaza esta parte:

@app.post("/summarize")
def summarize_local_document(request: SummarizeRequest):
    """
    Summarizes a supported local document using the configured local LLM.

    Args:
        request: SummarizeRequest containing the filename to summarize.
    """
    try:
        summary = summarize_document(request.filename)

        return {
            "filename": request.filename,
            "summary": summary,
            "model": OLLAMA_MODEL,
            "version": APP_VERSION,
        }

    except SummarizerError as error:
        raise HTTPException(status_code=500, detail=str(error))
por esta versión:

@app.post("/summarize")
def summarize_local_document(request: SummarizeRequest):
    """
    Summarizes a supported local document using the configured local LLM.

    Args:
        request: SummarizeRequest containing the filename to summarize.

    Returns:
        A JSON response containing the filename, generated summary,
        local model name, and application version.

    Raises:
        HTTPException: Returns a specific HTTP error when the document
        does not exist, the extension is unsupported, or the local LLM
        summarization process fails.
    """
    try:
        summary = summarize_document(request.filename)

        return {
            "filename": request.filename,
            "summary": summary,
            "model": OLLAMA_MODEL,
            "version": APP_VERSION,
        }

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except SummarizerError as error:
        raise HTTPException(status_code=500, detail=str(error))
Pero para que esto funcione bien, debemos ajustar también summarizer.py, porque ahora mismo atrapa todos los errores y los convierte en SummarizerError.

Ajuste en app/services/summarizer.py
Busca esta función:

def summarize_document(filename: str) -> str:
    """
    Summarizes a supported local document using the configured local LLM.

    Args:
        filename: The name of the document located in the data/input folder.

    Returns:
        The summary generated by the local LLM.

    Raises:
        SummarizerError: If the document cannot be summarized.
    """
    try:
        document_content = read_document(filename)
        prompt = build_summary_prompt(document_content)
        summary = generate_text(prompt)
    except Exception as error:
        raise SummarizerError(f"Error summarizing document '{filename}': {error}") from error

    return summary
Reemplázala por esta versión:

def summarize_document(filename: str) -> str:
    """
    Summarizes a supported local document using the configured local LLM.

    Args:
        filename: The name of the document located in the data/input folder.

    Returns:
        The summary generated by the local LLM.

    Raises:
        FileNotFoundError: If the requested document does not exist.
        ValueError: If the requested document has an unsupported extension.
        SummarizerError: If the prompt cannot be built or the local LLM fails.
    """
    try:
        document_content = read_document(filename)
        prompt = build_summary_prompt(document_content)
        summary = generate_text(prompt)
    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except Exception as error:
        raise SummarizerError(f"Error summarizing document '{filename}': {error}") from error

    return summary
Con este cambio, el sistema no “esconde” los errores de archivo como si fueran errores internos del LLM.

Pruebas rápidas
Con la API corriendo, prueba estos tres casos:

1. Documento válido
{
  "filename": "demo.md"
}
Resultado esperado:

200 OK
2. Documento inexistente
{
  "filename": "no_existe.md"
}
Resultado esperado:

404 Not Found
3. Extensión no soportada
Crea temporalmente un archivo:

data/input/demo.pdf
y prueba:

{
  "filename": "demo.pdf"
}
Resultado esperado:

400 Bad Request
Luego puedes borrar demo.pdf.

Paso 7 — Revisar estado de Git
Cuando termines esa mejora:

git status
Deberías ver cambios en algo como:

.env.example
requirements.txt
app/config.py
app/main.py
app/services/llm_client.py
app/services/summarizer.py
app/prompts/summarize_prompt.txt
Asegúrate de que .env no aparezca para ser subido. Si aparece, revisa que .gitignore tenga:

.env
Commit sugerido
Cuando todo esté probado:

git add .
git commit -m "feat: add local LLM document summarization"
git push origin feature/local-llm-summarization
Luego, si quieres cerrar la versión en main:

git checkout main
git merge feature/local-llm-summarization
git push origin main
Y tag:

git tag v0.2.0
git push origin v0.2.0
Resumen para el README
Puedes agregar esta sección:

## v0.2.0 - Local LLM Summarization

This version adds the first AI-powered capability to Private Doc Agent.

The application can now summarize local `.txt` and `.md` documents using a locally running LLM through Ollama. The summarization flow uses a controlled prompt template and keeps the document content within the local environment.

### New capabilities

- Local LLM integration with Ollama
- Configurable model through `.env`
- Prompt template for document summarization
- Document summarization service
- `POST /summarize` endpoint

### AI layer introduced

This version introduces a local LLM-based generation layer.

The system now follows this flow:

```text
Local document
  → prompt template
  → local LLM
  → generated summary
This is not RAG yet. The full document content is sent to the local model as context. RAG will be introduced in a later version using chunking, embeddings and vector search.


Con esto dejamos la v0.2.0 muy bien cerrada: funcional, documentada y explicable.

No he hecho el commit todavia, me puedes dar el readme actualizado? deberia tener en el mismo archivo el historia, es decir version 0.1.0 y la 0.2.0?

Sí, te recomiendo que el README.md tenga dos niveles de información:

Qué hace actualmente el proyecto, para que cualquier persona entienda el estado actual.

Historial de versiones, para mostrar la evolución: v0.1.0, v0.2.0, etc.

No pondría la historia demasiado larga en el README. Para el README basta una sección tipo Version History o Changelog. Más adelante, si crece mucho, podemos moverlo a un archivo separado llamado CHANGELOG.md.

Te dejo un README.md actualizado para la versión actual del proyecto.

private-doc-agent
Private Doc Agent is a local-first AI assistant designed to analyze and interact with private documents.

The project is being built incrementally, starting from deterministic document loading and keyword search, and evolving toward a private AI-powered document agent with local LLM support, RAG, tools, MCP, and multi-agent validation.

Current Version
v0.2.0

What it does now
Private Doc Agent currently provides a FastAPI backend that can read local .txt and .md documents, list available files, retrieve document content, search keywords across documents, and summarize documents using a locally running LLM through Ollama.

The current version introduces the first AI-powered capability: local document summarization.

The document content is processed locally and sent to a local model served by Ollama. This keeps the project aligned with a local-first and privacy-oriented architecture.

Current Features
FastAPI backend.

Health check endpoint.

Local document listing.

Support for .txt and .md files.

Document content retrieval.

Simple keyword search across supported documents.

Local LLM integration through Ollama.

Configurable model using environment variables.

Prompt template for document summarization.

Document summarization endpoint.

AI Layer Introduced
In version v0.2.0, the project introduces a local LLM-based generation layer.

Current AI flow:

Local document
  -> document loader
  -> prompt template
  -> local LLM client
  -> Ollama
  -> local generative model
  -> generated summary
At this stage, this is not RAG yet. The application sends the full document content to the local LLM as context.

RAG will be introduced in a future version using chunking, embeddings, vector storage, and context retrieval.

Project Structure
private-doc-agent/
  app/
    __init__.py
    main.py
    config.py
    prompts/
      summarize_prompt.txt
    services/
      __init__.py
      document_loader.py
      simple_search.py
      llm_client.py
      summarizer.py
  data/
    input/
      demo.txt
      demo.md
    processed/
  docs/
    roadmap.md
  tests/
  README.md
  requirements.txt
  .env.example
  .gitignore
Requirements
Python 3.11+

FastAPI

Uvicorn

Pydantic

python-dotenv

requests

Ollama installed and running locally

Setup
Clone the repository:

git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
Create a virtual environment:

python -m venv .venv
Activate it on Windows PowerShell:

.\.venv\Scripts\Activate.ps1
Install dependencies:

pip install -r requirements.txt
Environment Variables
Create a .env file in the project root based on .env.example.

Example:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
The .env file should not be committed to GitHub.

The .env.example file should be committed to document the required configuration.

Ollama Setup
Make sure Ollama is running locally.

Validate Ollama:

Invoke-WebRequest -UseBasicParsing http://localhost:11434
Expected response:

Ollama is running
List installed models:

ollama list
Example model used in this project:

qwen3.5:4b
If needed, update .env with the model available in your local environment.

Run the API
Start the FastAPI server:

uvicorn app.main:app --reload
Open the interactive API documentation:

http://localhost:8000/docs
API Endpoints
Health Check
GET /health
Expected response:

{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.2.0"
}
List Documents
GET /documents
Returns all supported documents from data/input.

Read Document
GET /documents/{filename}
Examples:

GET /documents/demo.txt
GET /documents/demo.md
Search Documents
POST /search
Request body:

{
  "query": "RAG"
}
Expected response structure:

{
  "query": "RAG",
  "matches": [
    {
      "filename": "demo.md",
      "line_number": 10,
      "line": "- Build a RAG pipeline"
    }
  ],
  "count": 1
}
Summarize Document
POST /summarize
Request body:

{
  "filename": "demo.md"
}
Expected response structure:

{
  "filename": "demo.md",
  "summary": "The document explains...",
  "model": "qwen3.5:4b",
  "version": "0.2.0"
}
Testing the LLM Client
You can test the local LLM client directly from PowerShell:

python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
Expected result:

An artificial intelligence tool that processes and organizes your files entirely on your local device rather than in the cloud for privacy.
The exact response may vary depending on the model.

Testing Document Summarization
You can test summarization directly from Python:

python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.md'))"
Version History
v0.1.0 - Basic Local Document Search
Initial version focused on deterministic document handling without AI.

Features introduced:

FastAPI application structure.

Health check endpoint.

Local document discovery.

Support for .txt and .md files.

Document content retrieval.

Case-insensitive keyword search across local documents.

AI status:

No AI capabilities yet.
This version establishes the document ingestion and search foundation.
v0.2.0 - Local LLM Document Summarization
This version introduces the first AI-powered capability.

Features introduced:

Local LLM integration through Ollama.

Configurable Ollama base URL and model through .env.

Local LLM client service.

Prompt template for summarization.

Document summarization service.

POST /summarize endpoint.

Improved separation between document loading, search, LLM communication, and summarization logic.

AI status:

Local document content
  -> controlled prompt
  -> local LLM
  -> generated summary
This version is still not RAG. The full document is passed as context to the local model.

Roadmap
v0.3.0 - Basic RAG
Planned capabilities:

Split documents into chunks.

Generate local embeddings.

Store vectors in ChromaDB.

Retrieve relevant chunks based on a user question.

Answer questions using retrieved context.

Return sources used to generate the answer.

v0.4.0 - Tool-Based Agent
Planned capabilities:

Add document tools such as search, summarize, and ask.

Create a simple agent router.

Allow the system to decide which tool to use based on user intent.

v0.5.0 - Auditor Agent
Planned capabilities:

Add a second validation layer.

Review answers for unsupported claims.

Check whether the response is grounded in document evidence.

Add confidence levels.

v0.6.0 - MCP Server
Planned capabilities:

Expose document tools through MCP.

Allow external clients or agents to call document-related tools using a standard protocol.

Design Principles
Local-first execution.

Privacy-oriented architecture.

Incremental learning by layers.

Clear separation of responsibilities.

Documented code.

No external LLM dependency for private document processing.

Build deterministic capabilities before adding agentic behavior.

Current Limitations
Only .txt and .md files are supported.

Summarization sends the full document content to the local model.

Large documents may exceed the model context window.

No chunking yet.

No embeddings yet.

No vector database yet.

No RAG yet.

No agent or MCP support yet.

No frontend yet.

Suggested Commit for v0.2.0
git add .
git commit -m "feat: add local LLM document summarization"
git push origin feature/local-llm-summarization
After merging into main, the suggested tag is:

git tag v0.2.0
git push origin v0.2.0
Mi recomendación: por ahora deja el historial en el mismo README.md. Cuando lleguemos a v0.4.0 o v0.5.0, lo más limpio será crear un archivo separado CHANGELOG.md y en el README dejar solo un resumen del historial.


quiero subir los cambios a github y cerrar la rama

Perfecto. Como trabajaste en la rama:

feature/local-llm-summarization
y quieres subir los cambios y cerrar la rama, haríamos este flujo:

1. Revisar estado
2. Confirmar que .env no se suba
3. Commit
4. Push de la rama
5. Merge a main
6. Push a main
7. Crear tag v0.2.0
8. Borrar rama local y remota
1. Revisa en qué rama estás
Desde PowerShell:

cd C:\Proyectos\private-doc-agent
git branch
Deberías ver:

* feature/local-llm-summarization
  main
Si no estás en esa rama:

git checkout feature/local-llm-summarization
2. Revisa los cambios
git status
Verifica que no aparezca .env.

Si aparece .env, no lo subas. Ejecuta:

git restore --staged .env
y confirma que .gitignore tenga:

.env
Si .env ya quedó trackeado por error, me dices antes de hacer push para corregirlo bien.

3. Agrega cambios
git add .
Revisa nuevamente:

git status
4. Crea el commit
git commit -m "feat: add local LLM document summarization"
5. Sube la rama a GitHub
git push origin feature/local-llm-summarization
Con esto ya queda publicada la rama en GitHub.

6. Cambia a main
git checkout main
Trae lo último del remoto:

git pull origin main
7. Haz merge de la rama
git merge feature/local-llm-summarization
Si no hay conflictos, verás que el merge termina correctamente.

8. Sube main a GitHub
git push origin main
9. Crear tag de versión
Como esta versión ya representa la v0.2.0, crea el tag:

git tag v0.2.0
Súbelo a GitHub:

git push origin v0.2.0
10. Cerrar la rama local
Una vez que main ya tiene los cambios:

git branch -d feature/local-llm-summarization
11. Cerrar la rama remota
Para borrar la rama en GitHub:

git push origin --delete feature/local-llm-summarization
Flujo completo en bloque
Puedes ejecutarlo así, paso a paso:

cd C:\Proyectos\private-doc-agent

git checkout feature/local-llm-summarization
git status

git add .
git status

git commit -m "feat: add local LLM document summarization"

git push origin feature/local-llm-summarization

git checkout main
git pull origin main

git merge feature/local-llm-summarization

git push origin main

git tag v0.2.0
git push origin v0.2.0

git branch -d feature/local-llm-summarization
git push origin --delete feature/local-llm-summarization
Validación final
Al final ejecuta:

git status
Deberías ver algo como:

On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
También puedes validar tags:

git tag
Debería aparecer:

v0.2.0
Nota práctica
Si quieres hacerlo más “GitHub formal”, en vez de hacer merge local puedes:

1. Subir la rama
2. Crear Pull Request en GitHub
3. Hacer merge desde GitHub
4. Borrar rama desde GitHub
5. Hacer git pull en local
Pero para este proyecto de aprendizaje, el merge local que te indiqué está perfecto.


miércoles 23:59
Antes de pasar a una nueva version, quiero agregar un trace o un log, que me pueda ver que va pasando en los diferentes servicios

Sí, muy buena idea. Antes de pasar a v0.3.0, yo agregaría una versión menor:

v0.2.1 - Add application logging
Esto no cambia la capacidad de IA, pero mejora la observabilidad del proyecto: podrás ver qué está pasando cuando se listan documentos, se lee un archivo, se construye un prompt, se llama a Ollama o se genera un resumen.

Qué vamos a agregar
Agregaremos una capa de logging centralizada:

private-doc-agent/
  app/
    logging_config.py       ← nuevo
    main.py                 ← ajustar logs en endpoints
    services/
      document_loader.py    ← logs de lectura/listado
      simple_search.py      ← logs de búsqueda
      llm_client.py         ← logs de llamada a Ollama
      summarizer.py         ← logs de resumen
  logs/
    app.log                 ← generado localmente, no se sube
Desde el punto de vista técnico, llegamos a esto:

Usuario/API
   ↓
Endpoint FastAPI
   ↓
Servicio
   ↓
Log de entrada / proceso / salida / error
   ↓
Archivo logs/app.log + consola
Paso 1 — Actualizar .gitignore
Agrega estas líneas a tu .gitignore:

logs/
*.log
Así evitamos subir archivos de trazas a GitHub.

Paso 2 — Crear app/logging_config.py
Crea este archivo:

app/logging_config.py
Con este contenido:

"""
Application logging configuration module.

This module centralizes the logging configuration for Private Doc Agent.

It configures logs to be written both to the console and to a local file.
The goal is to make the application easier to debug and observe while
keeping logging behavior consistent across all services.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import BASE_DIR


# Directory where local log files will be stored.
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"


def setup_logging() -> None:
    """
    Configures application-wide logging.

    The configuration includes:
    - Console logging for development visibility.
    - Rotating file logging to avoid unlimited log growth.
    - A consistent log format with timestamp, level, logger name and message.

    This function should be called once when the FastAPI application starts.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers when Uvicorn reloads the application.
    if root_logger.handlers:
        return

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
Paso 3 — Actualizar app/main.py
Al inicio de main.py, agrega:

import logging

from app.logging_config import setup_logging
Luego, antes de crear app = FastAPI(...), agrega:

setup_logging()

logger = logging.getLogger(__name__)
Después puedes agregar logs en los endpoints.

Te muestro las partes clave que deberías ajustar.

Importaciones esperadas en main.py
"""
FastAPI application entry point.

This module defines the HTTP API for Private Doc Agent.

Current capabilities:
1. Health check endpoint.
2. Local document listing.
3. Local document content retrieval.
4. Simple keyword search across .txt and .md files.
5. Local LLM-powered document summarization.
6. Application logging for traceability and debugging.
"""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import APP_NAME, APP_VERSION, OLLAMA_MODEL
from app.logging_config import setup_logging
from app.services.document_loader import list_documents, read_document
from app.services.simple_search import search_keyword
from app.services.summarizer import summarize_document, SummarizerError


setup_logging()

logger = logging.getLogger(__name__)
En /health
@app.get("/health")
def health_check():
    """
    Returns the current health status of the API.
    """
    logger.info("Health check requested.")

    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }
En /documents
@app.get("/documents")
def get_documents():
    """
    Lists all supported documents available in the local input folder.
    """
    logger.info("Listing available documents.")

    documents = list_documents()

    logger.info("Documents listed successfully. count=%s", len(documents))

    return {
        "documents": documents,
        "count": len(documents),
    }
En /documents/{filename}
@app.get("/documents/{filename}")
def get_document(filename: str):
    """
    Returns the full content of a specific local document.
    """
    logger.info("Document content requested. filename=%s", filename)

    try:
        content = read_document(filename)

        logger.info("Document read successfully. filename=%s", filename)

        return {
            "filename": filename,
            "content": content,
        }

    except FileNotFoundError as error:
        logger.warning("Document not found. filename=%s error=%s", filename, error)
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        logger.warning("Unsupported document requested. filename=%s error=%s", filename, error)
        raise HTTPException(status_code=400, detail=str(error))
En /search
@app.post("/search")
def search_documents(request: SearchRequest):
    """
    Searches a keyword or phrase across all supported local documents.
    """
    logger.info("Search requested. query=%s", request.query)

    results = search_keyword(request.query)

    logger.info(
        "Search completed. query=%s matches=%s",
        request.query,
        len(results),
    )

    return {
        "query": request.query,
        "matches": results,
        "count": len(results),
    }
En /summarize
@app.post("/summarize")
def summarize_local_document(request: SummarizeRequest):
    """
    Summarizes a supported local document using the configured local LLM.
    """
    logger.info(
        "Summarization requested. filename=%s model=%s",
        request.filename,
        OLLAMA_MODEL,
    )

    try:
        summary = summarize_document(request.filename)

        logger.info(
            "Summarization completed successfully. filename=%s summary_length=%s",
            request.filename,
            len(summary),
        )

        return {
            "filename": request.filename,
            "summary": summary,
            "model": OLLAMA_MODEL,
            "version": APP_VERSION,
        }

    except FileNotFoundError as error:
        logger.warning(
            "Summarization failed. Document not found. filename=%s error=%s",
            request.filename,
            error,
        )
        raise HTTPException(status_code=404, detail=str(error))
    except ValueError as error:
        logger.warning(
            "Summarization failed. Unsupported file. filename=%s error=%s",
            request.filename,
            error,
        )
        raise HTTPException(status_code=400, detail=str(error))
    except SummarizerError as error:
        logger.error(
            "Summarization failed due to internal error. filename=%s error=%s",
            request.filename,
            error,
        )
        raise HTTPException(status_code=500, detail=str(error))
Paso 4 — Agregar logs en document_loader.py
Al inicio del archivo agrega:

import logging
Luego después de los imports:

logger = logging.getLogger(__name__)
Ejemplo documentado:

"""
Local document loader service.

This module contains utility functions to list and read supported local
documents from the configured input folder.

Supported extensions are defined in app/config.py.
"""

import logging

from app.config import INPUT_DIR, SUPPORTED_EXTENSIONS


logger = logging.getLogger(__name__)
Dentro de list_documents() puedes agregar:

logger.info("Scanning input directory for supported documents. input_dir=%s", INPUT_DIR)
Antes del return documents:

logger.info("Supported documents found. count=%s", len(documents))
Dentro de read_document(filename: str):

logger.info("Reading document. filename=%s", filename)
Antes de retornar:

logger.info("Document read completed. filename=%s size_chars=%s", filename, len(content))
Para eso conviene ajustar la última línea así:

content = file_path.read_text(encoding="utf-8")
logger.info("Document read completed. filename=%s size_chars=%s", filename, len(content))
return content
Paso 5 — Agregar logs en simple_search.py
Al inicio:

"""
Simple keyword search service.

This module provides deterministic keyword search across all supported
local documents. It does not use AI or semantic search.
"""

import logging

from app.services.document_loader import list_documents, read_document


logger = logging.getLogger(__name__)
Dentro de search_keyword():

logger.info("Keyword search started. query=%s", query)
Si el query está vacío:

logger.warning("Keyword search skipped because query is empty.")
Antes del return:

logger.info("Keyword search completed. query=%s matches=%s", query, len(results))
Paso 6 — Agregar logs en llm_client.py
Al inicio:

import logging
import requests
Después de imports:

logger = logging.getLogger(__name__)
Dentro de generate_text():

logger.info("Sending prompt to local LLM. model=%s prompt_length=%s", OLLAMA_MODEL, len(prompt))
Después de recibir la respuesta:

logger.info(
    "Local LLM response received. model=%s response_length=%s",
    OLLAMA_MODEL,
    len(generated_text),
)
En el error:

logger.error("Error communicating with local LLM. endpoint=%s error=%s", endpoint, error)
Importante: no registres el prompt completo ni el contenido del documento, porque puede contener información privada.

Buena práctica:

Sí loguear:
- nombre de archivo
- longitud del texto
- modelo usado
- cantidad de resultados
- estado del proceso

No loguear:
- contenido completo del documento
- prompt completo
- resumen completo
- datos sensibles
Paso 7 — Agregar logs en summarizer.py
Al inicio:

import logging
Después de imports:

logger = logging.getLogger(__name__)
En load_summary_prompt_template():

logger.info("Loading summary prompt template. path=%s", PROMPT_PATH)
En build_summary_prompt():

logger.info("Building summary prompt. document_length=%s", len(document_content))
En summarize_document():

logger.info("Document summarization started. filename=%s", filename)
Antes del return:

logger.info("Document summarization finished. filename=%s summary_length=%s", filename, len(summary))
Paso 8 — Probar los logs
Ejecuta la API:

uvicorn app.main:app --reload
Abre:

http://localhost:8000/docs
Prueba:

GET /health
GET /documents
POST /search
POST /summarize
Luego revisa que se haya creado:

logs/app.log
También puedes verlo desde PowerShell:

Get-Content .\logs\app.log -Tail 50
O en vivo:

Get-Content .\logs\app.log -Wait
Paso 9 — Actualizar versión
Como esto es una mejora técnica sin cambiar funcionalidad principal, puedes actualizar la versión a:

APP_VERSION = "0.2.1"
en:

app/config.py
Y en el README agregar:

### v0.2.1 - Application Logging

This version adds centralized application logging.

Features introduced:

- Console and file logging.
- Rotating log file under `logs/app.log`.
- Traceability across API endpoints and services.
- Logs for document loading, keyword search, local LLM calls and summarization flow.
- Privacy-aware logging that avoids storing document content or prompts.
Commit sugerido
Como todavía no has hecho commit de v0.2.0, tienes dos opciones.

Opción A — Un solo commit para v0.2.0 + logging
Más simple:

git add .
git commit -m "feat: add local LLM summarization and logging"
Tag:

git tag v0.2.1
Opción B — Dos commits separados
Más profesional:

git add .
git commit -m "feat: add local LLM document summarization"
Luego agregas logging y haces:

git add .
git commit -m "chore: add application logging"
Tag final:

git tag v0.2.1
Yo te recomiendo la opción B, porque en GitHub se ve mejor la evolución:

v0.2.0 → IA local para resumen
v0.2.1 → logging y trazabilidad
Para este cambio, no estás agregando “más IA”; estás agregando una capacidad transversal de ingeniería: observabilidad básica.



Python Ejecutar

Convertir en un bloque de escritura

Claro.

Python

Ejecutar


Una marcacion para manana, voy por el paso 4

Listo, Alfredo. Te dejé una marcación para mañana en la mañana para continuar el proyecto private-doc-agent desde el paso 4 de logging/trazabilidad en los servicios.

Para retomarlo, el punto exacto es:

Paso 4 — Agregar logs en document_loader.py
Y veníamos en la versión:

v0.2.1 - Application Logging

jueves 22:54
Retomando desde el punto 4, dame la nueva version, por lo que te comparto el contenido del document_loader.py: from pathlib import Path
from app.config import INPUT_DIR, SUPPORTED_EXTENSIONS


def list_documents() -> list[dict]:
    """
    Lists supported documents from data/input.
    Currently supports .txt and .md files.
    """
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    documents = []

    for file_path in INPUT_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            documents.append(
                {
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "size_bytes": file_path.stat().st_size,
                    "path": str(file_path.relative_to(INPUT_DIR.parent.parent)),
                }
            )

    return documents


def read_document(filename: str) -> str:
    """
    Reads a supported document by filename from data/input.
    """
    file_path = INPUT_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {filename}")

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {file_path.suffix}")

    return file_path.read_text(encoding="utf-8")

Perfecto. Para el Paso 4 — Agregar logs en document_loader.py, reemplaza el contenido completo de tu archivo por esta versión.

Mantiene la funcionalidad actual, pero agrega trazabilidad sin registrar contenido privado del documento.

"""
Local document loader service.

This module contains utility functions to list and read supported local
documents from the configured input folder.

Supported extensions are defined in app/config.py.

Logging strategy:
- Logs

continua

"""
Local document loader service.

This module contains utility functions to list and read supported local
documents from the configured input folder.

Supported extensions are defined in app/config.py.

Logging strategy:
- Logs operational events such as directory scanning and document reading.
- Logs metadata such as filename, extension, file size and character count.
- Does not log document content to avoid exposing private information.
"""

import logging

from app.config import INPUT_DIR, SUPPORTED_EXTENSIONS


logger = logging.getLogger(__name__)


def list_documents() -> list[dict]:
    """
    Lists supported documents from the local input folder.

    The function scans the configured input directory and returns metadata
    for all files with supported extensions.

    Returns:
        A list of dictionaries containing document metadata:
        filename, extension, size in bytes and relative path.
    """
    logger.info(
        "Scanning input directory for supported documents. input_dir=%s supported_extensions=%s",
        INPUT_DIR,
        sorted(SUPPORTED_EXTENSIONS),
    )

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    documents = []

    for file_path in INPUT_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            document_metadata = {
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "size_bytes": file_path.stat().st_size,
                "path": str(file_path.relative_to(INPUT_DIR.parent.parent)),
            }

            documents.append(document_metadata)

            logger.info(
                "Supported document found. filename=%s extension=%s size_bytes=%s",
                document_metadata["filename"],
                document_metadata["extension"],
                document_metadata["size_bytes"],
            )

    logger.info("Document scan completed. count=%s", len(documents))

    return documents


def read_document(filename: str) -> str:
    """
    Reads a supported local document by filename.

    Args:
        filename: Name of the document located in the configured input folder.

    Returns:
        The document content as plain text.

    Raises:
        FileNotFoundError: If the document does not exist.
        ValueError: If the document extension is not supported.
    """
    logger.info("Reading document requested. filename=%s", filename)

    file_path = INPUT_DIR / filename

    if not file_path.exists():
        logger.warning("Document not found. filename=%s path=%s", filename, file_path)
        raise FileNotFoundError(f"Document not found: {filename}")

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        logger.warning(
            "Unsupported document extension. filename=%s extension=%s",
            filename,
            file_path.suffix.lower(),
        )
        raise ValueError(f"Unsupported file extension: {file_path.suffix}")

    content = file_path.read_text(encoding="utf-8")

    logger.info(
        "Document read completed. filename=%s size_chars=%s",
        filename,
        len(content),
    )

    return content
Qué agregamos aquí
Este archivo ahora registra eventos como:

Scanning input directory for supported documents
Supported document found
Document scan completed
Reading document requested
Document read completed
Document not found
Unsupported document extension
Pero evita registrar:

contenido del documento
prompt completo
resumen completo
datos sensibles
Eso es importante porque el proyecto tiene enfoque private/local-first.

Cómo probar este paso
Levanta la API:

uvicorn app.main:app --reload
Ejecuta:

GET /documents
GET /documents/demo.md
Luego revisa el archivo:

Get-Content .\logs\app.log -Tail 50
Deberías ver líneas parecidas a:

INFO | app.services.document_loader | Scanning input directory for supported documents...
INFO | app.services.document_loader | Supported document found. filename=demo.md...
INFO | app.services.document_loader | Document scan completed. count=2
INFO | app.services.document_loader | Reading document requested. filename=demo.md
INFO | app.services.document_loader | Document read completed. filename=demo.md size_chars=...
Cuando confirmes que esto funciona, seguimos con:

Paso 5 — Agregar logs en simple_search.py

Antes de pasar al paso 5, vamos a ejecutar el servicio, cual es la ip? o como la puedo encontrar para ponerla en el explorador?

Para ejecutarlo en tu propio equipo, normalmente no necesitas buscar una IP externa. FastAPI con Uvicorn corre por defecto en:

http://127.0.0.1:8000
o equivalente:

http://localhost:8000
1. Ejecutar el servicio
Desde PowerShell:

cd C:\Proyectos\private-doc-agent
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
Si todo está bien, deberías ver algo parecido a:

Uvicorn running on http://127.0.0.1:8000
2. Abrir en el navegador
Para la documentación interactiva:

http://localhost:8000/docs
O también:

http://127.0.0.1:8000/docs
Para probar el health check:

http://localhost:8000/health
Para listar documentos:

http://localhost:8000/documents
3. Si quieres acceder desde otro equipo en la misma red
Ahí sí necesitas la IP de tu máquina.

Ejecuta:

ipconfig
Busca algo como:

Adaptador de LAN inalámbrica Wi-Fi:

Dirección IPv4 . . . . . . . . . . . . . : 192.168.1.25
Entonces, en otro equipo de la misma red podrías intentar:

http://192.168.1.25:8000/docs
Pero para que funcione debes levantar Uvicorn así:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Para tu prueba local, usa simplemente:

http://localhost:8000/docs

Vamos al paso 5

Perfecto. Vamos con el Paso 5 — Agregar logs en simple_search.py.

Este servicio es el que hace la búsqueda determinística por palabra clave en los documentos locales. La idea es registrar:

- cuándo inicia una búsqueda
- qué query se recibió
- cuántos documentos se revisaron
- cuántas coincidencias se encontraron
- si el query llegó vacío
Sin registrar contenido sensible más allá de la línea coincidente que ya se devuelve por API.

Reemplaza app/services/simple_search.py
Abre:

app/services/simple_search.py
y reemplaza todo el contenido por esta versión:

"""
Simple keyword search service.

This module provides deterministic keyword search across all supported
local documents.

It does not use AI, embeddings, vector search, or semantic search.
It only performs case-insensitive keyword or phrase matching over the
document lines.

Logging strategy:
- Logs when a keyword search starts and finishes.
- Logs the number of documents scanned.
- Logs the number of matches found.
- Does not log full document content.
"""

import logging

from app.services.document_loader import list_documents, read_document


logger = logging.getLogger(__name__)


def search_keyword(query: str) -> list[dict]:
    """
    Searches a keyword or phrase across all supported local documents.

    The search is case-insensitive and returns the matching line number
    and line content for each match.

    Args:
        query: Keyword or phrase to search across supported documents.

    Returns:
        A list of dictionaries with search results, including filename,
        line number and matching line.
    """
    logger.info("Keyword search requested. query=%s", query)

    if not query or not query.strip():
        logger.warning("Keyword search skipped because query is empty.")
        return []

    query_normalized = query.strip().lower()
    results = []

    documents = list_documents()

    logger.info(
        "Keyword search started. query=%s documents_to_scan=%s",
        query,
        len(documents),
    )

    for document in documents:
        filename = document["filename"]

        logger.info("Scanning document for keyword. filename=%s", filename)

        content = read_document(filename)

        for line_number, line in enumerate(content.splitlines(), start=1):
            if query_normalized in line.lower():
                results.append(
                    {
                        "filename": filename,
                        "line_number": line_number,
                        "line": line.strip(),
                    }
                )

    logger.info(
        "Keyword search completed. query=%s matches=%s",
        query,
        len(results),
    )

    return results
Qué agregamos
Ahora este servicio registrará eventos como:

Keyword search requested
Keyword search started
Scanning document for keyword
Keyword search completed
Keyword search skipped because query is empty
Ejemplo esperado en logs/app.log:

INFO | app.services.simple_search | Keyword search requested. query=RAG
INFO | app.services.simple_search | Keyword search started. query=RAG documents_to_scan=2
INFO | app.services.simple_search | Scanning document for keyword. filename=demo.txt
INFO | app.services.simple_search | Scanning document for keyword. filename=demo.md
INFO | app.services.simple_search | Keyword search completed. query=RAG matches=2
Probar este paso
Levanta la API si no está corriendo:

uvicorn app.main:app --reload
Abre Swagger:

http://localhost:8000/docs
Prueba:

POST /search
Con este body:

{
  "query": "RAG"
}
Luego revisa el log:

Get-Content .\logs\app.log -Tail 50
También prueba un query vacío:

{
  "query": ""
}
Deberías ver un warning parecido a:

WARNING | app.services.simple_search | Keyword search skipped because query is empty.
Punto importante de privacidad
Este servicio todavía devuelve la línea coincidente en la API porque esa es la funcionalidad esperada de /search.

Pero en los logs evitamos guardar:

- contenido completo del documento
- documento completo
- prompt
- resumen
Cuando confirmes que funciona, seguimos con:

Paso 6 — Agregar logs en llm_client.py

Vamos al 6

Perfecto. Vamos con el Paso 6 — Agregar logs en llm_client.py.

Este archivo es crítico porque ahí ocurre la comunicación con Ollama. Queremos ver:

- cuándo se envía un prompt al modelo
- qué modelo se está usando
- a qué endpoint se llama
- longitud del prompt
- longitud de la respuesta
- errores de conexión o respuesta inválida
Pero no vamos a registrar el prompt completo ni la respuesta completa, porque pueden contener información privada.

Reemplaza app/services/llm_client.py
Abre:

app/services/llm_client.py
y reemplaza todo el contenido por esta versión:

"""
Local LLM client service.

This module provides a small abstraction layer to communicate with
a locally running Ollama server.

The rest of the application should use this service instead of calling
Ollama directly. This keeps the LLM integration isolated, easier to test,
and easier to replace later with another local model provider if needed.

Logging strategy:
- Logs local LLM requests and responses using metadata only.
- Logs model name, endpoint, prompt length and response length.
- Does not log full prompts or generated responses to avoid exposing
  private document content.
"""

import logging

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL


logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """
    Custom exception for errors related to the local LLM client.

    This exception is raised when the application cannot communicate with
    the local Ollama server or when the server returns an unexpected response.
    """

    pass


def generate_text(prompt: str) -> str:
    """
    Sends a prompt to the configured local LLM and returns the generated text.

    Args:
        prompt: The complete prompt that will be sent to the local model.

    Returns:
        The text generated by the configured local LLM.

    Raises:
        LLMClientError: If the prompt is empty, if Ollama is not reachable,
        or if the response from Ollama is invalid.
    """
    if not prompt or not prompt.strip():
        logger.warning("Local LLM request skipped because prompt is empty.")
        raise LLMClientError("Prompt cannot be empty.")

    endpoint = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    logger.info(
        "Sending prompt to local LLM. model=%s endpoint=%s prompt_length=%s",
        OLLAMA_MODEL,
        endpoint,
        len(prompt),
    )

    try:
        response = requests.post(endpoint, json=payload, timeout=120)

        if response.status_code == 404:
            logger.error(
                "Local LLM endpoint not found. endpoint=%s model=%s status_code=%s",
                endpoint,
                OLLAMA_MODEL,
                response.status_code,
            )
            raise LLMClientError(
                f"Ollama endpoint not found: {endpoint}. "
                "Verify that Ollama is running and that OLLAMA_BASE_URL points to the correct server."
            )

        response.raise_for_status()

    except requests.exceptions.RequestException as error:
        logger.error(
            "Error communicating with local LLM. endpoint=%s model=%s error=%s",
            endpoint,
            OLLAMA_MODEL,
            error,
        )
        raise LLMClientError(f"Error communicating with local LLM: {error}") from error

    data = response.json()

    generated_text = data.get("response")

    if generated_text is None:
        logger.error(
            "Invalid response from local LLM. Missing response field. model=%s",
            OLLAMA_MODEL,
        )
        raise LLMClientError("Invalid response from local LLM. Missing 'response' field.")

    generated_text = generated_text.strip()

    logger.info(
        "Local LLM response received. model=%s response_length=%s",
        OLLAMA_MODEL,
        len(generated_text),
    )

    return generated_text
Qué cambia en este paso
Antes tenías esto:

generate_text(prompt)
Ahora tienes:

generate_text(prompt)
  ├─ valida prompt vacío
  ├─ registra modelo, endpoint y longitud del prompt
  ├─ llama a Ollama
  ├─ registra errores si algo falla
  ├─ valida que exista response
  └─ registra longitud de respuesta
Ejemplo de log esperado
Cuando uses /summarize, deberías ver algo parecido a:

INFO | app.services.llm_client | Sending prompt to local LLM. model=qwen3.5:4b endpoint=http://localhost:11434/api/generate prompt_length=512
INFO | app.services.llm_client | Local LLM response received. model=qwen3.5:4b response_length=248
Prueba directa sin API
Puedes probar el cliente directamente:

python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
Luego revisa el log:

Get-Content .\logs\app.log -Tail 50
Prueba desde la API
Con la API corriendo:

uvicorn app.main:app --reload
Abre:

http://localhost:8000/docs
Ejecuta:

POST /summarize
Con body:

{
  "filename": "demo.md"
}
Luego revisa:

Get-Content .\logs\app.log -Tail 80
Importante
Si pruebas el cliente directo con:

python -c "..."
y no ves log en logs/app.log, puede pasar porque setup_logging() se ejecuta normalmente desde app/main.py.

Eso significa que el logging a archivo está garantizado cuando corres la API con Uvicorn.

Para pruebas directas, lo importante es que el código no falle. Para ver el archivo logs/app.log, prueba principalmente desde /summarize.

Cuando confirmes que este paso funciona, seguimos con:

Paso 7 — Agregar logs en summarizer.py

Vamos al paso 7

Perfecto. Vamos con el Paso 7 — Agregar logs en summarizer.py.

Este servicio conecta:

document_loader.py
   ↓
summarize_prompt.txt
   ↓
llm_client.py
   ↓
Ollama
Aquí queremos registrar:

- cuándo inicia un resumen
- qué archivo se va a resumir
- cuándo se carga el prompt template
- longitud del documento
- longitud del prompt generado
- longitud del resumen
- errores del proceso
Sin registrar el contenido completo del documento, del prompt o del resumen.

Reemplaza app/services/summarizer.py
Abre:

app/services/summarizer.py
y reemplaza todo el contenido por esta versión:

"""
Document summarization service.

This module provides the logic required to summarize supported local
documents using the configured local LLM.

It connects three parts of the application:
1. The document loader, which reads local .txt and .md files.
2. The prompt template, which defines how the model should summarize.
3. The local LLM client, which sends the prompt to Ollama.

Logging strategy:
- Logs summarization flow using operational metadata.
- Logs filename, document length, prompt length and summary length.
- Does not log full document content, full prompt or generated summary
  to avoid exposing private information.
"""

import logging

from app.config import BASE_DIR
from app.services.document_loader import read_document
from app.services.llm_client import generate_text


logger = logging.getLogger(__name__)


PROMPT_PATH = BASE_DIR / "app" / "prompts" / "summarize_prompt.txt"


class SummarizerError(Exception):
    """
    Custom exception for errors related to document summarization.

    This exception is raised when the prompt template cannot be found,
    when a document cannot be read, or when the local LLM cannot generate
    a valid summary.
    """

    pass


def load_summary_prompt_template() -> str:
    """
    Loads the summary prompt template from the prompts folder.

    Returns:
        The summary prompt template as a string.

    Raises:
        SummarizerError: If the prompt template file does not exist.
    """
    logger.info("Loading summary prompt template. path=%s", PROMPT_PATH)

    if not PROMPT_PATH.exists():
        logger.error("Summary prompt template not found. path=%s", PROMPT_PATH)
        raise SummarizerError(f"Summary prompt template not found: {PROMPT_PATH}")

    template = PROMPT_PATH.read_text(encoding="utf-8")

    logger.info(
        "Summary prompt template loaded successfully. template_length=%s",
        len(template),
    )

    return template


def build_summary_prompt(document_content: str) -> str:
    """
    Builds the final prompt used to summarize a document.

    Args:
        document_content: The full content of the document to summarize.

    Returns:
        A complete prompt with the document content injected into the template.

    Raises:
        SummarizerError: If the document content is empty.
    """
    if not document_content or not document_content.strip():
        logger.warning("Summary prompt build skipped because document content is empty.")
        raise SummarizerError("Document content cannot be empty.")

    logger.info(
        "Building summary prompt. document_length=%s",
        len(document_content),
    )

    template = load_summary_prompt_template()
    prompt = template.replace("{document_content}", document_content)

    logger.info(
        "Summary prompt built successfully. prompt_length=%s",
        len(prompt),
    )

    return prompt


def summarize_document(filename: str) -> str:
    """
    Summarizes a supported local document using the configured local LLM.

    Args:
        filename: The name of the document located in the data/input folder.

    Returns:
        The summary generated by the local LLM.

    Raises:
        FileNotFoundError: If the requested document does not exist.
        ValueError: If the requested document has an unsupported extension.
        SummarizerError: If the prompt cannot be built or the local LLM fails.
    """
    logger.info("Document summarization started. filename=%s", filename)

    try:
        document_content = read_document(filename)

        logger.info(
            "Document loaded for summarization. filename=%s document_length=%s",
            filename,
            len(document_content),
        )

        prompt = build_summary_prompt(document_content)
        summary = generate_text(prompt)

    except FileNotFoundError:
        logger.warning(
            "Document summarization failed because file was not found. filename=%s",
            filename,
        )
        raise

    except ValueError:
        logger.warning(
            "Document summarization failed because file extension is unsupported. filename=%s",
            filename,
        )
        raise

    except Exception as error:
        logger.error(
            "Document summarization failed due to internal error. filename=%s error=%s",
            filename,
            error,
        )
        raise SummarizerError(f"Error summarizing document '{filename}': {error}") from error

    logger.info(
        "Document summarization finished successfully. filename=%s summary_length=%s",
        filename,
        len(summary),
    )

    return summary
Qué agregamos
Este archivo ahora deja trazas como:

Document summarization started
Document loaded for summarization
Building summary prompt
Loading summary prompt template
Summary prompt built successfully
Local LLM response received
Document summarization finished successfully
Recuerda que Local LLM response received viene desde llm_client.py, no desde summarizer.py.

Probar este paso
Levanta la API:

uvicorn app.main:app --reload
Abre:

http://localhost:8000/docs
Ejecuta:

POST /summarize
Con body:

{
  "filename": "demo.md"
}
Luego revisa el log:

Get-Content .\logs\app.log -Tail 100
Deberías ver algo parecido a:

INFO | app.services.summarizer | Document summarization started. filename=demo.md
INFO | app.services.document_loader | Reading document requested. filename=demo.md
INFO | app.services.document_loader | Document read completed. filename=demo.md size_chars=...
INFO | app.services.summarizer | Document loaded for summarization. filename=demo.md document_length=...
INFO | app.services.summarizer | Building summary prompt. document_length=...
INFO | app.services.summarizer | Loading summary prompt template. path=...
INFO | app.services.summarizer | Summary prompt template loaded successfully. template_length=...
INFO | app.services.summarizer | Summary prompt built successfully. prompt_length=...
INFO | app.services.llm_client | Sending prompt to local LLM. model=qwen3.5:4b endpoint=http://localhost:11434/api/generate prompt_length=...
INFO | app.services.llm_client | Local LLM response received. model=qwen3.5:4b response_length=...
INFO | app.services.summarizer | Document summarization finished successfully. filename=demo.md summary_length=...
Prueba de error recomendada
Prueba también con:

{
  "filename": "no_existe.md"
}
Deberías ver un warning en logs:

WARNING | app.services.summarizer | Document summarization failed because file was not found. filename=no_existe.md
Qué logramos hasta ahora en logging
Ya tienes trazabilidad en:

document_loader.py
simple_search.py
llm_client.py
summarizer.py
Después de este paso, nos faltaría cerrar con:

Paso 8 — Probar logs end-to-end
Paso 9 — Actualizar versión, README y commit/tag v0.2.1

Quiero agregar una linea "------------------------------------------------------------------------------------------------" entre cada ejecucion, para que el log me quede como en la imagen. Antes de pasar al siguiente paso, hagamos este ajuste 

Sí, hagamos ese ajuste antes de seguir. La forma más limpia es agregar una función centralizada en logging_config.py y luego llamarla automáticamente al inicio de cada request usando un middleware de FastAPI.

Así cada vez que ejecutes un endpoint como /documents, /search o /summarize, el log quedará separado por una línea como:

------------------------------------------------------------------------------------------------
Paso A — Actualizar app/logging_config.py
Abre:

app/logging_config.py
Y deja el archivo así:

"""
Application logging configuration module.

This module centralizes the logging configuration for Private Doc Agent.

It configures logs to be written both to the console and to a local file.
The goal is to make the application easier to debug and observe while
keeping logging behavior consistent across all services.

Logging strategy:
- Logs are written to console and to logs/app.log.
- Log files rotate automatically to avoid unlimited growth.
- A separator line can be written between API executions to improve readability.
"""

import logging
from logging.handlers import RotatingFileHandler

from app.config import BASE_DIR


# Directory where local log files will be stored.
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

# Visual separator used to identify different API executions in the log file.
LOG_SEPARATOR = "-" * 96


def setup_logging() -> None:
    """
    Configures application-wide logging.

    The configuration includes:
    - Console logging for development visibility.
    - Rotating file logging to avoid unlimited log growth.
    - A consistent log format with timestamp, level, logger name and message.

    This function should be called once when the FastAPI application starts.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers when Uvicorn reloads the application.
    if root_logger.handlers:
        return

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def log_execution_separator(logger_name: str = "app.execution") -> None:
    """
    Writes a visual separator line to the application logs.

    This function is useful to visually separate different API executions
    when reviewing logs during local development or debugging.

    Args:
        logger_name: Name of the logger that will write the separator.
    """
    logger = logging.getLogger(logger_name)
    logger.info(LOG_SEPARATOR)
Paso B — Actualizar app/main.py
Ahora vamos a agregar un middleware para que esa línea se escriba automáticamente en cada ejecución de un endpoint.

En main.py, asegúrate de tener este import:

from app.logging_config import setup_logging, log_execution_separator
Si actualmente tienes:

from app.logging_config import setup_logging
cámbialo por:

from app.logging_config import setup_logging, log_execution_separator
Luego, después de crear la app:

app = FastAPI(
    title="Private Doc Agent",
    description="Local-first assistant for private document analysis.",
    version=APP_VERSION,
)
agrega este bloque:

@app.middleware("http")
async def add_log_separator(request, call_next):
    """
    Adds a visual separator line before each HTTP request execution.

    This middleware improves log readability by separating each API call
    in the console and log file.
    """
    log_execution_separator()

    response = await call_next(request)

    return response
Cómo debería quedar la parte inicial de main.py
La parte superior debería verse más o menos así:

"""
FastAPI application entry point.

This module defines the HTTP API for Private Doc Agent.

Current capabilities:
1. Health check endpoint.
2. Local document listing.
3. Local document content retrieval.
4. Simple keyword search across .txt and .md files.
5. Local LLM-powered document summarization.
6. Application logging for traceability and debugging.
"""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import APP_NAME, APP_VERSION, OLLAMA_MODEL
from app.logging_config import setup_logging, log_execution_separator
from app.services.document_loader import list_documents, read_document
from app.services.simple_search import search_keyword
from app.services.summarizer import summarize_document, SummarizerError


setup_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Private Doc Agent",
    description="Local-first assistant for private document analysis.",
    version=APP_VERSION,
)


@app.middleware("http")
async def add_log_separator(request, call_next):
    """
    Adds a visual separator line before each HTTP request execution.

    This middleware improves log readability by separating each API call
    in the console and log file.
    """
    log_execution_separator()

    response = await call_next(request)

    return response
Resultado esperado en logs/app.log
Después de ejecutar varios endpoints, deberías ver algo así:

2026-07-16 23:36:42,160 | INFO | app.execution | ------------------------------------------------------------------------------------------------
2026-07-16 23:36:42,160 | INFO | app.main | Summarization requested. filename=demo.md model=qwen3.5:4b
2026-07-16 23:36:42,162 | INFO | app.services.summarizer | Document summarization started. filename=demo.md
2026-07-16 23:36:42,164 | INFO | app.services.document_loader | Reading document requested. filename=demo.md
2026-07-16 23:36:42,165 | INFO | app.services.document_loader | Document read completed. filename=demo.md size_chars=...
2026-07-16 23:36:42,179 | INFO | app.services.llm_client | Sending prompt to local LLM. model=qwen3.5:4b endpoint=http://localhost:11434/api/generate prompt_length=...
2026-07-16 23:37:19,640 | INFO | app.services.llm_client | Local LLM response received. model=qwen3.5:4b response_length=...
2026-07-16 23:37:19,642 | INFO | app.main | Summarization completed successfully. filename=demo.md summary_length=...
Prueba
Levanta el servicio:

uvicorn app.main:app --reload
Ejecuta en Swagger:

http://localhost:8000/docs
Prueba:

GET /health
GET /documents
POST /search
POST /summarize
Luego revisa:

Get-Content .\logs\app.log -Tail 80
Nota importante
Con este enfoque la línea se agregará antes de cada request HTTP.

Eso incluye también llamadas automáticas del navegador a:

/docs
/openapi.json
/favicon.ico
Si ves muchas separaciones al abrir Swagger, es normal.

Si quieres que la separación solo aparezca para tus endpoints funcionales y no para Swagger, podemos ajustar el middleware así:

@app.middleware("http")
async def add_log_separator(request, call_next):
    """
    Adds a visual separator line before selected HTTP request executions.

    This middleware skips technical documentation endpoints to avoid
    unnecessary separators when using Swagger UI.
    """
    ignored_paths = {"/docs", "/openapi.json", "/favicon.ico"}

    if request.url.path not in ignored_paths:
        log_execution_separator()

    response = await call_next(request)

    return response
Yo usaría esta segunda versión para que el log quede más limpio.


Solo un detalle, como ves en la imagen, no hace un salto de linea para el separador, deberia quedar en una linea independiente. Hacemos este pequeno ajuste antes de retomar

Sí, hagamos el ajuste. Lo que está pasando es que el separador se está escribiendo como un mensaje normal del logger, por eso queda así:

2026-07-16 ... | INFO | app.execution | ------------------------------------------------------------------------------------------------
Para que visualmente quede en una línea independiente, podemos anteponer un salto de línea dentro del mensaje.

Ajuste en app/logging_config.py
Busca esta función:

def log_execution_separator(logger_name: str = "app.execution") -> None:
    """
    Writes a visual separator line to the application logs.

    This function is useful to visually separate different API executions
    when reviewing logs during local development or debugging.

    Args:
        logger_name: Name of the logger that will write the separator.
    """
    logger = logging.getLogger(logger_name)
    logger.info(LOG_SEPARATOR)
Reemplázala por esta versión:

def log_execution_separator(logger_name: str = "app.execution") -> None:
    """
    Writes a visual separator line to the application logs.

    This function is useful to visually separate different API executions
    when reviewing logs during local development or debugging.

    The separator starts with a newline so the visual line appears clearly
    separated from the previous log entry.

    Args:
        logger_name: Name of the logger that will write the separator.
    """
    logger = logging.getLogger(logger_name)
    logger.info("\n%s", LOG_SEPARATOR)
Resultado esperado
Ahora deberías ver algo más parecido a esto:

2026-07-16 23:57:18,277 | INFO | app.main | Summarization completed successfully. filename=demo.md summary_length=...

2026-07-16 23:58:24,763 | INFO | app.execution | 
------------------------------------------------------------------------------------------------
2026-07-16 23:58:24,767 | INFO | app.main | Summarization requested. filename=demo.md model=qwen3.5:4b
2026-07-16 23:58:24,770 | INFO | app.services.summarizer | Document summarization started. filename=demo.md
Si quieres que además quede una línea en blanco después del separador, puedes usar esta variante:

logger.info("\n%s\n", LOG_SEPARATOR)
Pero yo usaría primero:

logger.info("\n%s", LOG_SEPARATOR)
porque deja más limpio el bloque.

Prueba rápida
Reinicia Uvicorn:

uvicorn app.main:app --reload
Ejecuta otra vez /summarize y revisa:

Get-Content .\logs\app.log -Tail 40
Con eso dejamos el separador más legible antes de retomar el siguiente paso.


continuemos

Perfecto. Ya con el separador ajustado, retomamos el flujo.

Venimos de:

Paso 4 — Logs en document_loader.py
Paso 5 — Logs en simple_search.py
Paso 6 — Logs en llm_client.py
Paso 7 — Logs en summarizer.py
Ajuste adicional — Separador visual entre ejecuciones
Ahora seguimos con:

Paso 8 — Probar logs end-to-end
La idea de este paso es validar que todo el flujo quede trazado correctamente desde la API hasta los servicios internos.

Paso 8 — Probar logs end-to-end
1. Reinicia el servicio
Detén Uvicorn si está corriendo:

Ctrl + C
Luego vuelve a levantarlo:

cd C:\Proyectos\private-doc-agent
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
Abre Swagger:

http://localhost:8000/docs
2. Prueba /health
Ejecuta:

GET /health
Luego revisa el log:

Get-Content .\logs\app.log -Tail 30
Deberías ver algo parecido a:

------------------------------------------------------------------------------------------------
2026-07-16 23:58:24,767 | INFO | app.main | Health check requested.
3. Prueba /documents
Ejecuta:

GET /documents
Log esperado:

------------------------------------------------------------------------------------------------
INFO | app.main | Listing available documents.
INFO | app.services.document_loader | Scanning input directory for supported documents...
INFO | app.services.document_loader | Supported document found. filename=demo.txt...
INFO | app.services.document_loader | Supported document found. filename=demo.md...
INFO | app.services.document_loader | Document scan completed. count=2
INFO | app.main | Documents listed successfully. count=2
4. Prueba /documents/{filename}
Ejecuta:

GET /documents/demo.md
Log esperado:

------------------------------------------------------------------------------------------------
INFO | app.main | Document content requested. filename=demo.md
INFO | app.services.document_loader | Reading document requested. filename=demo.md
INFO | app.services.document_loader | Document read completed. filename=demo.md size_chars=...
INFO | app.main | Document read successfully. filename=demo.md
5. Prueba /search
Ejecuta:

POST /search
Body:

{
  "query": "RAG"
}
Log esperado:

------------------------------------------------------------------------------------------------
INFO | app.main | Search requested. query=RAG
INFO | app.services.simple_search | Keyword search requested. query=RAG
INFO | app.services.document_loader | Scanning input directory for supported documents...
INFO | app.services.simple_search | Keyword search started. query=RAG documents_to_scan=2
INFO | app.services.simple_search | Scanning document for keyword. filename=demo.txt
INFO | app.services.document_loader | Reading document requested. filename=demo.txt
INFO | app.services.document_loader | Document read completed. filename=demo.txt size_chars=...
INFO | app.services.simple_search | Scanning document for keyword. filename=demo.md
INFO | app.services.document_loader | Reading document requested. filename=demo.md
INFO | app.services.document_loader | Document read completed. filename=demo.md size_chars=...
INFO | app.services.simple_search | Keyword search completed. query=RAG matches=...
INFO | app.main | Search completed. query=RAG matches=...
6. Prueba /summarize
Ejecuta:

POST /summarize
Body:

{
  "filename": "demo.md"
}
Log esperado:

------------------------------------------------------------------------------------------------
INFO | app.main | Summarization requested. filename=demo.md model=qwen3.5:4b
INFO | app.services.summarizer | Document summarization started. filename=demo.md
INFO | app.services.document_loader | Reading document requested. filename=demo.md
INFO | app.services.document_loader | Document read completed. filename=demo.md size_chars=...
INFO | app.services.summarizer | Document loaded for summarization. filename=demo.md document_length=...
INFO | app.services.summarizer | Building summary prompt. document_length=...
INFO | app.services.summarizer | Loading summary prompt template. path=...
INFO | app.services.summarizer | Summary prompt template loaded successfully. template_length=...
INFO | app.services.summarizer | Summary prompt built successfully. prompt_length=...
INFO | app.services.llm_client | Sending prompt to local LLM. model=qwen3.5:4b endpoint=http://localhost:11434/api/generate prompt_length=...
INFO | app.services.llm_client | Local LLM response received. model=qwen3.5:4b response_length=...
INFO | app.services.summarizer | Document summarization finished successfully. filename=demo.md summary_length=...
INFO | app.main | Summarization completed successfully. filename=demo.md summary_length=...
7. Pruebas de error
Documento inexistente
Prueba:

{
  "filename": "no_existe.md"
}
En /summarize.

Log esperado:

WARNING | app.services.document_loader | Document not found. filename=no_existe.md...
WARNING | app.services.summarizer | Document summarization failed because file was not found. filename=no_existe.md
WARNING | app.main | Summarization failed. Document not found. filename=no_existe.md...
Query vacío
Prueba en /search:

{
  "query": ""
}
Log esperado:

WARNING | app.services.simple_search | Keyword search skipped because query is empty.
INFO | app.main | Search completed. query= matches=0
8. Ver log en vivo
También puedes dejar una terminal abierta viendo el log en tiempo real:

Get-Content .\logs\app.log -Wait
Luego desde Swagger vas ejecutando endpoints y ves el rastro en vivo.

Criterio de aceptación del Paso 8
Este paso queda listo si puedes confirmar:

1. logs/app.log se crea automáticamente.
2. Cada request queda separado con una línea visual.
3. /health registra su ejecución.
4. /documents registra listado y cantidad.
5. /documents/{filename} registra lectura correcta.
6. /search registra query, documentos escaneados y matches.
7. /summarize registra flujo completo hasta Ollama.
8. Los errores generan WARNING o ERROR según corresponda.
9. No se registra contenido completo de documentos, prompts o respuestas.
Siguiente paso
Cuando confirmes que el log se ve bien, cerramos con:

Paso 9 — Actualizar versión, README y preparar commit/tag v0.2.1
Ahí actualizamos:

APP_VERSION = "0.2.1"
README.md
docs/roadmap.md
commit
tag
Y dejamos esta mejora cerrada antes de pasar a RAG.


Vamos al paso 9

Perfecto. Vamos con el Paso 9 — Actualizar versión, README y preparar commit/tag v0.2.1.

Esta versión no agrega una nueva capacidad de IA, sino una mejora técnica importante:

v0.2.1 - Application Logging
1. Actualizar versión en app/config.py
Abre:

app/config.py
Busca:

APP_VERSION = "0.2.0"
Cámbialo por:

APP_VERSION = "0.2.1"
Debe quedar así:

# Application metadata
APP_NAME = "private-doc-agent"
APP_VERSION = "0.2.1"
2. Actualizar README.md
Te dejo una sección lista para agregar al README.

Busca la parte:

## Current Version
y déjala así:

## Current Version

v0.2.1
Luego, en Current Features, agrega estas capacidades:

- Centralized application logging.
- Console and rotating file logging.
- Request-level log separator for better traceability.
- Privacy-aware logs that avoid storing document content, full prompts or generated responses.
3. Agregar sección de logging al README
Puedes agregar esta sección después de AI Layer Introduced o después de Run the API.

## Application Logging

Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

Logs are written to:

```text
logs/app.log
The application also writes logs to the console while running with Uvicorn.

Logging capabilities
Logs API request flow.

Logs document listing and document reading events.

Logs keyword search execution.

Logs local LLM calls through Ollama.

Logs document summarization flow.

Adds a visual separator between API executions.

Uses rotating log files to avoid unlimited log growth.

Privacy-aware logging
The application intentionally avoids logging sensitive content.

The logs may include:

- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages
The logs should not include:

- full document content
- full prompt content
- full generated summary
- private document data
View logs
To view the latest log entries:

Get-Content .\logs\app.log -Tail 80
To watch logs in real time:

Get-Content .\logs\app.log -Wait

Ojo: si lo pegas en Markdown, cuida los bloques de código anidados. Si VS Code se confunde, te recomiendo usar esta versión más simple:

```md
## Application Logging

Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

Logs are written to `logs/app.log` and also displayed in the console while running with Uvicorn.

Logging capabilities:

- Logs API request flow.
- Logs document listing and document reading events.
- Logs keyword search execution.
- Logs local LLM calls through Ollama.
- Logs document summarization flow.
- Adds a visual separator between API executions.
- Uses rotating log files to avoid unlimited log growth.

Privacy-aware logging:

The application may log metadata such as endpoint execution, filename, model name, document size, prompt length, response length, number of search matches and error messages.

The application should not log full document content, full prompts, full generated summaries or private document data.

View latest logs:

```powershell
Get-Content .\logs\app.log -Tail 80
Watch logs in real time:

Get-Content .\logs\app.log -Wait

---

## 4. Agregar `v0.2.1` en Version History

En el README, dentro de:

```md
## Version History
agrega esta nueva sección después de v0.2.0:

### v0.2.1 - Application Logging

This version adds centralized application logging and traceability across the project.

Features introduced:

- Centralized logging configuration.
- Console logging.
- Rotating file logging under `logs/app.log`.
- Request-level visual separator.
- Logging across API endpoints and services.
- Traceability for document loading, keyword search, local LLM calls and summarization.
- Privacy-aware logging that avoids storing full document content, prompts or generated summaries.

AI status:

```text
No new AI capability introduced.
This version improves observability and debugging for the local LLM summarization flow.

---

## 5. Actualizar `docs/roadmap.md`

Abre:

```text
docs/roadmap.md
Agrega una sección después de v0.2.0:

## v0.2.1 - Application Logging

- Add centralized logging configuration.
- Add console logging.
- Add rotating file logging under `logs/app.log`.
- Add visual separator between API executions.
- Add logs to document loading service.
- Add logs to keyword search service.
- Add logs to local LLM client.
- Add logs to summarization service.
- Avoid logging private document content, full prompts or generated summaries.
Y si tienes una sección de roadmap futuro, mantenla así:

## v0.3.0 - Basic RAG

- Split documents into chunks.
- Generate local embeddings.
- Store vectors in ChromaDB.
- Retrieve relevant chunks based on a user question.
- Answer questions using retrieved context.
- Return sources.
6. Validar .gitignore
Verifica que tu .gitignore tenga estas líneas:

.env
logs/
*.log
Esto es importante para que no subas:

.env
logs/app.log
a GitHub.

7. Verificar estado antes del commit
Ejecuta:

git status
Debes revisar que aparezcan archivos como:

app/config.py
app/logging_config.py
app/main.py
app/services/document_loader.py
app/services/simple_search.py
app/services/llm_client.py
app/services/summarizer.py
README.md
docs/roadmap.md
.gitignore
Y que no aparezca:

.env
logs/app.log
Si aparece .env, dime antes de hacer commit.

Si aparece logs/app.log, ejecuta:

git restore --staged logs/app.log
y asegúrate de que logs/ esté en .gitignore.

8. Hacer commit
Como todavía no habías hecho commit de la v0.2.0, tienes dos opciones.

Mi recomendación ahora es dejar un solo commit con todo lo trabajado:

git add .
git commit -m "feat: add local LLM summarization with logging"
Ese commit incluye:

- Local LLM summarization
- Ollama integration
- Prompt template
- Summarizer service
- Logging and traceability
Si quieres separar más profesionalmente, puedes hacer dos commits, pero como ya están todos los cambios juntos en tu working tree, un solo commit está bien para este proyecto de aprendizaje.

9. Subir la rama
Estando en tu rama:

git branch
Si estás en:

feature/local-llm-summarization
sube la rama:

git push origin feature/local-llm-summarization
10. Merge a main
Luego:

git checkout main
git pull origin main
git merge feature/local-llm-summarization
git push origin main
11. Crear tag v0.2.1
Como el cierre real incluye logging, etiqueta como v0.2.1:

git tag v0.2.1
git push origin v0.2.1
12. Cerrar rama local y remota
Cuando ya esté todo en main:

git branch -d feature/local-llm-summarization
Y borrar la rama remota:

git push origin --delete feature/local-llm-summarization
13. Validación final
Ejecuta:

git status
Resultado esperado:

On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
Valida tags:

git tag
Deberías ver:

v0.2.1
Resumen de la versión
Para describir esta versión en GitHub:

v0.2.1 adds local LLM document summarization through Ollama and introduces centralized privacy-aware logging across the API and services. The project can now summarize local .txt and .md documents using a local model while providing traceability for document loading, keyword search, LLM calls and summarization flow.
Con esto cerramos muy bien la base antes de pasar a v0.3.0, donde ya entraríamos a RAG básico.


Te comparto la version actual del readme.md, para que generes la version corregida con lo que falta: # private-doc-agent

Private Doc Agent is a local-first AI assistant designed to analyze and interact with private documents.

The project is being built incrementally, starting from deterministic document loading and keyword search, and evolving toward a private AI-powered document agent with local LLM support, RAG, tools, MCP, and multi-agent validation.

## Current Version

v0.2.1

## What it does now

Private Doc Agent currently provides a FastAPI backend that can read local .txt and .md documents, list available files, retrieve document content, search keywords across documents, and summarize documents using a locally running LLM through Ollama.

The current version introduces the first AI-powered capability: local document summarization.

The document content is processed locally and sent to a local model served by Ollama. This keeps the project aligned with a local-first and privacy-oriented architecture.

## Current Features

* FastAPI backend.
* Health check endpoint.
* Local document listing.
* Support for .txt and .md files.
* Document content retrieval.
* Simple keyword search across supported documents.
* Local LLM integration through Ollama.
* Configurable model using environment variables.
* Prompt template for document summarization.
* Document summarization endpoint.
* Centralized application logging.
* Console and rotating file logging.
* Request-level log separator for better traceability.
* Privacy-aware logs that avoid storing document content, full prompts or generated responses.

## AI Layer Introduced

In version v0.2.0, the project introduces a local LLM-based generation layer.

Current AI flow:

text
Local document
  -> document loader
  -> prompt template
  -> local LLM client
  -> Ollama
  -> local generative model
  -> generated summary


At this stage, this is not RAG yet. The application sends the full document content to the local LLM as context.

RAG will be introduced in a future version using chunking, embeddings, vector storage, and context retrieval.

## Project Structure

text
private-doc-agent/
  app/
    __init__.py
    main.py
    config.py
    prompts/
      summarize_prompt.txt
    services/
      __init__.py
      document_loader.py
      simple_search.py
      llm_client.py
      summarizer.py
  data/
    input/
      demo.txt
      demo.md
    processed/
  docs/
    roadmap.md
  tests/
  README.md
  requirements.txt
  .env.example
  .gitignore


## Requirements

* Python 3.11+
* FastAPI
* Uvicorn
* Pydantic
* python-dotenv
* requests
* Ollama installed and running locally

## Setup

Clone the repository:

bash
git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent


Create a virtual environment:

bash
python -m venv .venv


Activate it on Windows PowerShell:

powershell
.\.venv\Scripts\Activate.ps1


Install dependencies:

bash
pip install -r requirements.txt


## Environment Variables

Create a .env file in the project root based on .env.example.

Example:

env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b


The .env file should not be committed to GitHub.

The .env.example file should be committed to document the required configuration.

## Ollama Setup

Make sure Ollama is running locally.

Validate Ollama:

powershell
Invoke-WebRequest -UseBasicParsing http://localhost:11434


Expected response:

text
Ollama is running


List installed models:

powershell
ollama list


Example model used in this project:

text
qwen3.5:4b


If needed, update .env with the model available in your local environment.

## Run the API

Start the FastAPI server:

bash
uvicorn app.main:app --reload


Open the interactive API documentation:

text
http://localhost:8000/docs


## Application Logging

Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

Logs are written to:

text
logs/app.log

## API Endpoints

### Health Check
http
GET /health
Expected response:
json
{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.2.0"
}
### List Documents
http
GET /documents
Returns all supported documents from `data/input`.

### Read Document
http
GET /documents/{filename}
Examples:
http
GET /documents/demo.txt
GET /documents/demo.md
### Search Documents
http
POST /search
Request body:
json
{
  "query": "RAG"
}
Expected response structure:
json
{
  "query": "RAG",
  "matches": [
    {
      "filename": "demo.md",
      "line_number": 10,
      "line": "- Build a RAG pipeline"
    }
  ],
  "count": 1
}
### Summarize Document
http
POST /summarize
Request body:
json
{
  "filename": "demo.md"
}
Expected response structure:
json
{
  "filename": "demo.md",
  "summary": "The document explains...",
  "model": "qwen3.5:4b",
  "version": "0.2.0"
}
## Testing the LLM Client

You can test the local LLM client directly from PowerShell:
powershell
python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
Expected result:
text
An artificial intelligence tool that processes and organizes your files entirely on your local device rather than in the cloud for privacy.
The exact response may vary depending on the model.

## Testing Document Summarization

You can test summarization directly from Python:
powershell
python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.md'))"
## Version History

### v0.1.0 - Basic Local Document Search

Initial version focused on deterministic document handling without AI.

Features introduced:

* FastAPI application structure.
* Health check endpoint.
* Local document discovery.
* Support for `.txt` and `.md` files.
* Document content retrieval.
* Case-insensitive keyword search across local documents.

AI status:
text
No AI capabilities yet.
This version establishes the document ingestion and search foundation.
### v0.2.0 - Local LLM Document Summarization

This version introduces the first AI-powered capability.

Features introduced:

* Local LLM integration through Ollama.
* Configurable Ollama base URL and model through `.env`.
* Local LLM client service.
* Prompt template for summarization.
* Document summarization service.
* `POST /summarize` endpoint.
* Improved separation between document loading, search, LLM communication, and summarization logic.

AI status:
text
Local document content
  -> controlled prompt
  -> local LLM
  -> generated summary
This version is still not RAG. The full document is passed as context to the local model.

## Roadmap

### v0.3.0 - Basic RAG

Planned capabilities:

* Split documents into chunks.
* Generate local embeddings.
* Store vectors in ChromaDB.
* Retrieve relevant chunks based on a user question.
* Answer questions using retrieved context.
* Return sources used to generate the answer.

### v0.4.0 - Tool-Based Agent

Planned capabilities:

* Add document tools such as search, summarize, and ask.
* Create a simple agent router.
* Allow the system to decide which tool to use based on user intent.

### v0.5.0 - Auditor Agent

Planned capabilities:

* Add a second validation layer.
* Review answers for unsupported claims.
* Check whether the response is grounded in document evidence.
* Add confidence levels.

### v0.6.0 - MCP Server

Planned capabilities:

* Expose document tools through MCP.
* Allow external clients or agents to call document-related tools using a standard protocol.

## Design Principles

* Local-first execution.
* Privacy-oriented architecture.
* Incremental learning by layers.
* Clear separation of responsibilities.
* Documented code.
* No external LLM dependency for private document processing.
* Build deterministic capabilities before adding agentic behavior.

## Current Limitations

* Only `.txt` and `.md` files are supported.
* Summarization sends the full document content to the local model.
* Large documents may exceed the model context window.
* No chunking yet.
* No embeddings yet.
* No vector database yet.
* No RAG yet.
* No agent or MCP support yet.
* No frontend yet.

## Suggested Commit for v0.2.0
bash
git add .
git commit -m "feat: add local LLM document summarization"
git push origin feature/local-llm-summarization
After merging into `main`, the suggested tag is:
bash
git tag v0.2.0
git push origin v0.2.0

Sí. Tu README está bien encaminado, pero tiene algunos puntos a corregir:

En Application Logging quedó un bloque de código abierto y por eso se “rompe” el Markdown.

En respuestas de ejemplo todavía aparece version: "0.2.0" y debería ser 0.2.1.

Falta incluir app/logging_config.py en la estructura del proyecto.

Falta documentar bien v0.2.1 en el historial.

El commit sugerido debe actualizarse a la versión actual.

Conviene dejar claro que logs/app.log se genera localmente y no debe subirse.

Te dejo una versión corregida completa para que reemplaces tu README.md.

# private-doc-agent

Private Doc Agent is a local-first AI assistant designed to analyze and interact with private documents.

The project is being built incrementally, starting from deterministic document loading and keyword search, and evolving toward a private AI-powered document agent with local LLM support, RAG, tools, MCP, and multi-agent validation.

## Current Version

v0.2.1

## What it does now

Private Doc Agent currently provides a FastAPI backend that can read local `.txt` and `.md` documents, list available files, retrieve document content, search keywords across documents, and summarize documents using a locally running LLM through Ollama.

The current version includes the first AI-powered capability: local document summarization.

The document content is processed locally and sent to a local model served by Ollama. This keeps the project aligned with a local-first and privacy-oriented architecture.

This version also adds centralized application logging to improve traceability and debugging across the API and internal services.

## Current Features

- FastAPI backend.
- Health check endpoint.
- Local document listing.
- Support for `.txt` and `.md` files.
- Document content retrieval.
- Simple keyword search across supported documents.
- Local LLM integration through Ollama.
- Configurable model using environment variables.
- Prompt template for document summarization.
- Document summarization endpoint.
- Centralized application logging.
- Console and rotating file logging.
- Request-level log separator for better traceability.
- Privacy-aware logs that avoid storing document content, full prompts or generated responses.

## AI Layer Introduced

In version `v0.2.0`, the project introduced a local LLM-based generation layer.

Current AI flow:

```text
Local document
  -> document loader
  -> prompt template
  -> local LLM client
  -> Ollama
  -> local generative model
  -> generated summary
At this stage, this is not RAG yet. The application sends the full document content to the local LLM as context.

RAG will be introduced in a future version using chunking, embeddings, vector storage, and context retrieval.

Project Structure
private-doc-agent/
  app/
    __init__.py
    main.py
    config.py
    logging_config.py
    prompts/
      summarize_prompt.txt
    services/
      __init__.py
      document_loader.py
      simple_search.py
      llm_client.py
      summarizer.py
  data/
    input/
      demo.txt
      demo.md
    processed/
  docs/
    roadmap.md
  logs/
    app.log
  tests/
  README.md
  requirements.txt
  .env.example
  .gitignore
Note: logs/app.log is generated locally and should not be committed to GitHub.

Requirements
Python 3.11+

FastAPI

Uvicorn

Pydantic

python-dotenv

requests

Ollama installed and running locally

Setup
Clone the repository:

git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
Create a virtual environment:

python -m venv .venv
Activate it on Windows PowerShell:

.\.venv\Scripts\Activate.ps1
Install dependencies:

pip install -r requirements.txt
Environment Variables
Create a .env file in the project root based on .env.example.

Example:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
The .env file should not be committed to GitHub.

The .env.example file should be committed to document the required configuration.

Ollama Setup
Make sure Ollama is running locally.

Validate Ollama:

Invoke-WebRequest -UseBasicParsing http://localhost:11434
Expected response:

Ollama is running
List installed models:

ollama list
Example model used in this project:

qwen3.5:4b
If needed, update .env with the model available in your local environment.

Run the API
Start the FastAPI server:

uvicorn app.main:app --reload
Open the interactive API documentation:

http://localhost:8000/docs
Application Logging
Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

Logs are written to:

logs/app.log
The application also writes logs to the console while running with Uvicorn.

Logging capabilities
Logs API request flow.

Logs document listing and document reading events.

Logs keyword search execution.

Logs local LLM calls through Ollama.

Logs document summarization flow.

Adds a visual separator between API executions.

Uses rotating log files to avoid unlimited log growth.

Privacy-aware logging
The application intentionally avoids logging sensitive content.

The logs may include:

- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages
The logs should not include:

- full document content
- full prompt content
- full generated summary
- private document data
View logs
To view the latest log entries:

Get-Content .\logs\app.log -Tail 80
To watch logs in real time:

Get-Content .\logs\app.log -Wait
API Endpoints
Health Check
GET /health
Expected response:

{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.2.1"
}
List Documents
GET /documents
Returns all supported documents from data/input.

Read Document
GET /documents/{filename}
Examples:

GET /documents/demo.txt
GET /documents/demo.md
Search Documents
POST /search
Request body:

{
  "query": "RAG"
}
Expected response structure:

{
  "query": "RAG",
  "matches": [
    {
      "filename": "demo.md",
      "line_number": 10,
      "line": "- Build a RAG pipeline"
    }
  ],
  "count": 1
}
Summarize Document
POST /summarize
Request body:

{
  "filename": "demo.md"
}
Expected response structure:

{
  "filename": "demo.md",
  "summary": "The document explains...",
  "model": "qwen3.5:4b",
  "version": "0.2.1"
}
Testing the LLM Client
You can test the local LLM client directly from PowerShell:

python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
Expected result:

An artificial intelligence tool that processes and organizes your files entirely on your local device rather than in the cloud for privacy.
The exact response may vary depending on the model.

Testing Document Summarization
You can test summarization directly from Python:

python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.md'))"
Version History
v0.1.0 - Basic Local Document Search
Initial version focused on deterministic document handling without AI.

Features introduced:

FastAPI application structure.

Health check endpoint.

Local document discovery.

Support for .txt and .md files.

Document content retrieval.

Case-insensitive keyword search across local documents.

AI status:

No AI capabilities yet.
This version establishes the document ingestion and search foundation.
v0.2.0 - Local LLM Document Summarization
This version introduced the first AI-powered capability.

Features introduced:

Local LLM integration through Ollama.

Configurable Ollama base URL and model through .env.

Local LLM client service.

Prompt template for summarization.

Document summarization service.

POST /summarize endpoint.

Improved separation between document loading, search, LLM communication, and summarization logic.

AI status:

Local document content
  -> controlled prompt
  -> local LLM
  -> generated summary
This version is still not RAG. The full document is passed as context to the local model.

v0.2.1 - Application Logging
This version adds centralized application logging and traceability across the project.

Features introduced:

Centralized logging configuration.

Console logging.

Rotating file logging under logs/app.log.

Request-level visual separator.

Logging across API endpoints and services.

Traceability for document loading, keyword search, local LLM calls and summarization.

Privacy-aware logging that avoids storing full document content, prompts or generated summaries.

AI status:

No new AI capability introduced.
This version improves observability and debugging for the local LLM summarization flow.
Roadmap
v0.3.0 - Basic RAG
Planned capabilities:

Split documents into chunks.

Generate local embeddings.

Store vectors in ChromaDB.

Retrieve relevant chunks based on a user question.

Answer questions using retrieved context.

Return sources used to generate the answer.

v0.4.0 - Tool-Based Agent
Planned capabilities:

Add document tools such as search, summarize, and ask.

Create a simple agent router.

Allow the system to decide which tool to use based on user intent.

v0.5.0 - Auditor Agent
Planned capabilities:

Add a second validation layer.

Review answers for unsupported claims.

Check whether the response is grounded in document evidence.

Add confidence levels.

v0.6.0 - MCP Server
Planned capabilities:

Expose document tools through MCP.

Allow external clients or agents to call document-related tools using a standard protocol.

Design Principles
Local-first execution.

Privacy-oriented architecture.

Incremental learning by layers.

Clear separation of responsibilities.

Documented code.

No external LLM dependency for private document processing.

Build deterministic capabilities before adding agentic behavior.

Current Limitations
Only .txt and .md files are supported.

Summarization sends the full document content to the local model.

Large documents may exceed the model context window.

No chunking yet.

No embeddings yet.

No vector database yet.

No RAG yet.

No agent or MCP support yet.

No frontend yet.

Suggested Commit for v0.2.1
git add .
git commit -m "feat: add local LLM summarization with logging"
git push origin feature/local-llm-summarization
After merging into main, the suggested tag is:

git tag v0.2.1
git push origin v0.2.1

Punto importante: antes del commit valida que tu `.gitignore` tenga esto:

```gitignore
.env
logs/
*.log
Así evitas subir .env y logs/app.log.


dame el readme.md descargable, en un archivo


Analizado
from pathlib import Path

readme_content = """# private-doc-agent

Private Doc Agent is a local-first AI assistant designed to analyze and interact with private documents.

The project is being built incrementally, starting from deterministic document loading and keyword search, and evolving toward a private AI-powered document agent with local LLM support, RAG, tools, MCP, and multi-agent validation.

## Current Version

v0.2.1

## What it does now

Private Doc Agent currently provides a FastAPI backend that can read local `.txt` and `.md` documents, list available files, retrieve document content, search keywords across documents, and summarize documents using a locally running LLM through Ollama.

The current version includes the first AI-powered capability: local document summarization.

The document content is processed locally and sent to a local model served by Ollama. This keeps the project aligned with a local-first and privacy-oriented architecture.

This version also adds centralized application logging to improve traceability and debugging across the API and internal services.

## Current Features

- FastAPI backend.
- Health check endpoint.
- Local document listing.
- Support for `.txt` and `.md` files.
- Document content retrieval.
- Simple keyword search across supported documents.
- Local LLM integration through Ollama.
- Configurable model using environment variables.
- Prompt template for document summarization.
- Document summarization endpoint.
- Centralized application logging.
- Console and rotating file logging.
- Request-level log separator for better traceability.
- Privacy-aware logs that avoid storing document content, full prompts or generated responses.

## AI Layer Introduced

In version `v0.2.0`, the project introduced a local LLM-based generation layer.

Current AI flow:

```text
Local document
  -> document loader
  -> prompt template
  -> local LLM client
  -> Ollama
  -> local generative model
  -> generated summary
At this stage, this is not RAG yet. The application sends the full document content to the local LLM as context.

RAG will be introduced in a future version using chunking, embeddings, vector storage, and context retrieval.

Project Structure
private-doc-agent/
  app/
    __init__.py
    main.py
    config.py
    logging_config.py
    prompts/
      summarize_prompt.txt
    services/
      __init__.py
      document_loader.py
      simple_search.py
      llm_client.py
      summarizer.py
  data/
    input/
      demo.txt
      demo.md
    processed/
  docs/
    roadmap.md
  logs/
    app.log
  tests/
  README.md
  requirements.txt
  .env.example
  .gitignore
Note: logs/app.log is generated locally and should not be committed to GitHub.

Requirements
Python 3.11+

FastAPI

Uvicorn

Pydantic

python-dotenv

requests

Ollama installed and running locally

Setup
Clone the repository:

git clone https://github.com/ajapontes/private-doc-agent.git
cd private-doc-agent
Create a virtual environment:

python -m venv .venv
Activate it on Windows PowerShell:

.\\.venv\\Scripts\\Activate.ps1
Install dependencies:

pip install -r requirements.txt
Environment Variables
Create a .env file in the project root based on .env.example.

Example:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:4b
The .env file should not be committed to GitHub.

The .env.example file should be committed to document the required configuration.

Ollama Setup
Make sure Ollama is running locally.

Validate Ollama:

Invoke-WebRequest -UseBasicParsing http://localhost:11434
Expected response:

Ollama is running
List installed models:

ollama list
Example model used in this project:

qwen3.5:4b
If needed, update .env with the model available in your local environment.

Run the API
Start the FastAPI server:

uvicorn app.main:app --reload
Open the interactive API documentation:

http://localhost:8000/docs
Application Logging
Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

Logs are written to:

logs/app.log
The application also writes logs to the console while running with Uvicorn.

Logging capabilities
Logs API request flow.

Logs document listing and document reading events.

Logs keyword search execution.

Logs local LLM calls through Ollama.

Logs document summarization flow.

Adds a visual separator between API executions.

Uses rotating log files to avoid unlimited log growth.

Privacy-aware logging
The application intentionally avoids logging sensitive content.

The logs may include:

- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages
The logs should not include:

- full document content
- full prompt content
- full generated summary
- private document data
View logs
To view the latest log entries:

Get-Content .\\logs\\app.log -Tail 80
To watch logs in real time:

Get-Content .\\logs\\app.log -Wait
API Endpoints
Health Check
GET /health
Expected response:

{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.2.1"
}
List Documents
GET /documents
Returns all supported documents from data/input.

Read Document
GET /documents/{filename}
Examples:

GET /documents/demo.txt
GET /documents/demo.md
Search Documents
POST /search
Request body:

{
  "query": "RAG"
}
Expected response structure:

{
  "query": "RAG",
  "matches": [
    {
      "filename": "demo.md",
      "line_number": 10,
      "line": "- Build a RAG pipeline"
    }
  ],
  "count": 1
}
Summarize Document
POST /summarize
Request body:

{
  "filename": "demo.md"
}
Expected response structure:

{
  "filename": "demo.md",
  "summary": "The document explains...",
  "model": "qwen3.5:4b",
  "version": "0.2.1"
}
Testing the LLM Client
You can test the local LLM client directly from PowerShell:

python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
Expected result:

An artificial intelligence tool that processes and organizes your files entirely on your local device rather than in the cloud for privacy.
The exact response may vary depending on the model.

Testing Document Summarization
You can test summarization directly from Python:

python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.md'))"
Version History
v0.1.0 - Basic Local Document Search
Initial version focused on deterministic document handling without AI.

Features introduced:

FastAPI application structure.

Health check endpoint.

Local document discovery.

Support for .txt and .md files.

Document content retrieval.

Case-insensitive keyword search across local documents.

AI status:

No AI capabilities yet.
This version establishes the document ingestion and search foundation.
v0.2.0 - Local LLM Document Summarization
This version introduced the first AI-powered capability.

Features introduced:

Local LLM integration through Ollama.

Configurable Ollama base URL and model through .env.

Local LLM client service.

Prompt template for summarization.

Document summarization service.

POST /summarize endpoint.

Improved separation between document loading, search, LLM communication, and summarization logic.

AI status:

Local document content
  -> controlled prompt
  -> local LLM
  -> generated summary
This version is still not RAG. The full document is passed as context to the local model.

v0.2.1 - Application Logging
This version adds centralized application logging and traceability across the project.

Features introduced:

Centralized logging configuration.

Console logging.

Rotating file logging under logs/app.log.

Request-level visual separator.

Logging across API endpoints and services.

Traceability for document loading, keyword search, local LLM calls and summarization.

Privacy-aware logging that avoids storing full document content, prompts or generated summaries.

AI status:

No new AI capability introduced.
This version improves observability and debugging for the local LLM summarization flow.
Roadmap
v0.3.0 - Basic RAG
Planned capabilities:

Split documents into chunks.

Generate local embeddings.

Store vectors in ChromaDB.

Retrieve relevant chunks based on a user question.

Answer questions using retrieved context.

Return sources used to generate the answer.

v0.4.0 - Tool-Based Agent
Planned capabilities:

Add document tools such as search, summarize, and ask.

Create a simple agent router.

Allow the system to decide which tool to use based on user intent.

v0.5.0 - Auditor Agent
Planned capabilities:

Add a second validation layer.

Review answers for unsupported claims.

Check whether the response is grounded in document evidence.

Add confidence levels.

v0.6.0 - MCP Server
Planned capabilities:

Expose document tools through MCP.

Allow external clients or agents to call document-related tools using a standard protocol.

Design Principles
Local-first execution.

Privacy-oriented architecture.

Incremental learning by layers.

Clear separation of responsibilities.

Documented code.

No external LLM dependency for private document processing.

Build deterministic capabilities before adding agentic behavior.

Current Limitations
Only .txt and .md files are supported.

Summarization sends the full document content to the local model.

Large documents may exceed the model context window.

No chunking yet.

No embeddings yet.

No vector database yet.

No RAG yet.

No agent or MCP support yet.

No frontend yet.

Suggested Commit for v0.2.1
git add .
git commit -m "feat: add local LLM summarization with logging"
git push origin feature/local-llm-summarization
After merging into main, the suggested tag is:

git tag v0.2.1
git push origin v0.2.1
"""

output_path = Path("/mnt/data/README.md")
output_path.write_text(readme_content, encoding="utf-8")
output_path

Resultado
PosixPath('/mnt/data/README.md')
Listo. Puedes descargar el archivo aquí:

 


Listo, siguiente paso

Dame un resumen de donde estamos y que nos falta

Claro, Alfredo. Estamos cerrando la versión v0.2.1 del proyecto private-doc-agent.

Dónde estamos
El proyecto ya tiene una base funcional bastante buena:

private-doc-agent v0.2.1
Actualmente el sistema puede:

Levantar una API con FastAPI.

Leer documentos locales .txt y .md.

Listar documentos disponibles en data/input.

Consultar el contenido de un documento específico.

Buscar palabras clave en los documentos.

Conectarse a un LLM local vía Ollama.

Usar el modelo local qwen3.5:4b.

Resumir documentos locales con IA.

Registrar trazas/logs en consola y archivo.

Separar visualmente cada ejecución en el log.

Evitar registrar contenido sensible en los logs.

La arquitectura actual se ve así:

Usuario / Swagger
   ↓
FastAPI
   ↓
Endpoints
   ├─ /health
   ├─ /documents
   ├─ /documents/{filename}
   ├─ /search
   └─ /summarize
        ↓
Servicios internos
   ├─ document_loader.py
   ├─ simple_search.py
   ├─ summarizer.py
   └─ llm_client.py
        ↓
Ollama local
        ↓
qwen3.5:4b
Desde el punto de vista de IA
Ya llegamos a esta etapa:

Aplicación documental local + LLM local + prompt controlado
El flujo de IA actual es:

Documento local
   ↓
Lectura del contenido completo
   ↓
Prompt template
   ↓
LLM local vía Ollama
   ↓
Resumen generado
Importante:

Esto todavía no es RAG.
Esto todavía no es un agente.
Esto todavía no usa embeddings.
Esto todavía no usa base vectorial.
Pero ya es una aplicación con IA real, privada y local.

Versiones completadas
v0.1.0 — Basic Local Document Search
Incluye:

- API FastAPI
- /health
- /documents
- /documents/{filename}
- /search
- lectura de .txt y .md
- búsqueda determinística por palabra clave
Estado de IA:

Sin IA todavía.
Base documental y búsqueda simple.
v0.2.0 — Local LLM Document Summarization
Incluye:

- conexión a Ollama
- configuración con .env
- llm_client.py
- summarize_prompt.txt
- summarizer.py
- endpoint /summarize
- resumen de documentos con modelo local
Estado de IA:

Primer uso real de LLM local.
v0.2.1 — Application Logging
Incluye:

- logging_config.py
- logs/app.log
- logs en main.py
- logs en document_loader.py
- logs en simple_search.py
- logs en llm_client.py
- logs en summarizer.py
- separador visual entre ejecuciones
- logging orientado a privacidad
Estado de IA:

No agrega nueva IA.
Mejora observabilidad y trazabilidad.
Qué archivos deberían estar listos
Deberías tener algo así:

private-doc-agent/
  app/
    __init__.py
    main.py
    config.py
    logging_config.py
    prompts/
      summarize_prompt.txt
    services/
      __init__.py
      document_loader.py
      simple_search.py
      llm_client.py
      summarizer.py
  data/
    input/
      demo.txt
      demo.md
    processed/
  docs/
    roadmap.md
  tests/
  README.md
  requirements.txt
  .env.example
  .gitignore
Y localmente también:

.env
logs/app.log
Pero estos no deben subirse a GitHub:

.env
logs/
*.log
Qué falta para cerrar v0.2.1
Antes de pasar a la siguiente versión, faltaría hacer esto:

1. Verificar .gitignore
Debe tener:

.venv/
__pycache__/
*.pyc
.env

data/processed/
logs/
*.log
chroma_db/

.DS_Store
.vscode/
.idea/
2. Validar que el proyecto corre
Ejecutar:

uvicorn app.main:app --reload
Abrir:

http://localhost:8000/docs
Probar:

GET  /health
GET  /documents
GET  /documents/demo.md
POST /search
POST /summarize
3. Verificar logs
Ejecutar:

Get-Content .\logs\app.log -Tail 80
Confirmar que ves trazas de:

- health
- documents
- search
- summarize
- llamada al LLM
- separador visual
4. Confirmar versión
En app/config.py debe estar:

APP_VERSION = "0.2.1"
Y en el README también:

v0.2.1
5. Revisar estado Git
git status
Confirmar que no aparezcan:

.env
logs/app.log
6. Hacer commit
Commit sugerido:

git add .
git commit -m "feat: add local LLM summarization with logging"
7. Subir rama
git push origin feature/local-llm-summarization
8. Merge a main
git checkout main
git pull origin main
git merge feature/local-llm-summarization
git push origin main
9. Crear tag
git tag v0.2.1
git push origin v0.2.1
10. Cerrar rama
git branch -d feature/local-llm-summarization
git push origin --delete feature/local-llm-summarization
Qué sigue después
La siguiente versión sería:

v0.3.0 — Basic RAG
Ahí sí vamos a entrar en una capa más avanzada de IA.

Lo que agregaremos:

- división de documentos en chunks
- embeddings locales
- base vectorial
- recuperación de fragmentos relevantes
- endpoint /ask
- respuestas basadas en evidencia
- fuentes usadas en la respuesta
El flujo cambiará de esto:

Documento completo
   ↓
Prompt
   ↓
LLM
   ↓
Resumen
a esto:

Documento
   ↓
Chunks
   ↓
Embeddings
   ↓
Vector DB
   ↓
Pregunta del usuario
   ↓
Recuperar fragmentos relevantes
   ↓
LLM responde usando solo ese contexto
   ↓
Respuesta con fuentes
Resumen ejecutivo
Hoy estamos aquí:

v0.2.1 lista funcionalmente.
Falta hacer commit, push, merge, tag y cerrar rama.
El proyecto ya tiene:

- base documental
- API local
- LLM local
- resumen con IA
- logging trazable
- README actualizado
Lo siguiente, después de cerrar esta versión en GitHub, será empezar:

v0.3.0 - Basic RAG

error: src refspec feature/local-llm-summarization does not match any
error: failed to push some refs to 'https://github.com/ajapontes/private-doc-agent.git'
(.venv) (base) PS C:\Proyectos\private-doc-agent> 

Ese error significa que Git no encuentra una rama local llamada:

feature/local-llm-summarization
Por eso no puede hacer push de esa referencia.

Puede pasar por varias razones:

1. Nunca creaste esa rama.
2. La rama tiene otro nombre.
3. Estás trabajando directamente en main.
4. Ya cambiaste o borraste la rama local.
Vamos a diagnosticarlo paso a paso.

1. Ver en qué rama estás
Ejecuta:

git branch
o:

git branch --show-current
También revisa el estado:

git status
Mira si te dice algo como:

On branch main
o:

On branch feature/local-llm-summarization
2. Caso A — Si estás en main
Si git status muestra:

On branch main
entonces probablemente hiciste todos los cambios directamente en main.

En ese caso puedes hacer esto:

git add .
git commit -m "feat: add local LLM summarization with logging"
git push origin main
Luego creas el tag:

git tag v0.2.1
git push origin v0.2.1
En este caso no necesitas cerrar rama, porque nunca trabajaste en una rama feature.

3. Caso B — Si quieres crear la rama ahora antes del commit
Si todavía no has hecho commit y quieres conservar el flujo con rama, puedes crearla ahora desde donde estás:

git checkout -b feature/local-llm-summarization
Luego:

git add .
git commit -m "feat: add local LLM summarization with logging"
git push -u origin feature/local-llm-summarization
Después haces merge a main:

git checkout main
git pull origin main
git merge feature/local-llm-summarization
git push origin main
Y tag:

git tag v0.2.1
git push origin v0.2.1
Finalmente cierras la rama:

git branch -d feature/local-llm-summarization
git push origin --delete feature/local-llm-summarization
4. Caso C — Si ya hiciste commit en una rama con otro nombre
Ejecuta:

git branch
Si ves algo como:

* feature/llm-summarization
  main
Entonces debes hacer push con el nombre real de tu rama:

git push -u origin feature/llm-summarization
No uses feature/local-llm-summarization si esa rama no existe.

5. Comando útil para subir la rama actual sin escribir el nombre
Si estás en una rama feature y no quieres equivocarte con el nombre, puedes usar:

git push -u origin HEAD
Eso sube la rama actual al remoto con el mismo nombre.

Pero primero valida que no estés en main:

git branch --show-current
Mi recomendación ahora
Ejecuta estos tres comandos y revisa qué dicen:

git branch --show-current
git branch
git status
Si ves que estás en main, usa este flujo simple:

git add .
git commit -m "feat: add local LLM summarization with logging"
git push origin main

git tag v0.2.1
git push origin v0.2.1
Si quieres, pégame la salida de:

git branch
git status
y te digo exactamente cuál camino usar sin riesgo.


rama main

Perfecto. Si estás en la rama main, entonces no existe la rama feature/local-llm-summarization y por eso salió el error.

En este caso haz el cierre directamente desde main.

1. Verifica el estado
git status
Revisa que no aparezcan:

.env
logs/app.log
Si aparecen como archivos nuevos, no hagas commit todavía y me compartes la salida.

2. Agrega cambios
git add .
Luego revisa:

git status
Confirma nuevamente que no esté subiendo .env ni logs/app.log.

3. Crea el commit
git commit -m "feat: add local LLM summarization with logging"
4. Sube a GitHub
git push origin main
5. Crea el tag v0.2.1
git tag v0.2.1
git push origin v0.2.1
6. Valida que quedó limpio
git status
Resultado esperado:

On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
Flujo completo
cd C:\Proyectos\private-doc-agent

git status

git add .
git status

git commit -m "feat: add local LLM summarization with logging"

git push origin main

git tag v0.2.1
git push origin v0.2.1

git status
Como trabajaste directamente en main, no hay rama que cerrar. El cierre de la versión se hace con el commit, el push y el tag v0.2.1.


Ya esta listo

Excelente, Alfredo. Entonces dejamos cerrada la versión:

v0.2.1 - Local LLM Summarization with Logging
Estado actual cerrado
Ya tienes en main:

- Lectura de documentos .txt y .md
- Listado de documentos
- Consulta de contenido
- Búsqueda por palabra clave
- Integración con Ollama local
- Resumen de documentos con LLM local
- Logging centralizado
- Logs en consola y archivo
- Separador visual por ejecución
- README actualizado
- Tag v0.2.1 publicado
Desde el punto de vista de IA, cerramos esta etapa:

Documento local
  -> prompt controlado
  -> LLM local
  -> resumen generado
Y desde el punto de vista de ingeniería, ya tenemos:

API + servicios separados + configuración + logs + documentación
Qué sigue
La siguiente versión natural es:

v0.3.0 - Basic RAG
Ahí vamos a pasar de “resumir un documento completo” a “responder preguntas usando fragmentos relevantes”.

El nuevo flujo será:

Documento
  -> chunks
  -> embeddings locales
  -> vector store
  -> pregunta del usuario
  -> recuperación de contexto relevante
  -> LLM local
  -> respuesta con fuentes
Qué agregaríamos en v0.3.0
Archivos nuevos probables:

app/services/text_splitter.py
app/services/embedding_client.py
app/services/vector_store.py
app/services/rag_service.py
app/prompts/rag_prompt.txt
Endpoints nuevos:

POST /index
POST /ask
Capacidades nuevas:

- Dividir documentos en fragmentos
- Generar embeddings locales
- Guardar vectores
- Buscar fragmentos similares a una pregunta
- Responder usando contexto recuperado
- Devolver fuentes usadas
Desde IA, el salto importante será
Pasamos de esto:

LLM con documento completo como contexto
a esto:

RAG: Retrieval-Augmented Generation
Ese es un salto clave porque ya no dependemos de enviar todo el documento al modelo. Enviamos solo los fragmentos más relevantes.

Cuando quieras arrancamos la v0.3.0 paso a paso, igual que hicimos con logging.


ayer 8:59
Continuaremos el proyecto private-doc-agent desde el punto en que quedó.

Estado alcanzado:

✅ v0.2.1 completada.

✅ Logging centralizado implementado.

✅ README actualizado.

✅ Commit realizado.

✅ Cambios publicados en main.

✅ Tag v0.2.1 creado.

El siguiente hito del proyecto será:

v0.3.0 - Basic RAG
Y retomaremos a partir del Paso 4 de la implementación de logging/trazabilidad en los servicios como referencia histórica, aunque esa etapa ya quedó finalizada. El siguiente trabajo práctico será construir la capa RAG, en este orden:

text_splitter.py para dividir documentos en fragmentos.

embedding_client.py para generar embeddings locales.

vector_store.py para almacenar y consultar vectores.

rag_service.py para orquestar recuperación + generación.

rag_prompt.txt.

Endpoints POST /index y POST /ask.

Respuestas con fuentes y contexto recuperado.

De esta forma mantendremos la evolución ordenada del proyecto desde una aplicación con resumen mediante LLM local hacia un asistente documental basado en RAG.


hoy 10:14
quiero agregar un nuevo log, en un archivo diferente, quiero que este log sea del prompt que mandamos al modelo y la respuesta del modelo... quiero ver que envio y que me da de vuelta. Ajustemos este paso

Sí, hagamos ese ajuste. Lo vamos a manejar como un log separado para trazabilidad de IA:

logs/llm_io.log
Ese archivo guardará:

- fecha/hora
- modelo usado
- longitud del prompt
- prompt completo enviado al modelo
- longitud de la respuesta
- respuesta completa del modelo
Importante: este log puede contener información privada del documento, porque el prompt incluye el contenido que mandamos al LLM. Por eso debe quedar en logs/ y nunca subirse a GitHub.

Paso 1 — Validar .gitignore
Asegúrate de que .gitignore tenga:

logs/
*.log
.env
Con eso evitamos subir:

logs/app.log
logs/llm_io.log
Paso 2 — Actualizar app/logging_config.py
Reemplaza tu archivo app/logging_config.py por esta versión completa.

"""
Application logging configuration module.

This module centralizes the logging configuration for Private Doc Agent.

It configures:
1. General application logs written to console and logs/app.log.
2. A dedicated LLM input/output log written to logs/llm_io.log.

Logging strategy:
- General logs are privacy-aware and should avoid storing document content,
  full prompts or generated responses.
- LLM I/O logs intentionally store the full prompt and full model response
  for local debugging and learning purposes.
- LLM I/O logs may contain private document content and must not be committed
  to GitHub.
"""

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from app.config import BASE_DIR


# Directory where local log files will be stored.
LOG_DIR = BASE_DIR / "logs"

# General application log file.
LOG_FILE = LOG_DIR / "app.log"

# Dedicated log file for prompts sent to the LLM and responses received.
LLM_IO_LOG_FILE = LOG_DIR / "llm_io.log"

# Visual separator used to identify different API executions in the log file.
LOG_SEPARATOR = "-" * 96


def setup_logging() -> None:
    """
    Configures application-wide logging.

    The configuration includes:
    - Console logging for development visibility.
    - Rotating file logging for general application logs.
    - A consistent log format with timestamp, level, logger name and message.

    This function should be called once when the FastAPI application starts.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers when Uvicorn reloads the application.
    if root_logger.handlers:
        return

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def log_execution_separator(logger_name: str = "app.execution") -> None:
    """
    Writes a visual separator line to the application logs.

    This function is useful to visually separate different API executions
    when reviewing logs during local development or debugging.

    The separator starts with a newline so the visual line appears clearly
    separated from the previous log entry.

    Args:
        logger_name: Name of the logger that will write the separator.
    """
    logger = logging.getLogger(logger_name)
    logger.info("\n%s", LOG_SEPARATOR)


def log_llm_interaction(prompt: str, response: str, model: str) -> None:
    """
    Writes the full prompt sent to the LLM and the full model response
    to a dedicated local log file.

    This log is intended only for local debugging and learning purposes.

    Important:
        This file may contain private document content because the prompt
        can include the document text. The logs directory must be excluded
        from Git using .gitignore.

    Args:
        prompt: Full prompt sent to the local LLM.
        response: Full response generated by the local LLM.
        model: Name of the local model used.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat(timespec="seconds")

    log_entry = f"""
{LOG_SEPARATOR}
Timestamp: {timestamp}
Model: {model}
Prompt length: {len(prompt)}
Response length: {len(response)}

PROMPT SENT TO MODEL:
{prompt}

MODEL RESPONSE:
{response}
{LOG_SEPARATOR}

"""

    with LLM_IO_LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
Paso 3 — Actualizar app/services/llm_client.py
Ahora vamos a llamar esa nueva función desde el cliente del LLM.

Busca este import:

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
Y agrega debajo:

from app.logging_config import log_llm_interaction
La sección de imports debe quedar así:

import logging

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.logging_config import log_llm_interaction
Luego busca esta parte al final de generate_text():

logger.info(
    "Local LLM response received. model=%s response_length=%s",
    OLLAMA_MODEL,
    len(generated_text),
)

return generated_text
Y reemplázala por esta versión:

logger.info(
    "Local LLM response received. model=%s response_length=%s",
    OLLAMA_MODEL,
    len(generated_text),
)

log_llm_interaction(
    prompt=prompt,
    response=generated_text,
    model=OLLAMA_MODEL,
)

return generated_text
Así debería quedar la parte final de llm_client.py
    generated_text = generated_text.strip()

    logger.info(
        "Local LLM response received. model=%s response_length=%s",
        OLLAMA_MODEL,
        len(generated_text),
    )

    log_llm_interaction(
        prompt=prompt,
        response=generated_text,
        model=OLLAMA_MODEL,
    )

    return generated_text
Paso 4 — Probar el nuevo log
Levanta la API:

uvicorn app.main:app --reload
Abre Swagger:

http://localhost:8000/docs
Ejecuta:

POST /summarize
Con body:

{
  "filename": "demo.md"
}
Luego revisa el nuevo archivo:

Get-Content .\logs\llm_io.log -Tail 120
Deberías ver algo así:

------------------------------------------------------------------------------------------------
Timestamp: 2026-07-18T10:32:15
Model: qwen3.5:4b
Prompt length: 589
Response length: 242

PROMPT SENT TO MODEL:
You are a private document assistant.

Your task is to summarize the provided document clearly and concisely.

...

MODEL RESPONSE:
The document explains that Private Doc Agent...
------------------------------------------------------------------------------------------------
Paso 5 — Verlo en vivo
Puedes dejar una terminal viendo el log de prompt/respuesta:

Get-Content .\logs\llm_io.log -Wait
Y en otra terminal o desde Swagger vas ejecutando /summarize.

Nota importante para el README
Luego agregamos una pequeña sección en el README indicando:

### LLM I/O Logging

For local debugging and learning purposes, the application writes full LLM prompts and responses to:

```text
logs/llm_io.log
This file may contain private document content and must not be committed to GitHub.


---

# Qué estamos agregando realmente

Antes teníamos:

```text
logs/app.log
Para trazabilidad general, sin contenido sensible.

Ahora agregamos:

logs/llm_io.log
Para inspeccionar exactamente:

Prompt enviado al modelo
Respuesta recibida del modelo
Esto es muy útil para aprender cómo el prompt afecta la respuesta, pero debe usarse con cuidado porque puede contener datos privados.


Esta es mi seccion de log actual: The application also writes logs to the console while running with Uvicorn.

### Logging capabilities

- Logs API request flow.
- Logs document listing and document reading events.
- Logs keyword search execution.
- Logs local LLM calls through Ollama.
- Logs document summarization flow.
- Adds a visual separator between API executions.
- Uses rotating log files to avoid unlimited log growth.

### Privacy-aware logging

The application intentionally avoids logging sensitive content.

The logs may include:

text
- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages


The logs should not include:

text
- full document content
- full prompt content
- full generated summary
- private document data


### View logs

To view the latest log entries:

powershell
Get-Content .\logs\app.log -Tail 80


To watch logs in real time:

powershell
Get-Content .\logs\app.log -Wait
   ===================== actualizala con los cambios que hicimos

Claro. Reemplaza toda tu sección actual de logging por esta versión actualizada:

## Application Logging

Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

The application writes general execution logs to:

```text
logs/app.log
The application also writes logs to the console while running with Uvicorn.

In addition, the application can write full LLM input/output interactions to a dedicated local file:

logs/llm_io.log
This second log is intended for local debugging and learning purposes. It allows you to inspect the exact prompt sent to the model and the exact response returned by the model.

Logging capabilities
Logs API request flow.

Logs document listing and document reading events.

Logs keyword search execution.

Logs local LLM calls through Ollama.

Logs document summarization flow.

Adds a visual separator between API executions.

Uses rotating log files to avoid unlimited log growth.

Writes full LLM prompt and model response to a dedicated local log file.

General application log
The general application log is written to:

logs/app.log
This log is designed to be privacy-aware.

It may include:

- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages
It should not include:

- full document content
- full prompt content
- full generated summary
- private document data
LLM input/output log
The LLM input/output log is written to:

logs/llm_io.log
This log includes:

- timestamp
- model name
- prompt length
- response length
- full prompt sent to the model
- full response returned by the model
Important: this file may contain private document content because the prompt can include the text extracted from local documents.

For that reason, logs/llm_io.log must remain local and should never be committed to GitHub.

Make sure .gitignore includes:

logs/
*.log
View general logs
To view the latest general log entries:

Get-Content .\logs\app.log -Tail 80
To watch general logs in real time:

Get-Content .\logs\app.log -Wait
View LLM input/output logs
To view the latest LLM input/output entries:

Get-Content .\logs\llm_io.log -Tail 120
To watch LLM input/output logs in real time:

Get-Content .\logs\llm_io.log -Wait

Ojo con el cierre de los bloques Markdown: esta sección ya viene con los ``` bien cerrados, así que puedes reemplazarla completa sin que se rompa el README.

damelo en un archivo .txt que pueda descargar para poder inclurirlo dentro del readme.md de mi proyecto, porque aca me lo das en diferentes celdas y pierdo el formato


Error durante el análisis
from pathlib import Path

logging_section = """## Application Logging

Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

The application writes general execution logs to:

```text
logs/app.log
The application also writes logs to the console while running with Uvicorn.

In addition, the application can write full LLM input/output interactions to a dedicated local file:

logs/llm_io.log
This second log is intended for local debugging and learning purposes. It allows you to inspect the exact prompt sent to the model and the exact response returned by the model.

Logging capabilities
Logs API request flow.

Logs document listing and document reading events.

Logs keyword search execution.

Logs local LLM calls through Ollama.

Logs document summarization flow.

Adds a visual separator between API executions.

Uses rotating log files to avoid unlimited log growth.

Writes full LLM prompt and model response to a dedicated local log file.

General application log
The general application log is written to:

logs/app.log
This log is designed to be privacy-aware.

It may include:

- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages
It should not include:

- full document content
- full prompt content
- full generated summary
- private document data
LLM input/output log
The LLM input/output log is written to:

logs/llm_io.log
This log includes:

- timestamp
- model name
- prompt length
- response length
- full prompt sent to the model
- full response returned by the model
Important: this file may contain private document content because the prompt can include the text extracted from local documents.

For that reason, logs/llm_io.log must remain local and should never be committed to GitHub.

Make sure .gitignore includes:

logs/
*.log
View general logs
To view the latest general log entries:

Get-Content .\\logs\\app.log -Tail 80
To watch general logs in real time:

Get-Content .\\logs\\app.log -Wait
View LLM input/output logs
To view the latest LLM input/output entries:

Get-Content .\\logs\\llm_io.log -Tail 120
To watch LLM input/output logs in real time:

Get-Content .\\logs\\llm_io.log -Wait
"""

output_path = Path("/mnt/data/application_logging_section.txt")
output_path.write_text(logging_section, encoding="utf-8")

output_path


Analizado
from pathlib import Path

logging_section = """## Application Logging

Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

The application writes general execution logs to:

```text
logs/app.log
The application also writes logs to the console while running with Uvicorn.

In addition, the application can write full LLM input/output interactions to a dedicated local file:

logs/llm_io.log
This second log is intended for local debugging and learning purposes. It allows you to inspect the exact prompt sent to the model and the exact response returned by the model.

Logging capabilities
Logs API request flow.

Logs document listing and document reading events.

Logs keyword search execution.

Logs local LLM calls through Ollama.

Logs document summarization flow.

Adds a visual separator between API executions.

Uses rotating log files to avoid unlimited log growth.

Writes full LLM prompt and model response to a dedicated local log file.

General application log
The general application log is written to:

logs/app.log
This log is designed to be privacy-aware.

It may include:

- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages
It should not include:

- full document content
- full prompt content
- full generated summary
- private document data
LLM input/output log
The LLM input/output log is written to:

logs/llm_io.log
This log includes:

- timestamp
- model name
- prompt length
- response length
- full prompt sent to the model
- full response returned by the model
Important: this file may contain private document content because the prompt can include the text extracted from local documents.

For that reason, logs/llm_io.log must remain local and should never be committed to GitHub.

Make sure .gitignore includes:

logs/
*.log
View general logs
To view the latest general log entries:

Get-Content .\\logs\\app.log -Tail 80
To watch general logs in real time:

Get-Content .\\logs\\app.log -Wait
View LLM input/output logs
To view the latest LLM input/output entries:

Get-Content .\\logs\\llm_io.log -Tail 120
To watch LLM input/output logs in real time:

Get-Content .\\logs\\llm_io.log -Wait
"""

output_path = Path("/mnt/data/application_logging_section.txt")
output_path.write_text(logging_section, encoding="utf-8")

print(output_path)

STDOUT/STDERR
/mnt/data/application_logging_section.txt
Listo. Puedes descargar el archivo .txt aquí:

 


Biblioteca
/
application_logging_section.txt


## Application Logging

Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

The application writes general execution logs to:

```text
logs/app.log
```

The application also writes logs to the console while running with Uvicorn.

In addition, the application can write full LLM input/output interactions to a dedicated local file:

```text
logs/llm_io.log
```

This second log is intended for local debugging and learning purposes. It allows you to inspect the exact prompt sent to the model and the exact response returned by the model.

### Logging capabilities

- Logs API request flow.
- Logs document listing and document reading events.
- Logs keyword search execution.
- Logs local LLM calls through Ollama.
- Logs document summarization flow.
- Adds a visual separator between API executions.
- Uses rotating log files to avoid unlimited log growth.
- Writes full LLM prompt and model response to a dedicated local log file.

### General application log

The general application log is written to:

```text
logs/app.log
```

This log is designed to be privacy-aware.

It may include:

```text
- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages
```

It should not include:

```text
- full document content
- full prompt content
- full generated summary
- private document data
```

### LLM input/output log

The LLM input/output log is written to:

```text
logs/llm_io.log
```

This log includes:

```text
- timestamp
- model name
- prompt length
- response length
- full prompt sent to the model
- full response returned by the model
```

Important: this file may contain private document content because the prompt can include the text extracted from local documents.

For that reason, `logs/llm_io.log` must remain local and should never be committed to GitHub.

Make sure `.gitignore` includes:

```gitignore
logs/
*.log
```

### View general logs

To view the latest general log entries:

```powershell
Get-Content .\logs\app.log -Tail 80
```

To watch general logs in real time:

```powershell
Get-Content .\logs\app.log -Wait
```

### View LLM input/output logs

To view the latest LLM input/output entries:

```powershell
Get-Content .\logs\llm_io.log -Tail 120
```

To watch LLM input/output logs in real time:

```powershell
Get-Content .\logs\llm_io.log -Wait
```
Biblioteca
/
application_logging_section.txt


## Application Logging

Private Doc Agent includes centralized application logging to improve traceability and debugging during local development.

The application writes general execution logs to:

```text
logs/app.log
```

The application also writes logs to the console while running with Uvicorn.

In addition, the application can write full LLM input/output interactions to a dedicated local file:

```text
logs/llm_io.log
```

This second log is intended for local debugging and learning purposes. It allows you to inspect the exact prompt sent to the model and the exact response returned by the model.

### Logging capabilities

- Logs API request flow.
- Logs document listing and document reading events.
- Logs keyword search execution.
- Logs local LLM calls through Ollama.
- Logs document summarization flow.
- Adds a visual separator between API executions.
- Uses rotating log files to avoid unlimited log growth.
- Writes full LLM prompt and model response to a dedicated local log file.

### General application log

The general application log is written to:

```text
logs/app.log
```

This log is designed to be privacy-aware.

It may include:

```text
- endpoint execution
- filename
- model name
- document size
- prompt length
- response length
- number of search matches
- error messages
```

It should not include:

```text
- full document content
- full prompt content
- full generated summary
- private document data
```

### LLM input/output log

The LLM input/output log is written to:

```text
logs/llm_io.log
```

This log includes:

```text
- timestamp
- model name
- prompt length
- response length
- full prompt sent to the model
- full response returned by the model
```

Important: this file may contain private document content because the prompt can include the text extracted from local documents.

For that reason, `logs/llm_io.log` must remain local and should never be committed to GitHub.

Make sure `.gitignore` includes:

```gitignore
logs/
*.log
```

### View general logs

To view the latest general log entries:

```powershell
Get-Content .\logs\app.log -Tail 80
```

To watch general logs in real time:

```powershell
Get-Content .\logs\app.log -Wait
```

### View LLM input/output logs

To view the latest LLM input/output entries:

```powershell
Get-Content .\logs\llm_io.log -Tail 120
```

To watch LLM input/output logs in real time:

```powershell
Get-Content .\logs\llm_io.log -Wait
```

## API Endpoints

### Health Check

```http
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "app": "private-doc-agent",
  "version": "0.2.1"
}
```

### List Documents

```http
GET /documents
```

Returns all supported documents from `data/input`.

### Read Document

```http
GET /documents/{filename}
```

Examples:

```http
GET /documents/demo.txt
GET /documents/demo.md
```

### Search Documents

```http
POST /search
```

Request body:

```json
{
  "query": "RAG"
}
```

Expected response structure:

```json
{
  "query": "RAG",
  "matches": [
    {
      "filename": "demo.md",
      "line_number": 10,
      "line": "- Build a RAG pipeline"
    }
  ],
  "count": 1
}
```

### Summarize Document

```http
POST /summarize
```

Request body:

```json
{
  "filename": "demo.md"
}
```

Expected response structure:

```json
{
  "filename": "demo.md",
  "summary": "The document explains...",
  "model": "qwen3.5:4b",
  "version": "0.2.1"
}
```

## Testing the LLM Client

You can test the local LLM client directly from PowerShell:

```powershell
python -c "from app.services.llm_client import generate_text; print(generate_text('Explain in one short sentence what a local document assistant is.'))"
```

Expected result:

```text
An artificial intelligence tool that processes and organizes your files entirely on your local device rather than in the cloud for privacy.
```

The exact response may vary depending on the model.

## Testing Document Summarization

You can test summarization directly from Python:

```powershell
python -c "from app.services.summarizer import summarize_document; print(summarize_document('demo.md'))"
```

## Version History

### v0.1.0 - Basic Local Document Search

Initial version focused on deterministic document handling without AI.

Features introduced:

- FastAPI application structure.
- Health check endpoint.
- Local document discovery.
- Support for `.txt` and `.md` files.
- Document content retrieval.
- Case-insensitive keyword search across local documents.

AI status:

```text
No AI capabilities yet.
This version establishes the document ingestion and search foundation.
```

### v0.2.0 - Local LLM Document Summarization

This version introduced the first AI-powered capability.

Features introduced:

- Local LLM integration through Ollama.
- Configurable Ollama base URL and model through `.env`.
- Local LLM client service.
- Prompt template for summarization.
- Document summarization service.
- `POST /summarize` endpoint.
- Improved separation between document loading, search, LLM communication, and summarization logic.

AI status:

```text
Local document content
  -> controlled prompt
  -> local LLM
  -> generated summary
```

This version is still not RAG. The full document is passed as context to the local model.

### v0.2.1 - Application Logging

This version adds centralized application logging and traceability across the project.

Features introduced:

- Centralized logging configuration.
- Console logging.
- Rotating file logging under `logs/app.log`.
- Request-level visual separator.
- Logging across API endpoints and services.
- Traceability for document loading, keyword search, local LLM calls and summarization.
- Privacy-aware logging that avoids storing full document content, prompts or generated summaries.

AI status:

```text
No new AI capability introduced.
This version improves observability and debugging for the local LLM summarization flow.
```

## Roadmap

### v0.3.0 - Basic RAG

Planned capabilities:

- Split documents into chunks.
- Generate local embeddings.
- Store vectors in ChromaDB.
- Retrieve relevant chunks based on a user question.
- Answer questions using retrieved context.
- Return sources used to generate the answer.

### v0.4.0 - Tool-Based Agent

Planned capabilities:

- Add document tools such as search, summarize, and ask.
- Create a simple agent router.
- Allow the system to decide which tool to use based on user intent.

### v0.5.0 - Auditor Agent

Planned capabilities:

- Add a second validation layer.
- Review answers for unsupported claims.
- Check whether the response is grounded in document evidence.
- Add confidence levels.

### v0.6.0 - MCP Server

Planned capabilities:

- Expose document tools through MCP.
- Allow external clients or agents to call document-related tools using a standard protocol.

## Design Principles

- Local-first execution.
- Privacy-oriented architecture.
- Incremental learning by layers.
- Clear separation of responsibilities.
- Documented code.
- No external LLM dependency for private document processing.
- Build deterministic capabilities before adding agentic behavior.

## Current Limitations

- Only `.txt` and `.md` files are supported.
- Summarization sends the full document content to the local model.
- Large documents may exceed the model context window.
- No chunking yet.
- No embeddings yet.
- No vector database yet.
- No RAG yet.
- No agent or MCP support yet.
- No frontend yet.

## Suggested Commit for v0.2.1

```bash
git add .
git commit -m "feat: add local LLM summarization with logging"
git push origin feature/local-llm-summarization
```

After merging into `main`, the suggested tag is:

```bash
git tag v0.2.1
git push origin v0.2.1
```