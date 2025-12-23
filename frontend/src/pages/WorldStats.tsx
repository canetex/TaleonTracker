import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
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
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface ServerStats {
  id: number;
  world: string;
  total_experience: number;
  active_characters: number;
  timestamp: string;
}

// Usa URL relativa para funcionar através do proxy do Caddy
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
});

const WorldStats: React.FC = () => {
  const [worlds, setWorlds] = useState<string[]>([]);
  const [selectedWorld, setSelectedWorld] = useState<string>('');
  const [expHistory, setExpHistory] = useState<ServerStats[]>([]);
  const [activeHistory, setActiveHistory] = useState<ServerStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorlds();
  }, []);

  useEffect(() => {
    if (selectedWorld) {
      fetchStats();
    }
  }, [selectedWorld]);

  const fetchWorlds = async () => {
    try {
      const response = await api.get<string[]>('/api/stats/worlds');
      setWorlds(response.data);
      if (response.data.length > 0) {
        setSelectedWorld(response.data[0]);
      }
    } catch (err) {
      setError('Erro ao carregar lista de mundos');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    if (!selectedWorld) return;
    
    try {
      setLoading(true);
      const [expResponse, activeResponse] = await Promise.all([
        api.get<ServerStats[]>(`/api/stats/worlds/${selectedWorld}/exp-history?days=30`),
        api.get<ServerStats[]>(`/api/stats/worlds/${selectedWorld}/active-history?days=30`),
      ]);
      
      setExpHistory(expResponse.data);
      setActiveHistory(activeResponse.data);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar estatísticas do mundo');
    } finally {
      setLoading(false);
    }
  };

  const handleWorldChange = (event: SelectChangeEvent) => {
    setSelectedWorld(event.target.value);
  };

  if (loading && !selectedWorld) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Estatísticas do Servidor/Mundo</Typography>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Mundo</InputLabel>
          <Select
            value={selectedWorld}
            onChange={handleWorldChange}
            label="Mundo"
          >
            {worlds.map((world) => (
              <MenuItem key={world} value={world}>
                {world}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Histórico de EXP Total - {selectedWorld}
            </Typography>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : expHistory.length > 0 ? (
              <Line
                data={{
                  labels: expHistory.map((stat) =>
                    new Date(stat.timestamp).toLocaleDateString()
                  ),
                  datasets: [
                    {
                      label: 'EXP Total',
                      data: expHistory.map((stat) => stat.total_experience),
                      borderColor: 'rgb(75, 192, 192)',
                      backgroundColor: 'rgba(75, 192, 192, 0.2)',
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
                    tooltip: {
                      callbacks: {
                        label: function(context) {
                          return `EXP Total: ${context.parsed.y.toLocaleString()}`;
                        },
                      },
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: false,
                      ticks: {
                        callback: function(value) {
                          return Number(value).toLocaleString();
                        },
                      },
                    },
                  },
                }}
              />
            ) : (
              <Typography variant="body2" color="text.secondary" align="center" p={4}>
                Nenhum dado disponível. Execute o cálculo de estatísticas primeiro.
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Histórico de Personagens Ativos - {selectedWorld}
            </Typography>
            {loading ? (
              <Box display="flex" justifyContent="center" p={4}>
                <CircularProgress />
              </Box>
            ) : activeHistory.length > 0 ? (
              <Line
                data={{
                  labels: activeHistory.map((stat) =>
                    new Date(stat.timestamp).toLocaleDateString()
                  ),
                  datasets: [
                    {
                      label: 'Personagens Ativos',
                      data: activeHistory.map((stat) => stat.active_characters),
                      borderColor: 'rgb(255, 99, 132)',
                      backgroundColor: 'rgba(255, 99, 132, 0.2)',
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
                    tooltip: {
                      callbacks: {
                        label: function(context) {
                          return `Ativos: ${context.parsed.y}`;
                        },
                      },
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        stepSize: 1,
                      },
                    },
                  },
                }}
              />
            ) : (
              <Typography variant="body2" color="text.secondary" align="center" p={4}>
                Nenhum dado disponível. Execute o cálculo de estatísticas primeiro.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default WorldStats;

