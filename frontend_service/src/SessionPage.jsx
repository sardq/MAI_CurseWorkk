import React, { useEffect, useState } from "react";

const API_URL = "http://report_service:8008/api/v1/sessions";

export default function SessionsPage() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(API_URL, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.json())
      .then(setSessions);
  }, []);

  return (
    <div>
      <h2>История анализов</h2>
      <ul>
        {sessions.map(s => (
          <li key={s.session_id}>
            {s.filename} — {s.status} — ошибок: {s.error_count}
          </li>
        ))}
      </ul>
    </div>
  );
}
