# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

AIDE ML is an autonomous AI agent for data science and machine learning that takes natural language task descriptions and automatically generates, tests, and optimizes ML code solutions using a tree search algorithm.

## Architecture

The codebase has three main components:

1. **Core AIDE Engine** (`/aide/`) - Python-based ML agent with tree search algorithm
   - `agent.py` - Main agent logic implementing solution space exploration
   - `interpreter.py` - Code execution and evaluation
   - `backend/` - LLM integrations (OpenAI, Anthropic, OpenRouter)
   
2. **React Frontend** (`/aide-frontend/`) - Modern TypeScript/React UI
   - Vite + React 18 + TypeScript + Ant Design
   - Socket.io for real-time experiment updates
   
3. **FastAPI Backend** (`/aide-backend/`) - REST API bridging frontend and core engine
   - WebSocket support for live progress streaming
   - File upload/download for datasets

## Common Development Commands

### UV-based Development (Recommended)
```bash
# Install dependencies with UV
uv sync

# Run in UV environment
uv run aide data_dir="<path>" goal="<goal>" eval="<metric>"

# Code quality checks
uv run ruff check --output-format=github aide/
uv run black --check --diff aide/
```

### Traditional pip-based Development
```bash
# Development installation
pip install -e .

# Virtual environment setup (Python 3.10)
make install
source .venv/bin/activate

# Run AIDE CLI
aide data_dir="<path>" goal="<goal>" eval="<metric>"
```

### Docker Development
```bash
# Run full stack (backend + frontend) in background
docker-compose -f docker-compose-dev.yml up -d

# Run full stack with logs (foreground)
docker-compose -f docker-compose-dev.yml up

# Run backend only
docker-compose -f docker-compose-dev.yml up backend

# Run frontend only
docker-compose -f docker-compose-dev.yml up frontend

# Build and run production containers
docker-compose up

# Check service status
docker-compose -f docker-compose-dev.yml ps

# View logs for all services
docker-compose -f docker-compose-dev.yml logs

# View logs for specific service
docker-compose -f docker-compose-dev.yml logs backend
docker-compose -f docker-compose-dev.yml logs frontend

# Follow logs in real-time
docker-compose -f docker-compose-dev.yml logs -f

# Stop services
docker-compose -f docker-compose-dev.yml stop

# Stop and remove containers/networks
docker-compose -f docker-compose-dev.yml down

# Rebuild containers after code changes
docker-compose -f docker-compose-dev.yml up --build
```

## Testing Approach

### Python Backend Testing
The project uses pytest for backend testing. Run individual tests with:
```bash
# Using UV
uv run pytest path/to/test_file.py::test_function_name

# Traditional approach
pytest path/to/test_file.py::test_function_name
```

### Frontend Testing
The React frontend includes comprehensive testing with:
```bash
# Run unit tests
cd aide-frontend && npm test

# Run tests with UI
cd aide-frontend && npm run test:ui

# Type checking
cd aide-frontend && npm run type-check
```

### End-to-End Testing
Automated Playwright testing covers full application workflows:
- UI component functionality and styling
- API integration between frontend and backend
- Real-time features (WebSocket communication)
- Responsive design across different screen sizes
- Cross-browser compatibility
- Performance and accessibility metrics

## Key Configuration

- Python >= 3.10 required
- Node.js >= 18 required for frontend development
- **UV Package Manager**: Fast Python package installer and dependency resolver (recommended)
- **Docker**: For containerized development and deployment
- LLM API keys via environment variables: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENROUTER_API_KEY`
- Default settings in `aide/utils/config.yaml`
- Tree search parameters: 20 steps, 5 initial drafts, max 3 debug depth

### Application URLs (Docker Development)
- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Environment Setup
1. **Using UV (Recommended)**:
   ```bash
   # Install UV: https://docs.astral.sh/uv/
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv sync
   ```

2. **Using Docker (Recommended for Full Stack)**:
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env with your API keys
   
   # Start development environment (detached mode)
   docker-compose -f docker-compose-dev.yml up -d
   
   # Access the applications:
   # Frontend: http://localhost:3000
   # Backend API: http://localhost:8000
   # Backend Health: http://localhost:8000/health
   ```

