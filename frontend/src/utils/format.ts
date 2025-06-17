export const formatNumber = (num: number | undefined | null): string => {
  if (num === undefined || num === null) {
    return '0';
  }
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}; 