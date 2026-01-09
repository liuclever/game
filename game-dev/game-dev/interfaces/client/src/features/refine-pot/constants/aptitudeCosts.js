export const aptitudeCosts = {
  hp: { coins: 50000, pills: 1 },
  speed: { coins: 50000, pills: 1 },
  physical: { coins: 100000, pills: 2 },
  physicalDefense: { coins: 50000, pills: 1 },
  magic: { coins: 100000, pills: 2 },
  magicDefense: { coins: 50000, pills: 1 },
}

export const getAptitudeCost = (type) => aptitudeCosts[type] || { coins: 0, pills: 0 }
