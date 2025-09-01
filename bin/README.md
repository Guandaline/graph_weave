# 📁 Folder `bin/` — Utility Scripts

This folder contains the project's executable scripts to facilitate setup, testing, CI/CD, and other local operations.

## Available Scripts

| Script         | Description                                                                |
|----------------|---------------------------------------------------------------------------|
| `setup.sh`     | Sets up virtual environment, installs dependencies and pre-commit hooks    |
| `run-act.sh`   | Runs GitHub Actions workflows locally using Docker (`act`)                 |
| `bootstrap.sh` | Prepares your local machine: installs Poetry, Docker, prerequisites        |
| `test.sh`      | Runs all tests and validations (pytest, lint, typecheck, etc.)             |

## How to use

```bash
chmod +x bin/*.sh  # Ensure permission
./bin/setup.sh
./bin/run-act.sh -e push -j lint
```