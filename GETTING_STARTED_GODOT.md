# Getting Started with Godot Port

Quick start guide for porting BRONZE: 1177 BC to Godot 4.

---

## Prerequisites

- **Godot 4.x** installed (https://godotengine.org/download)
- Python version (bronze_1177bc_v1.2_integrated.py) for reference
- Text editor (VS Code with Godot plugin recommended)

---

## Step 1: Create New Godot Project

1. Open Godot Engine
2. Click **"New Project"**
3. Name: `bronze_1177bc_godot`
4. Renderer: **Forward+** (for desktop) or **Mobile** (for web/mobile)
5. Click **"Create & Edit"**

---

## Step 2: Project Structure Setup

Create this folder structure in your project:

```
bronze_1177bc_godot/
├── scenes/
├── scripts/
├── data/
└── assets/
    ├── art/
    ├── fonts/
    └── audio/
```

---

## Step 3: Port Core Game Logic

### Create `scripts/game_state.gd`

```gdscript
extends Node
class_name GameState

# Resources
var grain: int = 50
var timber: int = 20
var bronze: int = 10

# Core Metrics
var military: int = 20
var stability: int = 60
var prestige: int = 30

# Crisis
var collapse: int = 50

# Buildings (booleans)
var has_bronze_mine: bool = false
var has_granary: bool = false
var has_barracks: bool = false
var has_palace: bool = false
var has_lighthouse: bool = false
var has_watchtower: bool = false

# Technologies (booleans)
var has_imperial_bureaucracy: bool = false
var has_tin_trade_routes: bool = false
var has_phalanx_formation: bool = false
var has_diplomatic_marriage: bool = false

# Game state
var turn: int = 1
var max_turns: int = 20

func _ready():
    print("Game State initialized")

# Resource checks
func can_afford(grain_cost: int, timber_cost: int, bronze_cost: int) -> bool:
    return grain >= grain_cost and timber >= timber_cost and bronze >= bronze_cost

func spend_resources(grain_cost: int, timber_cost: int, bronze_cost: int):
    grain -= grain_cost
    timber -= timber_cost
    bronze -= bronze_cost

func add_resources(grain_amount: int, timber_amount: int, bronze_amount: int):
    grain += grain_amount
    timber += timber_amount
    bronze += bronze_amount
```

### Create `scripts/action_handler.gd`

```gdscript
extends Node

var game_state: GameState

func _ready():
    game_state = get_node("/root/GameState")

# Action: Harvest
func harvest() -> bool:
    game_state.add_resources(15, 0, 10)  # v1.2.1 yields
    print("Harvested: +15 Grain, +10 Bronze")
    return true

# Action: Gather Timber
func gather_timber() -> bool:
    if not game_state.can_afford(8, 0, 0):
        print("Insufficient resources: Need 8 Grain")
        return false

    game_state.spend_resources(8, 0, 0)
    game_state.add_resources(0, 10, 0)
    print("Gathered Timber: -8 Grain, +10 Timber")
    return true

# Action: Build Bronze Mine
func build_bronze_mine() -> bool:
    if game_state.has_bronze_mine:
        print("Already built!")
        return false

    if not game_state.can_afford(15, 10, 0):
        print("Insufficient resources: Need 15 Grain, 10 Timber")
        return false

    game_state.spend_resources(15, 10, 0)
    game_state.has_bronze_mine = true
    print("Bronze Mine built! (+2 Bronze per turn)")
    return true

# Add more actions following this pattern...
```

---

## Step 4: Create Basic UI Scene

1. In Godot, right-click `scenes/` → **New Scene**
2. Select **User Interface** as root node
3. Rename root to `GameBoard`
4. Add child nodes:
   - `VBoxContainer` (for vertical layout)
     - `ResourcePanel` (Panel node)
     - `MetricsPanel` (Panel node)
     - `ActionsPanel` (Panel node)

### Sample UI Script

Attach this to your `GameBoard` node:

```gdscript
extends Control

@onready var game_state = $"/root/GameState"
@onready var grain_label = $VBoxContainer/ResourcePanel/GrainLabel
@onready var timber_label = $VBoxContainer/ResourcePanel/TimberLabel

func _ready():
    update_ui()

func update_ui():
    grain_label.text = "Grain: " + str(game_state.grain)
    timber_label.text = "Timber: " + str(game_state.timber)
    # ... update all labels

func _on_harvest_button_pressed():
    var action_handler = ActionHandler.new()
    if action_handler.harvest():
        update_ui()
```

---

## Step 5: Configure Autoload (Singletons)

1. **Project → Project Settings → Autoload**
2. Add `scripts/game_state.gd` as `GameState`
3. Now `GameState` is globally accessible

---

## Step 6: Test Build

1. Press **F5** (or click Play button)
2. Select `scenes/game_board.tscn` as main scene
3. Test basic actions (Harvest, Gather Timber)
4. Verify resource updates

---

## Step 7: Export Settings

### For Web (HTML5):
1. **Project → Export**
2. **Add → Web**
3. Set export path: `builds/web/index.html`
4. **Export Project**
5. Test locally with: `python -m http.server` in builds/web/

### For Desktop:
1. **Project → Export**
2. **Add → Windows Desktop** (or Mac/Linux)
3. Set export path: `builds/desktop/bronze.exe`
4. **Export Project**

### For Mobile:
1. Install Android/iOS export templates
2. **Project → Export → Add → Android** (or iOS)
3. Configure signing keys
4. Export APK/IPA

---

## Development Tips

### GDScript vs Python Differences

| Python | GDScript |
|--------|----------|
| `self.variable` | `variable` (no self needed) |
| `def function():` | `func function():` |
| `True/False` | `true/false` (lowercase) |
| `print(f"Value: {x}")` | `print("Value: ", x)` |
| `if x == None:` | `if x == null:` |

### Signals (Godot's Event System)

Replace callbacks with signals:

```gdscript
# Emit when turn ends
signal turn_ended(turn_number)

func end_turn():
    turn += 1
    turn_ended.emit(turn)

# In UI script:
func _ready():
    game_state.turn_ended.connect(_on_turn_ended)

func _on_turn_ended(turn_num: int):
    print("Turn ", turn_num, " ended")
    update_ui()
```

---

## Debugging Tools

- **F6**: Run current scene
- **F7**: Step through code
- **Remote Debug**: View live game state while running
- **Print statements**: Show in Output panel (bottom)

---

## Next Steps After MVP

1. **Add visual polish** (backgrounds, icons, animations)
2. **Implement save/load** (using `ConfigFile` or JSON)
3. **Add sound effects** (AudioStreamPlayer nodes)
4. **Create tutorial** (pop-up panels on first playthrough)
5. **Export to Itch.io** for playtesting

---

## Resources

- **Godot Docs:** https://docs.godotengine.org/en/stable/
- **GDScript Tutorial:** https://gdscript.com/
- **UI Tutorial:** https://docs.godotengine.org/en/stable/tutorials/ui/
- **Export Guide:** https://docs.godotengine.org/en/stable/tutorials/export/

---

## Estimated Timeline

- **Week 1:** Port core logic, basic UI
- **Week 2:** All actions functional, turn system working
- **Week 3:** Polish, playtesting, first web build

**Ready to start?** Open Godot and create your project!
