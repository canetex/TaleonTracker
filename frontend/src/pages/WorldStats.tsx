import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
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
  ToggleButton,
  ToggleButtonGroup,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
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
  BarElement,
  Title,
  Tooltip,
  Legend
);

const DAYS_OPTIONS = [
  { value: 7, label: '7 dias' },
  { value: 15, label: '15 dias' },
  { value: 30, label: '30 dias' },
  { value: 45, label: '45 dias' },
  { value: 90, label: '90 dias' },
  { value: 180, label: '180 dias' },
  { value: 0, label: 'Todos' },
];

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
  const [daysFilter, setDaysFilter] = useState<number>(30);
  const [rankingDays, setRankingDays] = useState<number>(30);
  const [ranking, setRanking] = useState<any[]>([]);
  const [rankingType, setRankingType] = useState<'accumulated' | 'average'>('accumulated');

  useEffect(() => {
    fetchWorlds();
  }, []);

  useEffect(() => {
    if (selectedWorld) {
      fetchStats();
    }
  }, [selectedWorld, daysFilter]);

  useEffect(() => {
    fetchRanking();
  }, [rankingDays, selectedWorld, rankingType]);

  const fetchWorlds = async () => {
    try {
      const response = await api.get<string[]>('/stats/worlds');
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
      const daysParam = daysFilter > 0 ? `?days=${daysFilter}` : '?days=0';
      const [expResponse, activeResponse] = await Promise.all([
        api.get<ServerStats[]>(`/stats/worlds/${selectedWorld}/exp-history${daysParam}`),
        api.get<ServerStats[]>(`/stats/worlds/${selectedWorld}/active-history${daysParam}`),
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

  const fetchRanking = async () => {
    if (!selectedWorld) return;
    try {
      const daysParam = rankingDays > 0 ? `&days=${rankingDays}` : '&days=0';
      const worldParam = selectedWorld ? `&world=${selectedWorld}` : '';
      const typeParam = `&type=${rankingType}`;
      const response = await api.get<any[]>(`/ranking/experience?limit=100${daysParam}${worldParam}${typeParam}`);
      // Garante que os dados estão ordenados decrescentemente (backend já envia ordenado, mas garantimos aqui também)
      const sortedData = [...response.data].sort((a, b) => {
        const aValue = rankingType === 'accumulated' 
          ? (a.accumulated_experience ?? a.max_experience ?? 0)
          : (a.average_experience ?? a.max_experience ?? 0);
        const bValue = rankingType === 'accumulated'
          ? (b.accumulated_experience ?? b.max_experience ?? 0)
          : (b.average_experience ?? b.max_experience ?? 0);
        return bValue - aValue; // Ordem decrescente
      });
      setRanking(sortedData);
    } catch (err) {
      console.error('Erro ao carregar ranking:', err);
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4">Estatísticas do Servidor/Mundo</Typography>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Mundo</InputLabel>
          <Select
            value={selectedWorld}
            onChange={handleWorldChange}
            label="Mundo"
          >
            {worlds.map((world) => (
              <MenuItem key={world} value={world}>
                {world.charAt(0).toUpperCase() + world.slice(1)}
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
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Histórico de EXP Total - {selectedWorld ? selectedWorld.charAt(0).toUpperCase() + selectedWorld.slice(1) : ''}
              </Typography>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Período</InputLabel>
                <Select
                  value={daysFilter}
                  onChange={(e) => setDaysFilter(e.target.value as number)}
                  label="Período"
                >
                  {DAYS_OPTIONS.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
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
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Histórico de Personagens Ativos - {selectedWorld ? selectedWorld.charAt(0).toUpperCase() + selectedWorld.slice(1) : ''}
              </Typography>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Período</InputLabel>
                <Select
                  value={daysFilter}
                  onChange={(e) => setDaysFilter(e.target.value as number)}
                  label="Período"
                >
                  {DAYS_OPTIONS.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
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
                Nenhum dado disponível para este período.
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Ranking de Experiência */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2} flexWrap="wrap" gap={2}>
              <Typography variant="h6">
                Ranking de Experiência Histórica
              </Typography>
              <Box display="flex" gap={2} flexWrap="wrap">
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Tipo</InputLabel>
                  <Select
                    value={rankingType}
                    onChange={(e) => setRankingType(e.target.value as 'accumulated' | 'average')}
                    label="Tipo"
                  >
                    <MenuItem value="accumulated">Acumulada</MenuItem>
                    <MenuItem value="average">Média Diária</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Período</InputLabel>
                  <Select
                    value={rankingDays}
                    onChange={(e) => setRankingDays(e.target.value as number)}
                    label="Período"
                  >
                    {DAYS_OPTIONS.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
            </Box>
            {ranking.length > 0 ? (
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TableContainer sx={{ maxHeight: 600, overflow: 'auto' }}>
                    <Table stickyHeader>
                      <TableHead>
                        <TableRow>
                          <TableCell>Rank</TableCell>
                          <TableCell>Nome</TableCell>
                          <TableCell>Nível</TableCell>
                          <TableCell>Mundo</TableCell>
                          <TableCell>Vocação</TableCell>
                          <TableCell align="right">
                            {rankingType === 'accumulated' ? 'EXP Acumulada' : 'EXP Média Diária'}
                          </TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {ranking.map((char) => (
                          <TableRow key={char.character_id}>
                            <TableCell>{char.rank}</TableCell>
                            <TableCell>
                              <Link 
                                to={`/characters/${char.character_id}`}
                                style={{ color: 'inherit', textDecoration: 'none' }}
                              >
                                {char.name}
                              </Link>
                            </TableCell>
                            <TableCell>{(char as any).level || 'N/A'}</TableCell>
                            <TableCell>{(char.world || '').charAt(0).toUpperCase() + (char.world || '').slice(1)}</TableCell>
                            <TableCell>{char.vocation}</TableCell>
                            <TableCell align="right">
                              {(() => {
                                const value = rankingType === 'accumulated' 
                                  ? (char.accumulated_experience ?? char.max_experience ?? 0)
                                  : (char.average_experience ?? char.max_experience ?? 0);
                                // Arredonda para cima e formata sem decimais
                                return Math.ceil(value || 0).toLocaleString('pt-BR', { maximumFractionDigits: 0 });
                              })()}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{ height: '100%', minHeight: '600px' }}>
                    <Bar
                      data={{
                        labels: ranking.slice(0, 20).map((char) => char.name),
                        datasets: [
                          {
                            label: rankingType === 'accumulated' ? 'EXP Acumulada' : 'EXP Média Diária',
                            data: ranking.slice(0, 20).map((char) => {
                              const value = rankingType === 'accumulated' 
                                ? (char.accumulated_experience ?? char.max_experience ?? 0)
                                : (char.average_experience ?? char.max_experience ?? 0);
                              // Arredonda para cima
                              return Math.ceil(value || 0);
                            }),
                            backgroundColor: 'rgba(75, 192, 192, 0.6)',
                            borderColor: 'rgb(75, 192, 192)',
                            borderWidth: 1,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: false,
                          },
                          tooltip: {
                            callbacks: {
                              label: function(context) {
                                return `EXP: ${context.parsed.y.toLocaleString()}`;
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
                  </Box>
                </Grid>
              </Grid>
            ) : (
              <Typography variant="body2" color="text.secondary" align="center" p={4}>
                Nenhum dado disponível para o ranking.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default WorldStats;

