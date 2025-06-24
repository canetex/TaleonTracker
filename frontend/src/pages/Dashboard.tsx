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

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Dashboard</Typography>
        <Button variant="contained" color="primary" onClick={() => navigate('/characters/new')}>
          Adicionar Personagem
        </Button>
      </Box>

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
                    labels: character.history.map((h: CharacterHistory) =>
                      new Date(h.timestamp).toLocaleDateString()
                    ),
                    datasets: [
                      {
                        label: 'Nível',
                        data: character.history.map((h: CharacterHistory) => h.level),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                      },
                      {
                        label: 'Experiência',
                        data: character.history.map((h: CharacterHistory) => h.experience),
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