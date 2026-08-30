export const CURRENT_YEAR = new Date().getFullYear();
export const START_YEAR = 1776;

export function normalizeDecade(value) {
  const safe = Math.min(CURRENT_YEAR, Math.max(START_YEAR, Number(value)));
  return Math.floor(safe / 10) * 10;
}

export function decades() {
  const values = [];
  for (let year = 1780; year <= CURRENT_YEAR; year += 10) values.push(year);
  return values;
}
