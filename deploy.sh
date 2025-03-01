#!/bin/bash

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI is not installed. Installing..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "Please log in to Vercel:"
    vercel login
fi

# Deploy to Vercel
echo "Deploying to Vercel..."
vercel

# Ask if user wants to deploy to production
read -p "Do you want to deploy to production? (y/n): " PROD
if [[ $PROD == "y" || $PROD == "Y" ]]; then
    echo "Deploying to production..."
    vercel --prod
    
    # Get the production URL
    PROD_URL=$(vercel --prod)
    
    echo "Updating frontend API URL..."
    # Extract just the URL from the output
    PROD_URL=$(echo $PROD_URL | grep -o 'https://[^ ]*')
    
    # Update the frontend API URL
    sed -i '' "s|baseURL: \"http://localhost:5001/api\"|baseURL: \"$PROD_URL/api\"|g" frontend/src/App.tsx
    
    echo "Frontend API URL updated to $PROD_URL/api"
    echo "You may need to rebuild and redeploy your frontend."
fi

echo "Deployment complete!" 