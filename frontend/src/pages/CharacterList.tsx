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
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [lastUpdateResponse, setLastUpdateResponse] = useState<any>(null);

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      console.log('Buscando lista de personagens...');
      
      const response = await fetch('http://192.168.1.200:8000/api/characters/');
      console.log('Resposta da lista:', response);
      
      const data = await response.json();
      console.log('Dados da lista:', data);
      
      setCharacters(data);
    } catch (error) {
      console.error('Erro ao buscar personagens:', error);
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
      const response = await api.post('/api/characters/', { name: newCharacterName });
      console.log('Resposta:', response.data);
      setOpenDialog(false);
      setNewCharacterName('');
      await fetchCharacters();
    } catch (err: any) {
      console.error('Erro detalhado:', err);
      let errorMessage = 'Erro ao adicionar personagem';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    }
  };

  const handleUpdateCharacter = async (id: number) => {
    try {
      setUpdatingId(id);
      console.log('Iniciando atualização do personagem:', id);
      
      const response = await fetch(`http://192.168.1.200:8000/api/characters/${id}/update`, {
        method: 'POST',
      });
      
      console.log('Resposta recebida:', response);
      const data = await response.json();
      console.log('Dados recebidos:', data);
      
      setLastUpdateResponse({
        status: response.status,
        statusText: response.statusText,
        data: data
      });
      
      await fetchCharacters();
    } catch (error) {
      console.error('Erro ao atualizar personagem:', error);
      setLastUpdateResponse({
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        timestamp: new Date().toISOString()
      });
    } finally {
      setUpdatingId(null);
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
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Lista de Personagens
          </Typography>
          {loading ? (
            <CircularProgress />
          ) : (
            <Grid container spacing={2}>
              {characters.map((character) => (
                <Grid item xs={12} sm={6} md={4} key={character.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{character.name}</Typography>
                      <Typography color="textSecondary">
                        Nível: {character.level}
                      </Typography>
                      <Typography color="textSecondary">
                        Vocação: {character.vocation}
                      </Typography>
                      <Typography color="textSecondary">
                        Mundo: {character.world}
                      </Typography>
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={() => handleUpdateCharacter(character.id)}
                        disabled={updatingId === character.id}
                        sx={{ mt: 2 }}
                      >
                        {updatingId === character.id ? "Atualizando..." : "Atualizar"}
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}

      {/* Div temporária para debug */}
      <Box sx={{ mt: 4, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
        <Typography variant="h6" gutterBottom>
          Debug - Retorno da API
        </Typography>
        <Typography variant="subtitle1" gutterBottom>
          Última atualização:
        </Typography>
        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {JSON.stringify(lastUpdateResponse, null, 2)}
        </pre>
        <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
          Lista de personagens:
        </Typography>
        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
          {JSON.stringify(characters, null, 2)}
        </pre>
      </Box>

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