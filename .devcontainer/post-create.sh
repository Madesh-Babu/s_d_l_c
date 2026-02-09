#!/bin/bash

echo "🚀 Setting up FastAPI development environment..."

# Set up environment variables
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please update the values as needed."
else
    echo "✅ .env file already exists."
fi

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✅ Pre-commit hooks installed."
else
    echo "⚠️  Pre-commit not found. Install it with: pip install pre-commit"
fi

# Set up Python virtual environment (if needed)
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv .venv
    echo "✅ Virtual environment created."
else
    echo "✅ Virtual environment already exists."
fi

# Activate virtual environment and install dependencies
echo "📦 Installing/updating dependencies..."
source .venv/bin/activate
pip install -r requirements/requirements.txt
pip install -r dev_requirements.txt

# Initialize database (if using SQLite for development)
if [ ! -f "test.db" ]; then
    echo "🗄️  Initializing database..."
    # Run database migrations
    alembic upgrade head
    echo "✅ Database initialized."
else
    echo "✅ Database already exists."
fi

# Create necessary directories
mkdir -p logs
mkdir -p htmlcov

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update your .env file with proper values"
echo "2. Run 'python -m src.api.main' to start the FastAPI server"
echo "3. Visit http://localhost:8000/docs for API documentation"
echo "4. Run 'pytest' to execute tests"
echo ""
echo "🔗 Useful commands:"
echo "- Start server: python -m src.api.main"
echo "- Run tests: pytest"
echo "- Run migrations: alembic upgrade head"
echo "- Format code: black ."
echo "- Lint code: flake8 ."
echo ""
