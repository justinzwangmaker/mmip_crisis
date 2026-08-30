import eras from "../data/eras.json";

export function getEra(year) {
  return eras.find((era) => year >= era.start && year < era.end) || eras[eras.length - 1];
}
