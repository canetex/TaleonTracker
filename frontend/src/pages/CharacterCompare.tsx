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
  Chip,
  Tooltip,
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
  const [maxChars, setMaxChars] = useState(5);
  const [urlLoaded, setUrlLoaded] = useState(false);

  useEffect(() => {
    fetchCharacters();
  }, []);

  useEffect(() => {
    // Carrega personagens da URL se existirem (apenas uma vez após carregar a lista de personagens)
    if (characters.length > 0 && !urlLoaded) {
      const charIds = searchParams.get('chars');
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

  const handleCharChange = (index: number, charId: number) => {
    const newSelected = [...selectedChars];
    newSelected[index] = charId;
    setSelectedChars(newSelected);
    // Atualiza URL com os personagens selecionados
    const validIds = newSelected.filter(id => id > 0);
    if (validIds.length >= 2) {
      setSearchParams({ chars: validIds.join(',') });
    } else {
      setSearchParams({});
    }
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
      if (validIds.length >= 2) {
        setSearchParams({ chars: validIds.join(',') });
      } else {
        setSearchParams({});
      }
    }
  };

  const handleShareLink = () => {
    const validIds = selectedChars.filter(id => id > 0);
    if (validIds.length >= 2) {
      const shareUrl = `${window.location.origin}/characters/compare?chars=${validIds.join(',')}`;
      navigator.clipboard.writeText(shareUrl).then(() => {
        alert('Link copiado para a área de transferência!');
      }).catch(() => {
        // Fallback para navegadores que não suportam clipboard API
        const textArea = document.createElement('textarea');
        textArea.value = shareUrl;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Link copiado para a área de transferência!');
      });
    }
  };

  const getTaleonUrl = (world: string, characterName: string): string => {
    return `https://${world.toLowerCase()}.taleon.online/characterprofile.php?name=${encodeURIComponent(characterName)}`;
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
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Atributo</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          <Link 
                            to={`/characters/${char.id}`}
                            style={{ color: 'inherit', textDecoration: 'none', fontWeight: 'bold' }}
                          >
                            {char.name}
                          </Link>
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell component="th" scope="row">Nível</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                            {char.level}
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
                    <TableRow>
                      <TableCell component="th" scope="row">Experiência</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                            {char.experience.toLocaleString()}
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
                    <TableRow>
                      <TableCell component="th" scope="row">Experiência nas últimas 24hs</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                            {char.daily_experience.toLocaleString()}
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
                    <TableRow>
                      <TableCell component="th" scope="row">Vocação</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                            {char.vocation}
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
                    <TableRow>
                      <TableCell component="th" scope="row">Mundo</TableCell>
                      {selectedCharacters.map((char) => (
                        <TableCell key={char.id} align="right">
                          <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                            {char.world}
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
                        labels: (() => {
                          // Pega todas as datas únicas dos históricos dos personagens selecionados
                          const allDates = new Set<string>();
                          selectedCharacters
                            .filter(char => char.history && char.history.length > 0)
                            .forEach(char => {
                              char.history.forEach((h: CharacterHistory) => {
                                allDates.add(new Date(h.timestamp).toLocaleDateString());
                              });
                            });
                          return Array.from(allDates).sort((a, b) => 
                            new Date(a).getTime() - new Date(b).getTime()
                          ).slice(-30);
                        })(),
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
                              .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
                              .slice(-30);
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
                        labels: (() => {
                          // Pega todas as datas únicas dos históricos dos personagens selecionados
                          const allDates = new Set<string>();
                          selectedCharacters
                            .filter(char => char.history && char.history.length > 0)
                            .forEach(char => {
                              char.history.forEach((h: CharacterHistory) => {
                                allDates.add(new Date(h.timestamp).toLocaleDateString());
                              });
                            });
                          return Array.from(allDates).sort((a, b) => 
                            new Date(a).getTime() - new Date(b).getTime()
                          ).slice(-30);
                        })(),
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
                              .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
                              .slice(-30);
                            return {
                              label: char.name,
                              data: sortedHistory.map((h: CharacterHistory) => h.daily_experience),
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

