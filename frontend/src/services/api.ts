import axios, { AxiosError, AxiosResponse } from 'axios';

// Interface para o tipo de personagem
interface Character {
  id: number;
  name: string;
  race: string;
  class: string;
  level: number;
  // Adicione outros campos conforme necessário
}

// Interface para resposta da API
interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

// Usa a URL base do ambiente
const baseURL = process.env.REACT_APP_API_URL || 'http://192.168.1.200:8000';

console.log('API URL:', baseURL); // Debug

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 30000, // Aumenta o timeout para 30 segundos
  withCredentials: false,
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
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

export const getCharacters = async (): Promise<Character[]> => {
  try {
    const response: AxiosResponse<ApiResponse<Character[]>> = await api.get('/api/characters');
    return response.data.data;
  } catch (error: unknown) {
    if (error instanceof AxiosError) {
      console.error('Erro ao buscar personagens:', error.response?.data);
    }
    throw error;
  }
};

export const addCharacter = async (characterData: Omit<Character, 'id'>): Promise<Character> => {
  try {
    const response: AxiosResponse<ApiResponse<Character>> = await api.post('/api/characters', characterData);
    return response.data.data;
  } catch (error: unknown) {
    if (error instanceof AxiosError) {
      console.error('Erro ao adicionar personagem:', error.response?.data);
    }
    throw error;
  }
};

export const updateCharacter = async (id: number, characterData: Partial<Character>): Promise<Character> => {
  try {
    const response: AxiosResponse<ApiResponse<Character>> = await api.put(`/api/characters/${id}`, characterData);
    return response.data.data;
  } catch (error: unknown) {
    if (error instanceof AxiosError) {
      console.error('Erro ao atualizar personagem:', error.response?.data);
    }
    throw error;
  }
};

export const deleteCharacter = async (id: number): Promise<void> => {
  try {
    await api.delete(`/api/characters/${id}`);
  } catch (error: unknown) {
    if (error instanceof AxiosError) {
      console.error('Erro ao deletar personagem:', error.response?.data);
    }
    throw error;
  }
};

export const updateCharacterData = async (id: number): Promise<Character> => {
  try {
    const response: AxiosResponse<ApiResponse<Character>> = await api.post(`/api/characters/${id}/update`);
    return response.data.data;
  } catch (error: unknown) {
    if (error instanceof AxiosError) {
      console.error('Erro ao atualizar dados do personagem:', error.response?.data);
    }
    throw error;
  }
};

export default api; 