import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import AnalysisForm from './components/AnalysisForm';
import SessionsPage from './SessionPage';
import AdminUsersPage from './AdminUsersPage';
import KnowledgeBasePage from './KnowledgeBase';
import MLTrainingPage from './MLTrainigPage';

const NavLink = ({ to, children }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link
      to={to}
      className={`px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
        isActive 
          ? 'bg-blue-50 text-blue-700' 
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
      }`}
    >
      {children}
    </Link>
  );
};

const Header = ({ role, onLogout }) => {
  if (!role) return null;

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 text-white p-1.5 rounded font-bold text-xl">CA</div>
            <span className="font-bold text-gray-800 text-lg">CodeAnalyzer</span>
          </div>

          <nav className="hidden md:flex space-x-2">
            <NavLink to="/">Анализ кода</NavLink>
            {(role === 'admin' || role === 'operator') && (
              <>
                <NavLink to="/sessions">Сессии</NavLink>
                <NavLink to="/knowledge-base">База знаний</NavLink>
                <NavLink to="/ml-training">Обучение ML</NavLink>
              </>
            )}
            {role === 'admin' && (
              <NavLink to="/admin/users">Пользователи</NavLink>
            )}
          </nav>

          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full capitalize">
              {role}
            </span>
            <button
              onClick={onLogout}
              className="text-sm text-red-600 hover:text-red-800 font-medium transition-colors"
            >
              Выйти
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};


const ProtectedRoute = ({ children, allowedRoles }) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (!token) return <Navigate to="/login" />;

  if (allowedRoles && !allowedRoles.includes(role)) {
    return <div>Доступ запрещён</div>;
  }

  return children;
};

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [role, setRole] = useState(localStorage.getItem('role'));
  const [showRegister, setShowRegister] = useState(false);

  const handleLogin = () => {
    setToken(localStorage.getItem('token'));
    setRole(localStorage.getItem('role'));
    return <Navigate to="/" />
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    setToken(null);
    setRole(null);
  };

  if (!token) {
    return showRegister ? (
      <RegisterPage onRegister={() => setShowRegister(false)} />
    ) : (
      <LoginPage onLogin={handleLogin} onShowRegister={() => setShowRegister(true)} />
    );
  }

  return (
    <Router>
      <Header role={role} onLogout={handleLogout} />
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AnalysisForm />
            </ProtectedRoute>
          }
        />
        <Route
          path="/sessions"
          element={
            <ProtectedRoute allowedRoles={['admin', 'operator']}>
              <SessionsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/knowledge-base"
          element={
            <ProtectedRoute allowedRoles={['admin', 'operator']}>
              <KnowledgeBasePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ml-training"
          element={
            <ProtectedRoute allowedRoles={['admin', 'operator']}>
              <MLTrainingPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/users"
          element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminUsersPage />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
