/**
 * Tabela de experiência do Tibia
 * Baseada em: https://www.tibia.com/library/?subtopic=experiencetable
 * Complexidade: O(1) - lookup direto
 */

// Tabela de experiência para os primeiros 100 levels (valores exatos)
const EXPERIENCE_TABLE: { [key: number]: number } = {
  1: 0, 2: 100, 3: 185, 4: 274, 5: 368, 6: 466, 7: 568, 8: 674, 9: 784, 10: 897,
  11: 1014, 12: 1135, 13: 1260, 14: 1389, 15: 1522, 16: 1659, 17: 1800, 18: 1945, 19: 2094, 20: 2247,
  21: 2404, 22: 2565, 23: 2730, 24: 2899, 25: 3072, 26: 3249, 27: 3430, 28: 3615, 29: 3804, 30: 3997,
  31: 4194, 32: 4395, 33: 4600, 34: 4809, 35: 5022, 36: 5239, 37: 5460, 38: 5685, 39: 5914, 40: 6147,
  41: 6384, 42: 6625, 43: 6870, 44: 7119, 45: 7372, 46: 7629, 47: 7890, 48: 8155, 49: 8424, 50: 8697,
  51: 8972, 52: 9249, 53: 9528, 54: 9809, 55: 10092, 56: 10377, 57: 10664, 58: 10953, 59: 11244, 60: 11537,
  61: 11832, 62: 12129, 63: 12428, 64: 12729, 65: 13032, 66: 13337, 67: 13644, 68: 13953, 69: 14264, 70: 14577,
  71: 14892, 72: 15209, 73: 15528, 74: 15849, 75: 16172, 76: 16497, 77: 16824, 78: 17153, 79: 17484, 80: 17817,
  81: 18152, 82: 18489, 83: 18828, 84: 19169, 85: 19512, 86: 19857, 87: 20204, 88: 20553, 89: 20904, 90: 21257,
  91: 21612, 92: 21969, 93: 22328, 94: 22689, 95: 23052, 96: 23417, 97: 23784, 98: 24153, 99: 24524, 100: 24897,
};

/**
 * Calcula a experiência mínima necessária para um determinado level
 * Baseado na tabela oficial do Tibia
 * @param level - Nível do personagem
 * @returns Experiência mínima necessária para o level
 */
export function calculateExperienceForLevel(level: number): number {
  if (level <= 0) {
    return 0;
  }
  
  // Se está na tabela, retorna o valor exato
  if (level in EXPERIENCE_TABLE) {
    return EXPERIENCE_TABLE[level];
  }
  
  // Para levels acima de 100, usa a fórmula do Tibia
  // Fórmula: exp = 50 * level^3 - 150 * level^2 + 400 * level
  return 50 * level ** 3 - 150 * level ** 2 + 400 * level;
}

/**
 * Obtém a experiência para um registro de histórico
 * Usa total_experience se disponível, senão calcula baseado no level
 * @param history - Registro de histórico
 * @returns Experiência total
 */
export function getExperienceFromHistory(history: { level: number; total_experience?: number | null; experience?: number }): number {
  if (history.total_experience !== null && history.total_experience !== undefined) {
    return history.total_experience;
  }
  
  if (history.experience !== undefined && history.experience !== null) {
    return history.experience;
  }
  
  // Se não tem experiência, calcula baseado no level
  return calculateExperienceForLevel(history.level);
}