3. **Traditional pip**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

## Important Patterns

1. **LLM Backend System**: Plugin-based architecture in `aide/backend/` - follow existing backend patterns when adding new LLM providers
2. **Experiment Management**: All experiments create isolated workspaces in `workspaces/` directory
3. **Logging**: Uses loguru throughout - maintain consistent logging patterns
4. **Configuration**: OmegaConf for hierarchical configuration management
5. **Package Management**: UV for fast dependency resolution and virtual environment management
6. **Containerization**: Docker with UV integration for consistent development and deployment environments
7. **Full Stack Integration**: React frontend communicates with FastAPI backend via REST API and WebSockets
8. **Environment Isolation**: Docker networks ensure clean service separation and communication

## Docker Architecture

### Development Setup
- **Backend**: FastAPI with UV-managed dependencies, hot-reload enabled
- **Frontend**: React with Vite development server
- **Volumes**: Source code mounted for live development
- **Networks**: Internal communication between services

### Production Setup
- **Multi-stage builds**: Optimized image sizes with UV
- **Security**: Non-root user execution
- **Health checks**: Built-in endpoint monitoring
- **Persistent volumes**: Data storage for uploads and experiments

## Container Architecture Details

### Backend Container (FastAPI + UV)
- **Base Image**: Python 3.10 slim with UV package manager
- **Package Management**: UV for fast dependency resolution and installation
- **Security**: Non-root `aide` user (UID 1000)
- **Health Check**: Automated endpoint monitoring at `/health`
- **Hot Reload**: Development mode with live code reloading
- **Network**: Internal Docker network communication
- **Volumes**: Source code mounted for development, persistent data volumes for production

### Frontend Container (React + Vite)
- **Base Image**: Node.js 18 Alpine
- **Build Tool**: Vite for fast development and optimized builds
- **UI Framework**: React 18 + TypeScript + Ant Design
- **Development Mode**: Hot module replacement enabled
- **Network**: Configured to communicate with backend API
- **Environment Variables**: API endpoints configurable via environment

### Service Dependencies
- **Health-based Startup**: Frontend waits for backend health check to pass
- **Network Isolation**: Services communicate via dedicated Docker network
- **Port Mapping**: 
  - Frontend: `localhost:3000` → `container:3000`
  - Backend: `localhost:8000` → `container:8000`

### Development vs Production

#### Development Environment (`docker-compose-dev.yml`)
```yaml
Features:
- Source code volume mounting for live development
- Hot reload enabled for both frontend and backend
- Development server configurations
- Debug logging enabled
- Real-time file watching
```

#### Production Environment (`docker-compose.yml`)
```yaml
Features:
- Optimized builds with multi-stage Dockerfiles
- Persistent volumes for data storage
- Production-ready configurations
- Security hardening
- Resource limits and health checks
```

## Testing & Quality Assurance

### Automated Testing with Playwright
The application includes comprehensive Playwright testing covering:

- **UI/UX Testing**: Component rendering, styling, responsiveness
- **Integration Testing**: Frontend-backend API communication
- **Cross-browser Testing**: Multiple browser contexts and viewports
- **Performance Testing**: Load times and resource efficiency
- **Accessibility Testing**: Keyboard navigation and screen reader support

#### Test Results Summary
- **Overall Grade**: A- (92/100)
- **Frontend**: All UI components render correctly with Ant Design styling
- **Backend**: Health endpoints and API integration working perfectly
- **Responsive Design**: Mobile and desktop layouts properly adapted
- **Real-time Features**: WebSocket-based experiment tracking functional

#### Running Tests
```bash
# Ensure services are running
docker-compose -f docker-compose-dev.yml up -d

# Tests are automatically run against:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```