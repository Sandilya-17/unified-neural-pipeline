// unified-ui/src/components/DiarizationTimeline.jsx
import React from "react";

function colorForSpeaker(name) {
  const palette = ["#06b6d4", "#7c3aed", "#fb7185", "#f59e0b", "#10b981"];
  const idx = Math.abs(name.split("").reduce((s, c) => s + c.charCodeAt(0), 0)) % palette.length;
  return palette[idx];
}

export default function DiarizationTimeline({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-sm text-slate-400">No diarization yet</div>;
  }

  return (
    <div className="space-y-3">
      {data.map((item, i) => {
        const color = colorForSpeaker(item.speaker || `S${i}`);
        return (
          <div key={i} className="flex gap-4 items-start">
            <div className="w-2 flex-none">
              <div style={{ background: color }} className="w-2 h-8 rounded" />
            </div>
            <div className="flex-1 bg-gray-900/60 border border-gray-800 p-3 rounded-lg">
              <div className="flex justify-between items-baseline">
                <div className="text-sm font-semibold text-white">{item.speaker}</div>
                <div className="text-xs text-slate-400">{item.start.toFixed(2)}s — {item.end.toFixed(2)}s</div>
              </div>
              <div className="mt-2 text-sm text-slate-200">{item.text}</div>
              <div className="mt-2 text-xs text-slate-400">Confidence: {item.confidence ? Number(item.confidence).toFixed(2) : "—"}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
