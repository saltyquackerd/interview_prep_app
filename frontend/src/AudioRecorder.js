import React, { useRef, useState } from "react";

function AudioRecorder() {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcript, setTranscript] = useState("");
  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);

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
    mediaRecorderRef.current.stop();
    setRecording(false);
  };

  const transcribeAudio = async () => {
    if (!audioBlob) return;
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.mp3");
    const response = await fetch("http://127.0.0.1:8000/transcribe", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    setTranscript(data.text);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Audio Recorder</h2>
      <button onClick={recording ? stopRecording : startRecording}>
        {recording ? "Stop Recording" : "Start Recording"}
      </button>
      {audioURL && (
        <div>
          <audio src={audioURL} controls />
          <div style={{ marginTop: 10 }}>
            <button onClick={transcribeAudio}>Transcribe</button>
          </div>
        </div>
      )}
      {transcript && (
        <div>
          <h3>Transcription:</h3>
          <p>{transcript}</p>
        </div>
      )}
    </div>
  );
}

export default AudioRecorder;
