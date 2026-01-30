#!/bin/bash

echo "🛑 Stopping Cybersecurity Application..."

# Stop all Node.js processes (auth-service, UI, admin UI)
echo "🔐 Stopping Auth Service and UI..."
pkill -f "node.*auth-service" 2>/dev/null
pkill -f "vite" 2>/dev/null
pkill -f "cybersecurity-admin" 2>/dev/null

# Stop Python processes (cyber-service)
echo "🛡️  Stopping Cyber Service..."
pkill -f "python.*app.py" 2>/dev/null

# Stop Jekyll documentation
echo "📚 Stopping Documentation..."
pkill -f "jekyll" 2>/dev/null

# Stop MongoDB
echo "📦 Stopping MongoDB..."
pkill -f "mongod" 2>/dev/null

echo "✅ All services stopped!" 