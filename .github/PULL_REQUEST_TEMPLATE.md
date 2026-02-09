# Pull Request Template

> **🎯 Purpose:** Use this template to ensure consistent, high-quality pull requests with proper documentation and validation.

---

## 📝 Description

Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context. List any dependencies that are required for this change.

**Fixes # (issue)**

---

## 🔄 Type of Change

Although branch type can describe the type of change, but is not long-lived. 

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality not to work as expected)
- [ ] This change requires a documentation update

---

## 🧪 How Has This Been Tested?

Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration.

- [ ] Test A
- [ ] Test B

---

## ✅ PR Checklist

## MUST (No Exceptions—Do These Every Time)

### 🏗️ **A. Core Code Quality**
- [ ] Follows SOLID Principles (Single Responsibility, Open/Closed, etc.)
- [ ] No Dead Code / Debug Leftovers (no console.log, print, commented-out code)
- [ ] Naming is Clear & Consistent (variables, functions, files)
- [ ] Functions/Methods are Short & Focused (ideally <30 lines)
- [ ] No Hardcoded Secrets/Config (use env vars or secret managers)

### 🧪 **B. Test Coverage**
- [ ] All New Logic is Tested (unit/integration tests for all new features/fixes)
- [ ] All Tests Pass (CI green locally)
- [ ] No Broken Existing Tests (fix before merge)

### 📝 **C. Linting, Style & Docs**
- [ ] All Linters/Formatters Pass (black, flake8, eslint, prettier, etc.)
- [ ] Public Functions/Classes are Documented (docstrings/JSDoc)
- [ ] README / Docs Updated (for API/features/config changes)

### 🛡️ **D. Security & Compliance**
- [ ] No Sensitive Data Leaks (PII, keys, passwords)
- [ ] No Known Vulnerabilities Introduced (dependency check)
- [ ] Input/Output Validations Present (especially for APIs)
- [ ] Proper Error Handling (friendly/logged errors, no raw exceptions)

### 🏛️ **E. Architecture & Patterns**
- [ ] Code is Modular & Reusable (no monoliths)
- [ ] Adheres to Existing Project Patterns
- [ ] Dependencies are justified (no unnecessary new packages)
- [ ] No Large Commits (keep PRs manageable or explain big ones in detail)

### 📢 **F. PR Description & Communication**
- [ ] Clear, Descriptive PR Title & Description (what, why, context)
- [ ] Linked to Related Issues/Tickets (Jira, GitHub Issue, etc.)
- [ ] Changelog Updated (if applicable)
- [ ] Checklist in PR Marked/Updated by Author

### 👥 **G. Review Process**
- [ ] At Least 1-2 Reviewer Approvals
- [ ] Requested Changes Addressed Before Merge
- [ ] No "LGTM" Without Reading the Code
- [ ] No Self-Merge Without Approval (unless emergency/hotfix)

### 🔍 **H. Technical Validation Checklist**
- [ ] How has this PR been tested? (Include clear test instructions or evidence in the PR description.)
- [ ] All DB migrations are reviewed, tested, and schema changes are backwards compatible. Rollback steps or mitigation plans are provided as needed. (if applicable)
- [ ] All AWS SAM/CloudFormation changes are reviewed and validated for correctness, security, and backwards compatibility. (if applicable)
- [ ] All SonarQube (or equivalent) code analysis checks must pass. No new critical issues or code smells introduced. (if applicable)

---

## 📋 Additional Information

### 📸 Screenshots
If applicable, add screenshots to help explain your changes.

### 🔗 Related Issues
List any related issues or pull requests.

### 📚 Documentation
- [ ] Documentation updated
- [ ] API documentation updated
- [ ] README updated

### 🚀 Deployment
- [ ] Deployment steps documented
- [ ] Migration scripts included
- [ ] Rollback plan documented

---

## 🤝 Review Guidelines

### For Reviewers
1. **Code Quality** - Check for clean, maintainable code
2. **Functionality** - Verify the change works as expected
3. **Testing** - Ensure adequate test coverage
4. **Documentation** - Confirm documentation is updated
5. **Security** - Check for security implications

### For Author
1. **Self-Review** - Review your own code first
2. **Testing** - Ensure all tests pass locally
3. **Documentation** - Update relevant documentation
4. **Communication** - Respond to review comments promptly

---

## 📊 Checklist Summary

| Category | Status | Notes |
|----------|--------|-------|
| Code Quality | ⏳ | |
| Test Coverage | ⏳ | |
| Documentation | ⏳ | |
| Security | ⏳ | |
| Architecture | ⏳ | |
| Review | ⏳ | |

---

## 🎉 Ready to Merge?

Before merging, ensure:
- [ ] All checklist items are completed
- [ ] CI/CD pipeline passes
- [ ] Reviewers have approved
- [ ] No merge conflicts
- [ ] Documentation is updated

---

## 📞 Contact

If you have questions about this PR template or the review process, please contact the development team.

---

*This template helps maintain code quality and consistency across all pull requests. Thank you for following our standards!* 🚀
