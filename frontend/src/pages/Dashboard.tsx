import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { getCharacters } from '../services/api';
import { Character, CharacterHistory } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCharacters();
  }, []);

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      const response = await getCharacters();
      setCharacters(response);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar dados dos personagens');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  // Calcula estatísticas gerais - O(n) onde n é o número de personagens
  const totalCharacters = characters.length;
  const totalExperience = characters.reduce((sum, char) => sum + (char.experience || 0), 0);
  const totalDailyExperience = characters.reduce((sum, char) => sum + (char.daily_experience || 0), 0);
  const averageLevel = totalCharacters > 0 
    ? Math.round(characters.reduce((sum, char) => sum + (char.level || 0), 0) / totalCharacters)
    : 0;
  const worlds = [...new Set(characters.map(char => char.world).filter(Boolean))];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Dashboard</Typography>
        <Button variant="contained" color="primary" onClick={() => navigate('/characters/new')}>
          Adicionar Personagem
        </Button>
      </Box>

      {/* Estatísticas Gerais */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {totalCharacters}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total de Personagens
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {averageLevel}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Nível Médio
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {totalExperience.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              EXP Total
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {totalDailyExperience.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              EXP Diária Total
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Mundos Ativos: {worlds.join(', ') || 'Nenhum'}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {characters.map((character) => (
          <Grid item xs={12} md={6} key={character.id}>
            <Paper sx={{ p: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">{character.name}</Typography>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => navigate(`/characters/${character.id}`)}
                >
                  Detalhes
                </Button>
              </Box>

              <Grid container spacing={2} mb={2}>
                <Grid item xs={4}>
                  <Typography variant="subtitle2">Nível</Typography>
                  <Typography>{character.level}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="subtitle2">Experiência</Typography>
                  <Typography>{character.experience.toLocaleString()}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="subtitle2">Exp. Diária</Typography>
                  <Typography>{character.daily_experience.toLocaleString()}</Typography>
                </Grid>
              </Grid>

              {character.history && character.history.length > 0 ? (
                <Line
                  data={{
                    labels: character.history
                      .slice()
                      .reverse()
                      .map((h: CharacterHistory) =>
                        new Date(h.timestamp).toLocaleDateString()
                      ),
                    datasets: [
                      {
                        label: 'Nível',
                        data: character.history
                          .slice()
                          .reverse()
                          .map((h: CharacterHistory) => h.level),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                      },
                      {
                        label: 'Experiência',
                        data: character.history
                          .slice()
                          .reverse()
                          .map((h: CharacterHistory) => h.experience),
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1,
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        position: 'top' as const,
                      },
                    },
                  }}
                />
              ) : (
                <Typography variant="body2" color="text.secondary" align="center">
                  Sem histórico disponível
                </Typography>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Dashboard; 