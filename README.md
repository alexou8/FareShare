# FareShare

FareShare is a full-stack ride-sharing web app that connects drivers and riders for posting, browsing, and booking rides. It includes authentication, ride listings, booking flows, user profiles, and a simple review/ratings experience.

## Key Features

- User authentication (sign up / login)
- Create and manage ride listings (driver flow)
- Browse and search rides (rider flow)
- Request/book a ride + basic booking management
- User profiles (account details, ride history)
- Reviews/ratings (post-ride feedback)
- REST API backend with a separate frontend client

## Tech Stack

**Backend**
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy (ORM)
- Pydantic (validation)

**Frontend**
- React + Vite
- TypeScript (if applicable)
- Modern component-based UI

## Quick Start

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/) (the script will automatically create a virtual environment)
- [Node.js 16+](https://nodejs.org/en/download)
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/Flapjacck/FareShare.git
cd FareShare

# One-time setup (installs npm dependencies for root and frontend)
npm install
npm run setup
```

### Running the Application

#### Option 1: Start Both Servers (Recommended)

```bash
npm start
# or
npm run dev
```

**The script will automatically:**

- Create a Python virtual environment (if not present)
- Upgrade pip to the latest version
- Install backend dependencies from requirements.txt
- Start the FastAPI backend on `http://localhost:8000`
- Start the Vite frontend on `http://localhost:5173`

#### Option 2: Start Servers Individually

```bash
# Backend only
npm run dev:backend

# Frontend only  
npm run dev:frontend
```

### Project Structure

- `backend/` - FastAPI backend server
- `frontend/` - React + Vite frontend

For more detailed information:

- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
