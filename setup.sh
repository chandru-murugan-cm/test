#!/bin/bash

echo "🚀 Setting up Cybersecurity Application..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if MongoDB is installed
if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB is not installed. Please install MongoDB first."
    echo "   You can install it using: brew install mongodb-community (macOS)"
    echo "   Or download from: https://www.mongodb.com/try/download/community"
fi

# Start MongoDB if not running
echo "📦 Starting MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "   Starting MongoDB daemon..."
    mongod --fork --logpath /tmp/mongod.log
else
    echo "   MongoDB is already running"
fi

# Setup Auth Service
echo "🔐 Setting up Auth Service..."
cd auth-service
if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm install
fi
if [ ! -f ".env" ] && [ -f "env.local" ]; then
    cp env.local .env
    echo "   Created .env file"
fi
cd ..

# Setup Cyber Service
echo "🛡️  Setting up Cyber Service..."
cd cyber-service/service
if [ ! -d "venv" ]; then
    echo "   Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "   Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt
if [ ! -f ".env" ] && [ -f "env.local" ]; then
    cp env.local .env
    echo "   Created .env file"
fi
deactivate
cd ../..

# Setup UI
echo "🎨 Setting up UI..."
cd cybersecurity-ui
if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm install
fi
if [ ! -f ".env.local" ] && [ -f "env.local" ]; then
    cp env.local .env.local
    echo "   Created .env.local file"
fi
cd ..

# Setup Admin UI
echo "🛠️  Setting up Admin UI..."
cd cybersecurity-admin
if [ ! -d "node_modules" ]; then
    echo "   Installing dependencies..."
    npm install
fi
if [ ! -f ".env.local" ] && [ -f "env.local" ]; then
    cp env.local .env.local
    echo "   Created .env.local file"
fi
cd ..

# Setup Documentation (Jekyll)
echo "📚 Setting up Documentation..."
cd cyberwacht-documentation
if ! command -v bundle &> /dev/null; then
    echo "   Bundler not found. Installing bundler..."
    gem install bundler
fi
bundle install
cd ..

echo "✅ Setup complete!"
echo ""
echo "📋 To start the application, run:"
echo "   ./start.sh"
echo ""
echo "🌐 The application will be available at:"
echo "   - UI: http://localhost:5173"
echo "   - Admin UI: http://localhost:5174"
echo "   - Documentation: http://localhost:4000"
echo "   - Auth Service: http://localhost:3030"
echo "   - Cyber Service: http://localhost:8080"