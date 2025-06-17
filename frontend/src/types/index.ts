export interface Character {
  id: number;
  name: string;
  level: number;
  experience: number;
  daily_experience: number;
  vocation: string;
  world: string;
  last_updated: string;
}

export interface CharacterHistory {
  id: number;
  character_id: number;
  level: number;
  experience: number;
  daily_experience: number;
  deaths: number;
  timestamp: string;
}

export interface CharacterCreate {
  name: string;
  world: string;
} 