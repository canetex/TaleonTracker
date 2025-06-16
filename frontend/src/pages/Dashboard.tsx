import React, { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Button,
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
import { Add as AddIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

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

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get('/api/characters');
        setCharacters(response.data);
        setError(null);
      } catch (err) {
        setError('Erro ao carregar dados dos personagens');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  if (characters.length === 0) {
    return (
      <Box 
        display="flex" 
        flexDirection="column" 
        alignItems="center" 
        justifyContent="center" 
        minHeight="60vh"
        textAlign="center"
      >
        <Typography variant="h5" color="textSecondary" gutterBottom>
          Bem-vindo ao TaleonTracker!
        </Typography>
        <Typography variant="h6" color="textSecondary" gutterBottom>
          Nenhum personagem cadastrado
        </Typography>
        <Typography color="textSecondary" mb={3}>
          Comece adicionando seu primeiro personagem para rastrear seu progresso
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => navigate('/characters')}
        >
          Adicionar Primeiro Personagem
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        {characters.map((character) => (
          <Grid item xs={12} md={6} key={character.id}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                {character.name}
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
        ))}
      </Grid>
    </Box>
  );
};

export default Dashboard; 