import React from 'react';

function ResultsDisplay({ report }) {
    if (!report) return null;

    if (report.total_errors === 0) {
        return (
            <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-xl text-center">
                <h3 className="text-xl font-bold text-green-800">Ошибок не найдено!</h3>
                <p className="text-green-600 mt-2">
                    Анализ завершен за {report.duration_ms} мс. Код выглядит отлично.
                </p>
                <p className="text-xs text-green-500 mt-4">ID Сессии: {report.session_id}</p>
            </div>
        );
    }

    const getSeverityBadge = (severity) => {
        const styles = {
            Critical: "bg-red-100 text-red-800 border-red-200",
            Warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
            Info: "bg-blue-100 text-blue-800 border-blue-200",
            Recommendation: "bg-gray-100 text-gray-800 border-gray-200"
        };
        const style = styles[severity] || styles.Recommendation;
        
        return (
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${style}`}>
                {severity}
            </span>
        );

    };

    return (
        <div className="mt-8 animate-fade-in">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-800">Результаты анализа</h2>
                <div className="text-sm text-gray-500 bg-white px-3 py-1 rounded-md shadow-sm border">
                    Найдено: <span className="font-bold text-red-600">{report.total_errors}</span> | Время: {report.duration_ms} мс
                </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Тип / Уровень</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Позиция</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/3">Сообщение</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/3">Рекомендация</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {report.errors.map((error, index) => (
                                <tr key={index} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex flex-col items-start gap-1">
                                            {getSeverityBadge(error.severity)}
                                            <span className="text-xs text-gray-500 font-mono">{error.error_type}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                                        Ln {error.line}, Col {error.column}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-900">
                                        <div className="font-mono bg-gray-50 p-1.5 rounded text-xs border border-gray-200 break-all whitespace-pre-wrap">
                                           {error.message} {error.descripton}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-700">
                                        {error.suggestion ? (
                                            <div className="flex items-start gap-2">
                                                <span>{error.suggestion}</span>
                                            </div>
                                        ) : (
                                            <span className="text-gray-400 italic">Нет рекомендаций</span>
                                        )}
                                        {error.ml_confidence && (
                                            <div className="mt-1 text-xs text-blue-500" title="Уверенность ML">
                                                 ML: {Math.round(error.ml_confidence * 100)}%
                                            </div>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default ResultsDisplay;