import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import UploadPage from "./pages/UploadPage.jsx";
import StreamingPage from "./pages/StreamingPage.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/stream" element={<StreamingPage />} />
      </Routes>
    </BrowserRouter>
  );
}
