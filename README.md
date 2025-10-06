💬 Chat Multiagente — Demo local
Este proyecto es una demo funcional de un chatbot multiagente con persistencia de conversaciones y soporte de voz. Incluye un backend FastAPI y un frontend en Next.js (React).

💡 Objetivo: que cualquier persona, incluso sin experiencia técnica, pueda ejecutar el proyecto fácilmente.

🚀 Requisitos previos
Antes de comenzar, asegúrate de tener instalado:

Python 3.10 o superior

Node.js 18+ y npm

Git

Puedes comprobarlo ejecutando:

Bash

python --version
node --version
npm --version
🧱 1. Clonar el proyecto
Abre una terminal (PowerShell, Terminal, o similar) y ejecuta:

Bash

git clone https://github.com/TU_USUARIO/chat-multiagent.git
cd chat-multiagent
⚙️ 2. Configurar y ejecutar el Backend
📁 Ir al backend
Bash

cd backend
🐍 Crear y activar el entorno virtual
Bash

python -m venv .venv
.\.venv\Scripts\activate     # En Windows
# source .venv/bin/activate    # En Mac / Linux
📦 Instalar dependencias
Bash

pip install -r requirements.txt
🔑 Crear archivo .env
Crea un archivo .env dentro de la carpeta backend con este contenido:

Bash

OPENAI_API_KEY=tu_clave_de_openai_aqui
Si no tienes una, crea una en https://platform.openai.com.

▶️ Ejecutar el backend
Bash

uvicorn main:app --reload --port 8000
El backend quedará disponible en:

👉 http://127.0.0.1:8000

💻 3. Configurar y ejecutar el Frontend
Abre otra terminal (deja el backend corriendo) y navega al frontend:

Bash

cd ../frontend
📦 Instalar dependencias
Bash

npm install
⚙️ Crear archivo .env.local
Crea un archivo .env.local dentro de frontend con el siguiente contenido:

Bash

NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
▶️ Ejecutar el frontend
Bash

npm run dev
Luego abre tu navegador en:

👉 http://localhost:3000

🎤 Funcionalidades principales
✅ Chat persistente por usuario

✅ Creación y selección de conversaciones

✅ Envío de mensajes de texto y voz

✅ Respuestas automáticas simuladas por IA

✅ Interfaz visual moderna con scroll inteligente y animaciones suaves

🧩 Estructura del proyecto
chat-multiagent/
│
├── backend/      → API con FastAPI
│   ├── main.py
│   ├── app/routers/chat.py
│   ├── requirements.txt
│   └── .env
│
└── frontend/     → Interfaz con Next.js
    ├── components/Chat.tsx
    ├── src/app/page.tsx
    └── .env.local
🛠️ Comandos útiles
Acción	Comando
Iniciar backend	uvicorn main:app --reload --port 8000
Instalar dependencias backend	pip install -r requirements.txt
Iniciar frontend	npm run dev
Instalar dependencias frontend	npm install

Exportar a Hojas de cálculo
🧠 Notas finales
Las conversaciones se guardan automáticamente en /backend/data/convos/. Puedes limpiar el historial borrando esa carpeta.

La clave de OpenAI se usa para transcribir audios (modelo Whisper) y generar respuestas.

El proyecto es 100% local y no envía tus datos a servidores externos (salvo la API de OpenAI si usas transcripción).
