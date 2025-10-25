# BRONZE: 1177 BC

A turn-based strategy about the Late Bronze Age Collapse. Govern a kingdom through crisis and pursue one of two paths: **Preservation** (reduce Collapse to 0) or **Vacuum** (survive 20 turns with Collapse ≥ 80 and strongest Military).

## Requirements
- **Python 3.10+**
- Terminal that supports ANSI colours (for coloured section borders)
- *(Optional)* **Pygame** if you use the separate 2D prototype

## Install & Run
```bash
# (Optional) create a virtual env
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# If using the 2D prototype, install:
pip install pygame
```

**Text version (main game):**
```bash
python3 bronze_1177bc_v1.2_integrated.py
```

## Controls (Text Version)
- **[1–7]** perform actions (Harvest, Gather Timber, Build, Research, Diplomacy, Fortify, Withdraw)
- **[0] Quit Game** exits cleanly at any time
- Turns advance automatically after a successful action
- Cancelling a sub-menu or lacking resources does not consume a turn

## QoL & UI
- Section borders are colour-coded for readability:
  - Resources = yellow, Core Metrics = cyan, Crisis = red, Technologies = green
- Numbers remain white for contrast

## Session Length
- 15–20 turns (≈10–15 minutes)

## License
See LICENSE.
