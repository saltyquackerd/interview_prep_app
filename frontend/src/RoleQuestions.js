import React, { useState } from "react";

function RoleQuestions() {
  const [role, setRole] = useState("");
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchQuestions = async () => {
    setLoading(true);
    setQuestions([]);
    const response = await fetch(
      `http://localhost:8000/questions?role=${encodeURIComponent(role)}`
    );
    const data = await response.json();
    setQuestions(data.questions || []);
    setLoading(false);
  };

  return (
    <div style={{ margin: 20 }}>
      <h2>Get Interview Questions</h2>
      <input
        type="text"
        value={role}
        onChange={e => setRole(e.target.value)}
        placeholder="Enter role (e.g. Software Engineer)"
        style={{ marginRight: 10 }}
      />
      <button onClick={fetchQuestions} disabled={!role || loading}>
        {loading ? "Loading..." : "Get Questions"}
      </button>
      {questions.length > 0 && (
        <ul style={{ marginTop: 20 }}>
          {questions.map((q, i) => (
            <li key={i}>{q}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default RoleQuestions;
