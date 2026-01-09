# Pull Request Guide

## Overview

Pull requests (PRs) are the primary way to propose changes, get code reviewed, and collaborate effectively. A well-crafted PR makes review faster and reduces back-and-forth communication.

## Before Creating a PR

### ✅ Pre-PR Checklist
- [ ] Code follows our [style guidelines](../code_standards/python_style_guide.md)
- [ ] All tests pass locally
- [ ] New functionality has tests
- [ ] Documentation updated (if needed)
- [ ] Commits follow [commit guidelines](commit_guidelines.md)
- [ ] Branch is up-to-date with target branch

### Code Quality Checks
```bash
# Format code
black .

# Check linting
flake8 .

# Run tests
pytest

# Check types (if using mypy)
mypy src/
```

## Creating a Pull Request

### 1. Push Your Branch
```bash
git push -u origin feature/your-feature-name
```

### 2. Use GitHub Interface
Navigate to the repository and click "Compare & pull request" or create one manually.

### 3. Fill Out PR Template

## PR Title Format

Use the same format as commit messages:

```
<type>(<scope>): <description>
```

**Examples:**
- `feat(auth): implement user registration with email verification`
- `fix(todo): resolve task duplication issue in list view`
- `docs(api): add comprehensive endpoint documentation`

## PR Description Template

```markdown
## Summary
Brief description of what this PR accomplishes.

## Changes Made
- List specific changes
- Use bullet points
- Be concrete and specific

## Related Issue
Closes #[issue-number]
Related to #[issue-number]

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
Describe how you tested these changes:
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] All existing tests pass

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Corresponding changes to documentation made
- [ ] No new warnings introduced
- [ ] Tests added for new functionality
- [ ] All tests pass locally

## Additional Notes
Any additional context, concerns, or notes for reviewers.
```

## PR Best Practices

### ✅ Good PR Characteristics

#### **Size and Scope**
- Keep PRs small and focused (< 400 lines of code)
- One feature or fix per PR
- Clear, single purpose

#### **Description Quality**
- Explain **why** the change is needed
- Describe **what** was changed
- Include **how** to test the changes
- Reference related issues

#### **Code Quality**
- All tests pass
- Code is well-documented
- Follows project conventions
- No debugging code left behind

### ❌ Common PR Mistakes

#### **Poor Descriptions**
```markdown
## Summary
Fixed stuff

## Changes
- Updated files
```

#### **Too Large**
- 50+ files changed
- Multiple unrelated features
- Months of development

#### **Missing Context**
- No explanation of why change is needed
- No testing instructions
- No issue references

## Review Process

### Requesting Reviews

#### **Who to Request**
- Code owners (automatic)
- Subject matter experts
- Team members familiar with the area

#### **Review Guidelines**
- Allow 24-48 hours for review
- Address feedback promptly
- Don't take feedback personally
- Ask questions if unclear

### Responding to Feedback

#### **Good Response**
```markdown
Thanks for the feedback! I've made the following changes:

1. Extracted the validation logic into a separate function
2. Added error handling for the database connection
3. Updated the tests to cover the edge cases you mentioned

The latest commit addresses all your concerns. Please take another look when you have a chance.
```

#### **Poor Response**
```markdown
Fixed.
```

### Making Changes After Review

#### **Small Changes**
For minor fixes, just push additional commits:
```bash
git add .
git commit -m "fix(auth): address PR feedback - extract validation logic"
git push origin feature/your-feature
```

#### **Major Rework**
For significant changes, consider:
```bash
# Interactive rebase to clean up history
git rebase -i HEAD~3

# Force push (only on feature branches)
git push --force-with-lease origin feature/your-feature
```

## Different PR Types

### Feature PRs
```markdown
## Summary
Implement user authentication system with JWT tokens and refresh mechanism.

## Changes Made
- Add User model with password hashing
- Create registration and login endpoints
- Implement JWT token generation and validation
- Add refresh token functionality
- Create authentication middleware

## Testing
- Unit tests for all auth functions (95% coverage)
- Integration tests for auth endpoints
- Manual testing with Postman collection
- Security testing with invalid tokens

Closes #123
```

### Bug Fix PRs
```markdown
## Summary
Fix race condition in task creation causing duplicate tasks.

## Root Cause
Database transaction isolation issue when multiple requests create tasks simultaneously.

## Solution
- Add database-level unique constraint
- Implement proper error handling for constraint violations
- Add retry logic with exponential backoff

## Testing
- Reproduced original bug with concurrent requests
- Verified fix prevents duplicates
- Added regression test

Fixes #456
```

### Documentation PRs
```markdown
## Summary
Add comprehensive API documentation with examples and error codes.

## Changes Made
- Document all authentication endpoints
- Add request/response examples
- Include error code reference
- Update README with API usage

## Validation
- Tested all examples against live API
- Verified error codes match actual responses
- Spell-checked and grammar-checked content
```

## Advanced PR Features

### Draft PRs
Use draft PRs for:
- Work in progress
- Getting early feedback
- Showing direction before full implementation

```bash
# Create draft PR via GitHub CLI
gh pr create --draft --title "WIP: User authentication system"
```

### PR Templates
Create `.github/pull_request_template.md`:

```markdown
## Summary


## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code reviewed by author
- [ ] Documentation updated
- [ ] No secrets in code
```

### Linking Issues
```markdown
<!-- Automatically close issues -->
Closes #123
Fixes #456
Resolves #789

<!-- Reference without closing -->
Related to #234
See #345
Part of #567
```

## Merge Strategies

### Squash and Merge (Recommended)
- Combines all commits into one
- Clean history on main branch
- Good for feature branches

### Merge Commit
- Preserves all commit history  
- Shows branch structure
- Use for important features

### Rebase and Merge
- Replays commits on target branch
- No merge commit created
- Linear history

## Troubleshooting

### PR Conflicts
```bash
# Update your branch
git checkout your-feature-branch
git fetch origin
git merge origin/main

# Resolve conflicts
# Edit conflicted files
git add resolved-files
git commit -m "resolve merge conflicts with main"
git push origin your-feature-branch
```

### Failed Checks
1. **Tests Failing**: Fix tests and push
2. **Linting Errors**: Run linters locally and fix
3. **Coverage Too Low**: Add more tests
4. **Security Issues**: Address security concerns

### Large PR Review
If PR is too large:
1. Break into smaller PRs
2. Create draft PRs for review
3. Use feature flags for gradual rollout

---

**Next Steps**: Learn about [Code Standards](../code_standards/) to ensure your code meets quality requirements.