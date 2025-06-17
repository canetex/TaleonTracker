export interface Character {
  id: number;
  name: string;
  level: number;
  experience: number;
  daily_experience: number;
  vocation: string;
  world: string;
  last_updated: string;
  history: CharacterHistory[];
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

export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}

export interface ApiError {
  response?: {
    data: any;
    status: number;
    statusText: string;
  };
  message: string;
}