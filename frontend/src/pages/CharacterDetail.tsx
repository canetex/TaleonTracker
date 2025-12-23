import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
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
import { getCharacterHistory, updateCharacter } from '../services/api';
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

const CharacterDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [character, setCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchCharacter();
  }, [id]);

  const fetchCharacter = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await getCharacterHistory(parseInt(id));
      setCharacter(response);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar dados do personagem');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!id) return;
    try {
      setUpdating(true);
      await updateCharacter(parseInt(id), {});
      await fetchCharacter();
    } catch (err) {
      setError('Erro ao atualizar dados do personagem');
    } finally {
      setUpdating(false);
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

  if (!character) {
    return (
      <Box p={2}>
        <Alert severity="warning">Personagem não encontrado</Alert>
      </Box>
    );
  }

  const latestHistory = character.history && character.history.length > 0 
    ? character.history[0] 
    : null;
  const history = character.history || [];

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box display="flex" alignItems="center" gap={2}>
                {character.outfit && (
                  <img 
                    src={character.outfit.startsWith('http') ? character.outfit : `https://san.taleon.online${character.outfit}`}
                    alt={`${character.name} outfit`}
                    style={{ width: 64, height: 64 }}
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                )}
                <Typography variant="h4">{character.name}</Typography>
              </Box>
              <Button
                variant="contained"
                color="primary"
                onClick={handleUpdate}
                disabled={updating}
              >
                {updating ? 'Atualizando...' : 'Atualizar Dados'}
              </Button>
            </Box>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1">Nível</Typography>
                <Typography variant="h6">
                  {latestHistory ? latestHistory.level : character.level || 'N/A'}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1">Experiência</Typography>
                <Typography variant="h6">
                  {latestHistory ? latestHistory.experience.toLocaleString() : (character.experience || 0).toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1">Experiência Diária</Typography>
                <Typography variant="h6">
                  {latestHistory ? latestHistory.daily_experience.toLocaleString() : (character.daily_experience || 0).toLocaleString()}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {history.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Progresso de Nível e Experiência
              </Typography>
              <Line
                data={{
                  labels: history
                    .slice()
                    .reverse()
                    .map((h: CharacterHistory) =>
                      new Date(h.timestamp).toLocaleDateString()
                    ),
                  datasets: [
                    {
                      label: 'Nível',
                      data: history
                        .slice()
                        .reverse()
                        .map((h: CharacterHistory) => h.level),
                      borderColor: 'rgb(75, 192, 192)',
                      backgroundColor: 'rgba(75, 192, 192, 0.2)',
                      tension: 0.1,
                      yAxisID: 'y',
                    },
                    {
                      label: 'Experiência',
                      data: history
                        .slice()
                        .reverse()
                        .map((h: CharacterHistory) => h.experience),
                      borderColor: 'rgb(255, 99, 132)',
                      backgroundColor: 'rgba(255, 99, 132, 0.2)',
                      tension: 0.1,
                      yAxisID: 'y1',
                    },
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
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default CharacterDetail; 