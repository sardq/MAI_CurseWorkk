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
    <div>
      <h1>Система обнаружения ошибок</h1>
      <form onSubmit={handleSubmit}>
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
          cols="80"
        />
        <button type="submit" disabled={loading || !code.trim()}>
          {loading ? 'Анализ...' : 'Запустить анализ'}
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {report && <ResultsDisplay report={report} />}
    </div>
  );
}
