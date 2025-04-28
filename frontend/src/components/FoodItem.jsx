import React from 'react';

/**
 * Food emoji mapping for common food items
 */
const FOOD_EMOJI_MAP = {
  apple: '🍎',
  banana: '🍌',
  orange: '🍊',
  lemon: '🍋',
  mango: '🥭',
  milk: '🥛',
  cheese: '🧀',
  yogurt: '🧁',
  egg: '🥚',
  bread: '🍞',
  chicken: '🍗',
  meat: '🥩',
  fish: '🐟',
  carrot: '🥕',
  tomato: '🍅',
  potato: '🥔',
  onion: '🧅',
  pepper: '🌶️',
  broccoli: '🥦',
  lettuce: '🥬',
  default: '🍽️'
};

/**
 * FoodItem component to display individual food items in the fridge
 * 
 * @param {Object} props - Component props
 * @param {string} props.name - The name of the food item
 */
const FoodItem = ({ name }) => {
  // Get the appropriate emoji for the food item, or use default
  const foodName = name.toLowerCase().trim();
  const emoji = FOOD_EMOJI_MAP[foodName] || FOOD_EMOJI_MAP.default;

  return (
    <div className="bg-white rounded-lg shadow-sm p-3 flex flex-col items-center justify-center text-center">
      <div className="text-3xl mb-2">{emoji}</div>
      <div className="text-sm font-medium capitalize">{name}</div>
    </div>
  );
};

export default FoodItem; 