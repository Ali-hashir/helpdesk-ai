import { useState } from "react";

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
      const res = await fetch("/n8n/webhook/assist-or-ticket", {
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
    <div style={styles.card}>
      <h2 style={styles.title}>Helpdesk-AI</h2>

      <form onSubmit={handleSubmit} style={styles.form}>
        <textarea
          style={styles.textarea}
          placeholder="Describe your issue…"
          rows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={busy}
          required
        />
        <button style={styles.button} disabled={busy || !message.trim()}>
          {busy ? "Thinking…" : "Ask"}
        </button>
      </form>

      {error && <div style={styles.error}>⚠️ {error}</div>}

      {result && result.action === "answer" && (
        <div style={styles.answer}>
          <div style={styles.badge}>AI Answer</div>
          <p style={{ whiteSpace: "pre-wrap", marginTop: 8 }}>
            {result.reply_text}
          </p>
          <div style={styles.meta}>
            Confidence: {(result.confidence * 100).toFixed(0)}%
          </div>
        </div>
      )}

      {result && result.action === "escalate" && (
        <div style={styles.ticket}>
          <div style={styles.badge}>Ticket Created</div>
          <p style={{ marginTop: 8 }}>
            We’ve opened ticket <b>#{result.ticket_id}</b> (status:{" "}
            <b>{result.status}</b>). Our team will follow up.
          </p>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    maxWidth: 560,
    width: "100%",
    margin: "24px auto",
    padding: 16,
    border: "1px solid #e5e7eb",
    borderRadius: 12,
    background: "#fff",
    boxShadow: "0 2px 10px rgba(0,0,0,0.06)",
    fontFamily:
      '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif',
  },
  title: { margin: 0, fontSize: 20, fontWeight: 600 },
  form: { display: "grid", gap: 8, marginTop: 12 },
  textarea: {
    padding: 10,
    fontSize: 14,
    border: "1px solid #d1d5db",
    borderRadius: 8,
    resize: "vertical",
  },
  button: {
    background: "#111827",
    color: "#fff",
    border: 0,
    borderRadius: 8,
    padding: "10px 14px",
    cursor: "pointer",
  },
  error: {
    marginTop: 12,
    color: "#b91c1c",
    background: "#fee2e2",
    border: "1px solid #fecaca",
    padding: 10,
    borderRadius: 8,
    fontSize: 14,
  },
  answer: {
    marginTop: 12,
    background: "#f0f9ff",
    border: "1px solid #bae6fd",
    padding: 10,
    borderRadius: 8,
  },
  ticket: {
    marginTop: 12,
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    padding: 10,
    borderRadius: 8,
  },
  badge: {
    display: "inline-block",
    fontSize: 12,
    padding: "4px 8px",
    borderRadius: 999,
    background: "#111827",
    color: "#fff",
  },
  meta: { marginTop: 6, fontSize: 12, color: "#374151" },
};
