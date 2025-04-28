import React from 'react';

/**
 * SensorCard component to display sensor readings
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Title of the sensor
 * @param {number} props.value - Current sensor value
 * @param {string} props.unit - Unit of measurement
 * @param {string} props.icon - Emoji or icon for the sensor
 * @param {string} props.status - Status based on value (normal, warning, danger)
 */
const SensorCard = ({ title, value, unit, icon, status = 'normal' }) => {
  // Define status colors based on status prop
  const statusColors = {
    normal: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    danger: 'bg-red-50 border-red-200 text-red-800'
  };

  // Get the appropriate color set based on status
  const colorClass = statusColors[status] || statusColors.normal;

  return (
    <div className={`rounded-lg p-4 border ${colorClass} shadow-sm`}>
      <div className="flex items-center justify-between">
        <div className="text-2xl">{icon}</div>
        <div className="text-xs font-semibold uppercase tracking-wider">{title}</div>
      </div>
      <div className="mt-3 flex items-end justify-between">
        <div className="text-3xl font-bold">{value}</div>
        <div className="text-sm">{unit}</div>
      </div>
    </div>
  );
};

export default SensorCard; 