"use client";

import React, { useState, useRef, useEffect } from "react";

const ROLES = [
  { label: "Software Engineer", value: "software engineer" },
  { label: "Data Scientist", value: "data scientist" },
  { label: "Product Manager", value: "product manager" },
];

type Message = {
  sender: "bot" | "user";
  text: string;
};

export default function Home() {
  const [hasMounted, setHasMounted] = useState(false);
  useEffect(() => { setHasMounted(true); }, []);
  const [role, setRole] = useState(ROLES[0].value);
  const [started, setStarted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [resume, setResume] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [transcript, setTranscript] = useState("");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  // Start interview
  const startInterview = async () => {
    setStarted(true);
    setMessages([]);
    setTranscript("");
    setAudioURL(null);
    setAudioBlob(null);
    setLoading(true);
    // Optionally, upload resume to backend here if needed
    const res = await fetch("http://localhost:8000/chat_interview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role, history: [] }),
    });
    const data = await res.json();
    setMessages([{ sender: "bot", text: data.reply }]);
    setLoading(false);
  };

  // Send user answer (audio transcript only)
  const sendAnswer = async (answer: string) => {
    const newHistory: Message[] = [...messages, { sender: "user", text: answer }];
    setMessages(newHistory);
    setTranscript("");
    setAudioURL(null);
    setAudioBlob(null);
    setLoading(true);
    const res = await fetch("http://localhost:8000/chat_interview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role,
        history: newHistory.map(m => ({ role: m.sender, text: m.text })),
      }),
    });
    const data = await res.json();
    setMessages([...newHistory, { sender: "bot" as const, text: data.reply }]);
    setLoading(false);
  };

  // Audio recording logic
  const startRecording = async () => {
    setTranscript("");
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new window.MediaRecorder(stream);
    audioChunks.current = [];
    mediaRecorderRef.current.ondataavailable = (e) => {
      audioChunks.current.push(e.data);
    };
    mediaRecorderRef.current.onstop = () => {
      const blob = new Blob(audioChunks.current, { type: "audio/mp3" });
      setAudioURL(URL.createObjectURL(blob));
      setAudioBlob(blob);
    };
    mediaRecorderRef.current.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  // Transcribe and send audio answer
  const transcribeAndSend = async () => {
    if (!audioBlob) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.mp3");
    const response = await fetch("http://localhost:8000/transcribe", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    setTranscript(data.text);
    await sendAnswer(data.text);
    setAudioBlob(null);
    setAudioURL(null);
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center py-10">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-lg p-10 border border-gray-200">
        <div className="mb-8">
          <label className="block mb-2 font-semibold text-lg">Select Role</label>
          <select
            className="w-full border border-gray-300 rounded-lg px-4 py-2 text-base focus:outline-none focus:ring-2 focus:ring-black"
            value={role}
            onChange={e => setRole(e.target.value)}
            disabled={started}
          >
            {ROLES.map(r => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>
          <div className="mt-4">
            <label className="block mb-2 font-semibold">Upload Resume (PDF, DOCX, etc.)</label>
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={e => setResume(e.target.files?.[0] || null)}
              disabled={started}
              className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-black file:text-white hover:file:bg-gray-900"
            />
            {resume && (
              <div className="mt-2 text-sm text-gray-600">Selected: {resume.name}</div>
            )}
          </div>
          {!started && (
            <button
              className="mt-4 px-5 py-2 w-full bg-black text-white rounded-lg font-semibold hover:bg-gray-900 transition"
              onClick={startInterview}
              disabled={!resume}
            >
              Start Interview
            </button>
          )}
        </div>
        {started && (
          <div className="mb-8 min-h-96 bg-gray-50 rounded-lg border border-gray-100 p-4 flex flex-col gap-6">
            {messages.map((msg, i) => (
              <div key={i} className="">
                {msg.sender === "bot" ? (
                  <div className="font-semibold text-lg text-black mb-2">{msg.text}</div>
                ) : (
                  <div className="text-gray-800 whitespace-pre-line border-l-4 border-black pl-4 italic">{msg.text}</div>
                )}
              </div>
            ))}
            {loading && (
              <div className="font-semibold text-lg text-black animate-pulse">...</div>
            )}
          </div>
        )}
        {started && (
          <div className="flex flex-col gap-4">
            <div className="flex items-center space-x-4">
              <button
                className={`px-5 py-2 rounded-lg font-semibold text-white bg-black hover:bg-gray-900 transition ${recording ? "opacity-70" : ""}`}
                onClick={recording ? stopRecording : startRecording}
                disabled={loading}
              >
                {recording ? "Stop Recording" : "Record Answer"}
              </button>
              {hasMounted && audioURL && (
                <audio src={audioURL} controls className="h-10" suppressHydrationWarning />
              )}
              {hasMounted && audioBlob && (
                <button
                  className="px-5 py-2 rounded-lg font-semibold text-white bg-black hover:bg-gray-900 transition"
                  onClick={transcribeAndSend}
                  disabled={loading}
                  suppressHydrationWarning
                >
                  Transcribe & Continue
                </button>
              )}
            </div>
            {hasMounted && transcript && (
              <div className="mt-2 text-sm text-gray-600" suppressHydrationWarning>Transcript: {transcript}</div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
