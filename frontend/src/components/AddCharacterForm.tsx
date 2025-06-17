import React, { useState } from 'react';
import { api } from '../services/api';

const AddCharacterForm: React.FC = () => {
  const [name, setName] = useState('');
  const [world, setWorld] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.post('/characters', { name, world });
      setName('');
      setWorld('');
      window.location.reload();
    } catch (err) {
      setError('Erro ao adicionar personagem. Verifique se o nome e mundo estão corretos.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nome do personagem"
          className="flex-1 p-2 border rounded"
          required
        />
        <input
          type="text"
          value={world}
          onChange={(e) => setWorld(e.target.value)}
          placeholder="Mundo"
          className="flex-1 p-2 border rounded"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
        >
          {loading ? 'Adicionando...' : 'Adicionar'}
        </button>
      </div>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </form>
  );
};

export default AddCharacterForm; 