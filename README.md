<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Chat Multi-Agent Travel — README</title>
  <style>
    :root{
      --bg:#0f1724; --card:#0b1220; --muted:#94a3b8; --accent:#06b6d4; --glass: rgba(255,255,255,0.03);
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;
      color-scheme: dark;
    }
    body{
      margin:0;
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
      background: linear-gradient(180deg,#071025 0%, #07192a 100%);
      color:#e6eef6;
      line-height:1.5;
      padding:32px;
    }
    .container{max-width:980px;margin:0 auto;}
    header{margin-bottom:22px}
    h1{font-size:28px;margin:0 0 8px}
    p.lead{color:var(--muted);margin:0 0 18px}
    section.card{background:var(--card);border-radius:12px;padding:18px;margin:18px 0;box-shadow:0 6px 18px rgba(2,6,23,0.6);border:1px solid rgba(255,255,255,0.02)}
    table{width:100%;border-collapse:collapse;margin-top:8px}
    th,td{padding:10px 8px;text-align:left;border-bottom:1px dashed rgba(255,255,255,0.03);vertical-align:top}
    th{color:var(--accent);font-weight:600}
    code, pre{font-family:var(--mono);background:var(--glass);padding:8px;border-radius:8px;color:#cfeffd;font-size:13px;display:block;overflow:auto}
    pre.inline{display:inline-block;padding:4px 8px;border-radius:6px}
    .badge{display:inline-block;padding:4px 8px;border-radius:999px;background:rgba(255,255,255,0.03);color:var(--muted);font-size:13px;margin-left:6px}
    footer{color:var(--muted);font-size:13px;margin-top:18px;text-align:center}
    a{color:var(--accent);text-decoration:none}
    .mono{font-family:var(--mono)}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🧭 Chat Multi-Agent Travel</h1>
      <p class="lead">Plataforma inteligente para crear planes de viaje completos usando una arquitectura multi-agente moderna. Funciona sobre FastAPI, Next.js, Whisper de OpenAI y un ecosistema de micro-servicios MCP.</p>
    </header>

    <section class="card" id="descripcion">
      <h2>🧠 Descripción general</h2>
      <p>Este proyecto muestra cómo un conjunto de agentes coordinados puede transformar un simple mensaje en una planificación de viaje totalmente estructurada.</p>

      <blockquote style="margin:12px 0;padding:12px;border-left:4px solid rgba(6,182,212,0.12);background:rgba(6,182,212,0.02);color:#dff7fb;">
        “Planea un viaje de 4 días a Manchester con mi novia.”
      </blockquote>

      <p>Y el sistema:</p>
      <ul>
        <li>Procesa tu mensaje con un modelo de lenguaje.</li>
        <li>Activa agentes especializados (vuelos, hoteles, destinos y cálculo).</li>
        <li>Consolida todo en un itinerario coherente de 72 h con presupuestos, recomendaciones y un resumen narrativo.</li>
        <li>Admite texto y voz, aprovechando Whisper para transcripción automática.</li>
      </ul>
    </section>

    <section class="card" id="arquitectura">
      <h2>🧩 Arquitectura del sistema</h2>
      <table>
        <thead>
          <tr>
            <th>Componente</th>
            <th>Tecnología</th>
            <th>Descripción</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>🧠 Backend</td>
            <td>FastAPI + Whisper</td>
            <td>Coordina a los agentes, gestiona conversaciones y maneja la entrada de voz.</td>
          </tr>
          <tr>
            <td>💬 Frontend</td>
            <td>Next.js</td>
            <td>Interfaz conversacional y visualización de itinerarios.</td>
          </tr>
          <tr>
            <td>✈️ Agente de vuelos</td>
            <td>MCP (Python + FastAPI)</td>
            <td>Simulación de consultas inspiradas en APIs tipo Amadeus.</td>
          </tr>
          <tr>
            <td>🏨 Agente de hoteles</td>
            <td>MCP (Python + FastAPI)</td>
            <td>Genera sugerencias de alojamiento.</td>
          </tr>
          <tr>
            <td>🌍 Agente de destinos</td>
            <td>MCP (Python + FastAPI)</td>
            <td>Produce rutas, puntos de interés y plan diario.</td>
          </tr>
          <tr>
            <td>🧮 Agente de cálculo</td>
            <td>MCP (Python + FastAPI)</td>
            <td>Calcula costes y agrega la información final.</td>
          </tr>
        </tbody>
      </table>

      <p style="margin-top:12px">Todos los servicios funcionan dentro de Docker sobre una red interna <span class="mono">multiagent_net</span> para garantizar aislamiento y velocidad.</p>
    </section>

    <section class="card" id="requisitos">
      <h2>⚙️ 1) Requisitos</h2>
      <ul>
        <li><strong>Docker Desktop</strong> (Windows / macOS / Linux)</li>
        <li><strong>Conexión a internet</strong> para dependencias</li>
        <li><strong>Opcional — claves reales:</strong>
          <div class="badge mono">OPENAI_API_KEY</div>
          <div class="badge mono">AMADEUS_API_KEY</div>
          <div class="badge mono">AMADEUS_API_SECRET</div>
          <div class="badge mono">WEATHER_API_KEY</div>
        </li>
      </ul>
    </section>

    <section class="card" id="env">
      <h2>🔐 2) Configuración de variables de entorno</h2>
      <p>Copia el archivo de ejemplo y añade tus claves (si las tienes):</p>
      <pre><code class="mono">cp .env.example .env</code></pre>

      <p>Edita el nuevo <code class="mono">.env</code>:</p>
      <pre><code class="mono">OPENAI_API_KEY=sk-xxxx
