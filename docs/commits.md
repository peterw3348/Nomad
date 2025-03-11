# Conventional Commits Standard

## 1. Commit Message Format
All commit messages must follow the structured format:
```
<type>(<scope>): <short description>

[Optional longer description]

[Optional references to issues or breaking changes]
```

- `<type>` must be one of the predefined commit types.
- `<scope>` is optional but should specify the affected module or component.
- The short description must be concise and written in the imperative mood (e.g., "fix bug" not "fixed bug").
- If the commit introduces a breaking change, it must include `BREAKING CHANGE:` in the footer.

---

## 2. Commit Types
Each commit must start with a **type** that accurately describes the nature of the change.

### ✅ **Standard Types**
| Type    | Description |
|---------|------------|
| `feat`  | Introduces a new feature (triggers a **minor** version bump). |
| `fix`   | Fixes a bug (triggers a **patch** version bump). |
| `docs`  | Updates documentation only (does NOT affect code functionality). |
| `style` | Code style changes (formatting, whitespace, etc.). |
| `refactor` | Code changes that do not fix bugs or add features. |
| `perf`  | Performance improvements. |
| `test`  | Adds or modifies tests. |
| `chore` | Routine maintenance, dependency updates, or tooling changes. |
| `ci`    | Changes to CI/CD workflows. |

---

## 3. Breaking Changes
If a commit **introduces breaking changes**, it must be explicitly marked by including `BREAKING CHANGE:` in the footer.

```
feat(api): change authentication method

BREAKING CHANGE: The API now requires OAuth tokens instead of API keys.
```
- **Breaking changes require a MAJOR version bump** (`1.2.3 → 2.0.0`).
- Any removal or modification of a public API function, CLI command, or configuration parameter is considered breaking.

---

## 4. Examples
### ✅ **Feature Addition**
```
feat(auth): add Google authentication support
```
### ✅ **Bug Fix**
```
fix(watcher): fix crash when client is closed
```
### ✅ **Documentation Update**
```
docs(readme): update setup instructions
```
### ✅ **Refactoring Code**
```
refactor(evaluator): convert evaluator.py to a class
```
### ✅ **Breaking Change**
```
feat(api): migrate to new champion ID system

BREAKING CHANGE: Old champion IDs are no longer supported.
```

---

## 5. Versioning Policy
This project follows **Semantic Versioning (SemVer)**:
```
MAJOR.MINOR.PATCH
```
| Type of Change | Example | Version Bump |
|---------------|---------|-------------|
| 🛠 Bug Fixes | Fixing a crash, fixing a calculation error | PATCH (`1.0.0 → 1.0.1`) |
| ✨ New Features | Adding champion role weighting system | MINOR (`1.0.0 → 1.1.0`) |
| 🏗 Refactoring | Converting watcher.py into a class (no breaking change) | PATCH (`1.2.3 → 1.2.4`) |
| 📚 Docs & Chore Work | Updating README, adding comments | PATCH (`1.2.3 → 1.2.4`) |
| ❌ Breaking Changes | Removing or changing API behavior | MAJOR (`1.2.3 → 2.0.0`) |

---

## 6. Automating Versioning
Versioning is managed via **Semantic Release**, which automates version bumps based on commit messages.

**Versioning Rules:**
- `feat:` → Increases the **MINOR** version (`1.2.3 → 1.3.0`).
- `fix:` → Increases the **PATCH** version (`1.2.3 → 1.2.4`).
- `BREAKING CHANGE:` → Increases the **MAJOR** version (`1.2.3 → 2.0.0`).

---

## 7. Enforcement
All commits must follow this standard to ensure consistency and maintainability. Automated tools such as commitlint and CI pipelines will enforce these rules where applicable.
