import React, { useEffect, useState } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
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
  Tooltip,
  TextField,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Share as ShareIcon, OpenInNew as OpenInNewIcon } from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
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
  ChartTooltip,
  Legend
);

const CharacterCompare: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedChars, setSelectedChars] = useState<number[]>([0, 0]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const maxChars = 5;
  const [urlLoaded, setUrlLoaded] = useState(false);
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');

  useEffect(() => {
    fetchCharacters();
  }, []);

  useEffect(() => {
    // Carrega personagens da URL se existirem (apenas uma vez após carregar a lista de personagens)
    if (characters.length > 0 && !urlLoaded) {
      const charIds = searchParams.get('chars');
      const fromParam = searchParams.get('from');
      const toParam = searchParams.get('to');
      
      if (fromParam) setDateFrom(fromParam);
      if (toParam) setDateTo(toParam);
      
      if (charIds) {
        const ids = charIds.split(',').map(id => parseInt(id)).filter(id => !isNaN(id) && id > 0);
        if (ids.length >= 2) {
          // Verifica se os IDs existem na lista de personagens
          const validIds = ids.filter(id => characters.some(c => c.id === id));
          if (validIds.length >= 2) {
            setSelectedChars([...validIds, ...Array(Math.max(0, validIds.length - 2)).fill(0)]);
            setUrlLoaded(true);
          }
        }
      } else {
        setUrlLoaded(true);
      }
    }
  }, [characters, urlLoaded, searchParams]);

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

  const updateUrlParams = (charIds: number[], from?: string, to?: string) => {
    const params: Record<string, string> = {};
    if (charIds.length >= 2) {
      params.chars = charIds.join(',');
    }
    if (from) params.from = from;
    if (to) params.to = to;
    setSearchParams(params);
  };

  const handleCharChange = (index: number, charId: number) => {
    const newSelected = [...selectedChars];
    newSelected[index] = charId;
    setSelectedChars(newSelected);
    // Atualiza URL com os personagens selecionados
    const validIds = newSelected.filter(id => id > 0);
    updateUrlParams(validIds, dateFrom || undefined, dateTo || undefined);
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
      // Atualiza URL com os personagens selecionados
      const validIds = newSelected.filter(id => id > 0);
      updateUrlParams(validIds, dateFrom || undefined, dateTo || undefined);
    }
  };

  const handleDateFromChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setDateFrom(value);
    const validIds = selectedChars.filter(id => id > 0);
    updateUrlParams(validIds, value || undefined, dateTo || undefined);
  };

  const handleDateToChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setDateTo(value);
    const validIds = selectedChars.filter(id => id > 0);
    updateUrlParams(validIds, dateFrom || undefined, value || undefined);
  };

  const handleShareLink = () => {
    const validIds = selectedChars.filter(id => id > 0);
    if (validIds.length >= 2) {
      const params = new URLSearchParams();
      params.set('chars', validIds.join(','));
      if (dateFrom) params.set('from', dateFrom);
      if (dateTo) params.set('to', dateTo);
      const shareUrl = `${window.location.origin}/characters/compare?${params.toString()}`;
      
      // Verifica se navigator.clipboard existe e está disponível
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(shareUrl).then(() => {
          alert('Link copiado para a área de transferência!');
        }).catch(() => {
          // Fallback para navegadores que não suportam clipboard API
          copyToClipboardFallback(shareUrl);
        });
      } else {
        // Fallback para navegadores que não suportam clipboard API
        copyToClipboardFallback(shareUrl);
      }
    }
  };

  const copyToClipboardFallback = (text: string) => {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
      alert('Link copiado para a área de transferência!');
    } catch (err) {
      alert('Erro ao copiar link. Por favor, copie manualmente: ' + text);
    }
    document.body.removeChild(textArea);
  };

  const getTaleonUrl = (world: string, characterName: string): string => {
    return `https://${world.toLowerCase()}.taleon.online/characterprofile.php?name=${encodeURIComponent(characterName)}`;
  };

  const filterHistoryByDate = (history: CharacterHistory[]): CharacterHistory[] => {
    if (!dateFrom && !dateTo) return history;
    
    return history.filter((h: CharacterHistory) => {
      const timestamp = new Date(h.timestamp);
      const fromDate = dateFrom ? new Date(dateFrom) : null;
      const toDate = dateTo ? new Date(dateTo) : null;
      
      if (fromDate && toDate) {
        return timestamp >= fromDate && timestamp <= toDate;
      } else if (fromDate) {
        return timestamp >= fromDate;
      } else if (toDate) {
        return timestamp <= toDate;
      }
      return true;
    });
  };

  // Função helper para obter labels ordenados e únicos
  const getOrderedDateLabels = (): string[] => {
    const allTimestamps = new Set<number>();
    selectedCharacters
      .filter(char => char.history && char.history.length > 0)
      .forEach(char => {
        const filteredHistory = filterHistoryByDate(char.history);
        filteredHistory.forEach((h: CharacterHistory) => {
          const date = new Date(h.timestamp);
          // Usa timestamp do início do dia para agrupar por dia
          const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
          allTimestamps.add(dayStart);
        });
      });
    // Ordena por timestamp e converte para string de data
    return Array.from(allTimestamps)
      .sort((a, b) => a - b)
      .map(ts => new Date(ts).toLocaleDateString());
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
        <Box display="flex" gap={2}>
          {selectedCharacters.length >= 2 && (
            <Button
              variant="contained"
              startIcon={<ShareIcon />}
              onClick={handleShareLink}
            >
              Compartilhar Link
            </Button>
          )}
          <Button variant="outlined" onClick={() => navigate('/characters')}>
            Voltar
          </Button>
        </Box>
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
              <Box display="flex" gap={2} mb={2} alignItems="center" flexWrap="wrap">
                <TextField
                  label="Data Inicial"
                  type="date"
                  value={dateFrom}
                  onChange={handleDateFromChange}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
                <TextField
                  label="Data Final"
                  type="date"
                  value={dateTo}
                  onChange={handleDateToChange}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Box>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Atributo</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                            <Link 
                              to={`/characters/${char.id}`}
                              style={{ color: 'inherit', textDecoration: 'none', fontWeight: 'bold' }}
                            >
                              {char.name}
                            </Link>
                            <Tooltip title="Ver no Taleon">
                              <IconButton
                                size="small"
                                href={getTaleonUrl(char.world, char.name)}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <OpenInNewIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Ver detalhes">
                              <IconButton
                                size="small"
                                component={Link}
                                to={`/characters/${char.id}`}
                              >
                                <OpenInNewIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
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
                        <TableCell key={char.id} align="right">{char.experience.toLocaleString()}</TableCell>
                      ))}
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">Experiência nas últimas 24hs</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">{char.daily_experience.toLocaleString()}</TableCell>
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
                        labels: getOrderedDateLabels(),
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
                            const filteredHistory = filterHistoryByDate(char.history);
                            const sortedHistory = [...filteredHistory]
                              .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
                            
                            // Cria um mapa de data para nível
                            const dateToLevel = new Map<string, number>();
                            sortedHistory.forEach((h: CharacterHistory) => {
                              const date = new Date(h.timestamp);
                              const dayKey = new Date(date.getFullYear(), date.getMonth(), date.getDate()).toLocaleDateString();
                              // Mantém o último valor do dia
                              dateToLevel.set(dayKey, h.level);
                            });
                            
                            const labels = getOrderedDateLabels();
                            
                            return {
                              label: char.name,
                              data: labels.map(label => dateToLevel.get(label) ?? null),
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
                        labels: getOrderedDateLabels(),
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
                            const filteredHistory = filterHistoryByDate(char.history);
                            const sortedHistory = [...filteredHistory]
                              .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
                            
                            // Cria um mapa de data para daily_experience
                            const dateToExp = new Map<string, number>();
                            sortedHistory.forEach((h: CharacterHistory) => {
                              const date = new Date(h.timestamp);
                              const dayKey = new Date(date.getFullYear(), date.getMonth(), date.getDate()).toLocaleDateString();
                              // Mantém o último valor do dia
                              dateToExp.set(dayKey, h.daily_experience);
                            });
                            
                            const labels = getOrderedDateLabels();
                            
                            return {
                              label: char.name,
                              data: labels.map(label => dateToExp.get(label) ?? null),
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

