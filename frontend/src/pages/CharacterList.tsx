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
  Container,
  Alert,
} from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

import { api, updateCharacterData } from '../services/api';
import type { Character } from '../types';
import { formatNumber, formatDate } from '../utils/format';
import AddCharacterForm from '../components/AddCharacterForm';

const CharacterList: React.FC = () => {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

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
      setError('Erro ao buscar lista de personagens');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCharacters();
  }, []);

  const handleAddCharacter = async () => {
    try {
      await fetchCharacters();
    } catch (err: any) {
      console.error('Erro ao atualizar lista:', err);
      setError('Erro ao atualizar lista de personagens');
    }
  };

  const handleUpdateCharacter = async (id: number) => {
    try {
      setUpdatingId(id);
      console.log('Iniciando atualização do personagem:', id);
      
      const response = await updateCharacterData(id);
      console.log('Resposta recebida:', response);
      
      if (response) {
        await fetchCharacters();
      } else {
        throw new Error('Resposta vazia da API');
      }
    } catch (error) {
      console.error('Erro ao atualizar personagem:', error);
      setError('Erro ao atualizar personagem');
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
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Personagens
      </Typography>

      <Box mb={3}>
        <AddCharacterForm onAdd={handleAddCharacter} />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2}>
        {characters.map((character) => (
          <Grid item xs={12} sm={6} md={4} key={character.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="div">
                  {character.name}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  Nível: {formatNumber(character.level)}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  Vocação: {character.vocation}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  Mundo: {character.world}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  Experiência: {formatNumber(character.experience)}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  Experiência Diária: {formatNumber(character.daily_experience)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Última atualização: {formatDate(character.last_updated)}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  color="primary"
                  onClick={() => handleUpdateCharacter(character.id)}
                  disabled={updatingId === character.id}
                  startIcon={<RefreshIcon />}
                >
                  {updatingId === character.id ? "Atualizando..." : "Atualizar"}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default CharacterList; 