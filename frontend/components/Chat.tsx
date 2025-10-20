"use client";

import { useState, useRef, useEffect, FC } from "react";
import ReactMarkdown from "react-markdown";

// --- Tipos de Datos Enriquecidos y Finales ---
type FlightInfo = {
  airline?: string;
  flight_number?: string;
  origin?: string;
  destination?: string;
  departure_time?: string;
  arrival_time?: string;
  duration?: string;
  stops?: number;
  price?: number;
  currency?: string;
};
type HotelInfo = { name?: string; hotelId?: string; rating?: number; address?: string };
type POIInfo = { name?: string; description?: string };
type DailyPlan = { day: number; activities: string[] };
type BudgetInfo = { total?: number; currency?: string };

type StructuredData = {
  city?: string;
  flights?: FlightInfo[];
  hotels?: HotelInfo[];
  pois?: POIInfo[];
  summary?: string;
  plan_sugerido?: DailyPlan[];
  budget?: BudgetInfo;
  error?: string;
};

type Message = { role: "user" | "bot"; text: string; structured_data?: StructuredData; ts: number };
type ConvoSummary = { convo_id: string; created_at: string };

// --- UI Components ---
function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm animate-fade-in">
      <div className="text-slate-700 font-semibold mb-2">{title}</div>
      <div className="text-sm text-slate-700">{children}</div>
    </div>
  );
}

const MarkdownRenderer: FC<{ content: string }> = ({ content }) => (
  <ReactMarkdown
    components={{
      p: ({ node, ...props }) => <p className="text-sm font-medium" {...props} />,
      strong: ({ node, ...props }) => <strong className="font-bold" {...props} />,
      ul: ({ node, ...props }) => <ul className="list-disc list-inside space-y-1" {...props} />,
      li: ({ node, ...props }) => <li className="pl-2" {...props} />,
    }}
  >
    {content}
  </ReactMarkdown>
);

// --- Subcomponentes visuales ---
function FlightCard({ flight }: { flight: FlightInfo }) {
  const formatTime = (isoString?: string) =>
    isoString ? new Date(isoString).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "?";
  return (
    <div className="border border-slate-200 bg-slate-50/80 rounded-xl p-3 flex items-center justify-between gap-4">
      <div className="flex flex-col">
        <span className="font-bold text-slate-800">{flight.airline || "Aerolínea"}</span>
        <span className="text-xs text-slate-500">{flight.flight_number}</span>
      </div>
      <div className="text-center">
        <span className="font-mono text-lg font-semibold text-slate-900">
          {flight.origin} → {flight.destination}
        </span>
        <div className="text-sm text-slate-600">
          {formatTime(flight.departure_time)} - {formatTime(flight.arrival_time)}
        </div>
      </div>
      <div className="text-right">
        <span className="text-lg font-bold text-indigo-600">
          {flight.price?.toFixed(2) || "?"} {flight.currency}
        </span>
        <div className="text-xs text-slate-500">{flight.duration}</div>
      </div>
    </div>
  );
}

function HotelCard({ hotel }: { hotel: HotelInfo }) {
  return (
    <div className="border border-slate-200 bg-slate-50/80 rounded-xl p-3">
      <div className="flex justify-between items-start">
        <span className="font-bold text-slate-800">{hotel.name}</span>
        {hotel.rating && (
          <span className="text-sm font-semibold bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
            {hotel.rating} ⭐
          </span>
        )}
      </div>
      {hotel.address && <p className="text-xs text-slate-500 mt-1">{hotel.address}</p>}
    </div>
  );
}

function FlightsList({ city, flights }: { city?: string; flights?: FlightInfo[] }) {
  if (!flights?.length) return null;
  return (
    <SectionCard title={`✈️ Vuelos a ${city || "tu destino"}`}>
      <div className="flex flex-col gap-2">{flights.map((f, i) => <FlightCard key={i} flight={f} />)}</div>
    </SectionCard>
  );
}

function HotelsList({ city, hotels }: { city?: string; hotels?: HotelInfo[] }) {
  if (!hotels?.length) return null;
  return (
    <SectionCard title={`🏨 Hoteles en ${city || "tu destino"}`}>
      <div className="flex flex-col gap-2">{hotels.map((h, i) => <HotelCard key={i} hotel={h} />)}</div>
    </SectionCard>
  );
}

