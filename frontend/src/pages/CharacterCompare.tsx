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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
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

const CharacterCompare: React.FC = () => {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedChars, setSelectedChars] = useState<number[]>([0, 0]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [maxChars, setMaxChars] = useState(5);

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

  const handleCharChange = (index: number, charId: number) => {
    const newSelected = [...selectedChars];
    newSelected[index] = charId;
    setSelectedChars(newSelected);
  };

  const handleAddChar = () => {
    if (selectedChars.length < maxChars) {
      setSelectedChars([...selectedChars, 0]);
    }
  };

  const handleRemoveChar = (index: number) => {
    if (selectedChars.length > 2) {
      const newSelected = selectedChars.filter((_, i) => i !== index);
      setSelectedChars(newSelected);
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

  const selectedCharacters = selectedChars
    .filter(id => id > 0)
    .map(id => characters.find(c => c.id === id))
    .filter((char): char is Character => char !== undefined);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Comparar Personagens</Typography>
        <Button variant="outlined" onClick={() => navigate('/characters')}>
          Voltar
        </Button>
      </Box>

      <Grid container spacing={3} mb={3}>
        {selectedChars.map((charId, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Box display="flex" gap={1} alignItems="center">
              <FormControl fullWidth>
                <InputLabel>Personagem {index + 1}</InputLabel>
                <Select
                  value={charId}
                  onChange={(e) => handleCharChange(index, e.target.value as number)}
                  label={`Personagem ${index + 1}`}
                >
                  <MenuItem value={0}>Selecione um personagem</MenuItem>
                  {characters.map((char) => (
                    <MenuItem key={char.id} value={char.id}>
                      {char.name} (Nível {char.level})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              {selectedChars.length > 2 && (
                <IconButton onClick={() => handleRemoveChar(index)} color="error">
                  <DeleteIcon />
                </IconButton>
              )}
            </Box>
          </Grid>
        ))}
        {selectedChars.length < maxChars && (
          <Grid item xs={12}>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={handleAddChar}
            >
              Adicionar Personagem
            </Button>
          </Grid>
        )}
      </Grid>

      {selectedCharacters.length >= 2 && (
        <>
          <Grid container spacing={3} mb={3}>
            <Grid item xs={12}>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Atributo</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          {char.name}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell component="th" scope="row">Nível</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">{char.level}</TableCell>
                      ))}
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">Experiência</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          {char.experience.toLocaleString()}
                        </TableCell>
                      ))}
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">Experiência Diária</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          {char.daily_experience.toLocaleString()}
                        </TableCell>
                      ))}
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">Vocação</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">{char.vocation}</TableCell>
                      ))}
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">Mundo</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">{char.world}</TableCell>
                      ))}
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>

            {/* Gráficos Comparativos */}
            {selectedCharacters.some(char => char.history && char.history.length > 0) && (
              <>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Comparação de Nível
                    </Typography>
                    <Line
                      data={{
                        labels: Array.from({ length: 30 }, (_, i) => {
                          const date = new Date();
                          date.setDate(date.getDate() - (29 - i));
                          return date.toLocaleDateString();
                        }),
                        datasets: selectedCharacters
                          .filter(char => char.history && char.history.length > 0)
                          .map((char, index) => {
                            const colors = [
                              'rgb(75, 192, 192)',
                              'rgb(255, 99, 132)',
                              'rgb(255, 205, 86)',
                              'rgb(54, 162, 235)',
                              'rgb(153, 102, 255)',
                            ];
                            const sortedHistory = [...(char.history || [])]
                              .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
                            return {
                              label: char.name,
                              data: sortedHistory.map((h: CharacterHistory) => h.level),
                              borderColor: colors[index % colors.length],
                              backgroundColor: colors[index % colors.length].replace('rgb', 'rgba').replace(')', ', 0.2)'),
                              tension: 0.1,
                            };
                          }),
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
                      Comparação de Experiência
                    </Typography>
                    <Line
                      data={{
                        labels: Array.from({ length: 30 }, (_, i) => {
                          const date = new Date();
                          date.setDate(date.getDate() - (29 - i));
                          return date.toLocaleDateString();
                        }),
                        datasets: selectedCharacters
                          .filter(char => char.history && char.history.length > 0)
                          .map((char, index) => {
                            const colors = [
                              'rgb(75, 192, 192)',
                              'rgb(255, 99, 132)',
                              'rgb(255, 205, 86)',
                              'rgb(54, 162, 235)',
                              'rgb(153, 102, 255)',
                            ];
                            const sortedHistory = [...(char.history || [])]
                              .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
                            return {
                              label: char.name,
                              data: sortedHistory.map((h: CharacterHistory) => h.experience),
                              borderColor: colors[index % colors.length],
                              backgroundColor: colors[index % colors.length].replace('rgb', 'rgba').replace(')', ', 0.2)'),
                              tension: 0.1,
                            };
                          }),
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
              </>
            )}
          </Grid>
        </>
      )}

      {selectedCharacters.length < 2 && (
        <Alert severity="info">
          Selecione pelo menos dois personagens para comparar
        </Alert>
      )}
    </Box>
  );
};

export default CharacterCompare;

