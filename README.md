# 🌐 Chat Multi-Agent Travel

Plataforma inteligente para crear planes de viaje completos usando una arquitectura multi-agente moderna. Funciona sobre FastAPI, Next.js, Whisper de OpenAI y un ecosistema de micro-servicios MCP.

## Descripción general

Este proyecto muestra cómo un conjunto de agentes coordinados puede transformar un simple mensaje en una planificación de viaje totalmente estructurada.

> "Planea un viaje de 4 días a Manchester con mi novia."

Y el sistema:

- Procesa tu mensaje con un modelo de lenguaje.
- Activa agentes especializados (vuelos, hoteles, destinos y cálculo).
- Consolida todo en un itinerario coherente de 72 h con presupuestos, recomendaciones y un resumen narrativo.
- Admite texto y voz, aprovechando Whisper para transcripción automática.

## Arquitectura del sistema

| Componente | Tecnología | Descripción |
|------------|------------|-------------|
| Backend | FastAPI + Whisper | Coordina a los agentes, gestiona conversaciones y maneja la entrada de voz. |
| Frontend | Next.js | Interfaz conversacional y visualización de itinerarios. |
| Agente de vuelos | MCP (Python + FastAPI) | Simulación de consultas inspiradas en APIs tipo Amadeus. |
| Agente de hoteles | MCP (Python + FastAPI) | Genera sugerencias de alojamiento. |
| Agente de destinos | MCP (Python + FastAPI) | Produce rutas, puntos de interés y plan diario. |
| Agente de cálculo | MCP (Python + FastAPI) | Calcula costes y agrega la información final. |

Todos los servicios funcionan dentro de Docker sobre una red interna `multiagent_net` para garantizar aislamiento y velocidad.

## ⚙️ 1) Requisitos

- **Docker Desktop** (Windows / macOS / Linux)
- **Conexión a internet** para dependencias
- **Opcional — claves reales:**
  - `OPENAI_API_KEY`
  - `AMADEUS_API_KEY`
  - `AMADEUS_API_SECRET`
  - `WEATHER_API_KEY`

## 🔐 2) Configuración de variables de entorno

Copia el archivo de ejemplo y añade tus claves (si las tienes):

```bash
cp .env.example .env
```

Edita el nuevo `.env`:

```bash
OPENAI_API_KEY=sk-xxxx
AMADEUS_API_KEY=xxxx
AMADEUS_API_SECRET=xxxx
WEATHER_API_KEY=xxxx
```

Si no añades claves, el sistema seguirá funcionando en **modo simulado**, generando datos de ejemplo.

## 3) Arranque rápido (con Docker)

```bash
docker compose up -d --build
```

