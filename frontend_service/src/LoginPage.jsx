import React, { useState } from "react";
import { jwtDecode } from "jwt-decode";

export default function LoginPage({ onLogin, onShowRegister }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8008/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) throw new Error("Неверный логин или пароль");

      const data = await res.json();
      const token = data.access_token;
      const decoded = jwtDecode(token);
      
      localStorage.setItem("token", token);
      localStorage.setItem("role", decoded.role || 'user'); 
      onLogin();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Вход в систему</h1>
          <p className="text-gray-500 mt-2">Введите свои данные для доступа</p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm text-center border border-red-100">
              {error}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Логин</label>
            <input 
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
              placeholder="Введите логин"
              value={username} 
              onChange={e => setUsername(e.target.value)} 
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
            <input 
              type="password" 
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
              placeholder="Введите пароль" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
            />
          </div>

          <button 
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-70 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
          >
            {loading ? "Вход..." : "Войти"}
          </button>
        </form>

        <div className="text-center text-sm text-gray-600">
          Нет аккаунта?{" "}
          <button 
            type="button" 
            onClick={onShowRegister}
            className="text-blue-600 font-semibold hover:underline"
          >
            Зарегистрироваться
          </button>
        </div>
      </div>
    </div>
  );
}