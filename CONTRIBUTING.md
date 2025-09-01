# 🤝 How to Contribute to Graph Weave RAG

First of all, thank you for considering contributing to Graph Weave RAG! 🎉 We greatly appreciate your time and effort.

This document provides guidelines for contributing to the project. Please read it carefully to ensure the process is as smooth and effective as possible for everyone.

---

## 📜 Code of Conduct

This project is governed by our [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to follow it.  
Unacceptable behavior should be reported to the maintainers or via email at `vhguandaline@gmail.com`.

---

## 🚀 How Can I Contribute?

- **Reporting Bugs:** Use the [Issue Tracker](https://github.com/Guandaline/graph_weave/issues).
- **Suggesting Improvements:** Also via the [Issue Tracker](https://github.com/Guandaline/graph_weave/issues).
- **Writing Code:** Fix bugs or implement features.
- **Improving Documentation**
- **Writing Automated Tests**

---

## ⚙️ Getting Started (Environment Setup)

```bash
git clone https://github.com/Gandaline/graph_weave.git
cd graph_weave
poetry install
poetry run pre-commit install  # optional, but recommended
```

---

## 🌱 Contribution Workflow

```bash
git checkout main
git pull origin main
git checkout -b feat/my-feature
```

1. Write your code/documentation/tests
2. Ensure quality with:
  ```bash
  poetry run ruff .
  poetry run pytest
  poetry run mypy src/
  ```
3. Use commit messages following our [Commit Guide](./COMMIT_GUIDE.md)
4. Push your branch:
  ```bash
  git push origin feat/my-feature
  ```
5. Open a Pull Request clearly explaining the change
6. Address comments and wait for approval to merge

---

## 🛠️ Technical Standards

- Code must be clean, tested, and typed
- We use `black`, `ruff`, `mypy`, `pytest`
- New modules should include:
  - Registration in `registry.py` (if applicable)
  - Tests in `tests/unit/` or `tests/integration/`
  - Documentation in `.md` following the project standard

---

## 🧠 Supporting Documents

- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Commit Guide](./COMMIT_GUIDE.md)
- [Security Policy](./SECURITY.md)
- [Architectural Decision Records (ADR)](./docs/adr/000-sample-doc.md) *(if applicable)*

---

## 🐛 Reporting Bugs

- Check if the bug has already been reported
- Include:
  - Steps to reproduce
  - Error messages
  - Environment and versions

---

## 💡 Suggesting Improvements

- Describe the problem your idea solves
- Explain the context and impact
- Provide implementation suggestions, if possible

---

Thank you again for your contribution and for being part of the `graph_weave` community!