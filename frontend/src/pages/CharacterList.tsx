import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Typography,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { Add as AddIcon, Refresh as RefreshIcon } from '@mui/icons-material';

import { api } from '../services/api';
import { Character } from '../types';

const CharacterList: React.FC = () => {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [newCharacterName, setNewCharacterName] = useState('');

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      const response = await api.get('/characters');
      setCharacters(response.data);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar personagens');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCharacters();
  }, []);

  const handleAddCharacter = async () => {
    try {
      console.log('Enviando dados:', { name: newCharacterName });
      const response = await api.post('/characters/', { name: newCharacterName });
      console.log('Resposta:', response.data);
      setOpenDialog(false);
      setNewCharacterName('');
      fetchCharacters();
    } catch (err: any) {
      console.error('Erro detalhado:', err.response?.data || err.message);
      const errorMessage = err.response?.data?.detail || err.message || 'Erro desconhecido';
      setError(`Erro ao adicionar personagem: ${errorMessage}`);
    }
  };

  const handleUpdateCharacter = async (id: number) => {
    try {
      await api.post(`/characters/${id}/update`);
      fetchCharacters();
    } catch (err) {
      setError('Erro ao atualizar personagem');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Personagens</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Novo Personagem
        </Button>
      </Box>

      {error && (
        <Typography color="error" mb={2}>
          {error}
        </Typography>
      )}

      {!error && characters.length === 0 ? (
        <Box 
          display="flex" 
          flexDirection="column" 
          alignItems="center" 
          justifyContent="center" 
          minHeight="40vh"
          textAlign="center"
        >
          <Typography variant="h6" color="textSecondary" gutterBottom>
            Nenhum personagem cadastrado
          </Typography>
          <Typography color="textSecondary" mb={3}>
            Clique no botão "Novo Personagem" para começar a rastrear seus personagens
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
          >
            Adicionar Primeiro Personagem
          </Button>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {characters.map((character) => (
            <Grid item xs={12} sm={6} md={4} key={character.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {character.name}
                  </Typography>
                  <Typography color="textSecondary">
                    Nível: {character.history[0]?.level || 'N/A'}
                  </Typography>
                  <Typography color="textSecondary">
                    Experiência: {character.history[0]?.experience.toLocaleString() || 'N/A'}
                  </Typography>
                  <Typography color="textSecondary">
                    Mortes: {character.history[0]?.deaths || 0}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    color="primary"
                    onClick={() => navigate(`/characters/${character.id}`)}
                  >
                    Detalhes
                  </Button>
                  <Button
                    size="small"
                    color="secondary"
                    startIcon={<RefreshIcon />}
                    onClick={() => handleUpdateCharacter(character.id)}
                  >
                    Atualizar
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Adicionar Novo Personagem</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nome do Personagem"
            type="text"
            fullWidth
            value={newCharacterName}
            onChange={(e) => setNewCharacterName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancelar</Button>
          <Button onClick={handleAddCharacter} color="primary">
            Adicionar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CharacterList; 