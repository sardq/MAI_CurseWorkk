import React, { useState, useEffect } from 'react';
import api from './components/api';

const AdminUsersPage = () => {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users/');
      setUsers(response.data);
    } catch (error) {
      console.error("Ошибка загрузки пользователей", error);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm("Вы уверены, что хотите удалить пользователя? Это действие необратимо.")) return;

    try {
      await api.delete(`/admin/users/${userId}`);
      alert("Пользователь удален");
      fetchUsers();
    } catch (error) {
      alert('Ошибка удаления: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getRoleBadge = (role) => {
    switch (role) {
      case 'admin':
        return <span className="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded uppercase">Admin</span>;
      case 'operator':
        return <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-1 rounded uppercase">Operator</span>;
      default:
        return <span className="bg-gray-100 text-gray-600 text-xs font-bold px-2 py-1 rounded uppercase">User</span>;
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 md:p-8">
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Управление пользователями</h2>
        <div className="text-sm text-gray-500">
          Всего пользователей: <span className="font-semibold text-gray-900">{users.length}</span>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Имя пользователя</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Роль</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider text-right">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map(u => (
                <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 text-sm text-gray-500 font-mono">#{u.id}</td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{u.username}</td>
                  <td className="px-6 py-4">
                    {getRoleBadge(u.role)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleDeleteUser(u.id)}
                      className="text-sm text-red-600 hover:text-red-800 font-medium hover:underline transition-colors focus:outline-none"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-gray-500 italic">
                    Пользователи не найдены
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminUsersPage;