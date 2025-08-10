import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

// Optional: point to your FastAPI backend for ElevenLabs voice streaming
window.__VITE_API__ = "http://localhost:8000";

createRoot(document.getElementById("root")).render(<App />);
