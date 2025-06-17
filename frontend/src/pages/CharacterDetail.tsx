import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Grid,
} from '@mui/material';
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
import { Line } from 'react-chartjs-2';
import { ArrowBack as ArrowBackIcon, Refresh as RefreshIcon } from '@mui/icons-material';

import { api } from '../services/api';
import { Character } from '../types';

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
  const navigate = useNavigate();
  const [character, setCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCharacter = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/characters/${id}/history`);
      setCharacter(response.data);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar dados do personagem');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCharacter();
  }, [id, fetchCharacter]);

  const handleUpdate = async () => {
    try {
      await api.post(`/api/characters/${id}/update`);
      fetchCharacter();
    } catch (err) {
      setError('Erro ao atualizar dados do personagem');
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

  if (error || !character) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Typography color="error">{error || 'Personagem não encontrado'}</Typography>
      </Box>
    );
  }

  const latestHistory = character.history[0];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/characters')}
        >
          Voltar
        </Button>
        <Button
          variant="contained"
          color="primary"
          startIcon={<RefreshIcon />}
          onClick={handleUpdate}
        >
          Atualizar Dados
        </Button>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          {character.name}
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={3}>
            <Typography variant="h6">Nível Atual</Typography>
            <Typography variant="h4">{latestHistory.level}</Typography>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Typography variant="h6">Experiência</Typography>
            <Typography variant="h4">
              {latestHistory.experience.toLocaleString()}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Typography variant="h6">Experiência Diária</Typography>
            <Typography variant="h4">
              {latestHistory.daily_experience.toLocaleString()}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Typography variant="h6">Mortes</Typography>
            <Typography variant="h4">{latestHistory.deaths}</Typography>
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Evolução de Nível
            </Typography>
            <Box height={300}>
              <Line
                data={{
                  labels: character.history.map((h) =>
                    new Date(h.timestamp).toLocaleDateString()
                  ),
                  datasets: [
                    {
                      label: 'Nível',
                      data: character.history.map((h) => h.level),
                      borderColor: 'rgb(75, 192, 192)',
                      tension: 0.1,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Evolução de Experiência
            </Typography>
            <Box height={300}>
              <Line
                data={{
                  labels: character.history.map((h) =>
                    new Date(h.timestamp).toLocaleDateString()
                  ),
                  datasets: [
                    {
                      label: 'Experiência',
                      data: character.history.map((h) => h.experience),
                      borderColor: 'rgb(255, 99, 132)',
                      tension: 0.1,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CharacterDetail; 