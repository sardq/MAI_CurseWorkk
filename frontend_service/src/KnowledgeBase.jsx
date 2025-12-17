import React, { useState, useEffect } from 'react';
import api from './components/api';

const KnowledgeBasePage = () => {
    const [entries, setEntries] = useState([]);
    const [editId, setEditId] = useState(null);
    const [formData, setFormData] = useState({
        error_type: '',
        keyword_pattern: '',
        description: '',
        correction: '',
        severity_level: 'Warning'
    });

    useEffect(() => {
        fetchKB();
    }, []);

    const fetchKB = async () => {
        try {
            const response = await api.get('/admin/knowledge/');
            setEntries(response.data);
        } catch (error) {
            console.error("Ошибка загрузки БЗ", error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editId) {
                await api.patch(`/admin/knowledge/${editId}`, formData);
            } else {
                await api.post(`/admin/knowledge/`, formData);
            }
            setFormData({ error_type: '', keyword_pattern: '', description: '', correction: '', severity_level: 'Warning' });
            setEditId(null);
            fetchKB();
        } catch (error) {
            alert('Ошибка сохранения');
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Удалить запись?")) return;
        try {
            await api.delete(`/admin/knowledge/${id}`);
            fetchKB();
        } catch (error) {
            alert('Ошибка удаления');
        }
    };

    const startEdit = (entry) => {
        setEditId(entry.id);
        setFormData({
            error_type: entry.error_type || '',
            keyword_pattern: entry.keyword_pattern || '',
            description: entry.description,
            correction: entry.correction,
            severity_level: entry.severity_level
        });
    };

  return (
    <div className="max-w-6xl mx-auto p-6 md:p-8">
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800">База Знаний</h2>
        <div className="bg-blue-50 text-blue-700 px-4 py-2 rounded-lg text-sm font-medium">
            Всего записей: {entries.length}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 sticky top-24">
                <h3 className="text-lg font-bold mb-4 text-gray-700">
                    {editId ? "Редактирование записи" : "Новая запись"}
                </h3>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="text-xs font-semibold text-gray-500 uppercase">Тип ошибки</label>
                        <input
                            className="w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                            value={formData.error_type}
                            onChange={e => setFormData({ ...formData, error_type: e.target.value })}
                            required
                            placeholder="Syntax, Logic..."
                        />
                    </div>
                     <div>
                        <label className="text-xs font-semibold text-gray-500 uppercase">Паттерн (опционально)</label>
                        <input
                            className="w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm font-mono"
                            value={formData.keyword_pattern}
                            onChange={e => setFormData({ ...formData, keyword_pattern: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="text-xs font-semibold text-gray-500 uppercase">Рекомендация</label>
                        <textarea
                            rows="3"
                            className="w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                            value={formData.correction}
                            onChange={e => setFormData({ ...formData, correction: e.target.value })}
                            required
                        />
                    </div>
                    
                    <select
                        value={formData.severity_level}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-white text-sm"
                        onChange={e => setFormData({ ...formData, severity_level: e.target.value })}
                    >
                        <option value="Info">Info</option>
                        <option value="Warning">Warning</option>
                        <option value="Critical">Critical</option>
                    </select>

                    <div className="flex gap-2 pt-2">
                        <button type="submit" className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition">
                            {editId ? "Сохранить" : "Добавить"}
                        </button>
                        {editId && (
                            <button 
                                type="button" 
                                className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
onClick={() => setEditId(null)}
                            >
                                Отмена
                            </button>
                        )}
                    </div>
                </form>
            </div>
        </div>

        {/* Правая колонка - Список */}
        <div className="lg:col-span-2 space-y-4">
            {entries.length === 0 && (
                <div className="text-center py-10 text-gray-500 bg-white rounded-xl border border-dashed">
                    База знаний пуста
                </div>
            )}
            {entries.map(entry => (
                <div key={entry.id} className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow group">
                    <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2 py-0.5 rounded text-xs font-bold 
                                ${entry.severity_level === 'Critical' ? 'bg-red-100 text-red-700' : 
                                  entry.severity_level === 'Warning' ? 'bg-yellow-100 text-yellow-700' : 
                                  'bg-blue-100 text-blue-700'}`}>
                                {entry.severity_level}
                            </span>
                            <span className="font-mono text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                                {entry.error_type}
                            </span>
                        </div>
                        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                             <button
                                onClick={() => startEdit(entry)}
                                className="text-blue-600 hover:bg-blue-50 p-1 rounded"
                             >Изменить
                             </button>
                             <button
                                onClick={() => handleDelete(entry.id)}
                                className="text-red-600 hover:bg-red-50 p-1 rounded"
                             >
                                🗑️
                             </button>
                        </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">
                        <span className="font-semibold">Паттерн:</span> {entry.keyword_pattern ? <code className="bg-gray-50 px-1 rounded border">{entry.keyword_pattern}</code> : <span className="italic text-gray-400">Любое совпадение</span>}
                    </p>
                    
                    <div className="grid md:grid-cols-2 gap-4 mt-3">
                        <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                            <h4 className="text-xs font-bold text-gray-500 uppercase mb-1">Описание</h4>
                            <p className="text-sm text-gray-800">{entry.description}</p>
                        </div>
                        <div className="bg-green-50 p-3 rounded-lg border border-green-100">
                             <h4 className="text-xs font-bold text-green-600 uppercase mb-1">Решение</h4>
                             <p className="text-sm text-green-900">{entry.correction}</p>
                        </div>
                    </div>
                </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBasePage;