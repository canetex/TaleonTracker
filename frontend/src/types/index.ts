export interface Character {
  id: number;
  name: string;
  level: number;
  vocation: string;
  world: string;
  created_at: string;
  updated_at: string;
  history: CharacterHistory[];
}

export interface CharacterHistory {
  id: number;
  character_id: number;
  level: number;
  experience: number;
  deaths: number;
  timestamp: string;
}

export interface CharacterCreate {
  name: string;
} 