function PoisList({ pois }: { pois?: POIInfo[] }) {
  if (!pois?.length) return null;
  return (
    <SectionCard title="📍 Lugares recomendados">
      <ul className="list-disc list-inside space-y-1">
        {pois.map((p, i) => (
          <li key={i}>
            <span className="font-medium">{p.name}</span>
            {p.description ? <span className="text-slate-500"> — {p.description}</span> : null}
          </li>
        ))}
      </ul>
    </SectionCard>
  );
}

function SummaryBox({ summary }: { summary?: string }) {
  if (!summary) return null;
  return (
    <SectionCard title="🧭 Resumen del destino">
      <p className="leading-relaxed">{summary}</p>
    </SectionCard>
  );
}

function PlanCard({ plan }: { plan?: DailyPlan[] }) {
  if (!plan?.length) return null;
  return (
    <SectionCard title="🗓️ Plan de viaje sugerido">
      <div className="flex flex-col gap-3">
        {plan.map((d) => (
          <div key={d.day} className="rounded-xl border border-slate-200 p-3 bg-slate-50/80">
            <div className="font-semibold mb-1 text-slate-800">Día {d.day}</div>
            <ul className="list-disc list-inside space-y-1 text-slate-600">
              {d.activities.map((a, i) => <li key={i}>{a}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

function BudgetBadge({ budget }: { budget?: BudgetInfo }) {
  if (!budget?.total) return null;
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm font-semibold">
      💰 Presupuesto estimado: {budget.total.toFixed(2)} {budget.currency || "EUR"}
    </div>
  );
}

function ErrorCard({ error }: { error?: string }) {
  if (!error) return null;
  return (
    <div className="bg-red-50 border border-red-200 rounded-2xl p-4 shadow-sm text-red-700">
      <div className="font-semibold mb-1">⚠️ Ocurrió un error</div>
      <p>{error}</p>
    </div>
  );
}

// --- Onda de audio ---
const VoiceVisualizer: FC<{ analyser: AnalyserNode | null; active: boolean }> = ({ analyser, active }) => {
  const [bars, setBars] = useState<number[]>(Array(20).fill(0));
  const animationRef = useRef<number>();

  useEffect(() => {
    if (!active || !analyser) return;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const draw = () => {
      analyser.getByteFrequencyData(dataArray);
      const slice = Array.from(dataArray.slice(0, 20)).map((v) => Math.max(5, (v / 255) * 40));
      setBars(slice);
      animationRef.current = requestAnimationFrame(draw);
    };
    draw();
    return () => animationRef.current && cancelAnimationFrame(animationRef.current);
  }, [active, analyser]);

  if (!active) return null;

  return (
    <div className="mt-4 text-center text-slate-600 font-medium">
      <div className="flex justify-center items-end gap-1 h-10">
        {bars.map((h, i) => (
          <div key={i} className="w-1 bg-indigo-500 rounded transition-all duration-75" style={{ height: `${h}px` }} />
        ))}
      </div>
      <p className="mt-2 text-sm animate-pulse">🎤 Grabando... habla ahora</p>
    </div>
  );
};
// ---------------- COMPONENTE PRINCIPAL ----------------
export default function Chat() {
  const [userName, setUserName] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");
  const [convoId, setConvoId] = useState<string | null>(null);
  const [availableConvos, setAvailableConvos] = useState<(ConvoSummary & { preview?: string })[]>([]);
  const [botTyping, setBotTyping] = useState(false);
  const [recording, setRecording] = useState(false);
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  // ---- Inicialización usuario ----
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

  const fetchConvos = async (user: string) => {
    try {
      const res = await fetch(`${API_URL}/convos?user=${encodeURIComponent(user)}`);
      const data: ConvoSummary[] = await res.json();

      // Obtener previews del primer mensaje de cada conversación
      const enriched = await Promise.all(
        data.map(async (c) => {
          try {
            const convoRes = await fetch(`${API_URL}/convo/${c.convo_id}`);
            const convoData = await convoRes.json();
            const firstMsg = convoData.messages?.find((m: Message) => m.role === "user")?.text || "Conversación vacía";
            return { ...c, preview: firstMsg.slice(0, 40) + (firstMsg.length > 40 ? "…" : "") };
          } catch {
            return { ...c, preview: "Error al cargar" };
          }
        })
      );

      setAvailableConvos(enriched);
      if (!convoId && enriched.length) setConvoId(enriched[0].convo_id);
    } catch (error) {
      console.error("Error al cargar conversaciones:", error);
    }
  };

  useEffect(() => { if (userName) fetchConvos(userName); }, [userName]);

  const createNewConvo = async () => {
    if (!userName) return;
    const form = new FormData();
    form.append("user", userName);
    const res = await fetch(`${API_URL}/new_convo`, { method: "POST", body: form });
    const data = await res.json();
    setAvailableConvos((prev) => [data, ...prev]);
    setConvoId(data.convo_id);
    setMessages([]);
  };

  const loadConvo = async (id: string) => {
    try {
      const res = await fetch(`${API_URL}/convo/${id}`);
      const data = await res.json();
      setConvoId(id);
      setMessages(data.messages || []);
      setSidebarOpen(false);
    } catch (err) {
      console.error("Error al cargar conversación:", err);
    }
  };

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  const sendText = async () => {
    if (!text.trim() || !convoId || !userName) return;
    const userMessage: Message = { role: "user", text, ts: Date.now() / 1000 };
    setMessages((prev) => [...prev, userMessage]);
    setText("");
    setBotTyping(true);
    try {
      const form = new FormData();
      form.append("message", text);
      form.append("convo_id", convoId);
      form.append("user", userName);
      const res = await fetch(`${API_URL}/chat/`, { method: "POST", body: form });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.reply_text, structured_data: data.structured_data, ts: Date.now() / 1000 },
      ]);
    } finally { setBotTyping(false); }
  };

  // ---- Grabación y transcripción ----
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyserNode = audioContext.createAnalyser();
      analyserNode.fftSize = 256;
      source.connect(analyserNode);
      setAnalyser(analyserNode);
      audioContextRef.current = audioContext;
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];
      setRecording(true);

      mediaRecorder.ondataavailable = (e) => e.data.size > 0 && chunksRef.current.push(e.data);

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("file", blob, "audio.webm");
        formData.append("user", userName || "demo");
        formData.append("convo_id", convoId || "");

        setMessages((prev) => [...prev, { role: "user", text: "🎙️ Procesando audio...", ts: Date.now() / 1000 }]);
        try {
          const res = await fetch(`${API_URL}/chat/audio`, { method: "POST", body: formData });
          const data = await res.json();

          const transcriptionText = data.transcription?.trim()
            ? `🎧 **Transcripción detectada:** ${data.transcription}`
            : "🎧 No se pudo detectar voz o texto claro.";

          const replyText = data.reply_text?.trim()
            ? data.reply_text
            : "No he entendido bien tu petición. Puedo planificar viajes, buscar vuelos u hoteles, y darte información sobre tu destino.";

          setMessages((prev) => [
            ...prev.filter((m) => m.text !== "🎙️ Procesando audio..."),
            { role: "user", text: transcriptionText, ts: Date.now() / 1000 },
            { role: "bot", text: replyText, structured_data: data.structured_data, ts: Date.now() / 1000 },
          ]);
        } catch (err) {
          console.error("Error al enviar audio:", err);
        } finally {
          if (audioContextRef.current) audioContextRef.current.close();
          setAnalyser(null);
        }
      };

      mediaRecorder.start();
    } catch (err) {
      console.error("Error al iniciar grabación:", err);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  // ---- Render principal ----
  return (
    <div className="flex w-full h-screen bg-gradient-to-b from-slate-50 to-slate-100 relative overflow-hidden">
      {/* === SIDEBAR === */}
      <aside
        className={`absolute top-0 left-0 h-full bg-white shadow-xl border-r border-slate-200 w-80 transform transition-transform duration-300 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-80"
        } z-30`}
      >
        <div className="p-4 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-800">💬 Conversaciones</h2>
          <button onClick={toggleSidebar} className="text-slate-500 hover:text-slate-800 text-xl">✖</button>
        </div>
        <div className="overflow-y-auto h-[calc(100%-60px)]">
          {availableConvos.length === 0 ? (
            <p className="p-4 text-slate-500 text-sm">Sin conversaciones previas.</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {availableConvos.map((c) => (
                <li
                  key={c.convo_id}
                  onClick={() => loadConvo(c.convo_id)}
                  className={`p-4 hover:bg-indigo-50 cursor-pointer ${
                    convoId === c.convo_id ? "bg-indigo-100" : ""
                  }`}
                >
                  <p className="text-sm font-semibold text-slate-800">
                    {new Date(c.created_at).toLocaleString("es-ES", {
                      day: "2-digit",
                      month: "2-digit",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-1">{c.preview}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>

      {/* === CONTENIDO PRINCIPAL === */}
      <div className="flex flex-col flex-1 relative">
        <header className="flex items-center justify-between h-[88px] px-6 bg-white border-b border-slate-200 z-20">
          <div className="flex items-center gap-3">
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-lg border border-slate-300 hover:bg-slate-100 text-slate-700"
            >
              ☰
            </button>
            <h1 className="text-2xl font-bold text-slate-800">
              Bienvenido{userName ? `, ${userName}` : ""} 👋
            </h1>
          </div>

          <button
            onClick={() => createNewConvo()}
            className="px-3 py-2 bg-indigo-600 text-white rounded-full text-sm font-bold hover:bg-indigo-700 transition"
          >
            Nueva conversación
          </button>
        </header>

        {/* Chat principal */}
        <main className="flex flex-col flex-1 w-full px-12 py-6 gap-3 overflow-y-auto mb-[120px]">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "bot" ? "justify-start" : "justify-end"} animate-fade-in`}>
              <div className="flex items-start gap-2 w-full max-w-[750px]">
                {m.role === "bot" && <img src="/icons/bot.svg" alt="Bot" className="w-10 h-10 rounded-full border border-slate-300" />}
                <div className="w-full">
                  <div
                    className={`p-3 rounded-2xl break-words shadow-md ${
                      m.role === "user"
                        ? "bg-gradient-to-r from-indigo-600 to-indigo-400 text-white ml-auto"
                        : "bg-white border border-slate-200"
                    }`}
                  >
                    <MarkdownRenderer content={m.text} />
                    {m.role === "bot" && m.structured_data && (
                      <div className="flex flex-col gap-3 mt-3">
                        <FlightsList city={m.structured_data.city} flights={m.structured_data.flights} />
                        <HotelsList city={m.structured_data.city} hotels={m.structured_data.hotels} />
                        <PoisList pois={m.structured_data.pois} />
                        <SummaryBox summary={m.structured_data.summary} />
                        <PlanCard plan={m.structured_data.plan_sugerido} />
                        <BudgetBadge budget={m.structured_data.budget} />
                        <ErrorCard error={m.structured_data.error} />
                      </div>
                    )}
                  </div>
                </div>
                {m.role === "user" && <img src="/icons/user.svg" alt="Usuario" className="w-10 h-10 rounded-full border border-slate-300" />}
              </div>
            </div>
          ))}
          {botTyping && (
            <div className="flex justify-start animate-pulse gap-2 mt-1">
              <img src="/icons/bot.svg" alt="Bot" className="w-10 h-10 rounded-full border border-slate-300" />
              <div className="p-3 rounded-2xl bg-white text-slate-700 shadow-sm">Bot está escribiendo...</div>
            </div>
          )}
        </main>

        {/* Input */}
        <footer className="absolute bottom-0 left-0 w-full p-6 bg-white border-t border-slate-200 z-20">
          <div className="flex gap-2 items-center">
            <input
              className="flex-1 p-3 border rounded-2xl"
              placeholder="Escribe o graba tu voz..."
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
              className={`w-12 h-12 flex items-center justify-center rounded-full text-white text-2xl transition ${
                recording ? "bg-red-500 animate-pulse" : "bg-blue-500 hover:bg-blue-600"
              }`}
            >
              {recording ? "■" : "🎙️"}
            </button>
          </div>
          <VoiceVisualizer analyser={analyser} active={recording} />
        </footer>
      </div>
    </div>
  );
}