AMADEUS_API_KEY=xxxx
AMADEUS_API_SECRET=xxxx
WEATHER_API_KEY=xxxx</code></pre>

      <p>Si no añades claves, el sistema seguirá funcionando en <strong>modo simulado</strong>, generando datos de ejemplo.</p>
    </section>

    <section class="card" id="arranque">
      <h2>🚀 3) Arranque rápido (con Docker)</h2>

      <pre><code class="mono">docker compose up -d --build</code></pre>

      <p>Esto levantará todos los servicios automáticamente.</p>

      <table>
        <thead>
          <tr><th>Servicio</th><th>Puerto</th><th>Descripción</th></tr>
        </thead>
        <tbody>
          <tr><td>🌍 Frontend</td><td><a href="http://127.0.0.1:3000">http://127.0.0.1:3000</a></td><td>Interfaz de chat</td></tr>
          <tr><td>⚙️ Backend</td><td><a href="http://127.0.0.1:8000/docs">http://127.0.0.1:8000/docs</a></td><td>API y documentación Swagger</td></tr>
          <tr><td>🧮 Calc Agent</td><td><a href="http://127.0.0.1:8770/docs">http://127.0.0.1:8770/docs</a></td><td>Servicio de cálculos</td></tr>
          <tr><td>✈️ Flights Agent</td><td><a href="http://127.0.0.1:8771/docs">http://127.0.0.1:8771/docs</a></td><td>Servicio de vuelos</td></tr>
          <tr><td>🏨 Hotels Agent</td><td><a href="http://127.0.0.1:8772/docs">http://127.0.0.1:8772/docs</a></td><td>Servicio de hoteles</td></tr>
          <tr><td>🌍 Destinations Agent</td><td><a href="http://127.0.0.1:8773/docs">http://127.0.0.1:8773/docs</a></td><td>Servicio de destinos</td></tr>
        </tbody>
      </table>
    </section>

    <section class="card" id="verificar">
      <h2>🧠 4) Verificar el estado del sistema</h2>

      <pre><code class="mono">docker compose ps</code></pre>

      <p>Si aparecen con <code class="mono">Up (healthy)</code>, el sistema está operativo. También puedes comprobar cada servicio:</p>

      <pre><code class="mono">curl -I http://127.0.0.1:8000/docs
