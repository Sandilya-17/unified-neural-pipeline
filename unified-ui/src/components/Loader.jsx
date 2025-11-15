// unified-ui/src/components/Loader.jsx
import React from "react";

export default function Loader({ text = "Processing", small = false }) {
  return (
    <div className={small ? "flex items-center gap-3 text-sm" : "flex items-center gap-4"}>
      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-emerald-400 to-indigo-500 flex items-center justify-center shadow-lg animate-pulse">
        <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3" />
        </svg>
      </div>
      <div>
        <div className="text-slate-100 font-semibold">{text}…</div>
        <div className="text-slate-400 text-xs mt-1">This may take a few seconds for CPU demos</div>
      </div>
    </div>
  );
}
