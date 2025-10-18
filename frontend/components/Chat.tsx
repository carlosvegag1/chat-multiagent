// frontend/components/Chat.tsx
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

// --- Componentes de UI (Base y Enriquecidos) ---
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

// ---------------- COMPONENTE PRINCIPAL ----------------
export default function Chat() {
    const [userName, setUserName] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [text, setText] = useState("");
    const [convoId, setConvoId] = useState<string | null>(null);
    const [availableConvos, setAvailableConvos] = useState<ConvoSummary[]>([]);
    const [botTyping, setBotTyping] = useState(false);
    const [recording, setRecording] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);
    const messagesEndRef = useRef<HTMLDivElement | null>(null);
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

    // ---- Inicialización usuario y conversaciones ----
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
            if (data?.length) {
                setAvailableConvos(data);
                if (!convoId) setConvoId(data[0].convo_id);
            } else await createNewConvo(true);
        } catch (error) {
            console.error("Error al cargar conversaciones:", error);
        }
    };

    useEffect(() => { if (userName) fetchConvos(userName); }, [userName]);

    useEffect(() => {
        if (!convoId) return;
        fetch(`${API_URL}/convo/${convoId}`)
            .then((r) => r.json())
            .then((data) => setMessages(data.messages || []))
            .catch(() => setMessages([]));
    }, [convoId, API_URL]);

    useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

    // ---- Envío de texto ----
    const sendText = async () => {
        if (!text.trim() || !convoId || !userName) return;
        const currentText = text;
        const userMessage: Message = { role: "user", text: currentText, ts: Date.now() / 1000 };
        setMessages((prev) => [...prev, userMessage]);
        setText("");
        setBotTyping(true);

        try {
            const form = new FormData();
            form.append("message", currentText);
            form.append("convo_id", convoId);
            form.append("user", userName);
            const res = await fetch(`${API_URL}/chat/`, { method: "POST", body: form });
            const data = await res.json();

            const botMessage: Message = {
                role: "bot",
                text: data.reply_text,
                structured_data: data.structured_data,
                ts: Date.now() / 1000,
            };
            setMessages((prev) => [...prev, botMessage]);
        } catch (error) {
            console.error("Error al enviar mensaje:", error);
        } finally {
            setBotTyping(false);
        }
    };

    const createNewConvo = async (isInitial: boolean = false) => {
        if (!userName) return;
        setMessages([]);
        try {
            const form = new FormData();
            form.append("user", userName);
            const res = await fetch(`${API_URL}/new_convo`, { method: "POST", body: form });
            const newConvoData = await res.json();
            const newConvoSummary: ConvoSummary = {
                convo_id: newConvoData.convo_id,
                created_at: newConvoData.created_at,
            };
            setAvailableConvos((prev) => [newConvoSummary, ...prev]);
            setConvoId(newConvoSummary.convo_id);
        } catch (error) {
            console.error("Error al crear nueva conversación:", error);
        }
    };

    // ---- 🎙️ Grabación y envío de audio (Whisper) ----
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];
            setRecording(true);

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) chunksRef.current.push(e.data);
            };

            mediaRecorder.onstop = async () => {
                const blob = new Blob(chunksRef.current, { type: "audio/webm" });
                const formData = new FormData();
                formData.append("file", blob, "audio.webm");
                formData.append("user", userName || "demo");
                formData.append("convo_id", convoId || "");

                try {
                    const res = await fetch(`${API_URL}/chat/audio`, {
                        method: "POST",
                        body: formData,
                    });
                    const data = await res.json();

                    setMessages((prev) => [
                        ...prev,
                        { role: "user", text: "🎙️ Mensaje de voz enviado", ts: Date.now() / 1000 },
                        {
                            role: "bot",
                            text: data.reply_text,
                            structured_data: data.structured_data,
                            ts: Date.now() / 1000,
                        },
                    ]);
                } catch (err) {
                    console.error("Error al enviar audio:", err);
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
        <div className="flex flex-col w-[1000px] h-screen bg-gradient-to-b from-slate-50 to-slate-100 shadow-lg mx-auto overflow-hidden">
            <header className="fixed top-0 left-1/2 -translate-x-1/2 flex items-center justify-between w-[1000px] h-[88px] p-6 bg-white border-b border-slate-200 z-20">
                <h1 className="text-2xl font-bold text-slate-800">
                    Bienvenido{userName ? `, {userName}` : ""} 👋
                </h1>
                <div className="flex gap-2 items-center">
                    <select
                        value={convoId ?? ""}
                        onChange={(e) => setConvoId(e.target.value)}
                        className="border rounded-lg p-2"
                        disabled={!convoId}
                    >
                        {availableConvos.map((c) => (
                            <option key={c.convo_id} value={c.convo_id}>
                                {new Date(c.created_at).toLocaleString([], {
                                    dateStyle: "short",
                                    timeStyle: "short",
                                })}
                            </option>
                        ))}
                    </select>
                    <button
                        onClick={() => createNewConvo()}
                        className="px-3 py-2 bg-indigo-600 text-white rounded-full text-sm font-bold hover:bg-indigo-700 transition"
                    >
                        Nueva
                    </button>
                </div>
            </header>

            <main className="flex flex-col flex-1 w-full px-12 py-6 gap-3 overflow-y-auto mt-[88px] mb-[120px]" style={{ height: "calc(100vh - 208px)" }}>
                {messages.map((m, i) => {
                    const isBot = m.role === "bot";
                    const timestamp = m.ts
                        ? new Date(m.ts * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                        : "";

                    return (
                        <div key={i} className={`flex ${isBot ? "justify-start" : "justify-end"} animate-fade-in`}>
                            <div className="flex items-start gap-2 w-full max-w-[750px]">
                                {isBot && (
                                    <img
                                        src="/icons/bot.svg"
                                        alt="Bot"
                                        className="w-10 h-10 rounded-full border border-slate-300"
                                    />
                                )}
                                <div className="w-full">
                                    <div
                                        className={`p-3 rounded-2xl break-words shadow-md ${
                                            m.role === "user"
                                                ? "bg-gradient-to-r from-indigo-600 to-indigo-400 text-white ml-auto"
                                                : "bg-white border border-slate-200"
                                        }`}
                                    >
                                        <MarkdownRenderer content={m.text} />
                                    </div>
                                    {timestamp && (
                                        <div
                                            className={`text-xs mt-1 ${
                                                m.role === "user"
                                                    ? "text-right text-slate-400"
                                                    : "text-left text-slate-500"
                                            }`}
                                        >
                                            {timestamp}
                                        </div>
                                    )}
                                </div>
                                {m.role === "user" && (
                                    <img
                                        src="/icons/user.svg"
                                        alt="Usuario"
                                        className="w-10 h-10 rounded-full border border-slate-300"
                                    />
                                )}
                            </div>
                        </div>
                    );
                })}

                {botTyping && (
                    <div className="flex justify-start animate-pulse gap-2 mt-1">
                        <img src="/icons/bot.svg" alt="Bot" className="w-10 h-10 rounded-full border border-slate-300" />
                        <div className="p-3 rounded-2xl bg-white text-slate-700 shadow-sm">Bot está escribiendo...</div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </main>

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
                        className={`w-12 h-12 flex items-center justify-center rounded-full text-white text-2xl transition ${
                            recording ? "bg-red-500 hover:bg-red-600" : "bg-blue-500 hover:bg-blue-600"
                        }`}
                        title={recording ? "Detener grabación" : "Grabar mensaje de voz"}
                    >
                        {recording ? "■" : "●"}
                    </button>
                </div>
            </footer>
        </div>
    );
}
