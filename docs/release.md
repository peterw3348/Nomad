# Release Branch Workflow

## 0. Overview

This document defines the **release process** for this project using **release branches**, **Conventional Commits**, and **automated versioning** with **Commitizen**.

Releases are managed via `release/*` branches. Upon pushing a release branch, CI:
- Runs `cz bump` to automatically determine the correct version
- Updates the version in `src/__version__.py`
- Updates `CHANGELOG.md`
- Tags the commit (e.g., `v1.2.0`)
- Opens a pull request to merge the release back into `main`

---

## 1. Creating a Release

### ✅ Step-by-step

1. Ensure all PRs are merged into `main`.
2. From `main`, cut a release branch:
   ```bash
   git checkout main
   git pull
   git checkout -b release/next
   git push origin release/next
   ```
3. CI will trigger on the `release/*` branch and automatically:
   - Analyze commits since the last version tag
   - Bump the version based on Conventional Commits
   - Generate and update `CHANGELOG.md`
   - Create and push a Git tag (e.g., `v1.3.0`)
   - Open a pull request to merge the release branch into `main`

---

## 2. Naming Release Branches

Release branch names **do not need to match the version number**. Examples:

| Branch Name        | Usage                        |
|--------------------|------------------------------|
| `release/next`     | General purpose release (auto-bumped) |
| `release/v1.5`     | Version-aligned release branch |
| `release/2025-04-01` | Date-based release branch |
| `release/candidate` | Pre-release candidate branch |

Use whichever naming convention fits your team or project.

---

## 3. How Versioning Works

Versioning is powered by **Commitizen** using **Conventional Commits**.  
The version bump is based on the most significant change type in commits since the last tag:

| Commit Type        | Version Bump |
|--------------------|--------------|
| `fix:`             | Patch (`1.2.3 → 1.2.4`) |
| `feat:`            | Minor (`1.2.3 → 1.3.0`) |
| `BREAKING CHANGE:` | Major (`1.2.3 → 2.0.0`) |

Only commits merged into `main` prior to the release branch will be considered.

To preview what will happen:
```bash
cz bump --dry-run --changelog
```

---

## 4. Merging Release Back to Main

Once the release PR is created automatically:

1. Review the PR — ensure the bump and changelog are correct.
2. Merge it into `main` via GitHub (squash, merge, or rebase — your call).
3. `main` will now reflect the new version and changelog.

> This step is **manual by default** to allow human verification.

---

## 5. Summary Flow

```text
[feature/fix branches] → main → release/* → (CI bump + tag) → PR to main → merge
```

---

## 6. Enforcement & Tools

| Tool       | Purpose                                   |
|------------|-------------------------------------------|
| **Commitizen (`cz`)** | Automates version bumps + changelog |
| **Conventional Commits** | Required for commit formatting |
| **GitHub Actions** | Runs on `release/*` branches to trigger release |
| **commitlint (optional)** | Validates commit messages before merge |
| **cz bump --dry-run** | Lets you preview version bump & changelog |

---

## 7. Example Output

After pushing a `release/next` branch:

- `src/__version__.py` → `__version__ = "0.3.0"`
- `CHANGELOG.md` → New section for `v0.3.0` with commit summaries
- Git tag created: `v0.3.0`
- Pull request opened to merge `release/next → main`