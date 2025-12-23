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
  // Filtra apenas os mundos válidos (san e aura)
  const validWorlds = ['san', 'aura'];
  const worlds = Array.from(new Set(
    characters
      .map(char => char.world?.toLowerCase())
      .filter(world => world && validWorlds.includes(world))
  )).map(w => w.charAt(0).toUpperCase() + w.slice(1));

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
                EXP nas últimas 24hs Total
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
                    <Typography variant="subtitle2">Exp. nas últimas 24hs</Typography>
                    <Typography>{character.daily_experience.toLocaleString()}</Typography>
                  </Grid>
              </Grid>

              {character.history && character.history.length > 0 ? (() => {
                const sortedHistory = character.history
                  .slice()
                  .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
                
                // Calcula média diária de experiência
                let averageDailyExp = 0;
                if (sortedHistory.length > 1) {
                  const firstExp = sortedHistory[0].experience;
                  const lastExp = sortedHistory[sortedHistory.length - 1].experience;
                  const totalExpGained = lastExp - firstExp;
                  const firstDate = new Date(sortedHistory[0].timestamp);
                  const lastDate = new Date(sortedHistory[sortedHistory.length - 1].timestamp);
                  const daysDiff = Math.max(1, Math.ceil((lastDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24)));
                  averageDailyExp = totalExpGained / daysDiff;
                }
                
                return (
                  <Line
                    data={{
                      labels: sortedHistory.map((h: CharacterHistory) =>
                        new Date(h.timestamp).toLocaleDateString()
                      ),
                      datasets: [
                        {
                          label: 'Nível',
                          data: sortedHistory.map((h: CharacterHistory) => h.level),
                          borderColor: 'rgb(75, 192, 192)',
                          backgroundColor: 'rgba(75, 192, 192, 0.2)',
                          tension: 0.1,
                          yAxisID: 'y',
                        },
                        {
                          label: 'Experiência',
                          data: sortedHistory.map((h: CharacterHistory) => h.experience),
                          borderColor: 'rgb(255, 99, 132)',
                          backgroundColor: 'rgba(255, 99, 132, 0.2)',
                          tension: 0.1,
                          yAxisID: 'y1',
                        },
                        ...(averageDailyExp > 0 ? [{
                          label: 'Média Diária de EXP',
                          data: sortedHistory.map((_, index) => {
                            const firstExp = sortedHistory[0].experience;
                            return firstExp + averageDailyExp * index;
                          }),
                          borderColor: 'rgba(255, 206, 86, 0.8)',
                          backgroundColor: 'rgba(255, 206, 86, 0.1)',
                          borderDash: [5, 5],
                          borderWidth: 2,
                          pointRadius: 0,
                          tension: 0,
                          yAxisID: 'y1',
                          fill: false,
                        }] : []),
                      ],
                    }}
                    options={{
                    responsive: true,
                    interaction: {
                      mode: 'index' as const,
                      intersect: false,
                    },
                    plugins: {
                      legend: {
                        position: 'top' as const,
                      },
                    },
                    scales: {
                      y: {
                        type: 'linear' as const,
                        display: true,
                        position: 'left' as const,
                        title: {
                          display: true,
                          text: 'Nível',
                        },
                      },
                      y1: {
                        type: 'linear' as const,
                        display: true,
                        position: 'right' as const,
                        title: {
                          display: true,
                          text: 'Experiência',
                        },
                        grid: {
                          drawOnChartArea: false,
                        },
                    },
                  },
                }}
                  />
                );
              })() : (
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