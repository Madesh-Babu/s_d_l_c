# Troubleshooting Guide

## Environment Setup Issues

### Python Version Problems
**Problem**: Wrong Python version or command not found
```bash
python --version  # Check current version
which python      # Check which Python is being used
```

**Solutions**:
```bash
# Install Python 3.12 (Ubuntu/Debian)
sudo apt update
sudo apt install python3.12 python3.12-venv

# Install Python 3.12 (macOS with Homebrew)
brew install python@3.12

# Use specific Python version
python3.12 -m venv venv
```

### Virtual Environment Issues
**Problem**: Virtual environment not activating or packages not found

**Solutions**:
```bash
# Make sure you're in the right directory
pwd

# Recreate virtual environment
rm -rf venv
python -m venv venv

# Activate properly
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Verify activation
which python
which pip
```

### Dependency Installation Problems
**Problem**: `pip install` fails or packages not found

**Solutions**:
```bash
# Update pip first
pip install --upgrade pip

# Install with verbose output to see errors
pip install -r requirements.txt -v

# Clear pip cache
pip cache purge

# Install individual packages to isolate issue
pip install fastapi
pip install sqlalchemy
```

## Database Issues

### Connection Problems
**Problem**: Can't connect to PostgreSQL database

**Check Connection**:
```bash
# Test PostgreSQL is running
pg_isready -h localhost -p 5432

# Try connecting manually
psql -U postgres -h localhost
```

**Solutions**:
```bash
# Start PostgreSQL service (Ubuntu/Debian)
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql

# Reset PostgreSQL password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'newpassword';"
```

### Database Configuration
**Problem**: Wrong database URL or credentials

**Check `.env` file**:
```bash
# Verify .env file exists and has correct format
cat .env

# Example correct format
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

**Test Database Connection**:
```python
# Quick test script
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
connection = engine.connect()
print("Database connection successful!")
connection.close()
```

## Git Issues

### Authentication Problems
**Problem**: Git push/pull fails with authentication error

**Solutions**:
```bash
# Check current remote URL
git remote -v

# Update to use HTTPS with token
git remote set-url origin https://username:token@github.com/user/repo.git

# Or use SSH (after setting up SSH keys)
git remote set-url origin git@github.com:user/repo.git

# Cache credentials
git config --global credential.helper cache
```

### Branch Problems
**Problem**: Branch conflicts or merge issues

**Solutions**:
```bash
# See current branch status
git status
git log --oneline -5

# Abort current merge
git merge --abort

# Reset to clean state
git reset --hard HEAD

# Update from remote
git fetch origin
git reset --hard origin/develop
```

### Commit Issues
**Problem**: Can't commit or wrong commit message format

**Solutions**:
```bash
# Check what's staged
git diff --staged

# Fix commit message
git commit --amend -m "feat(auth): correct commit message"

# Undo last commit (keep changes)
git reset --soft HEAD~1
```

## Development Server Issues

### FastAPI Server Won't Start
**Problem**: Server fails to start or crashes immediately

**Check for Common Issues**:
```bash
# Verify main.py exists and is correct
ls src/main.py

# Check for syntax errors
python -m py_compile src/main.py

# Try starting with debug output
uvicorn src.main:app --reload --log-level debug
```

**Port Already in Use**:
```bash
# Find process using port 8000
lsof -i :8000
# OR
netstat -tulpn | grep 8000

# Kill process
kill -9 <process_id>

# Or use different port
uvicorn src.main:app --reload --port 8001
```

### Import Errors
**Problem**: Module not found or import errors

**Solutions**:
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Add current directory to path (temporary fix)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Proper solution: Use relative imports in code
# from .models import User  (instead of from models import User)
```

## Code Quality Issues

### Black Formatting Problems
**Problem**: Black formatter fails or conflicts with editor

**Solutions**:
```bash
# Check Black version
black --version

# Format specific file
black src/main.py

# Check what would be formatted (dry run)
black --check .

# Configure line length if needed
black --line-length 79 .
```

### Flake8 Linting Errors
**Problem**: Too many linting errors or false positives

**Solutions**:
```bash
# Check specific file
flake8 src/main.py

# Ignore specific error types
flake8 --ignore=E203,W503 .

# Show only errors (not warnings)
flake8 --select=E,F .
```

### Test Failures
**Problem**: Tests failing unexpectedly

**Debug Steps**:
```bash
# Run tests with verbose output
pytest -v

# Run single failing test
pytest tests/test_auth.py::test_user_login -v

# Run with print statements visible
pytest -s

# Run with debugger
pytest --pdb
```

## Common Error Messages

### "ModuleNotFoundError: No module named 'X'"
**Causes & Solutions**:
1. **Virtual environment not activated**
   ```bash
   source venv/bin/activate
   ```

2. **Package not installed**
   ```bash
   pip install package-name
   ```

3. **Wrong Python path**
   ```bash
   which python
   pip list  # Check installed packages
   ```

### "Access denied" or Permission Errors
**Solutions**:
```bash
# Fix file permissions
chmod +x script_name.py

# Use sudo for system-wide installs (not recommended)
# Better: use virtual environment

# Fix directory permissions
chmod -R 755 project_directory
```

### "Port already in use"
**Solutions**:
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn src.main:app --reload --port 8001
```

### "SSL Certificate verification failed"
**Solutions**:
```bash
# Update certificates (macOS)
/Applications/Python\ 3.12/Install\ Certificates.command

# For pip (temporary fix)
pip install --trusted-host pypi.org --trusted-host pypi.python.org package-name
```

## IDE-Specific Issues

### VS Code Problems
**Problem**: Python interpreter not found or wrong version

**Solutions**:
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Python: Select Interpreter"
3. Choose the Python from your virtual environment
4. Path should be: `./venv/bin/python` (or `.\venv\Scripts\python.exe` on Windows)

**Extensions Not Working**:
- Install Python extension by Microsoft
- Install Pylance for better IntelliSense
- Restart VS Code after installing extensions

## Performance Issues

### Slow Development Server
**Problem**: Server responds slowly or hangs

**Solutions**:
```bash
# Enable auto-reload only for development
uvicorn src.main:app --reload

# Disable debug mode in production
# In .env file:
DEBUG=False

# Check for infinite loops in code
# Add logging to identify slow operations
```

### Memory Issues
**Problem**: High memory usage or out of memory errors

**Solutions**:
```bash
# Monitor memory usage
top -p $(pgrep -f uvicorn)

# Restart development server regularly
# Check for memory leaks in code
# Use database connection pooling
```

## Getting Help

### When You're Really Stuck

1. **Check the Error Message Carefully**
   - Copy the exact error message
   - Note the file and line number
   - Look for the root cause (often at the bottom of the stack trace)

2. **Search for Similar Issues**
   - Google the exact error message
   - Check Stack Overflow
   - Look at project issues on GitHub

3. **Ask for Help Effectively**
   ```markdown
   ## Problem Description
   Brief description of what you're trying to do
   
   ## Error Message
   ```
   Exact error message here
   ```
   
   ## What I've Tried
   - Tried solution A
   - Tried solution B
   
   ## Environment
   - OS: macOS/Windows/Linux
   - Python version: 3.12
   - FastAPI version: 0.104
   ```

4. **Create Minimal Reproduction**
   - Isolate the problem to smallest possible code
   - Remove unrelated code
   - Share only what's necessary

### Emergency Contacts
- Team chat for immediate help
- GitHub issues for bugs
- Documentation for reference
- Stack Overflow for general programming questions

---

**💡 Remember**: Most problems have been solved before. Search first, then ask for help with specific details!