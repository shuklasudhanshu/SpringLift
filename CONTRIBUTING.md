# Contributing to SpringLift

Thanks for your interest in contributing to SpringLift! We're actively developing this tool and welcome help from the community. This document explains how to contribute, our expectations, and a small PR checklist to speed reviews.

## Getting started

1. Fork the repository and clone your fork:

```bash
git clone https://github.com/<your-username>/SpringLift.git
cd SpringLift
```

2. Create a feature branch from `main`:

```bash
git checkout -b feat/my-change
```

3. Run tests and linters before opening a PR (see `requirements.txt`):

```bash
pip install -r requirements.txt
pytest tests/ -q
```

## Contribution types

- Bug fixes
- New modernization rules or updaters
- Documentation improvements
- Tests and CI

## Code style

- Use the existing project structure and follow existing code conventions.
- Keep changes small and focused; one logical change per PR.
- Add tests for new behavior where practical.

## Commit messages

- Use clear, short titles (50 chars or less) and an explanatory body when needed.
- Prefix with type, for example: `fix:`, `feat:`, `docs:`, `test:`.

## Pull Request checklist

Before requesting review, please ensure:

- [ ] The PR targets the `main` branch.
- [ ] All tests pass locally: `pytest tests/ -q`.
- [ ] New code includes unit tests or an explanation why tests are not applicable.
- [ ] Relevant files are updated (README, docs) if behavior or interfaces changed.
- [ ] No sensitive information (API keys, secrets) is included.
- [ ] Short description of what and why in the PR description.

## Reporting issues

If you find a bug or have a feature request, please open an issue with a clear title, reproduction steps, and any relevant logs or screenshots.

## Code of Conduct

By contributing, you agree to follow the project's code of conduct. Be respectful, constructive, and open to feedback.

---

Thanks — maintainers ❤️
