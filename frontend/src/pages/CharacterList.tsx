import React, { useEffect, useState, useMemo } from 'react';
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
  TextField,
  InputAdornment,
} from '@mui/material';
import { Refresh as RefreshIcon, Search as SearchIcon } from '@mui/icons-material';

import { getCharacters, updateCharacter } from '../services/api';
import type { Character } from '../types';
import { formatNumber, formatDate } from '../utils/format';
import AddCharacterForm from '../components/AddCharacterForm';

const CharacterList: React.FC = () => {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [worldFilter, setWorldFilter] = useState<string>('');

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      console.log('Buscando lista de personagens...');
      
      const data = await getCharacters();
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

  // Filtros de busca - O(n) onde n é o número de personagens
  const filteredCharacters = useMemo(() => {
    return characters.filter((character) => {
      const matchesSearch = !searchTerm || 
        character.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        character.vocation.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesWorld = !worldFilter || 
        character.world.toLowerCase().includes(worldFilter.toLowerCase());
      return matchesSearch && matchesWorld;
    });
  }, [characters, searchTerm, worldFilter]);

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
      
      const response = await updateCharacter(id, {});
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

      <Box mb={3} sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Buscar por nome ou vocação..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1, minWidth: 200 }}
        />
        <TextField
          placeholder="Filtrar por mundo..."
          value={worldFilter}
          onChange={(e) => setWorldFilter(e.target.value)}
          sx={{ minWidth: 200 }}
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {filteredCharacters.length === 0 && !loading && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Nenhum personagem encontrado com os filtros aplicados.
        </Alert>
      )}

      <Grid container spacing={2}>
        {filteredCharacters.map((character) => (
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