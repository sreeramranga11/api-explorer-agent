type Props = {
  markdown: string;
};

export default function MarkdownPreview({ markdown }: Props) {
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 bg-slate-50 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-600">
        Markdown Preview
      </div>
      <pre className="max-h-[560px] overflow-auto p-5 text-sm leading-relaxed whitespace-pre-wrap text-slate-800">
        {markdown}
      </pre>
    </div>
  );
}
