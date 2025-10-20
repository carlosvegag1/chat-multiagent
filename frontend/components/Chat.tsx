"use client";

import { useState, useRef, useEffect, FC, useMemo } from "react";
import ReactMarkdown from "react-markdown";

/* ===================== Utilidades ===================== */

/** Repara texto mal codificado (mojibake tipo “AquÃ­”). */
function fixMojibake(s?: string | null): string | undefined {
  if (!s) return s ?? undefined;
  if (!/[ÃÂ¡Â¿Â¡ÂºÂªÂ´Â¨Â·]/.test(s)) return s;
  try {
    const fixed = decodeURIComponent(escape(s));
    return /[ÃÂ]/.test(fixed) ? s : fixed;
  } catch {
    return s;
  }
}

/* ===================== Tipos ===================== */

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

/* ===================== UI helpers ===================== */

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm animate-fade-in overflow-visible">
      <div className="text-slate-700 font-semibold mb-2">{title}</div>
      <div className="text-sm text-slate-700">{children}</div>
    </div>
  );
}

const MarkdownRenderer: FC<{ content: string }> = ({ content }) => {
  const cleaned = useMemo(() => fixMojibake(content) ?? content, [content]);
  return (
    <ReactMarkdown
      components={{
        p: ({ node, ...props }) => <p className="text-sm font-medium leading-relaxed" {...props} />,
        strong: ({ node, ...props }) => <strong className="font-bold" {...props} />,
        ul: ({ node, ...props }) => <ul className="list-disc list-inside space-y-1" {...props} />,
        li: ({ node, ...props }) => <li className="pl-2" {...props} />,
      }}
    >
      {cleaned}
    </ReactMarkdown>
  );
};

/* ===================== Subcomponentes visuales ===================== */

function FlightCard({ flight }: { flight: FlightInfo }) {
  const formatTime = (iso?: string) =>
    iso ? new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "?";
  return (
    <div className="border border-slate-200 bg-slate-50/80 rounded-xl p-3 flex items-center justify-between gap-4">
      <div className="flex flex-col">
        <span className="font-bold text-slate-800">{fixMojibake(flight.airline) || "Aerolínea"}</span>
        <span className="text-xs text-slate-500">{fixMojibake(flight.flight_number)}</span>
      </div>
      <div className="text-center">
        <span className="font-mono text-lg font-semibold text-slate-900">
          {fixMojibake(flight.origin)} → {fixMojibake(flight.destination)}
        </span>
        <div className="text-sm text-slate-600">
          {formatTime(flight.departure_time)} - {formatTime(flight.arrival_time)}
        </div>
      </div>
      <div className="text-right">
        <span className="text-lg font-bold text-indigo-600">
          {flight.price?.toFixed(2) || "?"} {fixMojibake(flight.currency)}
        </span>
        <div className="text-xs text-slate-500">{fixMojibake(flight.duration)}</div>
      </div>
    </div>
  );
}

function HotelCard({ hotel }: { hotel: HotelInfo }) {
  return (
    <div className="border border-slate-200 bg-slate-50/80 rounded-xl p-3">
      <div className="flex justify-between items-start">
        <span className="font-bold text-slate-800">{fixMojibake(hotel.name)}</span>
        {hotel.rating && (
          <span className="text-sm font-semibold bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
            {hotel.rating} ⭐
          </span>
        )}
      </div>
      {hotel.address && <p className="text-xs text-slate-500 mt-1">{fixMojibake(hotel.address)}</p>}
    </div>
  );
}

function FlightsList({ city, flights }: { city?: string; flights?: FlightInfo[] }) {
  if (!flights?.length) return null;
  return (
    <SectionCard title={`✈️ Vuelos a ${fixMojibake(city) || "tu destino"}`}>
      <div className="flex flex-col gap-2">{flights.map((f, i) => <FlightCard key={i} flight={f} />)}</div>
    </SectionCard>
  );
}

function HotelsList({ city, hotels }: { city?: string; hotels?: HotelInfo[] }) {
  if (!hotels?.length) return null;
  return (
    <SectionCard title={`🏨 Hoteles en ${fixMojibake(city) || "tu destino"}`}>
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
            <span className="font-medium">{fixMojibake(p.name)}</span>
            {p.description ? <span className="text-slate-500"> — {fixMojibake(p.description)}</span> : null}
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
      <p className="leading-relaxed">{fixMojibake(summary)}</p>
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
              {d.activities.map((a, i) => <li key={i}>{fixMojibake(a)}</li>)}
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
      💰 Presupuesto estimado: {budget.total.toFixed(2)} {fixMojibake(budget.currency) || "EUR"}
    </div>
  );
}

