# Changelog

All notable changes to Suggit are documented here.

## [1.0.2] - 2026-04-02

### Added
- AI-powered commit message suggestion via Google Gemini 2.5 Flash
- Local offline fallback engine with 55+ scope patterns
- Interactive pre-filled prompt — press Enter to accept or edit freely
- `--add` flag — runs `git add .` before committing
- `--push` flag — runs `git add .` + commit + `git push` in one command
- `--dry-run` flag — shows suggestion without committing
- Auto-detects unstaged changes and asks to stage them
- Conventional Commits format — `type(scope): description`
- Supports Django, React, Flutter, Node.js scope detection
- Modular structure split across 5 clean Python files
- One-command installer (`install.sh`)

### Scope detection covers
- Auth, user, permissions, security
- Django: views, urls, serializers, models, migrations, signals, tasks
- React/Next: components, pages, hooks, state, styles, router
- Flutter: widgets, blocs, firebase, payments
- General: utils, config, logging, errors, cache, scheduler
