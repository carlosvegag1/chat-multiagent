💬 Chat Multiagente — Demo Local
GitHub

⚙️ Demo funcional de un chatbot multiagente que combina un backend con FastAPI y un frontend con Next.js (React). Permite chatear con agentes inteligentes, guardar las conversaciones y usar voz.
💡 Objetivo
Esta guía está pensada para que cualquier persona, incluso sin experiencia técnica, pueda ejecutar el proyecto paso a paso en su propio ordenador. No necesitas saber programar.

🚀 Antes de empezar
Solo necesitarás instalar tres herramientas. Te explico exactamente cómo hacerlo:

🐍 Python 3.10 o superior → Descargar aquí. Durante la instalación, asegúrate de marcar la casilla “Add Python to PATH”.
🧩 Node.js 18 o superior (incluye npm) → Descargar aquí NO DESCARGAR USANDO DOCKER, DESCARGAR INSTALADOR MSI.
🔧 Git → Descargar aquí.
Una vez instalados, abre tu terminal y comprueba que todo funciona:

python --version
node --version
npm --version
git --version
Si ves los números de versión (por ejemplo, Python 3.12.1), todo está listo ✅.

🧱 Paso 1. Clonar el proyecto
Recomendamos usar Visual Studio Code (VS Code) porque es gratuito y sencillo.

Abre Visual Studio Code.
Presiona Ctrl + Shift/Mayús + Ñ para abrir la terminal integrada.
En esa terminal, ejecuta los siguientes comandos uno por uno:
git clone https://github.com/carlosvegag1/chat-multiagent.git
cd chat-multiagent
Esto descargará el proyecto y entrará en la carpeta correcta.

⚙️ Paso 2. Configurar y ejecutar el Backend
1️⃣ Entra en la carpeta del backend:
cd backend
2️⃣ Crea el entorno virtual (es un espacio aislado para instalar dependencias):
Ejecuta lo siguiente dependiendo de tu sistema operativo:

Windows (VS Code o PowerShell):
python -m venv .venv
.\.venv\Scripts\activate
Mac / Linux:
python3 -m venv .venv
source .venv/bin/activate
Cuando el entorno esté activo, verás algo así al principio de la línea: (.venv).

3️⃣ Instala las dependencias del backend:
pip install -r requirements.txt
4️⃣ Crea el archivo .env:
Dentro de la carpeta backend, crea un nuevo archivo.env y pega este contenido:

OPENAI_API_KEY=tu_clave_de_openai_aqui
Si no tienes una clave, créala gratis en 👉 OpenAI API Keys.

Este archivo puedes crearlo como archivo .txt sin nombre y simplemente cambiarle la extensión

5️⃣ Ejecuta el backend:
uvicorn main:app --reload --port 8000
Deja esta ventana abierta. El backend quedará funcionando en:

➡️ http://127.0.0.1:8000

💻 Paso 3. Configurar y ejecutar el Frontend
1️⃣ Abre una nueva terminal en Visual Studio Code (SIN CERRAR LA ANTERIOR):
Haz clic en el símbolo + en la parte superior de la terminal o usa Ctrl + Shift/Mayús + Ñ.

2️⃣ Entra en la carpeta del frontend:
cd ../frontend
3️⃣ Instala las dependencias:
npm install
4️⃣ Crea el archivo .env.local:
Dentro de la carpeta frontend, crea un archivo llamado .env.local con este contenido:

NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
5️⃣ Ejecuta el frontend:
npm run dev
Luego abre tu navegador y entra en:

➡️ http://localhost:3000

🎤 Funcionalidades principales
✅ Chat persistente por usuario (guarda tus conversaciones)
✅ Creación y selección de conversaciones
✅ Envío de mensajes de texto y voz
✅ Respuestas automáticas simuladas por IA
✅ Interfaz visual moderna con scroll inteligente y animaciones suaves
🧩 Estructura del proyecto
chat-multiagent/
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
🛠️ Comandos útiles
Acción	Comando
Iniciar backend	uvicorn main:app --reload --port 8000
Instalar dependencias backend	pip install -r requirements.txt
Iniciar frontend	npm run dev
Instalar dependencias frontend	npm install
🧠 Notas finales
🗂️ Las conversaciones se guardan automáticamente en /backend/data/convos/.
🧹 Puedes limpiar el historial borrando esa carpeta.
🔐 La clave de OpenAI se usa solo para transcribir audios (Whisper) y simular respuestas.
💻 El proyecto se ejecuta totalmente de forma local (solo se conecta con OpenAI si activas la transcripción de voz).
Autor: Carlos Vega González
