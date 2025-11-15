// unified-ui/src/components/AudioUploader.jsx
import React, { useRef, useState } from "react";
import clsx from "clsx";

export default function AudioUploader({ label, file, setFile, idPrefix = "" }) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef();

  function handleFiles(files) {
    if (!files || files.length === 0) return;
    const f = files[0];
    if (!f.type.startsWith("audio/")) {
      alert("Please upload an audio file (wav/mp3/m4a)");
      return;
    }
    setFile(f);
  }

  function onInputChange(e) {
    handleFiles(e.target.files);
  }

  function onDrop(e) {
    e.preventDefault();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  }

  return (
    <div>
      <label className="block text-sm font-medium mb-2 text-slate-200">{label}</label>
      <div
        onDrop={onDrop}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        className={clsx(
          "w-full rounded-lg p-4 border-2 border-dashed transition-all",
          dragActive ? "border-indigo-400 bg-indigo-950/10" : "border-gray-700 bg-gray-800"
        )}
        style={{ minHeight: 96 }}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          id={`${idPrefix}-file`}
          type="file"
          accept="audio/*"
          className="hidden"
          onChange={onInputChange}
        />
        <div className="flex items-center gap-4">
          <div className="flex-none w-12 h-12 rounded-md bg-gradient-to-br from-indigo-600 to-fuchsia-600 flex items-center justify-center text-white font-bold">
            🎤
          </div>
          <div className="flex-1">
            <div className="text-sm text-slate-200 font-semibold">Drag & drop or click to select</div>
            <div className="text-xs text-slate-400 mt-1">Supported: WAV, MP3, M4A — Try 3–10s target clips</div>
          </div>
          <div>
            {file ? (
              <div className="text-sm text-slate-200 text-right">
                <div className="font-medium">{file.name}</div>
                <div className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
              </div>
            ) : (
              <div className="text-sm text-slate-400">No file</div>
            )}
          </div>
        </div>
      </div>

      {file && (
        <div className="mt-3 flex items-center gap-3">
          <audio controls src={URL.createObjectURL(file)} className="w-full" />
          <button
            onClick={() => setFile(null)}
            className="text-xs bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded"
            title="Remove"
          >
            Remove
          </button>
        </div>
      )}
    </div>
  );
}
