export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('pt-BR').format(num);
};

export const formatDate = (date: string): string => {
  return new Date(date).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Normaliza o caminho do outfit para construir a URL correta
 * Remove duplicações e garante formato correto
 */
export const getOutfitUrl = (outfit: string | undefined | null): string => {
  if (!outfit) return '';
  
  const cleanOutfit = outfit.trim();
  
  // Remove duplicações de /outfits/ se houver
  let normalized = cleanOutfit.replace(/\/+outfits\/+/g, '/outfits/');
  
  // Se já começa com /static/outfits/, usa diretamente
  if (normalized.startsWith('/static/outfits/')) {
    return `/api${normalized}`;
  }
  
  // Se começa com static/outfits/ (sem barra inicial), adiciona /api/
  if (normalized.startsWith('static/outfits/')) {
    return `/api/${normalized}`;
  }
  
  // Se começa com /outfits/, adiciona /api/static
  if (normalized.startsWith('/outfits/')) {
    return `/api/static${normalized}`;
  }
  
  // Se é URL completa, usa diretamente
  if (normalized.startsWith('http')) {
    return normalized;
  }
  
  // Caso contrário, assume que é apenas o nome do arquivo
  return `/api/static/outfits/${normalized}`;
}; 