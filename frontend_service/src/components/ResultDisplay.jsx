import React from 'react';

function ResultsDisplay({ report }) {
    const getSeverityClass = (severity) => {
        return `severity-${severity.toLowerCase()}`
    }
    if (!report || report.total_errors === 0) {
        return (
            <div className="success-message">
                 Анализ завершен за {report.duration_ms} мс. Ошибок не найдено.
                <p>ID Сессии: {report.session_id}</p>
            </div>
        );
    }

    return (
        <div className="results-display">
            <h2>Отчет по Анализу (ID Сессии: {report.session_id})</h2>
            <p>Найдено ошибок: <strong>{report.total_errors}</strong>. Время: {report.duration_ms} мс.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Серьезность</th>
                        <th>Тип</th>
                        <th>Строка:Столбец</th>
                        <th>Сообщение</th>
                        <th>Рекомендация</th>
                    </tr>
                </thead>
                <tbody>
                    {report.errors.map((error, index) => (
                        <tr key={index} className={getSeverityClass(error.severity)}>
                            <td>{error.severity}</td>
                            <td>{error.error_type}</td>
                            <td>{error.line}:{error.column}</td>
                            <td>{error.message} ({error.description})</td>
                            <td>{error.suggestion || 'Нет данных в Базе Знаний'}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default ResultsDisplay;