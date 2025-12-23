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
  IconButton,
  Paper,
  FormControlLabel,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
} from '@mui/material';
import { Refresh as RefreshIcon, Search as SearchIcon, Star as StarIcon, StarBorder as StarBorderIcon } from '@mui/icons-material';

import { getCharacters, updateCharacter, addFavorite, removeFavorite, getFavorites } from '../services/api';
import type { Character } from '../types';
import { formatNumber, formatDate, getOutfitUrl } from '../utils/format';

const CharacterList: React.FC = () => {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [worldFilter, setWorldFilter] = useState<string>('');
  const [favorites, setFavorites] = useState<number[]>([]);
  const [showFavoritesOnly, setShowFavoritesOnly] = useState<boolean>(false);
  const [experienceDaysFilter, setExperienceDaysFilter] = useState<number>(0); // 0 = desativado

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
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      const favs = await getFavorites();
      setFavorites(favs);
    } catch (err) {
      console.error('Erro ao buscar favoritos:', err);
    }
  };

  const handleToggleFavorite = async (characterId: number) => {
    try {
      if (favorites.includes(characterId)) {
        await removeFavorite(characterId);
        setFavorites(favorites.filter(id => id !== characterId));
      } else {
        await addFavorite(characterId);
        setFavorites([...favorites, characterId]);
      }
    } catch (err) {
      console.error('Erro ao atualizar favorito:', err);
    }
  };

  // Filtros de busca - O(n) onde n é o número de personagens
  const filteredCharacters = useMemo(() => {
    return characters.filter((character) => {
      const matchesSearch = !searchTerm || 
        character.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        character.vocation.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesWorld = !worldFilter || 
        character.world.toLowerCase().includes(worldFilter.toLowerCase());
      const matchesFavorites = !showFavoritesOnly || favorites.includes(character.id);
      
      // Filtro de experiência nos últimos dias
      const matchesExperienceDays = !experienceDaysFilter || (() => {
        if (experienceDaysFilter === 0) return true;
        
        // Calcula a data de corte (milissegundos desde epoch)
        const now = new Date();
        const cutoffTime = now.getTime() - (experienceDaysFilter * 24 * 60 * 60 * 1000);
        
        // Verifica se tem experiência diária > 0 e foi atualizado recentemente
        if (character.daily_experience > 0 && character.last_updated) {
          const lastUpdatedTime = new Date(character.last_updated).getTime();
          if (lastUpdatedTime >= cutoffTime) {
            return true;
          }
        }
        
        // Verifica histórico recente
        if (character.history && character.history.length > 0) {
          // Ordena histórico por data (mais recente primeiro)
          const sortedHistory = [...character.history].sort((a, b) => 
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          );
          
          // Encontra registros no período
          const periodHistory = sortedHistory.filter(h => {
            const historyTime = new Date(h.timestamp).getTime();
            return historyTime >= cutoffTime;
          });
          
          if (periodHistory.length > 0) {
            // Se há mais de um registro no período, verifica se houve aumento de experiência
            if (periodHistory.length > 1) {
              for (let i = 0; i < periodHistory.length - 1; i++) {
                if (periodHistory[i].experience > periodHistory[i + 1].experience) {
                  return true;
                }
              }
            }
            
            // Verifica se algum registro no período tem daily_experience > 0
            if (periodHistory.some(h => h.daily_experience > 0)) {
              return true;
            }
            
            // Verifica se o primeiro registro do período tem experiência maior que o último fora do período
            const firstInPeriod = periodHistory[0];
            const lastBeforePeriod = sortedHistory.find(h => {
              const historyTime = new Date(h.timestamp).getTime();
              return historyTime < cutoffTime;
            });
            
            if (lastBeforePeriod && firstInPeriod.experience > lastBeforePeriod.experience) {
              return true;
            }
          }
        }
        
        return false;
      })();
      
      return matchesSearch && matchesWorld && matchesFavorites && matchesExperienceDays;
    });
  }, [characters, searchTerm, worldFilter, showFavoritesOnly, favorites, experienceDaysFilter]);

  // Calcula estatísticas gerais - O(n) onde n é o número de personagens
  const totalCharacters = characters.length;
  const totalDailyExperience = characters.reduce((sum, char) => sum + (char.daily_experience || 0), 0);
  const averageLevel = totalCharacters > 0 
    ? Math.round(characters.reduce((sum, char) => sum + (char.level || 0), 0) / totalCharacters)
    : 0;

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

      {/* Estatísticas Gerais */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {totalCharacters}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total de Personagens
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {averageLevel}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Nível Médio
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {totalDailyExperience.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              EXP no Dia de Hoje
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Box mb={3} sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
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
        <FormControlLabel
          control={
            <Checkbox
              checked={showFavoritesOnly}
              onChange={(e) => setShowFavoritesOnly(e.target.checked)}
              color="primary"
            />
          }
          label="Apenas Favoritos"
        />
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Chars com EXP nos últimos dias</InputLabel>
          <Select
            value={experienceDaysFilter}
            onChange={(e: SelectChangeEvent<number>) => setExperienceDaysFilter(e.target.value as number)}
            label="Chars com EXP nos últimos dias"
          >
            <MenuItem value={0}>Todos</MenuItem>
            <MenuItem value={1}>1 dia</MenuItem>
            <MenuItem value={3}>3 dias</MenuItem>
            <MenuItem value={7}>7 dias</MenuItem>
            <MenuItem value={15}>15 dias</MenuItem>
            <MenuItem value={30}>30 dias</MenuItem>
            <MenuItem value={60}>60 dias</MenuItem>
            <MenuItem value={90}>90 dias</MenuItem>
          </Select>
        </FormControl>
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
                <Box display="flex" alignItems="center" gap={2} mb={1}>
                  {character.outfit && (
                    <img 
                      src={getOutfitUrl(character.outfit)}
                      alt={`${character.name} outfit`}
                      style={{ width: 48, height: 48 }}
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  )}
                  <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                    {character.name}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => handleToggleFavorite(character.id)}
                    color={favorites.includes(character.id) ? "warning" : "default"}
                  >
                    {favorites.includes(character.id) ? <StarIcon /> : <StarBorderIcon />}
                  </IconButton>
                </Box>
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
                  Experiência nas últimas 24hs: {formatNumber(character.daily_experience)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Última atualização: {formatDate(character.last_updated)}
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