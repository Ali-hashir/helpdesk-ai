import { useState } from "react";
import { N8N_BASE } from "../lib/config";

type Result =
  | { action: "answer"; confidence: number; reply_text: string }
  | { action: "escalate"; ticket_id: number; status: string };

export default function HelpdeskWidget() {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Result | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${N8N_BASE}/webhook/assist-or-ticket`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Request failed");
      }
      const data = (await res.json()) as Result;
      setResult(data);
    } catch (err: any) {
      setError(err.message ?? "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-xl">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold tracking-tight">Helpdesk‑AI Assistant</h2>
        <div className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-[10px] text-white/70">
          beta
        </div>
      </div>

      {/* conversation area */}
      <div className="mt-4 rounded-xl border border-white/10 bg-black/30 p-3 text-sm text-slate-200 shadow-inner">
        {!result && !error && (
          <div className="text-slate-400">Ask about any IT issue. I’ll propose a fix or open a ticket.</div>
        )}
        {error && (
          <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-rose-200">
            ⚠️ {error}
          </div>
        )}

        {result?.action === "answer" && (
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-2 py-1 text-[10px] uppercase tracking-wide text-emerald-300">
              <span>AI Answer</span>
              <span className="ml-1 inline-block rounded-full bg-emerald-400/20 px-1.5 py-0.5 text-[10px] text-emerald-200">
                {(result.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <p className="whitespace-pre-wrap leading-relaxed text-slate-200">{result.reply_text}</p>
          </div>
        )}

        {result?.action === "escalate" && (
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-2 py-1 text-[10px] uppercase tracking-wide text-cyan-300">
              Ticket Created
            </div>
            <p>
              We’ve opened ticket <b>#{result.ticket_id}</b> (status: <b>{result.status}</b>). Our team will follow up.
            </p>
          </div>
        )}
      </div>

      {/* form */}
      <form onSubmit={handleSubmit} className="mt-4 grid gap-3">
        <textarea
          className="min-h-28 w-full resize-y rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white placeholder:text-slate-400 shadow-[inset_0_1px_0_rgba(255,255,255,0.06)] outline-none backdrop-blur transition focus:border-fuchsia-400/40 focus:ring-2 focus:ring-fuchsia-400/20"
          placeholder="Describe your issue…"
          rows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={busy}
          required
        />
        <button
          className="relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-fuchsia-500 to-cyan-400 px-4 py-2.5 text-sm font-semibold text-slate-900 shadow-[0_10px_30px_-10px_rgba(244,114,182,0.6)] transition focus:outline-none enabled:hover:scale-[1.02] disabled:opacity-60"
          disabled={busy || !message.trim()}
        >
          <span className="relative z-10">{busy ? "Thinking…" : "Ask"}</span>
          {!busy && (
            <span className="relative z-10 text-base">→</span>
          )}
          {/* shine */}
          <span className="pointer-events-none absolute inset-0 -translate-x-full bg-[linear-gradient(120deg,transparent,rgba(255,255,255,0.6),transparent)] opacity-0 transition-all duration-700 group-hover:translate-x-0 group-hover:opacity-75" />
        </button>
      </form>

      <div className="mt-2 text-[11px] text-slate-400">We may open a ticket automatically if a human expert is needed.</div>
    </div>
  );
}
