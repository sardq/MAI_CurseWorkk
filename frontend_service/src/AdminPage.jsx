import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:8004/admin/users/";

export default function AdminPage() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(API_URL, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.json())
      .then(setUsers);
  }, []);

  return (
    <div>
      <h2>Администрирование</h2>
      <ul>
        {users.map(u => (
          <li key={u.id}>{u.username} ({u.role})</li>
        ))}
      </ul>
    </div>
  );
}
