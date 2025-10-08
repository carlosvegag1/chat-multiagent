<!-- README HTML version — Guía 100% para principiantes -->
<h1>💬 Chat Multiagente — Demo Local</h1>

<p align="center">
  <a href="https://github.com/carlosvegag1/chat-multiagent">
    <img src="https://img.shields.io/badge/GitHub-Chat_Multiagente-blue?logo=github" alt="GitHub">
  </a>
</p>

<blockquote>
  <strong>⚙️ Demo funcional de un chatbot multiagente</strong> que combina un <strong>backend con FastAPI</strong> y un <strong>frontend con Next.js (React)</strong>. Permite chatear con agentes inteligentes, guardar las conversaciones y usar voz.
</blockquote>

<hr />

<h2>💡 Objetivo</h2>
<p>Esta guía está pensada para que <strong>cualquier persona, incluso sin experiencia técnica</strong>, pueda ejecutar el proyecto paso a paso en su propio ordenador. No necesitas saber programar.</p>

<hr />

<h2>🚀 Antes de empezar</h2>
<p>Solo necesitarás instalar tres herramientas. Te explico exactamente cómo hacerlo:</p>

<ol>
  <li>🐍 <strong>Python 3.10 o superior</strong> → <a href="https://www.python.org/downloads/" target="_blank">Descargar aquí</a>. Durante la instalación, asegúrate de marcar la casilla <strong>“Add Python to PATH”</strong>.</li>
  <li>🧩 <strong>Node.js 18 o superior</strong> (incluye npm) → <a href="https://nodejs.org/en/download" target="_blank">Descargar aquí</a> <strong>NO DESCARGAR USANDO DOCKER, DESCARGAR INSTALADOR MSI</strong>.</li> 
  <li>🔧 <strong>Git</strong> → <a href="https://git-scm.com/downloads" target="_blank">Descargar aquí</a>.</li>
</ol>

<p>Una vez instalados, abre tu terminal y comprueba que todo funciona:</p>
<pre><code>python --version
node --version
npm --version
git --version
</code></pre>

<p>Si ves los números de versión (por ejemplo, <code>Python 3.12.1</code>), todo está listo ✅.</p>

<hr />

<h2>🧱 Paso 1. Clonar el proyecto</h2>
<p>Recomendamos usar <strong>Visual Studio Code (VS Code)</strong> porque es gratuito y sencillo.</p>

<ol>
  <li>Abre <strong>Visual Studio Code</strong>.</li>
  <li>Presiona <strong>Ctrl + Shift/Mayús + Ñ</strong> para abrir la terminal integrada.</li>
  <li>En esa terminal, ejecuta los siguientes comandos uno por uno:</li>
</ol>

<pre><code>git clone https://github.com/carlosvegag1/chat-multiagent.git
cd chat-multiagent
</code></pre>

<p>Esto descargará el proyecto y entrará en la carpeta correcta.</p>

<hr />

<h2>⚙️ Paso 2. Configurar y ejecutar el Backend</h2>

<h3>1️⃣ Entra en la carpeta del backend:</h3>
<pre><code>cd backend</code></pre>

<h3>2️⃣ Crea el entorno virtual (es un espacio aislado para instalar dependencias):</h3>
<p>Ejecuta lo siguiente dependiendo de tu sistema operativo:</p>

<ul>
  <li><strong>Windows (VS Code o PowerShell):</strong></li>
</ul>
<pre><code>python -m venv .venv
.\.venv\Scripts\activate</code></pre>

<ul>
  <li><strong>Mac / Linux:</strong></li>
</ul>
<pre><code>python3 -m venv .venv
source .venv/bin/activate</code></pre>

<p>Cuando el entorno esté activo, verás algo así al principio de la línea: <code>(.venv)</code>.</p>

<h3>3️⃣ Instala las dependencias del backend:</h3>
<pre><code>pip install -r requirements.txt</code></pre>

<h3>4️⃣ Crea el archivo <code>.env</code>:</h3>
<p>Dentro de la carpeta <code>backend</code>, crea un nuevo archivo<code>.env</code> y pega este contenido:</p>
<pre><code>OPENAI_API_KEY=tu_clave_de_openai_aqui</code></pre>
<p>Si no tienes una clave, créala gratis en 👉 <a href="https://platform.openai.com" target="_blank">OpenAI API Keys</a>.</p>
<p>Este archivo puedes crearlo como archivo .txt sin nombre y simplemente cambiarle la extensión</p>

<h3>5️⃣ Ejecuta el backend:</h3>
<pre><code>uvicorn main:app --reload --port 8000</code></pre>

<p>Deja esta ventana abierta. El backend quedará funcionando en:</p>
<p><strong>➡️ http://127.0.0.1:8000</strong></p>

<hr />

<h2>💻 Paso 3. Configurar y ejecutar el Frontend</h2>

<h3>1️⃣ Abre una nueva terminal en Visual Studio Code (SIN CERRAR LA ANTERIOR):</h3>
<p>Haz clic en el símbolo <strong>+</strong> en la parte superior de la terminal o usa <strong>Ctrl + Shift/Mayús + Ñ</strong>.</p>

<h3>2️⃣ Entra en la carpeta del frontend:</h3>
<pre><code>cd ../frontend</code></pre>

<h3>3️⃣ Instala las dependencias:</h3>
<pre><code>npm install</code></pre>

<h3>4️⃣ Crea el archivo <code>.env.local</code>:</h3>
<p>Dentro de la carpeta <code>frontend</code>, crea un archivo llamado <code>.env.local</code> con este contenido:</p>
<pre><code>NEXT_PUBLIC_API_URL=http://127.0.0.1:8000</code></pre>

<h3>5️⃣ Ejecuta el frontend:</h3>
<pre><code>npm run dev</code></pre>

<p>Luego abre tu navegador y entra en:</p>
<p><strong>➡️ http://localhost:3000</strong></p>

<hr />

<h2>🎤 Funcionalidades principales</h2>
<ul>
  <li>✅ Chat persistente por usuario (guarda tus conversaciones)</li>
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
      <th style="border:1px solid #ddd; padding:8px;">Acción</th>
      <th style="border:1px solid #ddd; padding:8px;">Comando</th>
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
  <li>🔐 La clave de OpenAI se usa solo para <strong>transcribir audios (Whisper)</strong> y <strong>simular respuestas</strong>.</li>
  <li>💻 El proyecto se ejecuta <strong>totalmente de forma local</strong> (solo se conecta con OpenAI si activas la transcripción de voz).</li>
</ul>

<hr />

<p><strong>Autor:</strong> <a href="https://github.com/carlosvegag1">Carlos Vega González</a></p>