function ErrorCard({ error }: { error?: string }) {
  if (!error) return null;
  return (
    <div className="bg-red-50 border border-red-200 rounded-2xl p-4 shadow-sm text-red-700">
      <div className="font-semibold mb-1">⚠️ Ocurrió un error</div>
      <p>{fixMojibake(error)}</p>
    </div>
  );
}

const VoiceVisualizer: FC<{ analyser: AnalyserNode | null; active: boolean }> = ({
  analyser,
  active,
}) => {
  const [bars, setBars] = useState<number[]>(Array(20).fill(0));
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    // Si no hay grabación o no existe el analizador, salimos
    if (!active || !analyser) return;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    const draw = () => {
      analyser.getByteFrequencyData(dataArray);

      // Suavizamos el movimiento para evitar parpadeo brusco
      const newBars = Array.from(dataArray.slice(0, 20)).map((v, i) => {
        const intensity = Math.max(5, (v / 255) * 40);
        // Mezclamos con el valor anterior para lograr un movimiento más fluido
        return bars[i] * 0.6 + intensity * 0.4;
      });

      setBars(newBars);
      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    // Limpieza: cancelamos la animación al detener grabación o desmontar
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    };
  }, [active, analyser]); // ← Dependencias correctas

  if (!active) return null;

  return (
    <div className="mt-4 text-center text-slate-600 font-medium">
      <div className="flex justify-center items-end gap-1 h-10 transition-all">
        {bars.map((h, i) => (
          <div
            key={i}
            className={`w-1 rounded transition-all duration-100 ${
              h > 30
                ? "bg-indigo-600"
                : h > 20
                ? "bg-indigo-500"
                : h > 10
                ? "bg-indigo-400"
                : "bg-indigo-300"
            }`}
            style={{ height: `${h}px` }}
          />
        ))}
      </div>
      <p className="mt-2 text-sm animate-pulse text-indigo-600 font-medium">
        🎤 Grabando... habla ahora
      </p>
    </div>
  );
};

