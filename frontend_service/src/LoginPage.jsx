import React, { useState } from "react";

const API_URL = "http://localhost:8008/api/v1/auth/login"; 

export default function LoginPage({ onLogin, onShowRegister }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);

    const res = await fetch("http://localhost:8008/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      setError("Неверный логин или пароль");
      return;
    }

    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    onLogin();
  };

  return (
    <form onSubmit={submit}>
      <h2>Вход</h2>
      <input placeholder="Логин" value={username} onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="Пароль" value={password} onChange={e => setPassword(e.target.value)} />
      <button>Войти</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <p>
        Нет аккаунта?{" "}
        <button type="button" onClick={onShowRegister}>
          Зарегистрироваться
        </button>
      </p>
    </form>
  );
}

