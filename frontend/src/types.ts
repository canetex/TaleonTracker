export interface CharacterHistory {
  level: number;
  experience: number;
  deaths: number;
  created_at: string;
}

export interface Character {
  id: number;
  name: string;
  level: number;
  vocation: string;
  world: string;
  outfit: string;
  experience: number;
  deaths: number;
  last_updated: string;
  created_at: string;
  updated_at: string;
  history: CharacterHistory[];
} 