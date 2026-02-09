# FastAPI Development Container

This directory contains the configuration for the GitHub Codespaces development environment for the FastAPI project.

## Files

- `devcontainer.json` - Main configuration file for the dev container
- `Dockerfile` - Custom Docker image definition
- `post-create.sh` - Setup script that runs after container creation
- `README.md` - This documentation file

## Features

### Included Tools and Extensions
- **Python 3.11** with FastAPI, SQLAlchemy, and all project dependencies
- **PostgreSQL client** and **SQLite3** for database operations
- **VS Code extensions** for Python development:
  - Python language support
  - Black formatter
  - Flake8 linter
  - MyPy type checker
  - Pytest testing framework
  - GitHub Copilot
  - Docker support
  - YAML and JSON support

### Pre-installed Dependencies
- All Python packages from `requirements.txt` 
- Development tools from `dev_requirements.txt` 
- Pre-commit hooks (if configured)
- GitHub CLI for repository operations

## Getting Started

### Using GitHub Codespaces

1. **Open in GitHub Codespaces**: Click the "Code" button on GitHub and select "Open with Codespaces"
2. **Wait for setup**: The container will automatically build and configure
3. **Environment setup**: The post-create script will run automatically to set up your environment
4. **Start developing**: Your FastAPI application is ready to run!

### Using Locally with VS Code

1. **Prerequisites**: Install Docker and the "Dev Containers" extension in VS Code
2. **Open project**: Open this project in VS Code
3. **Reopen in container**: Use Command Palette (`Ctrl+Shift+P`) and select "Dev Containers: Reopen in Container"
4. **Wait for setup**: The container will build and configure automatically

### Using with Docker Compose (Local Development)

For local development with a full PostgreSQL database:

```bash
# Start the services
docker-compose up -d

# Access the application
# FastAPI app: http://localhost:8000
# PostgreSQL: localhost:5432
```

## Environment Configuration

The dev container automatically:
- Copies `env.example` to `.env` if it doesn't exist
- Sets up the virtual environment
- Installs all dependencies
- Initializes the database (if using SQLite)
- Installs pre-commit hooks

### Important Environment Variables

Make sure to update your `.env` file with appropriate values:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/todo_app
SECRET_KEY=your-secure-secret-key-here
ALLOWED_ORIGINS=["http://localhost:8000", "http://127.0.0.1:8000"]
```

## Development Workflow

### Starting the Application

```bash
# Activate virtual environment (if needed)
source .venv/bin/activate

# Start the FastAPI server
python -m src.api.main

# Access the API documentation
# Open http://localhost:8000/docs in your browser
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/api/test_auth_router.py
```

### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

## Port Forwarding

The dev container automatically forwards these ports:
- **8000**: FastAPI application
- **5432**: PostgreSQL database (if using docker-compose)

## Troubleshooting

### Common Issues

1. **Environment file not created**: Check if `env.example` exists and run the post-create script manually
2. **Dependencies not installed**: Run `pip install -r requirements/requirements.txt` 
3. **Database connection issues**: Update `DATABASE_URL` in your `.env` file
4. **Port conflicts**: Check if ports 8000 and 5432 are available

### Manual Setup

If automatic setup fails, you can run the post-create script manually:

```bash
bash .devcontainer/post-create.sh
```

### Rebuilding the Container

If you need to rebuild the dev container:

```bash
# In VS Code
# Command Palette -> Dev Containers: Rebuild Container

# Or with Docker
docker-compose down
docker-compose up --build
```

## Customization

### Adding Extensions

Add VS Code extensions to the `devcontainer.json`:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "your.extension.id"
      ]
    }
  }
}
```

### Adding System Dependencies

Modify the `Dockerfile` to install additional system packages:

```dockerfile
RUN apt-get update && apt-get install -y \
    your-package-name \
    && rm -rf /var/lib/apt/lists/*
```

### Environment Variables

Add custom environment variables in `devcontainer.json`:

```json
{
  "containerEnv": {
    "CUSTOM_VAR": "value"
  }
}
```

## Contributing

When making changes to the dev container configuration:

1. Test locally with VS Code Dev Containers
2. Update this README if adding new features
3. Ensure all dependencies are properly documented
4. Test with both GitHub Codespaces and local Docker

---

For more information about Dev Containers, visit: https://containers.dev/
