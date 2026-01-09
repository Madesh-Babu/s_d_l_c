# Commit Guidelines

## Overview

Clear, consistent commit messages help maintain project history and make it easier to understand changes. We follow the **Conventional Commits** specification.

## Commit Message Format

```
<type>(<scope>): <short description>

[optional body]

[optional footer(s)]
```

### Components Explained

#### Type (Required)
Describes the kind of change:

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature or enhancement | `feat(auth): add user registration` |
| `fix` | Bug fix | `fix(todo): correct task title validation` |
| `docs` | Documentation changes | `docs(readme): update installation steps` |
| `test` | Adding or modifying tests | `test(auth): add login endpoint tests` |
| `chore` | Maintenance tasks | `chore(deps): update FastAPI to v0.104` |
| `refactor` | Code restructuring | `refactor(todo): extract validation logic` |
| `perf` | Performance improvements | `perf(db): optimize user query performance` |
| `style` | Code formatting only | `style(auth): fix indentation in user model` |

#### Scope (Optional)
The area of code affected:

```bash
feat(auth): add JWT token validation
fix(todo): resolve task creation bug  
docs(api): update endpoint documentation
test(db): add database connection tests
```

**Common Scopes:**
- `auth` - Authentication/authorization
- `todo` - TODO functionality  
- `db` - Database operations
- `api` - API endpoints
- `ui` - User interface
- `config` - Configuration
- `docker` - Docker setup
- `ci` - CI/CD pipeline

#### Description (Required)
- Use present tense: "add feature" not "added feature"
- Use imperative mood: "fix bug" not "fixes bug"  
- Start with lowercase
- No period at the end
- Maximum 50 characters

## Examples

### ✅ Good Commit Messages

```bash
feat(auth): add user registration endpoint
fix(todo): resolve task deletion error
docs(api): update authentication documentation
test(auth): add user login integration tests
chore(deps): bump python version to 3.12
refactor(todo): extract task validation to service layer
perf(db): add index on user_id column
style(auth): format code with black formatter
```

### ❌ Bad Commit Messages

```bash
Update stuff                    # Too vague
Fixed bug                      # What bug? Where?
Added feature                  # What feature?
WIP                           # Work in progress, should be squashed
Updated documentation.         # Unnecessary period
FEAT: Added user auth          # Wrong case
auth: fixed login             # Missing type
```

## Multi-line Commits

For complex changes, use the body to explain **what** and **why**:

```bash
feat(auth): implement JWT refresh token mechanism

Add automatic token refresh to prevent user logout during active sessions.
The refresh token is stored securely and rotates on each use to prevent
replay attacks.

Closes #123
```

## Body Guidelines

When to include a body:
- Complex changes that need explanation
- Breaking changes
- Security implications
- Performance impacts

Body format:
- Leave blank line after subject
- Wrap at 72 characters  
- Explain **what** and **why**, not **how**
- Use present tense

## Footer

Include footers for:
- **Issue references**: `Closes #123`, `Fixes #456`
- **Breaking changes**: `BREAKING CHANGE: API endpoint changed`
- **Co-authors**: `Co-authored-by: Name <email>`

```bash
feat(api): restructure user endpoints

Move all user-related endpoints under /api/v2/users path for better
organization and consistency with REST conventions.

BREAKING CHANGE: User endpoints moved from /users to /api/v2/users
Closes #234
Co-authored-by: Jane Developer <jane@example.com>
```

## Atomic Commits

Each commit should represent **one logical change**:

### ✅ Atomic Commits
```bash
feat(auth): add user model
feat(auth): add registration endpoint  
feat(auth): add login endpoint
test(auth): add authentication tests
```

### ❌ Non-atomic Commit
```bash
feat(auth): add user auth and fix todo bug and update docs
```

## Special Cases

### Reverting Commits
```bash
revert: feat(auth): add user registration endpoint

This reverts commit 1234567890abcdef.
Reason: Registration endpoint causing database conflicts.
```

### Work in Progress
Avoid WIP commits in main branches. If necessary:
```bash
wip(auth): partial implementation of JWT validation
```
**Note**: Squash WIP commits before merging.

### Dependencies
```bash
chore(deps): update FastAPI from 0.103.0 to 0.104.1
chore(deps): add python-jose for JWT handling  
chore(deps): remove unused pytest-cov dependency
```

## Tools and Automation

### Pre-commit Hooks
Set up automatic commit message validation:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v2.42.1
    hooks:
      - id: commitizen
```

### VS Code Extensions
- **Conventional Commits**: Auto-complete commit types
- **GitLens**: Enhanced git history visualization

### Command Line Tools
```bash
# Install commitizen for interactive commits
pip install commitizen
cz commit
```

## Git Commit Best Practices

### Before Committing
```bash
# Review your changes
git diff

# Stage specific files
git add file1.py file2.py

# Review staged changes
git diff --staged
```

### Interactive Staging
```bash
# Stage parts of files
git add -p filename.py

# Interactive add
git add -i
```

### Amending Commits
```bash
# Fix last commit message
git commit --amend -m "corrected message"

# Add forgotten files to last commit
git add forgotten_file.py
git commit --amend --no-edit
```

## Common Mistakes to Avoid

### ❌ Don't
- Mix multiple unrelated changes in one commit
- Use vague messages like "fix", "update", "changes"
- Commit broken code (unless clearly marked as WIP)
- Include sensitive information (passwords, keys)
- Use past tense in commit messages

### ✅ Do  
- Make atomic commits (one logical change)
- Test before committing
- Write descriptive messages
- Use consistent formatting
- Reference issues when applicable

## Commit Message Templates

Create a git template for consistency:

```bash
# ~/.gitmessage
<type>(<scope>): <subject>

# <body>

# <footer>

# Type: feat, fix, docs, style, refactor, test, chore, perf
# Scope: auth, todo, db, api, ui, config, docker, ci
# Subject: present tense, imperative mood, lowercase, no period
# Body: explain what and why (optional)
# Footer: reference issues, breaking changes (optional)
```

Set the template:
```bash
git config --global commit.template ~/.gitmessage
```

---

**Next Steps**: Learn about [Pull Request Guide](pull_request_guide.md) to create effective PRs with your well-crafted commits.