import React, { useState } from 'react';
import axios from 'axios';

const MLTrainingPage = () => {
  const [data, setData] = useState({
    buggy_code: '',
    fixed_code: '',
    commit_message: ''
  });
  const [status, setStatus] = useState({ type: '', msg: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: 'info', msg: 'Отправка данных...' });
    
    try {
      await axios.post('http://localhost:8005/train/feedback', data);
      setStatus({ type: 'success', msg: 'Успешно! Данные добавлены в очередь обучения.' });
      setData({ buggy_code: '', fixed_code: '', commit_message: '' });
    } catch (error) {
      setStatus({ type: 'error', msg: 'Ошибка отправки: ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 md:p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Обучение ML-модели</h2>
        <p className="text-gray-500 mt-1">
          Помогите улучшить систему, добавив примеры ошибочного кода и их исправления.
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <form onSubmit={handleSubmit} className="p-6 md:p-8 space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700">
                Ошибочный код
              </label>
              <textarea
                rows="6"
                className="w-full bg-red-50 border border-red-100 rounded-lg p-3 font-mono text-sm focus:ring-2 focus:ring-red-200 focus:border-red-300 outline-none transition-all placeholder-gray-400"
                value={data.buggy_code}
                onChange={e => setData({ ...data, buggy_code: e.target.value })}
                required
                placeholder="def my_function()"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-700">
                Исправленный код
              </label>
              <textarea
                rows="6"
                className="w-full bg-green-50 border border-green-100 rounded-lg p-3 font-mono text-sm focus:ring-2 focus:ring-green-200 focus:border-green-300 outline-none transition-all placeholder-gray-400"
                value={data.fixed_code}
                onChange={e => setData({ ...data, fixed_code: e.target.value })}
                required
                placeholder="def my_function():"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-semibold text-gray-700">
              Описание исправления (для базы знаний)
            </label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-sm"
              value={data.commit_message}
              onChange={e => setData({ ...data, commit_message: e.target.value })}
              required
              placeholder="Например: Пропущено двоеточие в объявлении функции"
            />
          </div>

          <div className="pt-4 border-t border-gray-100">
            <button
              type="submit"
              disabled={loading}
              className="w-full md:w-auto bg-blue-600 text-white font-semibold px-6 py-2.5 rounded-lg hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? 'Отправка...' : 'Отправить в обучение'}
            </button>
          </div>
        </form>
      </div>

{status.msg && (
        <div className={`mt-6 p-4 rounded-lg border text-sm font-medium ${
          status.type === 'success' ? 'bg-green-50 text-green-800 border-green-200' :
          status.type === 'error' ? 'bg-red-50 text-red-800 border-red-200' :
          'bg-blue-50 text-blue-800 border-blue-200'
        }`}>
          {status.msg}
        </div>
      )}
    </div>
  );
};

export default MLTrainingPage;