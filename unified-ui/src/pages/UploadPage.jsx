// unified-ui/src/pages/UploadPage.jsx
import React, { useState } from "react";
import { motion } from "framer-motion";

import AudioUploader from "../components/AudioUploader";
import Loader from "../components/Loader";
import DiarizationTimeline from "../components/DiarizationTimeline";
import Waveform from "../components/Waveform";

export default function UploadPage() {
  const [mixtureFile, setMixtureFile] = useState(null);
  const [targetFile, setTargetFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = "http://localhost:8000/api/process";

  async function handleProcess() {
    setError(null);
    setResult(null);

    if (!mixtureFile || !targetFile) {
      setError("Please upload both mixture and target audio files.");
      return;
    }

    setLoading(true);

    try {
      const form = new FormData();
      form.append("mixture", mixtureFile);
      form.append("target", targetFile);

      const res = await fetch(API_URL, { method: "POST", body: form });
      const data = await res.json();

      if (!res.ok) setError(data.error || `Server error (${res.status})`);
      else setResult(data);
    } catch (err) {
      setError("Server unreachable: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  function downloadJson() {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "diarization.json";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gradient-to-b from-slate-900 via-black to-slate-950 text-white p-8"
    >
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.header
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="flex items-center justify-between mb-10"
        >
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-emerald-300 to-cyan-400">
              Unified Neural Pipeline
            </h1>
            <p className="mt-1 text-slate-400">
              Target speaker matching · Multispeaker ASR · Turn-level diarization
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-400">Demo</div>
            <div className="mt-1 text-xs text-slate-500">Local Mode</div>
          </div>
        </motion.header>

        {/* Main 2-column layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* LEFT PANEL */}
          <motion.div
            initial={{ x: -40, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="bg-gray-900/40 backdrop-blur-xl p-6 rounded-xl border border-gray-700/60 shadow-xl shadow-black/40"
          >
            <AudioUploader
              label="Mixture Audio (multi-speaker)"
              file={mixtureFile}
              setFile={setMixtureFile}
              idPrefix="mix"
            />
            <Waveform file={mixtureFile} />

            <div className="my-6" />

            <AudioUploader
              label="Target Speaker Sample (3–10 sec)"
              file={targetFile}
              setFile={setTargetFile}
              idPrefix="tgt"
            />
            <Waveform file={targetFile} />

            {/* Buttons */}
            <div className="mt-8 flex items-center gap-3">
              <motion.button
                whileTap={{ scale: 0.97 }}
                onClick={handleProcess}
                disabled={loading}
                className="px-5 py-2 bg-emerald-400 text-black font-semibold rounded shadow-lg hover:bg-emerald-500 transition disabled:opacity-60"
              >
                {loading ? "Processing..." : "Process Audio"}
              </motion.button>

              <button
                onClick={() => {
                  setMixtureFile(null);
                  setTargetFile(null);
                  setResult(null);
                  setError(null);
                }}
                className="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 text-sm"
              >
                Reset
              </button>

              {result && (
                <button
                  onClick={downloadJson}
                  className="ml-auto px-4 py-2 bg-indigo-600 rounded text-sm hover:bg-indigo-700"
                >
                  Download JSON
                </button>
              )}
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-900/50 border border-red-700 rounded text-sm">
                {error}
              </div>
            )}
          </motion.div>

          {/* RIGHT PANEL */}
          <motion.div
            initial={{ x: 40, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="bg-gray-900/30 p-6 rounded-xl border border-gray-700/60 min-h-[360px] shadow-xl shadow-black/40"
          >
            {loading ? (
              <Loader text="Processing audio…" />
            ) : result ? (
              <div>
                <h2 className="text-xl font-semibold mb-4">Diarization Output</h2>
                <DiarizationTimeline
                  data={Array.isArray(result) ? result : result.segments || []}
                />
              </div>
            ) : (
              <div className="h-full flex flex-col justify-center items-center text-slate-500">
                <p className="text-lg">Output will appear here</p>
                <p className="text-sm">After processing both audio files</p>
              </div>
            )}
          </motion.div>
        </div>

        <footer className="mt-12 text-center text-sm text-slate-500">
          Built by <span className="text-emerald-300">P. Sandilya</span> · CPU Mode
        </footer>
      </div>
    </motion.div>
  );
}
