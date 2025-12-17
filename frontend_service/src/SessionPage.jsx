import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:8008/api/v1/sessions";

export default function SessionsPage() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(API_URL, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.json())
      .then(data => {
        setSessions(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const getStatusStyle = (status) => {
    const s = status?.toLowerCase();
    if (s === 'completed') return 'bg-green-100 text-green-700 border-green-200';
    if (s === 'failed') return 'bg-red-100 text-red-700 border-red-200';
    return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  };

  const getStatusLabel = (status) => {
    const s = status?.toLowerCase();
    if (s === 'completed') return 'Завершено';
    if (s === 'failed') return 'Ошибка';
    return 'В обработке';
  };

  return (
    <div className="max-w-4xl mx-auto p-6 md:p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">История анализов</h2>
        <p className="text-gray-500 text-sm mt-1">Список ваших предыдущих проверок кода</p>
      </div>
      
      {loading ? (
        <div className="text-center py-12 text-gray-500">Загрузка истории...</div>
      ) : (
        <div className="space-y-4">
          {sessions.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
              <p className="text-gray-500 font-medium">История пуста</p>
              <p className="text-gray-400 text-sm mt-1">Запустите анализ кода, чтобы увидеть результат здесь</p>
            </div>
          )}
          
          {sessions.map(s => (
            <div key={s.session_id} className="group bg-white p-5 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200">
              <div className="flex justify-between items-start md:items-center flex-col md:flex-row gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-gray-800 text-lg">{s.filename || "Без названия"}</span>
                    <span className="text-xs font-mono text-gray-400 bg-gray-50 px-2 py-0.5 rounded border border-gray-100">
                      ID: {s.session_id}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>
                      Ошибок найдено: <span className={s.error_count > 0 ? "text-red-600 font-bold" : "text-green-600 font-bold"}>
                        {s.error_count}
                      </span>
                    </span>
                    {s.start_time && (
                      <span title="Время запуска">
                        {new Date(s.start_time).toLocaleString('ru-RU')}
                      </span>
                    )}
                  </div>
                </div>
                
                <div>
                  <span className={`px-3 py-1.5 rounded-full text-xs font-bold border uppercase tracking-wide ${getStatusStyle(s.status)}`}>
                    {getStatusLabel(s.status)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}