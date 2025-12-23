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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
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
import { getOutfitUrl } from '../utils/format';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
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

const CharacterDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [character, setCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);
  const [daysFilter, setDaysFilter] = useState<number>(0);

  useEffect(() => {
    fetchCharacter();
  }, [id, daysFilter]);

  const fetchCharacter = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await getCharacterHistory(parseInt(id), daysFilter);
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
  
  // Filtra histórico por intervalo de dias
  let history = character.history || [];
  if (daysFilter > 0 && history.length > 0) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysFilter);
    history = history.filter((h: CharacterHistory) => 
      new Date(h.timestamp) >= cutoffDate
    );
  }
  
  // Ordena histórico por data (mais antigo primeiro para gráficos)
  history = history
    .slice()
    .sort((a: CharacterHistory, b: CharacterHistory) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

  // Calcula média diária de experiência no intervalo
  let averageDailyExp = 0;
  if (history.length > 1) {
    const firstExp = history[0].experience;
    const lastExp = history[history.length - 1].experience;
    const totalExpGained = lastExp - firstExp;
    const firstDate = new Date(history[0].timestamp);
    const lastDate = new Date(history[history.length - 1].timestamp);
    const daysDiff = Math.max(1, Math.ceil((lastDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24)));
    averageDailyExp = totalExpGained / daysDiff;
  }

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box display="flex" alignItems="center" gap={2}>
                {character.outfit && (
                  <img 
                    src={getOutfitUrl(character.outfit)}
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
                  <Typography variant="subtitle1">Experiência nas últimas 24hs</Typography>
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
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Progresso de Nível e Experiência
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
              <Line
                data={{
                  labels: history.map((h: CharacterHistory) =>
                    new Date(h.timestamp).toLocaleDateString()
                  ),
                  datasets: [
                    {
                      label: 'Nível',
                      data: history.map((h: CharacterHistory) => h.level),
                      borderColor: 'rgb(75, 192, 192)',
                      backgroundColor: 'rgba(75, 192, 192, 0.2)',
                      tension: 0.1,
                      yAxisID: 'y',
                    },
                    {
                      label: 'Experiência',
                      data: history.map((h: CharacterHistory) => h.experience),
                      borderColor: 'rgb(255, 99, 132)',
                      backgroundColor: 'rgba(255, 99, 132, 0.2)',
                      tension: 0.1,
                      yAxisID: 'y1',
                    },
                    ...(averageDailyExp > 0 ? [{
                      label: 'Média Diária de EXP',
                      data: history.map((_, index) => {
                        // Linha que mostra o crescimento esperado baseado na média diária
                        const firstExp = history[0].experience;
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
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default CharacterDetail; 