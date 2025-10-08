<!-- README HTML version for GitHub rendering -->
<h1>💬 Chat Multiagente — Demo Local</h1>

<p align="center">
  <a href="https://github.com/carlosvegag1/chat-multiagent">
    <img src="https://img.shields.io/badge/GitHub-Chat_Multiagente-blue?logo=github" alt="GitHub">
  </a>
</p>

<blockquote>
  <strong>⚙️ Demo funcional de un chatbot multiagente</strong> con persistencia de conversaciones, soporte de voz y arquitectura <strong>FastAPI + Next.js (React)</strong>.
</blockquote>

<hr />

<h2>💡 Objetivo</h2>
<p>Permitir que <strong>cualquier persona, incluso sin experiencia técnica</strong>, pueda ejecutar el proyecto en su propio equipo paso a paso.</p>

<hr />

<h2>🚀 Requisitos previos</h2>
<p>Antes de comenzar, asegúrate de tener instalado:</p>
<ul>
  <li>🐍 <strong>Python 3.10 o superior</strong></li>
  <li>🧩 <strong>Node.js 18+</strong> y <strong>npm</strong></li>
  <li>🔧 <strong>Git</strong></li>
</ul>
<p>Comprueba las versiones ejecutando:</p>
<pre><code>python --version
node --version
npm --version
</code></pre>

<hr />

<h2>🧱 1. Clonar el proyecto</h2>
<p>Abre una terminal (PowerShell, Terminal o similar) y ejecuta:</p>
<pre><code>git clone https://github.com/carlosvegag1/chat-multiagent.git
cd chat-multiagent
</code></pre>

<hr />

<h2>⚙️ 2. Configurar y ejecutar el Backend</h2>
<p>📁 Ir al backend:</p>
<pre><code>cd backend
</code></pre>

<p>🐍 Crear y activar el entorno virtual:</p>
<pre><code>python -m venv .venv
.\.venv\Scripts\activate     # En Windows
# o
source .venv/bin/activate     # En Mac / Linux
</code></pre>

<p>📦 Instalar dependencias:</p>
<pre><code>pip install -r requirements.txt
</code></pre>

<p>🔑 Crear archivo <code>.env</code> dentro de <code>/backend</code>:</p>
<pre><code>OPENAI_API_KEY=tu_clave_de_openai_aqui
</code></pre>
<p>Si no tienes una clave, crea una en 👉 <a href="https://platform.openai.com" target="_blank" rel="noreferrer">OpenAI API Keys</a>.</p>

<p>▶️ Ejecutar el backend:</p>
<pre><code>uvicorn main:app --reload --port 8000
</code></pre>
<p>📍 El backend quedará disponible en:<br><strong>http://127.0.0.1:8000</strong></p>

<hr />

<h2>💻 3. Configurar y ejecutar el Frontend</h2>
<p>Abre otra terminal (deja el backend corriendo) y navega al frontend:</p>
<pre><code>cd ../frontend
</code></pre>

<p>📦 Instalar dependencias:</p>
<pre><code>npm install
</code></pre>

<p>⚙️ Crear archivo <code>.env.local</code> dentro de <code>/frontend</code>:</p>
<pre><code>NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
</code></pre>

<p>▶️ Ejecutar el frontend:</p>
<pre><code>npm run dev
</code></pre>
<p>🌐 Luego abre tu navegador en:<br><strong>http://localhost:3000</strong></p>

<hr />

<h2>🎤 Funcionalidades principales</h2>
<ul>
  <li>✅ Chat persistente por usuario</li>
  <li>✅ Creación y selección de conversaciones</li>
  <li>✅ Envío de mensajes de texto y voz</li>
  <li>✅ Respuestas automáticas simuladas por IA</li>
  <li>✅ Interfaz visual moderna con scroll inteligente y animaciones suaves</li>
</ul>

<hr />

<h2>🧩 Estructura del proyecto</h2>
<pre><code>chat-multiagent/
│
├── backend/        → API con FastAPI
│   ├── main.py
│   ├── app/routers/chat.py
│   ├── requirements.txt
│   └── .env
│
└── frontend/       → Interfaz con Next.js
    ├── components/Chat.tsx
    ├── src/app/page.tsx
    └── .env.local
</code></pre>

<hr />

<h2>🛠️ Comandos útiles</h2>
<table style="border-collapse:collapse; width:100%;">
  <thead>
    <tr>
      <th style="border:1px solid #ddd; padding:8px; text-align:left;">Acción</th>
      <th style="border:1px solid #ddd; padding:8px; text-align:left;">Comando</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="border:1px solid #ddd; padding:8px;">Iniciar backend</td>
      <td style="border:1px solid #ddd; padding:8px;"><code>uvicorn main:app --reload --port 8000</code></td>
    </tr>
    <tr>
      <td style="border:1px solid #ddd; padding:8px;">Instalar dependencias backend</td>
      <td style="border:1px solid #ddd; padding:8px;"><code>pip install -r requirements.txt</code></td>
    </tr>
    <tr>
      <td style="border:1px solid #ddd; padding:8px;">Iniciar frontend</td>
      <td style="border:1px solid #ddd; padding:8px;"><code>npm run dev</code></td>
    </tr>
    <tr>
      <td style="border:1px solid #ddd; padding:8px;">Instalar dependencias frontend</td>
      <td style="border:1px solid #ddd; padding:8px;"><code>npm install</code></td>
    </tr>
  </tbody>
</table>

<hr />

<h2>🧠 Notas finales</h2>
<ul>
  <li>🗂️ Las conversaciones se guardan automáticamente en <code>/backend/data/convos/</code>.</li>
  <li>🧹 Puedes limpiar el historial borrando esa carpeta.</li>
  <li>🔐 La clave de OpenAI se usa para <strong>transcribir audios (Whisper)</strong> y <strong>generar respuestas</strong>.</li>
  <li>💻 El proyecto se ejecuta <strong>de forma local</strong> y no envía tus datos a servidores externos (salvo el uso explícito de la API de OpenAI para transcripción).</li>
</ul>

<hr />

<p>🤝 <strong>Autor:</strong> <a href="https://github.com/carlosvegag1">Carlos Vega González</a></p>
