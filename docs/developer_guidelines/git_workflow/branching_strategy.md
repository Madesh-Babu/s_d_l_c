# Branching Strategy

## Git Feature Branching Model

### Main Branches
- **`main`**: Production-ready code only (protected)
- **`develop`**: Integration branch for features

### Feature Branches
Create feature branches for new work:

```bash
# Branch naming format
feature/feature-name

# Examples
feature/user-authentication
feature/todo-crud-operations
```

## Workflow Steps

### 1. Start New Feature
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 2. Make Changes
```bash
git add .
git commit -m "feat(scope): description"
```

### 3. Push and Create PR
```bash
git push -u origin feature/your-feature-name
# Create PR through GitHub UI
```

### 4. Clean Up After Merge
```bash
git checkout develop
git pull origin develop
git branch -d feature/your-feature-name
```

## Best Practices
- Keep branches small and focused
- Use descriptive branch names
- Regularly sync with develop
- Delete merged branches

## Branch Protection
- `main`: Requires PR review, CI checks
- `develop`: Requires PR review