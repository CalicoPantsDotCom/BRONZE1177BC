# Changelog

All notable changes to this project will be documented in this file.

## [1.2.6] - 2025-10-25
### Added
- **[0] Quit Game** option in the in-game action menu; cleanly exits and prints final status.
### Fixed
- Minor alignment/label polish in the menu.

## [1.2.5] - 2025-10-25
### Changed
- **UI readability:** coloured **borders only** (resources=yellow, metrics=cyan, crisis=red, tech=green). Values remain white for clarity.
- No logic changes.

## [1.2.4] - 2025-10-25
### Changed
- **Withdraw**: Locked below Stability ≥45; confirmation prompt; cancellation no longer consumes a turn.
### Fixed
- Removed duplicate function definitions introduced during integration.
- Standardized actions to return success booleans.

## [1.2.3] - 2025-10-25
### Changed
- **Turns only advance on successful actions.** Cancelling sub-menus or attempting an action with insufficient resources no longer consumes a turn.
- Sub-menus (Build/Research/Diplomacy/Withdraw) return `False` on cancel/insufficient resources.

## [1.2.2] - 2025-10-25
### Changed
- **Auto End-of-Turn** after each successful action. Removed explicit "End Turn" from the menu.
- End-of-turn processing (drift, per-turn yields, events) now runs immediately after an action succeeds.

## [1.2.1] - 2025-10-25
### Added
- **Gather Timber** action: `-8 Grain → +10 Timber`.
### Changed
- **Harvest** now grants `+15 Grain` **and** `+10 Bronze`.
- Updated action menu labels to reflect new yields.

## [1.2.0] - 2025-10-24
### Baseline
- v1.2 Integrated build (Vacuum path validated; Withdraw action; reduced drift; more positive events).
