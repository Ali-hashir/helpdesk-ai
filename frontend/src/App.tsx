import HelpdeskWidget from "./components/HelpdeskWidget.tsx";

export default function App() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-black text-slate-100">
      {/* Glow backdrops */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-24 -top-24 h-96 w-96 rounded-full bg-fuchsia-500/20 blur-3xl" />
        <div className="absolute -right-32 top-40 h-[28rem] w-[28rem] rounded-full bg-cyan-400/20 blur-3xl" />
        <div className="absolute bottom-0 left-1/2 h-80 w-80 -translate-x-1/2 rounded-full bg-amber-400/10 blur-3xl" />
      </div>

      <header className="relative z-10">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-fuchsia-500 to-cyan-400 shadow-lg shadow-fuchsia-500/30" />
              <span className="text-lg font-semibold tracking-tight">Helpdesk‑AI</span>
            </div>
            <div className="hidden gap-3 md:flex">
              <a
                href="#widget"
                className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/90 backdrop-blur transition hover:bg-white/10"
              >
                Try the Assistant
              </a>
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10">
        {/* hero */}
  <section className="mx-auto max-w-7xl px-6 pt-6 pb-4 md:pt-10 lg:pt-16">
          <div className="grid items-center gap-10 md:grid-cols-2">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/80 backdrop-blur">
                <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                <span>Live IT Copilot</span>
              </div>
              <h1 className="mt-5 text-4xl font-black leading-[1.05] tracking-tight sm:text-5xl md:text-6xl">
                <span>Fix issues instantly.</span>
                <span className="block bg-gradient-to-r from-fuchsia-400 via-cyan-300 to-emerald-300 bg-clip-text text-transparent">
                  Escalate when it matters.
                </span>
              </h1>
              <p className="mt-5 max-w-xl text-base text-slate-300 sm:text-lg">
                Meet your glowing problem‑solver. Helpdesk‑AI suggests precise fixes in seconds and
                seamlessly creates tickets for human experts when needed.
              </p>
              <div className="mt-6 flex flex-wrap items-center gap-3">
                <a
                  href="#widget"
                  className="group relative inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-fuchsia-500 to-cyan-400 px-5 py-3 text-sm font-semibold text-slate-900 shadow-[0_10px_30px_-10px] shadow-fuchsia-500/50 transition-transform hover:-translate-y-0.5"
                >
                  <span>Start troubleshooting</span>
                  <span className="transition-transform group-hover:translate-x-0.5">→</span>
                </a>
                <span className="text-xs text-slate-400">No signup • Instant answers</span>
              </div>
              <div className="mt-8 grid max-w-lg grid-cols-3 gap-3 text-center text-xs text-slate-300">
                <div className="rounded-xl border border-white/10 bg-white/5 p-3 backdrop-blur">
                  <div className="text-lg font-bold text-white">10x</div>
                  Faster resolution
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-3 backdrop-blur">
                  <div className="text-lg font-bold text-white">95%</div>
                  Auto‑answers
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-3 backdrop-blur">
                  <div className="text-lg font-bold text-white">24/7</div>
                  Always on
                </div>
              </div>
            </div>

            {/* Widget card */}
            <div id="widget" className="">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-2 shadow-2xl backdrop-blur-xl">
                <div className="rounded-2xl bg-slate-950/60 p-4 sm:p-5">
                  <HelpdeskWidget />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* highlights */}
        <section className="mx-auto max-w-7xl px-6 py-12">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {(() => {
              const items = [
                {
                  title: "Unified knowledge",
                  desc:
                    "Search configs, logs, and playbooks with one prompt—no context switching.",
                  glowClass: "card-glow-0",
                },
                {
                  title: "Human‑grade escalation",
                  desc:
                    "When AI isn’t enough, it creates a rich ticket and routes it instantly.",
                  glowClass: "card-glow-1",
                },
                {
                  title: "Audit trail",
                  desc:
                    "Every step is tracked for compliance and continuous improvement.",
                  glowClass: "card-glow-2",
                },
              ];
              return items.map((it) => (
                <div
                  key={it.title}
                  className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.06] p-5 shadow-lg backdrop-blur transition hover:bg-white/[0.09]"
                >
                  <div className={`pointer-events-none absolute -inset-1 -z-10 opacity-25 blur-2xl ${it.glowClass}`} />
                  <div className="mb-2 text-sm text-slate-300">Feature</div>
                  <div className="text-lg font-semibold text-white">{it.title}</div>
                  <p className="mt-2 text-sm text-slate-400">{it.desc}</p>
                </div>
              ));
            })()}
          </div>
        </section>
      </main>

      <footer className="relative z-10 border-t border-white/10/5">
        <div className="mx-auto max-w-7xl px-6 py-8 text-center text-xs text-slate-400">
          © {new Date().getFullYear()} Helpdesk‑AI. Built for rapid IT resolution.
        </div>
      </footer>
    </div>
  );
}
