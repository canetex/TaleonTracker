import axios from 'axios';
import type { Character, CharacterCreate, ApiResponse, ApiError } from '../types';

const api = axios.create({
  baseURL: 'http://192.168.1.200:8000',
});

export const getCharacters = async (): Promise<Character[]> => {
  try {
    const response = await api.get<ApiResponse<Character[]>>('/api/characters');
    return response.data.data;
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao buscar personagens:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const addCharacter = async (character: CharacterCreate): Promise<Character> => {
  try {
    const response = await api.post<ApiResponse<Character>>('/api/characters', character);
    return response.data.data;
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao adicionar personagem:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const updateCharacter = async (id: number, character: Partial<Character>): Promise<Character> => {
  try {
    const response = await api.put<ApiResponse<Character>>(`/api/characters/${id}`, character);
    return response.data.data;
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao atualizar personagem:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const deleteCharacter = async (id: number): Promise<void> => {
  try {
    await api.delete(`/api/characters/${id}`);
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao deletar personagem:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const getCharacterHistory = async (id: number): Promise<Character> => {
  try {
    const response = await api.get<ApiResponse<Character>>(`/api/characters/${id}/history`);
    return response.data.data;
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao atualizar dados do personagem:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export default api; 