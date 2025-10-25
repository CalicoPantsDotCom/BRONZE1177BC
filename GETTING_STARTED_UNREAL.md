# Getting Started with Unreal Engine Port

Guide for creating a showcase version of BRONZE: 1177 BC in Unreal Engine 5.

---

## Prerequisites

- **Unreal Engine 5.x** installed (via Epic Games Launcher)
- ~50 GB disk space for engine + project
- GPU: GTX 1060 or equivalent (for UE5 features)
- Familiarity with Blueprint visual scripting (optional but helpful)

---

## Why Unreal for BRONZE?

**Not recommended as primary platform**, but excellent for:
- Creating a **cinematic trailer** (3D Bronze Age city)
- Learning Unreal with a small, contained project
- Portfolio piece showing engine versatility
- Future 3D expansion (walk around your city)

**For actual game release**, use Godot (see PLATFORM_ROADMAP.md).

---

## Step 1: Create New Project

1. Open **Epic Games Launcher → Unreal Engine**
2. Click **Launch** (UE 5.3 or later)
3. **Games → Blank** template
4. **Blueprint** (not C++)
5. No Starter Content (we'll add specific assets)
6. Name: `Bronze1177BC_UE5`
7. Click **Create**

---

## Step 2: Project Organization

Create these folders in Content Browser:

```
Content/
├── Blueprints/
│   ├── BP_GameState
│   ├── BP_TurnManager
│   └── BP_ActionHandler
├── UI/
│   ├── WBP_MainHUD
│   ├── WBP_ActionMenu
│   └── WBP_VictoryScreen
├── Data/
│   ├── DT_Buildings (Data Table)
│   ├── DT_Technologies (Data Table)
│   └── DT_Events (Data Table)
├── Art/
│   ├── Textures/
│   ├── Materials/
│   └── UI/
└── Audio/
    ├── SFX/
    └── Music/
```

---

## Step 3: Create Game State Blueprint

### BP_GameState (Blueprint Class → Actor Component)

**Variables to create:**

| Name | Type | Default | Category |
|------|------|---------|----------|
| Grain | Integer | 50 | Resources |
| Timber | Integer | 20 | Resources |
| Bronze | Integer | 10 | Resources |
| Military | Integer | 20 | Metrics |
| Stability | Integer | 60 | Metrics |
| Prestige | Integer | 30 | Metrics |
| Collapse | Integer | 50 | Crisis |
| Turn | Integer | 1 | Game State |
| HasBronzeMine | Boolean | false | Buildings |

### Functions to create:

**CanAfford** (returns Boolean)
- Inputs: GrainCost (int), TimberCost (int), BronzeCost (int)
- Logic: `Grain >= GrainCost AND Timber >= TimberCost AND Bronze >= BronzeCost`

**SpendResources**
- Inputs: GrainCost, TimberCost, BronzeCost
- Logic: `Grain -= GrainCost`, etc.

**AddResources**
- Inputs: GrainAmount, TimberAmount, BronzeAmount
- Logic: `Grain += GrainAmount`, etc.

---

## Step 4: Create UI with UMG (Unreal Motion Graphics)

### WBP_MainHUD (Widget Blueprint)

1. **Right-click in UI/ → User Interface → Widget Blueprint**
2. Name: `WBP_MainHUD`
3. Open the widget

**Add these elements in Designer:**

```
Canvas Panel (root)
└── VerticalBox
    ├── Text Block - "BRONZE: 1177 BC"
    ├── HorizontalBox (Resources)
    │   ├── Text Block - "Grain: "
    │   ├── Text Block (bind to GameState.Grain)
    │   ├── Text Block - "Timber: "
    │   └── Text Block (bind to GameState.Timber)
    ├── HorizontalBox (Metrics)
    │   └── [Similar pattern for Military, Stability, Prestige]
    └── VerticalBox (Action Buttons)
        ├── Button - "Harvest"
        ├── Button - "Gather Timber"
        ├── Button - "Build..."
        └── Button - "End Turn"
```

### Binding Variables to UI

1. Select a Text Block (e.g., Grain value)
2. In Details panel → **Content → Text → Bind → Create Binding**
3. In the Graph:
   - Get reference to `BP_GameState`
   - Get variable `Grain`
   - Convert to String (`To String`)
   - Return as Text (`To Text`)

---

## Step 5: Button Click Events

### Example: Harvest Button

1. Select **Harvest Button** in designer
2. Details panel → **On Clicked** → Add event `OnHarvestClicked`
3. In Event Graph:

```
[OnHarvestClicked]
  → Get GameState
  → Call AddResources (Grain=15, Timber=0, Bronze=10)
  → Play Sound (SFX_Harvest)
  → Update UI
```

---

## Step 6: Data Tables (Optional but Recommended)

### Create Building Data Table

1. **Right-click in Data/ → Miscellaneous → Data Table**
2. Row Structure: Create new struct `F_BuildingData`
3. Struct fields:
   - `Name` (Text)
   - `GrainCost` (int)
   - `TimberCost` (int)
   - `Description` (Text)
4. Add rows for each building (Bronze Mine, Granary, etc.)

**Benefits:**
- Easy to balance (edit CSV, no code changes)
- Moddable (players can add buildings)
- Cleaner than hardcoding costs in Blueprints

---

## Step 7: Add Game Mode

1. **Blueprints/ → Blueprint Class → Game Mode Base**
2. Name: `BP_BronzeGameMode`
3. **Class Defaults:**
   - Default Pawn Class: `None` (we don't need movement)
   - HUD Class: `WBP_MainHUD`

4. **Project Settings → Maps & Modes:**
   - Default GameMode: `BP_BronzeGameMode`

---

## Step 8: Create Main Menu Level

1. **File → New Level → Empty Level**
2. Save as `MainMenu`
3. Add **Directional Light** and **Sky Atmosphere** (so it's not black)
4. Create Widget: `WBP_MainMenu`
   - Title text
   - "Start Game" button → Open Level "GameBoard"
   - "Quit" button → Quit Game

---

## Step 9: Test Your Build

1. Press **Alt + P** (Play in Editor)
2. Click buttons, verify:
   - Resources update
   - Actions consume resources correctly
   - Turn advances

---

## Step 10: Package for Windows

1. **Platforms → Windows → Package Project**
2. Select output folder (e.g., `Builds/Windows/`)
3. Wait 5-15 minutes for first build
4. Run `.exe` to test standalone build

---

## Adding 3D Visualization (Showcase Feature)

### Create a Bronze Age City Scene

1. **Marketplace → Free Assets:**
   - "Ancient City Builder" pack
   - "Desert Temple" assets
   - Free rock/terrain materials

2. **Build a simple city:**
   - Place buildings on terrain
   - Add palm trees, market stalls
   - Position camera at cinematic angle

3. **Link to Collapse Metric:**
   - Blueprint: If Collapse > 80, spawn fire particles on buildings
   - If Collapse < 30, add celebration flags/banners
   - Dynamic visual feedback

4. **Cinematic Camera:**
   - Add Cine Camera Actor
   - Set up camera shake when crisis events trigger
   - Slow pan across city during turns

---

## Performance Optimization

Since BRONZE is UI-heavy, Unreal might be overkill:

**Optimization Tips:**
- Use **Scalability Settings → Low** for UI-only scenes
- Disable Lumen, Nanite for 2D/UI builds
- Set **Frame Rate Limit** to 30 FPS (UI doesn't need 60+)
- Use **Sparse Class Data** for GameState variables

---

## When to Use Unreal vs Godot

| Task | Engine | Reason |
|------|--------|--------|
| Release build (PC/Web/Mobile) | Godot | Smaller files, faster iteration |
| Trailer video | Unreal | AAA graphics, cinematic tools |
| 3D city expansion | Unreal | Better 3D workflow |
| Rapid prototyping | Godot | Lighter, faster compile |
| Learning Blueprints | Unreal | Industry-standard skill |

---

## Estimated Timeline

- **Week 1:** Basic UI and game state in Blueprints
- **Week 2:** All actions functional, Data Tables set up
- **Week 3:** 3D city scene, cinematic camera
- **Week 4:** Polish, record trailer, package build

---

## Blueprint Tips for Python Developers

| Python Concept | Unreal Blueprint Equivalent |
|----------------|------------------------------|
| `if x > 5:` | **Branch** node (condition → True/False) |
| `for item in list:` | **ForEachLoop** node |
| `print(x)` | **Print String** node |
| `self.variable` | **Get** variable node |
| `return value` | **Return Node** (with output pin) |

---

## Resources

- **Unreal Docs:** https://docs.unrealengine.com/
- **Blueprint Tutorial:** https://www.youtube.com/unrealengine
- **UMG UI Guide:** https://docs.unrealengine.com/en-US/umg-ui-designer/
- **Data Tables:** https://docs.unrealengine.com/en-US/data-driven-gameplay/

---

## Final Recommendation

**Start with Godot for the game, use Unreal for a showcase trailer.**

Godot gets you to market faster. Unreal makes your portfolio stand out.
