#!/bin/bash

# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Build the frontend
npm run build

# Return to the root directory
cd ..

echo "Build completed successfully!" 