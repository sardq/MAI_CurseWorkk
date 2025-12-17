import React, { useState } from 'react';
import ResultsDisplay from './ResultDisplay'; 

const API_URL = "http://localhost:8008/api/v1/analyze_code";

export default function AnalysisForm() {
  const [code, setCode] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setReport(null);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          code: code,
          filename: 'user_input.py',
          user_id: 1
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP Error ${response.status}`);
      }

      const data = await response.json();
      setReport(data);

    } catch (err) {
      setError(`Ошибка анализа: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 md:p-8">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">Система обнаружения ошибок</h1>
        <p className="text-gray-500 mt-2">Вставьте ваш Python код ниже для автоматической проверки</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wider">
              Исходный код
            </label>
            <div className="relative">
              <textarea
                value={code}
                onChange={e => setCode(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Tab') {
                    e.preventDefault();
                    const start = e.target.selectionStart;
                    const end = e.target.selectionEnd;
                    setCode(code.substring(0, start) + '\t' + code.substring(end));
                    setTimeout(() => {
                      e.target.selectionStart = e.target.selectionEnd = start + 1;
                    }, 0);
                  }
                }}
                rows="15"
                className="w-full bg-gray-50 border border-gray-300 rounded-lg p-4 font-mono text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y transition-shadow"
                placeholder="def my_function():&#10;    print('Hello World')"
                spellCheck="false"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading || !code.trim()}
              className="bg-blue-600 text-white font-medium py-2.5 px-6 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            >
              {loading ? 'Выполняется анализ...' : 'Запустить анализ'}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="mt-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
          <p className="text-red-700 font-medium">Ошибка выполнения</p>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      )}

      {report && (
        <div className="mt-8">
          <ResultsDisplay report={report} />
        </div>
      )}
    </div>
  );
}