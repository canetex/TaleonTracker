import axios from 'axios';
import type { Character, CharacterCreate, ApiResponse, ApiError } from '../types';

// Usa URL relativa para funcionar através do proxy do Caddy
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
});

export const getCharacters = async (): Promise<Character[]> => {
  try {
    const response = await api.get<Character[]>('/characters');
    return response.data;
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao buscar personagens:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const addCharacter = async (character: CharacterCreate): Promise<Character> => {
  try {
    const response = await api.post<Character>('/characters', character);
    return response.data;
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao adicionar personagem:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const updateCharacter = async (id: number, character: Partial<Character>): Promise<Character> => {
  try {
    const response = await api.post<Character>(`/characters/${id}/update`, character);
    return response.data;
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao atualizar personagem:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const deleteCharacter = async (id: number): Promise<void> => {
  try {
    await api.delete(`/characters/${id}`);
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao deletar personagem:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const getCharacterHistory = async (id: number): Promise<Character> => {
  try {
    const response = await api.get<Character>(`/characters/${id}`);
    return response.data;
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao buscar histórico do personagem:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const addFavorite = async (characterId: number): Promise<void> => {
  try {
    await api.post(`/favorites/${characterId}`);
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao adicionar favorito:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const removeFavorite = async (characterId: number): Promise<void> => {
  try {
    await api.delete(`/favorites/${characterId}`);
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao remover favorito:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export const getFavorites = async (): Promise<number[]> => {
  try {
    const response = await api.get<{character_id: number}[]>('/favorites');
    return response.data.map(f => f.character_id);
  } catch (error) {
    const apiError = error as ApiError;
    console.error('Erro ao buscar favoritos:', apiError.response?.data || apiError.message);
    throw error;
  }
};

export default api; 