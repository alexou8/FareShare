
# FareShare Backend

Contains the backend for FareShare.

## Getting Started

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)

### Setting up the Backend

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate
```

### Running the Backend Server

```bash
# Make sure your virtual environment is activated
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Start the server in development mode (auto-reload on code changes)
uvicorn app:app --reload

# Or start in production mode
uvicorn app:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000` by default. You can access:

- API root: `http://localhost:8000/`
- Health check: `http://localhost:8000/health`
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

### Deactivating the Environment

When you're done working on the project:

```bash
# Deactivate the virtual environment
deactivate
```
