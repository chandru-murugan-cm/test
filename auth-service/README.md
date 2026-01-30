# Auth-Service

Authentication - Passport Middleware - JWT authentication

### Option 1 : Using Docker Compose - Build and Run Locally (non-dev mode)

Note: Make sure docker is installed in the local machine.

usefull for developer who just want to use the a2-service, but not acttively devloping anything in a2-service.

In the root folder (./a2-service), Run below commands.

```
docker compose build
docker compose up
```

### Option 2 : Build and Run Locally (dev-mode)

for running locally and doing active development in a2-service,

#### DB:

Install mongo DB in docker,
configure the DB connrction in .env file

#### Setup

use node verison: 14
Update .env.dev file in root folder of a2-service with relevant settings

In the root folder (./auth-service), Run below commands.

```
npm install
npm run start:dev
```