curl -I http://127.0.0.1:8770/docs
curl -I http://127.0.0.1:8771/docs
curl -I http://127.0.0.1:8772/docs
curl -I http://127.0.0.1:8773/docs</code></pre>
    </section>

    <section class="card" id="uso">
      <h2>💬 5) Uso del chat</h2>

      <p>Abre el navegador en <a href="http://127.0.0.1:3000">http://127.0.0.1:3000</a>. Verás una interfaz conversacional limpia y moderna. Puedes escribir mensajes naturales como:</p>

      <ul>
        <li>“Planea un viaje a París de 3 días con mi pareja.”</li>
        <li>“Qué información tienes sobre Londres.”</li>
        <li>“Planea un viaje de negocios a Berlín.”</li>
      </ul>

      <p>El sistema recuerda tus viajes anteriores (persistencia JSON en <code class="mono">backend/data/v2/users/</code>) y permite grabar mensajes de voz; Whisper se encarga de la transcripción automática.</p>
    </section>

    <section class="card" id="api">
      <h2>🔊 6) Pruebas por API (modo avanzado)</h2>

      <p>Ejemplo en PowerShell para enviar un mensaje al backend:</p>

      <pre><code class="mono">$body = @{
  user     = "Demo"
  message  = "Planea un viaje de 2 días a Palma de Mallorca"
  convo_id = ""
} | ConvertTo-Json

curl.exe -s -X POST "http://127.0.0.1:8000/chat/" `
  -H "Content-Type: application/json" `
  --data-raw $body</code></pre>

      <p>Respuesta esperada (ejemplo):</p>

      <pre><code class="mono">{
  "conversation_id": "20251017T223205_652666",
  "intent": "PLAN_TRIP",
  "reply_text": "Aquí tienes tu plan para Palma de Mallorca...",
  "structured_data": {...},
  "agents_called": ["FlightAgent", "HotelAgent", "DestinationAgent"]
}</code></pre>
    </section>

    <section class="card" id="monitorizar">
      <h2>🪵 7) Monitorizar y depurar</h2>

      <pre><code class="mono">docker compose logs -f backend
docker compose logs --tail=200
docker compose logs backend | findstr /I "ERROR"</code></pre>
    </section>

    <section class="card" id="problemas">
      <h2>🧰 8) Solución de problemas frecuentes</h2>

      <ul>
        <li><strong>❌ Backend llama a 127.0.0.1 dentro de Docker</strong><br>
            Asegúrate de que los servicios usan los nombres de servicio Docker (por ejemplo <code class="mono">flights:8771</code>, <code class="mono">destinations:8773</code>).</li>

        <li><strong>⚠️ Falta <code class="mono">WEATHER_API_KEY</code></strong><br>
            Es opcional; añade la variable al <code class="mono">.env</code> si quieres quitar la advertencia.</li>

        <li><strong>🎙️ Whisper no transcribe audio</strong><br>
            Verifica que <code class="mono">ffmpeg</code> esté disponible (el Dockerfile lo instala). Si ejecutas fuera de Docker, instala <code class="mono">ffmpeg</code> manualmente:
            <pre class="inline"><code class="mono">sudo apt install ffmpeg</code></pre>
        </li>
      </ul>
    </section>

    <section class="card" id="sin-docker">
      <h2>💻 9) Ejecución sin Docker (modo desarrollador)</h2>

      <pre><code class="mono"># MCPs
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
npm run dev</code></pre>
    </section>

    <section class="card" id="estructura">
      <h2>📦 10) Estructura del proyecto</h2>

      <pre><code class="mono">chat-multiagent/
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
└── README.md</code></pre>
    </section>

    <section class="card" id="valor">
      <h2>🔎 11) Perspectiva y valor práctico</h2>
      <p>Esta plataforma sirve como punto de partida para construir asistentes inteligentes capaces de coordinar múltiples micro-servicios, procesar lenguaje natural, manejar voz y generar resultados estructurados. Es un entorno ideal para experimentar con MCP, diseñar pipelines de agentes y entender cómo se integran sistemas conversacionales en una aplicación web completa.</p>
    </section>

    <section class="card" id="creditos">
      <h2>🤝 Créditos y autoría</h2>
      <p>Proyecto académico creado como Trabajo Fin de Máster, centrado en sistemas multiagente, IA generativa y comunicación entre servicios (MCP + A2A).</p>

      <p style="margin-top:10px">Hecho con ❤️ para que lo enciendas, explores y sigas ampliándolo.</p>
    </section>

    <footer>
      <p>Documento generado para uso técnico — adaptalo libremente a tu README o documentación.</p>
    </footer>
  </div>
</body>
</html>