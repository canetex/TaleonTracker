import React, { useState } from 'react';
import { addCharacter } from '../services/api';
import { TextField, Button, Box, Alert } from '@mui/material';

export interface AddCharacterFormProps {
  onAdd: () => Promise<void>;
}

const AddCharacterForm: React.FC<AddCharacterFormProps> = ({ onAdd }) => {
  const [name, setName] = useState('');
  const [world, setWorld] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await addCharacter({ name, world });
      setName('');
      setWorld('');
      await onAdd();
    } catch (err) {
      setError('Erro ao adicionar personagem. Verifique se o nome e mundo estão corretos.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', gap: 2 }}>
        <TextField
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nome do personagem"
          required
          fullWidth
        />
        <TextField
          value={world}
          onChange={(e) => setWorld(e.target.value)}
          placeholder="Mundo"
          required
          fullWidth
        />
        <Button
          type="submit"
          variant="contained"
          disabled={loading}
          sx={{ minWidth: 120 }}
        >
          {loading ? 'Adicionando...' : 'Adicionar'}
        </Button>
      </Box>
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default AddCharacterForm; 