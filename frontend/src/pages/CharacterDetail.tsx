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

  const latestHistory = character.history[0];

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h4">{character.name}</Typography>
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
                <Typography variant="h6">{latestHistory.level}</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1">Experiência</Typography>
                <Typography variant="h6">{latestHistory.experience.toLocaleString()}</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1">Experiência Diária</Typography>
                <Typography variant="h6">{latestHistory.daily_experience.toLocaleString()}</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Progresso de Nível
            </Typography>
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
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Progresso de Experiência
            </Typography>
            <Line
              data={{
                labels: character.history.map((h: CharacterHistory) =>
                  new Date(h.timestamp).toLocaleDateString()
                ),
                datasets: [
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
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CharacterDetail; 