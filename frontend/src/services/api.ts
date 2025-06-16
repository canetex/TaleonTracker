import axios from 'axios';

// Usa a URL base do ambiente ou fallback para localhost
const baseURL = process.env.REACT_APP_API_URL || 'http://192.168.1.178:8000';

console.log('API URL:', baseURL); // Debug

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 10000, // Aumenta o timeout para 10 segundos
  withCredentials: false, // Desabilita o envio de cookies
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // O servidor respondeu com um status de erro
      console.error('Erro na resposta:', error.response.data);
      if (error.response.status === 403) {
        console.error('Erro de CORS ou permissão negada');
      } else if (error.response.status === 500) {
        console.error('Erro interno do servidor:', error.response.data);
      }
    } else if (error.request) {
      // A requisição foi feita mas não houve resposta
      console.error('Erro na requisição:', error.request);
    } else {
      // Algo aconteceu na configuração da requisição
      console.error('Erro:', error.message);
    }
    return Promise.reject(error);
  }
);

export const getCharacters = async () => {
  try {
    const response = await api.get('/api/characters');
    return response.data;
  } catch (error) {
    console.error('Erro na resposta:', error.response?.data);
    throw error;
  }
};

export const addCharacter = async (characterData: any) => {
  try {
    const response = await api.post('/api/characters', characterData);
    return response.data;
  } catch (error) {
    console.error('Erro na resposta:', error.response?.data);
    throw error;
  }
};

export const updateCharacter = async (id: number, characterData: any) => {
  try {
    const response = await api.put(`/api/characters/${id}`, characterData);
    return response.data;
  } catch (error) {
    console.error('Erro na resposta:', error.response?.data);
    throw error;
  }
};

export const deleteCharacter = async (id: number) => {
  try {
    const response = await api.delete(`/api/characters/${id}`);
    return response.data;
  } catch (error) {
    console.error('Erro na resposta:', error.response?.data);
    throw error;
  }
};

export default api; 