Esto levantará todos los servicios automáticamente.

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| 🌍 Frontend | [http://127.0.0.1:3000](http://127.0.0.1:3000) | Interfaz de chat |
| ⚙️ Backend | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | API y documentación Swagger |
| 🧮 Calc Agent | [http://127.0.0.1:8770/docs](http://127.0.0.1:8770/docs) | Servicio de cálculos |
| ✈️ Flights Agent | [http://127.0.0.1:8771/docs](http://127.0.0.1:8771/docs) | Servicio de vuelos |
| 🏨 Hotels Agent | [http://127.0.0.1:8772/docs](http://127.0.0.1:8772/docs) | Servicio de hoteles |
| 🌍 Destinations Agent | [http://127.0.0.1:8773/docs](http://127.0.0.1:8773/docs) | Servicio de destinos |

## 4) Verificar el estado del sistema

```bash
docker compose ps
```

Si aparecen con `Up (healthy)`, el sistema está operativo. También puedes comprobar cada servicio:

```bash
curl -I http://127.0.0.1:8000/docs
curl -I http://127.0.0.1:8770/docs
curl -I http://127.0.0.1:8771/docs
curl -I http://127.0.0.1:8772/docs
curl -I http://127.0.0.1:8773/docs
```

## 💬 5) Uso del chat

Abre el navegador en [http://127.0.0.1:3000](http://127.0.0.1:3000). Verás una interfaz conversacional limpia y moderna. Puedes escribir mensajes naturales como:

- "Planea un viaje a París de 3 días con mi pareja."
- "Qué información tienes sobre Londres."
- "Planea un viaje de negocios a Berlín."

El sistema recuerda tus viajes anteriores (persistencia JSON en `backend/data/v2/users/`) y permite grabar mensajes de voz; Whisper se encarga de la transcripción automática.

## 🔊 6) Pruebas por API (modo avanzado)

Ejemplo en PowerShell para enviar un mensaje al backend:

```powershell
$body = @{
  user     = "Demo"
  message  = "Planea un viaje de 2 días a Palma de Mallorca"
  convo_id = ""
} | ConvertTo-Json

curl.exe -s -X POST "http://127.0.0.1:8000/chat/" `
  -H "Content-Type: application/json" `
  --data-raw $body
```

Respuesta esperada (ejemplo):

```json
{
  "conversation_id": "20251017T223205_652666",
  "intent": "PLAN_TRIP",
  "reply_text": "Aquí tienes tu plan para Palma de Mallorca...",
  "structured_data": {...},
  "agents_called": ["FlightAgent", "HotelAgent", "DestinationAgent"]
}
```

## 🪵 7) Monitorizar y depurar

```bash
docker compose logs -f backend
docker compose logs --tail=200
docker compose logs backend | findstr /I "ERROR"
```

## 🧰 8) Solución de problemas frecuentes

- **Backend llama a 127.0.0.1 dentro de Docker**  
  Asegúrate de que los servicios usan los nombres de servicio Docker (por ejemplo `flights:8771`, `destinations:8773`).

- **Falta `WEATHER_API_KEY`**  
  Es opcional; añade la variable al `.env` si quieres quitar la advertencia.

- **Whisper no transcribe audio**  
  Verifica que `ffmpeg` esté disponible (el Dockerfile lo instala). Si ejecutas fuera de Docker, instala `ffmpeg` manualmente:
  ```bash
  sudo apt install ffmpeg
  ```

## 💻 9) Ejecución sin Docker (modo desarrollador)

```bash
# MCPs
cd mcp_flight_server && uvicorn server:app --port 8771
cd mcp_hotel_server && uvicorn server:app --port 8772
cd mcp_destination_server && uvicorn server:app --port 8773
cd mcp_calc_server && uvicorn server:app --port 8770

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## 📦 10) Estructura del proyecto

```
chat-multiagent/
├── backend/
│   ├── main.py
│   ├── app/core/orchestrator/
│   ├── data/v2/users/
│   └── requirements.txt
├── frontend/
│   ├── components/Chat.tsx
│   ├── app/page.tsx
│   ├── app/layout.tsx
│   ├── public/icons/
│   └── styles/globals.css
├── mcp_calc_server/
├── mcp_flight_server/
├── mcp_hotel_server/
├── mcp_destination_server/
├── Dockerfile.backend
├── Dockerfile.frontend
├── Dockerfile.mcp
├── docker-compose.yml
└── README.md
```

## 🔎 11) Perspectiva y valor práctico

Esta plataforma sirve como punto de partida para construir asistentes inteligentes capaces de coordinar múltiples micro-servicios, procesar lenguaje natural, manejar voz y generar resultados estructurados. Es un entorno ideal para experimentar con MCP, diseñar pipelines de agentes y entender cómo se integran sistemas conversacionales en una aplicación web completa.

## Créditos y autoría

Proyecto académico creado como Trabajo Fin de Máster, centrado en sistemas multiagente, IA generativa y comunicación entre servicios (MCP + A2A).

Hecho con ❤️ para que lo enciendas, explores y sigas ampliándolo.
