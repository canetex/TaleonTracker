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