// ===================== COMPONENTE PRINCIPAL =====================
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
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const endRef = useRef<HTMLDivElement | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  /* === Inicialización usuario === */
  useEffect(() => {
    const saved = localStorage.getItem("chatUserName");
    if (saved) {
      setUserName(saved);
    } else {
      const name = prompt("¡Bienvenido! ¿Cómo te llamas?");
      if (name) {
        localStorage.setItem("chatUserName", name);
        setUserName(name);
      }
    }
  }, []);


  /* === Scroll automático con easing tipo iMessage === */
  const scrollToEnd = () => {
    if (!endRef.current) return;

    const start = window.scrollY;
    const end = endRef.current.getBoundingClientRect().top + window.scrollY - 40;
    const duration = 500; // ms
    const startTime = performance.now();

    const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

    const animateScroll = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = easeOutCubic(progress);
      window.scrollTo(0, start + (end - start) * ease);
      if (progress < 1) requestAnimationFrame(animateScroll);
    };

    requestAnimationFrame(animateScroll);
  };

  useEffect(() => {
    const lastMsg = messages[messages.length - 1];
    if (!lastMsg) return;
    scrollToEnd();
  }, [messages]);

  /* === Carga de conversaciones === */
  const fetchConvos = async (user: string) => {
    try {
      const res = await fetch(`${API_URL}/convos?user=${encodeURIComponent(user)}`);
      const data: ConvoSummary[] = await res.json();

      const enriched = await Promise.all(
        data.map(async (c) => {
          try {
            const convoRes = await fetch(`${API_URL}/convo/${c.convo_id}`);
            const convoData = await convoRes.json();

            // Aseguramos que convoData.messages sea un array de tipo Message
            const msgs: Message[] = Array.isArray(convoData.messages)
              ? convoData.messages
              : [];

            // 🧠 Filtra solo mensajes con texto válido (compatibilidad con antiguos que usan "content")
            const validMsgs = msgs.filter(
              (m: Message) =>
                (m.text && m.text.trim().length > 0) ||
                ((m as unknown as { content?: string }).content &&
                  (m as unknown as { content?: string }).content!.trim().length > 0)
            );

            // Si no hay mensajes, indicamos que está vacía
            if (validMsgs.length === 0) {
              return { ...c, preview: "Conversación vacía o sin mensajes guardados" };
            }

            // 🧩 Creamos la vista previa con los dos primeros mensajes (usuario + bot)
            const previewMsgs = validMsgs
              .slice(0, 2)
              .map((m: Message) => {
                const prefix = m.role === "bot" ? "🤖" : "🧑";
                const content =
                  m.text ||
                  (m as unknown as { content?: string }).content ||
                  "";
                return `${prefix} ${content.replace(/\n/g, " ")}`;
              })
              .join(" | ");

            const cleanPreview =
              previewMsgs.length > 100
                ? `${previewMsgs.slice(0, 100)}…`
                : previewMsgs;

            return { ...c, preview: cleanPreview };
          } catch (err) {
            console.error("Error al obtener conversación:", err);
            return { ...c, preview: "Error al cargar" };
          }
        })
      );

      setAvailableConvos(enriched);
      if (!convoId && enriched.length) setConvoId(enriched[0].convo_id);
    } catch (err) {
      console.error("Error al cargar conversaciones:", err);
    }
  };


  useEffect(() => {
    if (userName) fetchConvos(userName);
  }, [userName]);

  /* === Crear nueva conversación === */
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

  /* === Envío de texto === */
  const sendText = async () => {
    if (!text.trim() || !convoId || !userName) return;

    const userMsg: Message = { role: "user", text, ts: Date.now() / 1000 };
    setMessages((p) => [...p, userMsg]);
    setText("");
    setBotTyping(true);

    try {
      const form = new FormData();
      form.append("message", text);
      form.append("convo_id", convoId);
      form.append("user", userName);

      const res = await fetch(`${API_URL}/chat/`, { method: "POST", body: form });
      const data = await res.json();

      const reply = fixMojibake(data.reply_text || "") || "";

      setMessages((p) => [
        ...p,
        {
          role: "bot",
          text: reply,
          structured_data: data.structured_data,
          ts: Date.now() / 1000,
        },
      ]);
    } catch (error) {
      console.error("Error al enviar mensaje:", error);
    } finally {
      setBotTyping(false);
    }
  };

  /* === Grabación de audio === */
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream);
      const audioCtx = new AudioContext();
      const src = audioCtx.createMediaStreamSource(stream);
      const analyserNode = audioCtx.createAnalyser();
      analyserNode.fftSize = 256;
      src.connect(analyserNode);
      setAnalyser(analyserNode);
      audioContextRef.current = audioCtx;
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

        setMessages((p) => [...p, { role: "user", text: "🎙️ Procesando audio...", ts: Date.now() / 1000 }]);

        try {
          const res = await fetch(`${API_URL}/chat/audio`, { method: "POST", body: formData });
          const data = await res.json();

          const trans = data.transcription?.trim()
            ? `🎧 **Transcripción detectada:** ${data.transcription}`
            : "🎧 No se pudo detectar voz o texto claro.";

          const reply = fixMojibake(data.reply_text || "") || "";

          setMessages((p) => [
            ...p.filter((m) => m.text !== "🎙️ Procesando audio..."),
            { role: "user", text: trans, ts: Date.now() / 1000 },
            {
              role: "bot",
              text: reply,
              structured_data: data.structured_data,
              ts: Date.now() / 1000,
            },
          ]);
        } catch (err) {
          console.error("Error al enviar audio:", err);
        } finally {
          streamRef.current?.getTracks().forEach((t) => t.stop());
          streamRef.current = null;
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

  /* === Render principal === */
  return (
    <div className="flex w-full h-screen bg-gradient-to-b from-slate-50 to-slate-100 relative overflow-hidden">
      {/* === SIDEBAR === */}
      <aside
        className={`absolute top-0 left-0 h-full bg-white shadow-xl border-r border-slate-200 w-80 transform transition-transform duration-300 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-80"
        } z-30`}
      >
        <div className="p-4 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
            💬 <span>Conversaciones</span>
          </h2>
          <button onClick={toggleSidebar} className="text-slate-500 hover:text-slate-800 text-xl">
            ✖
          </button>
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
                  className={`p-4 transition-colors cursor-pointer ${
                    convoId === c.convo_id
                      ? "bg-indigo-50 border-l-4 border-indigo-500"
                      : "hover:bg-indigo-50"
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
        {/* === HEADER === */}
        <header className="flex items-center justify-between h-[72px] px-4 md:px-6 bg-white border-b border-slate-200 z-20">
          <div className="flex items-center gap-3">
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-lg border border-slate-300 hover:bg-slate-100 text-slate-700"
              aria-label="Abrir historial"
            >
              ☰
            </button>
            <h1 className="text-xl md:text-2xl font-bold text-slate-800">
              Bienvenido{userName ? `, ${userName}` : ""} 👋
            </h1>
          </div>

          <button
            onClick={createNewConvo}
            className="px-3 py-2 bg-indigo-600 text-white rounded-full text-sm font-bold hover:bg-indigo-700 transition"
          >
            Nueva conversación
          </button>
        </header>

        {/* === CHAT PRINCIPAL === */}
        <main className="flex flex-col flex-1 w-full px-4 md:px-12 py-4 md:py-6 gap-6 overflow-y-auto overflow-x-hidden h-auto min-h-[calc(100vh-160px)] pb-[160px]">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "bot" ? "justify-start" : "justify-end"} animate-fade-in`}>
              <div className="flex items-start gap-2 w-full max-w-[900px] mx-auto">
                {m.role === "bot" && (
                  <img
                    src="/icons/bot.svg"
                    alt="Bot"
                    className="w-9 h-9 md:w-10 md:h-10 rounded-full border border-slate-300"
                  />
                )}

                <div className="w-full overflow-visible">
                  <div
                    className={`p-3 md:p-4 rounded-2xl break-words shadow-md ${
                      m.role === "user"
                        ? "bg-gradient-to-r from-indigo-600 to-indigo-400 text-white ml-auto"
                        : "bg-white border border-slate-200 w-full"
                    }`}
                    style={{
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                      overflow: "visible",
                      maxHeight: "none",
                    }}
                  >
                    <MarkdownRenderer content={m.text} />
                    {m.role === "bot" && m.structured_data && (
                      <div className="flex flex-col gap-3 mt-3 overflow-visible">
                        <FlightsList city={m.structured_data.city} flights={m.structured_data.flights} />
                        <HotelsList
                          city={m.structured_data.city}
                          hotels={
                            m.structured_data.hotels ||
                            (
                              (m.structured_data as unknown as {
                                result?: { hotels?: HotelInfo[] };
                              }).result?.hotels ?? []
                            )
                          }
                        />
                        <PoisList pois={m.structured_data.pois} />
                        <SummaryBox summary={m.structured_data.summary} />
                        <PlanCard plan={m.structured_data.plan_sugerido} />
                        <BudgetBadge budget={m.structured_data.budget} />
                        <ErrorCard error={m.structured_data.error} />
                      </div>
                    )}
                  </div>
                </div>

                {m.role === "user" && (
                  <img
                    src="/icons/user.svg"
                    alt="Usuario"
                    className="w-9 h-9 md:w-10 md:h-10 rounded-full border border-slate-300"
                  />
                )}
              </div>
            </div>
          ))}

          {/* Indicador de escritura del bot */}
          {botTyping && (
            <div className="flex justify-start animate-pulse gap-2 mt-1 max-w-[900px] mx-auto">
              <img
                src="/icons/bot.svg"
                alt="Bot"
                className="w-9 h-9 md:w-10 md:h-10 rounded-full border border-slate-300"
              />
              <div className="p-3 rounded-2xl bg-white text-slate-700 shadow-sm">
                Bot está escribiendo...
              </div>
            </div>
          )}

          <div ref={endRef} />
        </main>

        {/* === FOOTER === */}
        <footer className="sticky bottom-0 left-0 w-full p-4 md:p-6 bg-white border-t border-slate-200 z-20">
          <div className="max-w-[900px] mx-auto">
            <div className="flex gap-2 items-center">
              <input
                className="flex-1 p-3 border rounded-2xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-400"
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
          </div>
        </footer>
      </div>
    </div>
  );
}
