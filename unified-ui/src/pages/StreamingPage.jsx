import { useState, useEffect, useRef } from "react";

export default function StreamingPage() {
  const [wsStatus, setWsStatus] = useState("Disconnected");
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);

  const wsRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);

  const connectWebSocket = () => {
    wsRef.current = new WebSocket("ws://localhost:8000/api/stream");

    wsRef.current.onopen = () => {
      setWsStatus("Connected");
      console.log("WebSocket connected");
    };

    wsRef.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      console.log("WS Message:", msg);

      setMessages((prev) => [...prev, msg]);
    };

    wsRef.current.onclose = () => {
      setWsStatus("Disconnected");
      console.log("WebSocket disconnected");
    };
  };

  useEffect(() => {
    connectWebSocket();
    return () => wsRef.current?.close();
  }, []);

  const startStreaming = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0 && wsRef.current.readyState === WebSocket.OPEN) {
          e.data.arrayBuffer().then((buffer) => {
            wsRef.current.send(buffer);
          });
        }
      };

      mediaRecorderRef.current.start(500); // send chunks every 500ms
      setStreaming(true);
    } catch (error) {
      alert("Microphone access blocked! Enable mic permissions.");
      console.error(error);
    }
  };

  const stopStreaming = () => {
    mediaRecorderRef.current?.stop();
    setStreaming(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center py-10 text-white px-4">
      <h1 className="text-3xl font-bold text-blue-400 mb-4">
        Real-Time Streaming (WebSocket)
      </h1>

      {/* WebSocket Status */}
      <div
        className={`px-4 py-2 rounded-lg mb-6 ${
          wsStatus === "Connected" ? "bg-green-600" : "bg-red-600"
        }`}
      >
        WebSocket: {wsStatus}
      </div>

      {/* Buttons */}
      <div className="space-x-4 mb-8">
        {!streaming ? (
          <button
            onClick={startStreaming}
            className="bg-blue-500 hover:bg-blue-600 px-6 py-3 rounded-lg font-semibold"
          >
            Start Streaming
          </button>
        ) : (
          <button
            onClick={stopStreaming}
            className="bg-red-500 hover:bg-red-600 px-6 py-3 rounded-lg font-semibold"
          >
            Stop Streaming
          </button>
        )}
      </div>

      {/* Incoming Messages */}
      <div className="bg-gray-800 p-6 rounded-lg w-full max-w-2xl shadow-xl">
        <h2 className="text-xl font-semibold text-green-400 mb-3">
          Incoming Messages
        </h2>

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {messages.length === 0 && (
            <p className="text-gray-300 text-sm">No messages yet...</p>
          )}

          {messages.map((msg, idx) => (
            <pre
              key={idx}
              className="bg-gray-700 p-3 rounded text-sm text-gray-200"
            >
              {JSON.stringify(msg, null, 2)}
            </pre>
          ))}
        </div>
      </div>
    </div>
  );
}
