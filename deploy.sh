#!/bin/bash

# Heroku deployment script for py-txt-trnsfrm

echo "🚀 Deploying py-txt-trnsfrm to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not a git repository. Please run 'git init' first."
    exit 1
fi

# Check if .python-version exists
if [ ! -f ".python-version" ]; then
    echo "📝 Creating .python-version file for Python 3.13..."
    echo "3.13" > .python-version
fi

# Get app name from user or use default
read -p "Enter Heroku app name (or press Enter for auto-generated): " APP_NAME

# Create Heroku app
if [ -z "$APP_NAME" ]; then
    echo "📦 Creating new Heroku app..."
    heroku create
else
    echo "📦 Creating Heroku app: $APP_NAME"
    heroku create "$APP_NAME"
fi

# Set environment variables
echo "🔧 Setting environment variables..."
heroku config:set FLASK_CONFIG=production
heroku config:set SECRET_KEY="$(openssl rand -base64 32)"

# Add Python buildpack (should be automatic, but let's be explicit)
heroku buildpacks:set heroku/python

# Deploy
echo "🚢 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku - $(date)"
git push heroku main

# Open the app
echo "✅ Deployment complete!"
echo "🌐 Opening your app..."
heroku open

echo "📊 View logs with: heroku logs --tail"
