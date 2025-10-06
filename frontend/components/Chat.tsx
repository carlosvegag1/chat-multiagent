"use client";

import { useState, useRef, useEffect } from "react";

type Message = { role: "user" | "bot"; text: string; timestamp?: string };
type Convo = { convo_id: string; created_at: string; title?: string };

export default function ChatV2() {
  const [userName, setUserName] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");
  const [convoId, setConvoId] = useState<string | null>(null);
  const [availableConvos, setAvailableConvos] = useState<Convo[]>([]);
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [botTyping, setBotTyping] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const chatContainerRef = useRef<HTMLDivElement | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  // 🔹 Al cargar: pedir nombre de usuario
  useEffect(() => {
    const saved = localStorage.getItem("chatUserName");
    if (saved) setUserName(saved);
    else {
      const name = prompt("¡Bienvenido! ¿Cómo te llamas?");
      if (name) {
        localStorage.setItem("chatUserName", name);
        setUserName(name);
      }
    }
  }, []);

  // 🔹 Cargar conversaciones previas
  useEffect(() => {
    if (!userName) return;
    fetch(`${API_URL}/convos?user=${encodeURIComponent(userName)}`)
      .then((r) => r.json())
      .then(async (data) => {
        if (data.length === 0) {
          const res = await fetch(`${API_URL}/new_convo`, {
            method: "POST",
            body: new URLSearchParams({ user: userName }),
          });
          const newConvo = await res.json();
          setConvoId(newConvo.convo_id);
          setAvailableConvos([newConvo]);
        } else {
          setAvailableConvos(data);
          setConvoId(data[0].convo_id);
        }
      })
      .catch(() => console.warn("No se pudieron cargar las conversaciones."));
  }, [userName]);

  // 🔹 Cargar mensajes de la conversación activa
  useEffect(() => {
    if (!convoId) return;
    fetch(`${API_URL}/convo/${convoId}`)
      .then((r) => r.json())
      .then((data) => {
        if (data && data.messages) {
          const mapped = data.messages.map((m: any) => ({
            role: m.role === "bot" ? "bot" : "user",
            text: m.text,
            timestamp: new Date(m.ts * 1000).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
          }));
          setMessages(mapped);
        } else setMessages([]);
      });
  }, [convoId]);

  // 🔹 Scroll automático
  useEffect(() => {
    if (!messagesEndRef.current || !chatContainerRef.current) return;
    const container = chatContainerRef.current;
    const nearBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight < 100;
    if (nearBottom || messages.length > 5) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // 🔹 Enviar texto
  const sendText = async () => {
    if (!text || !convoId || !userName) return;
    const timestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages((p) => [...p, { role: "user", text, timestamp }]);
    setText("");
    setBotTyping(true);

    try {
      const form = new FormData();
      form.append("message", text);
      form.append("convo_id", convoId);
      form.append("user", userName);

      const res = await fetch(`${API_URL}/chat/`, { method: "POST", body: form });
      const data = await res.json();

      setMessages((p) => [
        ...p,
        {
          role: "bot",
          text: data.reply || "[Sin respuesta del bot]",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch {
      setMessages((p) => [...p, { role: "bot", text: "[Error de conexión con el servidor]" }]);
    }
    setBotTyping(false);
  };

  // 🔹 Audio
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      mediaRecorderRef.current = mr;
      chunksRef.current = [];
      mr.ondataavailable = (e) => chunksRef.current.push(e.data);
      mr.onstop = async () => {
        if (!userName || !convoId) return;
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setMessages((p) => [...p, { role: "user", text: "(voz — enviando...)" }]);
        setTranscribing(true);
        const fd = new FormData();
        fd.append("file", blob, "rec.webm");
        fd.append("convo_id", convoId);
        fd.append("user", userName);
        setBotTyping(true);
        try {
          const res = await fetch(`${API_URL}/chat/audio`, { method: "POST", body: fd });
          const data = await res.json();
          setMessages((p) => [
            ...p.filter((m) => m.text !== "(voz — enviando...)"),
            { role: "user", text: data.transcription },
            { role: "bot", text: data.reply },
          ]);
        } catch {
          setMessages((p) => [
            ...p.filter((m) => m.text !== "(voz — enviando...)"),
            { role: "bot", text: "[Error enviando audio]" },
          ]);
        }
        setTranscribing(false);
        setRecording(false);
        setBotTyping(false);
      };
      mr.start();
      setRecording(true);
    } catch {
      alert("No se pudo acceder al micrófono.");
    }
  };
  const stopRecording = () => mediaRecorderRef.current?.stop();

  // 🔹 Crear nueva conversación
  const createNewConvo = async () => {
    if (!userName) return;
    const res = await fetch(`${API_URL}/new_convo`, {
      method: "POST",
      body: new URLSearchParams({ user: userName }),
    });
    const newConvo = await res.json();
    setAvailableConvos((p) => [newConvo, ...p]);
    setConvoId(newConvo.convo_id);
    setMessages([]);
  };

  // -------------------------------------------------------------------

  return (
    <div className="flex flex-col w-[1000px] h-screen bg-gradient-to-b from-slate-50 to-slate-100 shadow-lg mx-auto overflow-hidden">
      {/* HEADER */}
      <header className="fixed top-0 left-1/2 -translate-x-1/2 flex items-center justify-between w-[1000px] h-[88px] p-6 bg-white border-b border-slate-200 z-20">
        <h1 className="text-2xl font-bold text-slate-800">
          Bienvenido{userName ? `, ${userName}` : ""} 👋
        </h1>
        <div className="flex gap-2 items-center">
          <select
            value={convoId ?? ""}
            onChange={(e) => setConvoId(e.target.value)}
            className="border rounded-lg p-2"
          >
            {availableConvos.map((c) => (
              <option key={c.convo_id} value={c.convo_id}>
                {c.title
                  ? c.title
                  : new Date(c.created_at).toLocaleString([], {
                      dateStyle: "short",
                      timeStyle: "short",
                    })}
              </option>
            ))}
          </select>
          <button
            onClick={createNewConvo}
            className="px-3 py-2 bg-indigo-600 text-white rounded-full text-sm font-bold hover:bg-indigo-700 transition"
          >
            Nueva
          </button>
        </div>
      </header>

      {/* MAIN CHAT */}
      <main
        ref={chatContainerRef}
        className="flex flex-col flex-1 w-full px-12 py-6 gap-3 overflow-y-auto mt-[88px] mb-[120px]"
        style={{ height: "calc(100vh - 208px)" }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
          >
            <div className="flex items-start gap-2">
              {m.role === "bot" && (
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-200 to-indigo-400 flex items-center justify-center text-indigo-900 font-bold">
                  B
                </div>
              )}
              <div
                className={`p-3 rounded-2xl max-w-[400px] break-words shadow-md ${
                  m.role === "user"
                    ? "bg-gradient-to-r from-indigo-600 to-indigo-400 text-white self-end"
                    : "bg-white border border-slate-200 text-slate-800"
                }`}
              >
                <p className="text-sm font-medium">{m.text}</p>
                {m.timestamp && (
                  <div
                    className={`text-xs mt-1 text-right ${
                      m.role === "user" ? "text-white/80" : "text-slate-500"
                    }`}
                  >
                    {m.timestamp}
                  </div>
                )}
              </div>
              {m.role === "user" && <div className="w-10 h-10 rounded-full bg-gray-300"></div>}
            </div>
          </div>
        ))}

        {botTyping && (
          <div className="flex justify-start animate-pulse gap-2 mt-1">
            <div className="w-10 h-10 rounded-full bg-indigo-200 flex items-center justify-center text-indigo-900 font-bold">
              B
            </div>
            <div className="p-3 rounded-2xl bg-white text-slate-700 shadow-sm">
              <span>Bot está escribiendo...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* FOOTER */}
      <footer className="fixed bottom-0 left-1/2 -translate-x-1/2 w-[1000px] p-6 bg-white border-t border-slate-200 z-20">
        <div className="flex gap-2">
          <input
            className="flex-1 p-3 border rounded-2xl"
            placeholder="Envía un mensaje..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendText()}
          />
          <button
            onClick={sendText}
            className="px-4 py-2.5 bg-indigo-600 rounded-full text-white font-bold hover:bg-indigo-700 transition"
          >
            Enviar
          </button>
          <button
            onClick={recording ? stopRecording : startRecording}
            className={`w-10 h-10 rounded-full text-white transition ${
              recording ? "bg-red-500 hover:bg-red-600" : "bg-blue-500 hover:bg-blue-600"
            }`}
          >
            {recording ? "⏹" : "🎙️"}
          </button>
        </div>
        {transcribing && <div className="text-gray-600 italic mt-2">Transcribiendo audio...</div>}
      </footer>
    </div>
  );
}
