#!/bin/bash

echo "🚀 Starting Cybersecurity Application..."

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Stopping all services..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start MongoDB if not running
if ! pgrep -x "mongod" > /dev/null; then
    echo "📦 Starting MongoDB..."
    mongod --fork --logpath /tmp/mongod.log
    sleep 2
fi

# Start Auth Service
echo "🔐 Starting Auth Service on port 3030..."
cd auth-service
npm run dev &
AUTH_PID=$!
cd ..

# Start Cyber Service
echo "🛡️  Starting Cyber Service on port 8080..."
cd cyber-service/service
source venv/bin/activate
python app.py &
CYBER_PID=$!
deactivate
cd ../..

# Start UI
echo "🎨 Starting UI on port 5173..."
cd cybersecurity-ui
npx vite --port 5173 &
UI_PID=$!
cd ..

# Start Admin UI
echo "🛠️  Starting Admin UI on port 5174..."
cd cybersecurity-admin
npx vite --port 5174 &
cd ..

# Start Documentation (Jekyll)
echo "📚 Starting Documentation on port 4000..."
cd cyberwacht-documentation
bundle exec jekyll serve --port 4000 &
cd ..

echo "✅ All services started!"
echo ""
echo "🌐 Application URLs:"
echo "   - UI: http://localhost:5173"
echo "   - Admin UI: http://localhost:5174"
echo "   - Documentation: http://localhost:4000"
echo "   - Auth Service: http://localhost:3030"
echo "   - Cyber Service: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all background processes
wait 