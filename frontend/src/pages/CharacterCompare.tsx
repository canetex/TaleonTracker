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
} from '@mui/material';
import { getCharacters } from '../services/api';
import { Character } from '../types';

const CharacterCompare: React.FC = () => {
  const navigate = useNavigate();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedChars, setSelectedChars] = useState<number[]>([0, 0]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  const char1 = selectedChars[0] > 0 ? characters.find(c => c.id === selectedChars[0]) : null;
  const char2 = selectedChars[1] > 0 ? characters.find(c => c.id === selectedChars[1]) : null;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Comparar Personagens</Typography>
        <Button variant="outlined" onClick={() => navigate('/characters')}>
          Voltar
        </Button>
      </Box>

      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Personagem 1</InputLabel>
            <Select
              value={selectedChars[0]}
              onChange={(e) => handleCharChange(0, e.target.value as number)}
              label="Personagem 1"
            >
              <MenuItem value={0}>Selecione um personagem</MenuItem>
              {characters.map((char) => (
                <MenuItem key={char.id} value={char.id}>
                  {char.name} (Nível {char.level})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Personagem 2</InputLabel>
            <Select
              value={selectedChars[1]}
              onChange={(e) => handleCharChange(1, e.target.value as number)}
              label="Personagem 2"
            >
              <MenuItem value={0}>Selecione um personagem</MenuItem>
              {characters.map((char) => (
                <MenuItem key={char.id} value={char.id}>
                  {char.name} (Nível {char.level})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {char1 && char2 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Atributo</TableCell>
                <TableCell align="right">{char1.name}</TableCell>
                <TableCell align="right">{char2.name}</TableCell>
                <TableCell align="right">Diferença</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell component="th" scope="row">Nível</TableCell>
                <TableCell align="right">{char1.level}</TableCell>
                <TableCell align="right">{char2.level}</TableCell>
                <TableCell align="right">
                  {char1.level > char2.level ? '+' : ''}
                  {char1.level - char2.level}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell component="th" scope="row">Experiência</TableCell>
                <TableCell align="right">{char1.experience.toLocaleString()}</TableCell>
                <TableCell align="right">{char2.experience.toLocaleString()}</TableCell>
                <TableCell align="right">
                  {char1.experience > char2.experience ? '+' : ''}
                  {(char1.experience - char2.experience).toLocaleString()}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell component="th" scope="row">Experiência Diária</TableCell>
                <TableCell align="right">{char1.daily_experience.toLocaleString()}</TableCell>
                <TableCell align="right">{char2.daily_experience.toLocaleString()}</TableCell>
                <TableCell align="right">
                  {char1.daily_experience > char2.daily_experience ? '+' : ''}
                  {(char1.daily_experience - char2.daily_experience).toLocaleString()}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell component="th" scope="row">Vocação</TableCell>
                <TableCell align="right">{char1.vocation}</TableCell>
                <TableCell align="right">{char2.vocation}</TableCell>
                <TableCell align="right">-</TableCell>
              </TableRow>
              <TableRow>
                <TableCell component="th" scope="row">Mundo</TableCell>
                <TableCell align="right">{char1.world}</TableCell>
                <TableCell align="right">{char2.world}</TableCell>
                <TableCell align="right">-</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {(!char1 || !char2) && (
        <Alert severity="info">
          Selecione dois personagens para comparar
        </Alert>
      )}
    </Box>
  );
};

export default CharacterCompare;

