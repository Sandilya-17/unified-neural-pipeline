import React, { useEffect, useRef } from "react";
import WaveSurfer from "wavesurfer.js";

export default function Waveform({ file }) {
  const containerRef = useRef(null);
  const wavesurfer = useRef(null);

  useEffect(() => {
    if (!file) return;

    if (wavesurfer.current) wavesurfer.current.destroy();

    wavesurfer.current = WaveSurfer.create({
      container: containerRef.current,
      height: 60,
      waveColor: "#475569",
      progressColor: "#0ea5e9",
      cursorColor: "#fff",
      barWidth: 2,
      responsive: true,
    });

    const url = URL.createObjectURL(file);
    wavesurfer.current.load(url);

    return () => wavesurfer.current?.destroy();
  }, [file]);

  if (!file) return null;

  return (
    <div className="mt-3">
      <div className="text-xs mb-1 text-slate-400">Waveform Preview</div>
      <div ref={containerRef} className="bg-slate-800 rounded-lg overflow-hidden" />
    </div>
  );
}
