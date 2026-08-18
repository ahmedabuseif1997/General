/* NeverEnding.Kicks — 2026 Running Collection data
   Concept lineup: 2026 model names/specs are illustrative, not official brand data. */

const SHOES = [
  { n: "01", brand: "Nike",        model: "Pegasus 42",            cat: "Daily Trainer", price: 140, weight: 284, drop: 10, colors: ["#c6ff2e", "#111111", "#e8e8e8"] },
  { n: "02", brand: "Nike",        model: "Vaporfly 4",             cat: "Race Day",      price: 260, weight: 184, drop: 8,  colors: ["#e8321f", "#f5efe2"] },
  { n: "03", brand: "Adidas",      model: "Ultraboost 26",          cat: "Daily Trainer", price: 190, weight: 310, drop: 6,  colors: ["#111111", "#f4f4f4", "#d1281f"] },
  { n: "04", brand: "Adidas",      model: "Adizero Adios Pro 5",    cat: "Race Day",      price: 250, weight: 195, drop: 6,  colors: ["#8f6bff", "#f4c81a"] },
  { n: "05", brand: "New Balance", model: "Fresh Foam X 1090v14",   cat: "Max Cushion",   price: 165, weight: 289, drop: 8,  colors: ["#5c6670", "#8fe3c4"] },
  { n: "06", brand: "New Balance", model: "FuelCell SC Elite v5",   cat: "Race Day",      price: 225, weight: 198, drop: 6,  colors: ["#e0432b", "#2f6fed"] },
  { n: "07", brand: "Asics",       model: "Gel-Nimbus 27",          cat: "Max Cushion",   price: 160, weight: 295, drop: 8,  colors: ["#1c2b4a", "#f28ba8"] },
  { n: "08", brand: "Asics",       model: "Metaspeed Sky Paris+",   cat: "Race Day",      price: 250, weight: 178, drop: 5,  colors: ["#e5177e", "#1f4fd8"] },
  { n: "09", brand: "Hoka",        model: "Clifton 10",             cat: "Daily Trainer", price: 145, weight: 249, drop: 5,  colors: ["#b9c2c9", "#f2a51e"] },
  { n: "10", brand: "Hoka",        model: "Rocket X 3",             cat: "Race Day",      price: 200, weight: 213, drop: 5,  colors: ["#e8622c", "#111111"] },
  { n: "11", brand: "Brooks",      model: "Ghost 17",               cat: "Daily Trainer", price: 140, weight: 269, drop: 12, colors: ["#4a4f57", "#1f6f6a"] },
  { n: "12", brand: "Brooks",      model: "Hyperion Elite 4",       cat: "Race Day",      price: 225, weight: 198, drop: 6,  colors: ["#111827", "#f2542d"] },
  { n: "13", brand: "Saucony",     model: "Endorphin Speed 5",      cat: "Tempo",         price: 170, weight: 233, drop: 8,  colors: ["#e8e14a", "#3a3a3a"] },
  { n: "14", brand: "Saucony",     model: "Triumph 22",             cat: "Max Cushion",   price: 160, weight: 269, drop: 10, colors: ["#c9a688", "#e6a9c0"] },
  { n: "15", brand: "On",          model: "Cloudmonster 3",         cat: "Max Cushion",   price: 180, weight: 290, drop: 6,  colors: ["#e3e6e8", "#e8562c"] },
  { n: "16", brand: "On",          model: "Cloudboom Strike LS",    cat: "Race Day",      price: 290, weight: 210, drop: 8,  colors: ["#9fb8c2", "#c97a3d"] },
  { n: "17", brand: "Puma",        model: "Deviate Nitro 3",        cat: "Tempo",         price: 160, weight: 240, drop: 8,  colors: ["#2ee6a8", "#111111"] },
  { n: "18", brand: "Mizuno",      model: "Wave Rider 29",          cat: "Daily Trainer", price: 150, weight: 255, drop: 12, colors: ["#1f4fd8", "#e0342a"] },
  { n: "19", brand: "Under Armour",model: "Velociti Elite 3",       cat: "Race Day",      price: 175, weight: 213, drop: 6,  colors: ["#4fe07a", "#0e0e0e"] },
  { n: "20", brand: "Salomon",     model: "DRX Bliss",              cat: "Road Hybrid",   price: 170, weight: 265, drop: 4,  colors: ["#5c6b4f", "#a7a49c"] },
];

const BRANDS = [...new Set(SHOES.map(s => s.brand))];
