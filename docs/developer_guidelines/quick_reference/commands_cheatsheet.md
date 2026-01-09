# Commands Cheatsheet

## Git Commands

### Daily Git Workflow
```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/feature-name

# Make changes and commit
git add .
git commit -m "feat(scope): description"

# Push and create PR
git push -u origin feature/feature-name
```

### Common Git Operations
```bash
# Check status
git status

# View changes
git diff
git diff --staged

# Update branch from develop
git checkout develop
git pull origin develop
git checkout feature/your-branch
git merge develop

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard changes
git checkout -- filename
git reset --hard HEAD
```

### Branch Management
```bash
# List branches
git branch -a

# Delete merged branch
git branch -d feature/branch-name

# Delete remote branch
git push origin --delete feature/branch-name

# Rename current branch
git branch -m new-branch-name
```

## Python Development

### Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate

# Install dependencies
pip install -r requirements.txt

# Update requirements
pip freeze > requirements.txt
```

### Code Quality Tools
```bash
# Format code with Black
black .
black filename.py

# Check code style
flake8 .
flake8 filename.py

# Run tests
pytest
pytest tests/test_file.py
pytest -v  # verbose output
pytest --cov=src  # with coverage
```

## FastAPI Development

### Run Development Server
```bash
# Start server with auto-reload
uvicorn src.main:app --reload

# Start on different port
uvicorn src.main:app --reload --port 8001

# Start with specific host
uvicorn src.main:app --reload --host 0.0.0.0
```

### API Testing
```bash
# Access interactive docs
# http://localhost:8000/docs

# Access ReDoc
# http://localhost:8000/redoc

# Test endpoint with curl
curl -X POST "http://localhost:8000/api/v1/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "SecurePass123"}'
```

## Database Operations

### PostgreSQL Commands
```bash
# Connect to database
psql -U username -d database_name

# Create database
createdb todoapp

# Drop database
dropdb todoapp

# Run SQL file
psql -U username -d database_name -f script.sql
```

### Common SQL Queries
```sql
-- Check if tables exist
\dt

-- Describe table structure
\d table_name

-- Show all users
SELECT * FROM users;

-- Count records
SELECT COUNT(*) FROM users;
```

## Testing

### pytest Commands
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_user_registration

# Run with coverage
pytest --cov=src --cov-report=html

# Run failed tests only
pytest --lf

# Run tests in parallel
pytest -n auto
```

### Test Debugging
```bash
# Run with output (print statements)
pytest -s

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific test pattern
pytest -k "test_user"
```

## Environment & Configuration

### Environment Variables
```bash
# Set environment variable (Linux/Mac)
export DATABASE_URL="postgresql://..."

# Set environment variable (Windows)
set DATABASE_URL=postgresql://...

# Load from .env file (with python-dotenv)
# Automatically loaded in FastAPI apps
```

### Common .env Variables
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/todoapp
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
DEBUG=True
```

## Package Management

### pip Commands
```bash
# Install package
pip install package-name

# Install specific version
pip install package-name==1.2.3

# Install from requirements
pip install -r requirements.txt

# List installed packages
pip list

# Show package info
pip show package-name

# Upgrade package
pip install --upgrade package-name
```

## IDE Shortcuts (VS Code)

### General
- `Ctrl+Shift+P` - Command palette
- `Ctrl+P` - Quick open file
- `Ctrl+Shift+F` - Search in files
- `Ctrl+``  - Toggle terminal

### Code Navigation
- `Ctrl+Click` - Go to definition
- `F12` - Go to definition
- `Shift+F12` - Find all references
- `Ctrl+Shift+O` - Go to symbol

### Code Editing
- `Ctrl+D` - Select next occurrence
- `Alt+Up/Down` - Move line up/down
- `Shift+Alt+Up/Down` - Duplicate line
- `Ctrl+/` - Toggle comment

## Useful One-liners

### Generate Secrets
```bash
# Generate JWT secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Generate UUID
python -c "import uuid; print(uuid.uuid4())"
```

### Quick File Operations
```bash
# Create multiple directories
mkdir -p src/{auth,todo,core}

# Find Python files
find . -name "*.py" -type f

# Count lines of code
find . -name "*.py" | xargs wc -l
```

### Database Quick Setup
```bash
# Create user and database (PostgreSQL)
sudo -u postgres psql -c "CREATE USER todouser WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE todoapp OWNER todouser;"
```

## Emergency Commands

### When Things Go Wrong
```bash
# Reset to last commit
git reset --hard HEAD

# Clean untracked files
git clean -fd

# Force pull (destructive)
git fetch origin
git reset --hard origin/main

# Restart development server
pkill -f uvicorn
uvicorn src.main:app --reload
```

### Recovery Commands
```bash
# Recover deleted file
git checkout HEAD -- filename

# See what changed
git log --oneline -10
git show commit-hash

# Undo merge
git reset --merge
```

---

**💡 Pro Tip**: Bookmark this page and keep it handy during development!