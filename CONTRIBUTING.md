# Contributing

## Environment
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # if present; pygame optional for 2D prototype
```

## Branching & Commits
- Use feature branches: `feature/ui-colour-borders`, `fix/withdraw-cancel-turn`
- Conventional commit style (recommended): `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`
- Keep PRs small and focused; include before/after screenshots for UI tweaks

## Code Style
- Pure Python, no external deps needed for text version
- Return a boolean from action handlers to indicate success (drives turn progression)
- Keep UI (printing) separate from core state mutations where possible

## Tests (Manual)
- Verify: cancel in sub-menus does not consume a turn
- Verify: insufficient resources do not consume a turn
- Verify: Withdraw is locked <45 Stability and confirmation works
- Verify: Quit option [0] exits cleanly and prints final status
