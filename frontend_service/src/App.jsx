import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './LoginPage';
import AnalysisForm from './components/AnalysisForm';
import SessionsPage from './SessionPage';
import RegisterPage from './RegisterPage';
import AdminPage from './AdminPage';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [showRegister, setShowRegister] = useState(false);
  const handleLogin = () => {
    setToken(localStorage.getItem('token'));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
  return showRegister ? (
    <RegisterPage onRegister={() => setShowRegister(false)} />
  ) : (
    <LoginPage 
      onLogin={handleLogin} 
      onShowRegister={() => setShowRegister(true)} 
    />
  );
} 

  return (
    <Router>
      <div>
        <nav>
          <button onClick={handleLogout}>Выйти</button>
          <a href="/">Анализ</a> | <a href="/sessions">История</a> | <a href="/admin">Админ</a>
        </nav>

        <Routes>
          <Route path="/" element={<AnalysisForm />} />
          <Route path="/sessions" element={<SessionsPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
