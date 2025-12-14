import React, { useState } from 'react';
import ResultsDisplay from './ResultsDisplay'; 

const API_URL = 'http://localhost:8080/api/v1/analyze_code'; 

function AnalysisForm() {
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
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
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
            console.error('Analysis failed:', err);
            setError("Ошибка анализа: ${err.message}. Проверьте доступность бэкенда.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="analysis-container">
            <h1>Система обнаружения ошибок</h1>
            
            <form onSubmit={handleSubmit}>
                <textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="Вставьте исходный код Python..."
                    rows="15"
                    cols="80"
                    disabled={loading}
                />
                <button type="submit" disabled={loading || code.trim() === ''}>
                    {loading ? 'Анализ...' : 'Запустить Анализ Кода'}
                </button>
            </form>

            {error && <p className="error-message"> {error}</p>}
            {report && <ResultsDisplay report={report} />}
        </div>
    );
}

export default AnalysisForm;