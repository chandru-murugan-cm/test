<a href="https://gitmoji.dev">
  <img
    src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square"
    alt="Gitmoji"
  />
</a>

# Cybersecurity Application

A comprehensive cybersecurity platform with authentication, scanning services, and a modern web interface.

## 🏗️ Architecture

The application consists of three main components:

- **auth-service** (Node.js/Express) - Authentication and user management service
- **cyber-service** (Python/Flask) - Main cybersecurity scanning and analysis service
- **cybersecurity-ui** (React/Vite) - Modern web interface

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

- **Node.js** (v16 or higher)
- **Python 3** (v3.8 or higher)
- **MongoDB** (v4.4 or higher)
- **Git**

### Installing Prerequisites

#### macOS (using Homebrew)

```bash
# Install Node.js
brew install node

# Install Python 3
brew install python3

# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community
```

#### Ubuntu/Debian

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python 3
sudo apt-get install python3 python3-pip python3-venv

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd cybersecurity
```

### 2. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:

- Check for required dependencies
- Install Node.js dependencies for auth-service and UI
- Create Python virtual environment and install dependencies for cyber-service
- Set up environment files
- Start MongoDB

### 3. Start the Application

```bash
chmod +x start.sh
./start.sh
```

### 4. Access the Application

Once all services are running, you can access:

- **Web Interface**: http://localhost:5173
- **Auth Service API**: http://localhost:3030
- **Cyber Service API**: http://localhost:8080

## 🛠️ Manual Setup

If you prefer to set up each service manually:

### Auth Service Setup

```bash
cd auth-service
npm install
cp env.local .env
npm run dev
```

### Cyber Service Setup

```bash
cd cyber-service/service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.local .env
python app.pynp
```

### UI Setup

```bash
cd cybersecurity-ui
npm install
cp env.local .env.local
npm run dev
```

## 📁 Project Structure

```
cybersecurity/
├── auth-service/           # Authentication service (Node.js/Express)
│   ├── server/
│   │   ├── routes/        # API routes
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   └── config/        # Configuration
│   └── package.json
├── cyber-service/         # Main cybersecurity service (Python/Flask)
│   └── service/
│       ├── apis/         # API endpoints
│       ├── controllers/  # Request handlers
│       ├── entities/     # Data models
│       └── utility/      # Utility functions
├── cybersecurity-ui/     # Frontend application (React/Vite)
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── views/        # Page components
│   │   ├── store/        # Redux store
│   │   └── util/         # Utilities
│   └── package.json
└── README.md
```

## 🔧 Configuration

### Environment Variables

Each service has its own environment configuration:

#### Auth Service (auth-service/.env)

```
MONGODBDSN=mongodb://localhost:27017/auth_db
JWTSECRET=myownsecret
PORT=3030
```

#### Cyber Service (cyber-service/service/.env)

```
DATABASE_CONNECTION_STRING=mongodb://localhost:27017/
DATABASE_NAME=scans_db
EXAMPLES_COLLECTION_NAME=jobs
JWTSECRET=myownsecret
```

#### UI (cybersecurity-ui/.env.local)

```
VITE_API_AUTH_BASE_URL=http://localhost:3030
VITE_API_CYBER_SERVICE_BASE_URL=http://localhost:8080
```

## 🧪 Testing

### Auth Service Tests

```bash
cd auth-service
npm test
```

### Cyber Service Tests

```bash
cd cyber-service/service
source venv/bin/activate
python -m pytest tests/
```

## 🐳 Docker Support

The cyber-service includes Docker support:

```bash
cd cyber-service
docker-compose up
```

## 📊 API Documentation

### Auth Service Endpoints

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/profile` - Get user profile
- `POST /auth/logout` - User logout

### Cyber Service Endpoints

- `GET /scans` - List scans
- `POST /scans` - Create new scan
- `GET /scanners` - List available scanners
- `GET /projects` - List projects
- `POST /projects` - Create new project

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation
- Session management

### Logs

- Auth Service logs: Check terminal output
- Cyber Service logs: Check terminal output
- MongoDB logs: `/tmp/mongod.log`
- UI logs: Check browser console
