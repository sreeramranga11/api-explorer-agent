"use client";

import { useMemo, useState } from "react";
import MarkdownPreview from "@/components/MarkdownPreview";
import { generateGuide } from "@/lib/api";

const PHASES = ["Crawling documentation", "Analyzing endpoints", "Generating markdown"];

export default function GeneratePage() {
  const [docsUrl, setDocsUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [markdown, setMarkdown] = useState("");
  const [error, setError] = useState("");
  const [activeStep, setActiveStep] = useState(0);

  const canGenerate = Boolean(docsUrl) && !loading;

  const statusLabel = useMemo(() => {
    if (loading) return `${PHASES[activeStep]}...`;
    if (markdown) return "Guide generated successfully.";
    return "Ready to generate.";
  }, [loading, activeStep, markdown]);

  const onGenerate = async () => {
    setLoading(true);
    setError("");
    setMarkdown("");
    setActiveStep(0);

    const timerOne = setTimeout(() => setActiveStep(1), 700);
    const timerTwo = setTimeout(() => setActiveStep(2), 1500);

    try {
      const result = await generateGuide(docsUrl);
      setMarkdown(result.markdown);
      setActiveStep(2);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      clearTimeout(timerOne);
      clearTimeout(timerTwo);
      setLoading(false);
    }
  };

  const onDownload = () => {
    const blob = new Blob([markdown], { type: "text/markdown" });
    const href = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = "integration.md";
    anchor.click();
    URL.revokeObjectURL(href);
  };

  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <header className="mb-8 flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-6 py-5 shadow-sm">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-indigo-600">API Explorer</p>
            <h1 className="mt-1 text-2xl font-bold text-slate-900">Integration Guide Generator</h1>
            <p className="mt-1 text-sm text-slate-600">
              Transform scattered docs into a structured markdown guide for AI coding agents.
            </p>
          </div>
          <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
            MVP
          </span>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.1fr_1.4fr]">
          <div className="space-y-6">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-slate-900">Generate API Guide</h2>
              <p className="mt-1 text-sm text-slate-600">Enter an API documentation URL to begin crawling and analysis.</p>

              <label className="mt-5 block text-xs font-medium uppercase tracking-wide text-slate-500">Documentation URL</label>
              <input
                className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100"
                type="url"
                placeholder="https://developer.getjobber.com/docs"
                value={docsUrl}
                onChange={(event) => setDocsUrl(event.target.value)}
              />

              <button
                className="mt-4 w-full rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-indigo-300"
                onClick={onGenerate}
                disabled={!canGenerate}
              >
                {loading ? "Generating..." : "Generate API Guide"}
              </button>

              <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <span className="font-medium">Status:</span> {statusLabel}
              </div>

              {error && <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-900">Pipeline Progress</h3>
              <ol className="mt-4 space-y-3">
                {PHASES.map((phase, index) => {
                  const isDone = !loading && markdown ? true : index < activeStep;
                  const isActive = loading && index === activeStep;
                  return (
                    <li key={phase} className="flex items-center gap-3">
                      <span
                        className={`inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                          isDone
                            ? "bg-emerald-100 text-emerald-700"
                            : isActive
                              ? "bg-indigo-100 text-indigo-700"
                              : "bg-slate-100 text-slate-500"
                        }`}
                      >
                        {isDone ? "✓" : index + 1}
                      </span>
                      <span className={`text-sm ${isActive ? "font-semibold text-indigo-700" : "text-slate-700"}`}>{phase}</span>
                    </li>
                  );
                })}
              </ol>
            </div>
          </div>

          <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-base font-semibold text-slate-900">Guide Output</h2>
              <div className="flex gap-2">
                <button
                  className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                  onClick={() => navigator.clipboard.writeText(markdown)}
                  disabled={!markdown}
                >
                  Copy to Clipboard
                </button>
                <button
                  className="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-medium text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-emerald-300"
                  onClick={onDownload}
                  disabled={!markdown}
                >
                  Download Markdown
                </button>
              </div>
            </div>

            {markdown ? (
              <MarkdownPreview markdown={markdown} />
            ) : (
              <div className="flex h-[560px] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 text-center text-sm text-slate-500">
                Your generated integration guide will appear here.
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
