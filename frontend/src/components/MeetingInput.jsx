import { useMemo, useState } from 'react';

const starterNotes = `- Build onboarding workflow for ACME account owner: Priya deadline: 2026-03-30
- Draft compliance report owner: Omar deadline: 2026-03-28
- QA test integration with finance ERP owner: Linh deadline: 2026-04-02`;

export default function MeetingInput({ onSubmit, loading }) {
  const [content, setContent] = useState(starterNotes);
  const [source, setSource] = useState('text');
  const [listening, setListening] = useState(false);

  const speechSupported = useMemo(
    () => typeof window !== 'undefined' && 'webkitSpeechRecognition' in window,
    []
  );

  function startVoiceCapture() {
    if (!speechSupported) return;

    const Recognition = window.webkitSpeechRecognition;
    const recognition = new Recognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onstart = () => {
      setSource('voice');
      setListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setContent((prev) => `${prev}\n${transcript}`.trim());
    };

    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognition.start();
  }

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit({ source, content });
  }

  function handleFileUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!/\.(txt|md)$/i.test(file.name)) {
      alert('Only .txt or .md transcript files are supported.');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      setContent(String(reader.result));
      setSource('file');
    };
    reader.readAsText(file);
    event.target.value = '';
  }

  return (
    <section className="glass animate-rise rounded-3xl p-5 sm:p-7" style={{ animationDelay: '80ms' }}>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl font-semibold text-white sm:text-2xl">Meeting Intake</h2>
        <div className="flex items-center gap-2">
          <label className="cursor-pointer rounded-full border border-white/30 px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-white transition hover:bg-white/10">
            Upload .txt/.md
            <input type="file" accept=".txt,.md" className="hidden" onChange={handleFileUpload} />
          </label>
          <button
            type="button"
            disabled={!speechSupported || listening}
            onClick={startVoiceCapture}
            className="rounded-full border border-white/30 px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {listening ? 'Listening...' : speechSupported ? 'Voice Input' : 'Voice N/A'}
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          rows={7}
          className="w-full rounded-2xl border border-white/20 bg-slate-900/40 p-4 font-body text-sm text-white outline-none ring-cyan-300 transition focus:ring"
          placeholder="Paste meeting notes or capture voice transcript"
          required
        />
        <button
          type="submit"
          disabled={loading || !content.trim()}
          className="w-full rounded-2xl bg-gradient-to-r from-orange-400 via-pink-500 to-rose-500 px-5 py-3 font-display text-base font-semibold text-white shadow-candy transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Processing...' : 'Run Agentic Workflow'}
        </button>
      </form>
    </section>
  );
}
