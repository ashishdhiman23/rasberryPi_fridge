#!/bin/bash
set -e

echo "Installing dependencies..."
npm install --no-audit --prefer-offline

echo "Making react-scripts executable..."
chmod +x ./node_modules/.bin/react-scripts

echo "Building React application..."
CI=false NODE_ENV=production ./node_modules/.bin/react-scripts build

echo "Build completed successfully!" 