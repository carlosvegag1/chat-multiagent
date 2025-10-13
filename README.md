<h1>💬 Chat Multiagente — Demo Local</h1>

<p>
  <a href="https://github.com/carlosvegag1/chat-multiagent" target="_blank"><strong>🌐 GitHub</strong></a>
</p>

<p>⚙️ Demo funcional de un chatbot multiagente que combina un <strong>backend con FastAPI</strong> y un <strong>frontend con Next.js (React)</strong>.  
Permite chatear con agentes inteligentes, guardar las conversaciones y usar voz.</p>

<h2>💡 Objetivo</h2>
<p>Esta guía está pensada para que cualquier persona, incluso sin experiencia técnica, pueda ejecutar el proyecto paso a paso en su propio ordenador.  
<strong>No necesitas saber programar.</strong></p>

<hr>

<h2>🚀 Antes de empezar</h2>
<p>Solo necesitarás instalar tres herramientas. Te explico exactamente cómo hacerlo:</p>

<ul>
  <li>🐍 <strong>Python 3.10 o superior</strong> → <a href="https://www.python.org/downloads/" target="_blank">Descargar aquí</a>.  
  Durante la instalación, asegúrate de marcar la casilla <em>“Add Python to PATH”</em>.</li>
  <li>🧩 <strong>Node.js 18 o superior</strong> (incluye npm) → 
  <a href="https://nodejs.org/en/download/" target="_blank">Descargar aquí</a> <strong>(NO DESCARGAR USANDO DOCKER, DESCARGAR INSTALADOR MSI)</strong>.</li>
  <li>🔧 <strong>Git</strong> → <a href="https://git-scm.com/downloads" target="_blank">Descargar aquí</a>.</li>
</ul>

<p>Una vez instalados, abre tu terminal y comprueba que todo funciona:</p>

<pre><code>python --version
node --version
npm --version
git --version
</code></pre>

<p>Si ves los números de versión (por ejemplo, <code>Python 3.12.1</code>), todo está listo ✅.</p>

<hr>

<h2>🧱 Paso 1. Clonar el proyecto</h2>
<p>Recomendamos usar <strong>Visual Studio Code (VS Code)</strong> porque es gratuito y sencillo.</p>

<ol>
  <li>Abre Visual Studio Code.</li>
  <li>Presiona <kbd>Ctrl + Shift + Ñ</kbd> para abrir la terminal integrada.</li>
  <li>En esa terminal, ejecuta los siguientes comandos uno por uno:</li>
</ol>

<pre><code>git clone https://github.com/carlosvegag1/chat-multiagent.git
cd chat-multiagent
</code></pre>

<p>Esto descargará el proyecto y entrará en la carpeta correcta.</p>

<hr>

<h2>⚙️ Paso 2. Configurar y ejecutar el Backend</h2>

<ol>
  <li><strong>Entra en la carpeta del backend:</strong><br>
  <pre><code>cd backend</code></pre></li>

  <li><strong>Crea el entorno virtual:</strong><br>
  <p>Ejecuta lo siguiente dependiendo de tu sistema operativo:</p>

  <p><strong>Windows (VS Code o PowerShell):</strong></p>
  <pre><code>python -m venv .venv
.\.venv\Scripts\activate
</code></pre>

  <p><strong>Mac / Linux:</strong></p>
  <pre><code>python3 -m venv .venv
source .venv/bin/activate
</code></pre>

  <p>Cuando el entorno esté activo, verás algo así al principio de la línea: <code>(.venv)</code>.</p>
  </li>

  <li><strong>Instala las dependencias del backend:</strong><br>
  <pre><code>pip install -r requirements.txt</code></pre></li>

  <li><strong>Crea el archivo <code>.env</code>:</strong><br>
  Dentro de la carpeta <code>backend</code>, crea un nuevo archivo llamado <code>.env</code> y pega este contenido:</li>

  <pre><code>OPENAI_API_KEY=tu_clave_de_openai_aqui</code></pre>

  <p>Si no tienes una clave, créala gratis en 👉 
  <a href="https://platform.openai.com/account/api-keys" target="_blank">OpenAI API Keys</a>.</p>

  <p><em>Consejo:</em> puedes crear un archivo .txt y luego cambiarle la extensión a <code>.env</code>.</p>

  <li><strong>Ejecuta el backend:</strong><br>
  <pre><code>uvicorn main:app --reload --port 8000</code></pre>
  <p>Deja esta ventana abierta. El backend quedará funcionando en:<br>
  ➡️ <a href="http://127.0.0.1:8000" target="_blank">http://127.0.0.1:8000</a></p></li>
</ol>

<hr>

<h2>💻 Paso 3. Configurar y ejecutar el Frontend</h2>

<ol>
  <li><strong>Abre una nueva terminal en Visual Studio Code</strong> (sin cerrar la anterior).  
  Haz clic en el símbolo <code>+</code> o usa <kbd>Ctrl + Shift + Ñ</kbd>.</li>

  <li><strong>Entra en la carpeta del frontend:</strong><br>
  <pre><code>cd ../frontend</code></pre></li>

  <li><strong>Instala las dependencias:</strong><br>
  <pre><code>npm install</code></pre></li>

  <li><strong>Crea el archivo <code>.env.local</code>:</strong><br>
  Dentro de la carpeta frontend, crea un archivo llamado <code>.env.local</code> con este contenido:</li>

  <pre><code>NEXT_PUBLIC_API_URL=http://127.0.0.1:8000</code></pre>

  <li><strong>Ejecuta el frontend:</strong><br>
  <pre><code>npm run dev</code></pre>
  <p>Luego abre tu navegador y entra en:<br>
  ➡️ <a href="http://localhost:3000" target="_blank">http://localhost:3000</a></p></li>
</ol>

<hr>

<h2>🎤 Funcionalidades principales</h2>
<ul>
  <li>✅ Chat persistente por usuario (guarda tus conversaciones)</li>
  <li>✅ Creación y selección de conversaciones</li>
  <li>✅ Envío de mensajes de texto y voz</li>
  <li>✅ Respuestas automáticas simuladas por IA</li>
  <li>✅ Interfaz visual moderna con scroll inteligente y animaciones suaves</li>
</ul>

<hr>

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

<hr>

<h2>🛠️ Comandos útiles</h2>

<table>
  <thead>
    <tr>
      <th>Acción</th>
      <th>Comando</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Iniciar backend</td>
      <td><code>uvicorn main:app --reload --port 8000</code></td>
    </tr>
    <tr>
      <td>Instalar dependencias backend</td>
      <td><code>pip install -r requirements.txt</code></td>
    </tr>
    <tr>
      <td>Iniciar frontend</td>
      <td><code>npm run dev</code></td>
    </tr>
    <tr>
      <td>Instalar dependencias frontend</td>
      <td><code>npm install</code></td>
    </tr>
  </tbody>
</table>

<hr>

<h2>🧠 Notas finales</h2>
<ul>
  <li>🗂️ Las conversaciones se guardan automáticamente en <code>/backend/data/convos/</code>.</li>
  <li>🧹 Puedes limpiar el historial borrando esa carpeta.</li>
  <li>🔐 La clave de OpenAI se usa solo para transcribir audios (Whisper) y simular respuestas.</li>
  <li>💻 El proyecto se ejecuta totalmente de forma local (solo se conecta con OpenAI si activas la transcripción de voz).</li>
</ul>

<p><strong>Autor:</strong> Carlos Vega González</p>
