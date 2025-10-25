# BRONZE: 1177 BC - Multi-Platform Roadmap

Strategy for bringing BRONZE to Godot, Unreal, Web, and Mobile.

---

## Current State

- ✅ **Python CLI version** - Fully functional v1.2.6
- ✅ Core game loop validated
- ✅ Two win conditions tested (Preservation & Vacuum paths)
- ✅ Turn-based mechanics proven

---

## Platform Targets

### 1. **Godot 4** (Primary Target)

**Why Godot:**
- Perfect fit for turn-based strategy
- Exports to: Windows, Mac, Linux, Web, iOS, Android
- Free, no royalties, open-source
- GDScript is Python-like (easy port from current code)
- Excellent 2D UI system

**Implementation Plan:**
- Port game logic to GDScript
- Build UI with Control nodes (panels, labels, buttons)
- Add visual polish: Bronze Age art assets, animated borders
- Implement save/load system
- **Timeline:** 2-3 weeks for MVP

**Export Targets from Godot:**
- Desktop: Windows, Mac, Linux (native executables)
- Web: HTML5 via WebAssembly (playable in browser)
- Mobile: iOS and Android (with touch-optimized UI)

---

### 2. **Unreal Engine 5** (Stretch Goal)

**Why Unreal:**
- AAA visual quality
- Blueprint visual scripting (no C++ needed initially)
- Potential for future 3D expansion
- Asset marketplace for quick prototyping

**Considerations:**
- Heavier engine for a text-based game
- 5% royalty after $1M revenue
- Longer iteration time
- Best saved for visual showcase/trailer build

**Implementation Plan:**
- Widget Blueprint for UI (UMG)
- GameMode Blueprint for turn logic
- Data Tables for buildings, techs, events
- **Timeline:** 4-6 weeks for MVP

**Use Case:**
- Create a "cinematic" version for marketing
- 3D Bronze Age city visualization
- Portfolio piece to show engine versatility

---

### 3. **Web/Browser (HTML5)**

**Primary Method: Godot HTML5 Export**
- Godot exports directly to WebAssembly
- Playable in any modern browser
- Host on: Itch.io, GitHub Pages, personal site

**Alternative: Pygame to Web (PyScript)**
- Experimental: Run Python in browser via PyScript
- Slower, less reliable
- **Not recommended** - use Godot instead

**Features for Web:**
- Auto-save to browser localStorage
- Responsive design (desktop & tablet)
- Fast load times (<5 MB total)
- No install required

---

### 4. **Mobile (iOS & Android)**

**Via Godot Export:**
- Touch-optimized UI (larger buttons, swipe gestures)
- Portrait orientation for phone play
- Landscape for tablet
- Cloud save integration (Google Play, Game Center)

**UX Changes for Mobile:**
- Simplified menus (no nested sub-menus)
- Gesture controls (swipe between panels)
- Larger fonts for readability
- Reduced particle effects (battery/performance)

**Monetization Options (Future):**
- Free with ads (AdMob integration)
- Premium unlock ($2.99 - removes ads, bonus scenarios)
- Cosmetic DLC (alternate art styles)

---

## Recommended Development Order

### Phase 1: **Godot Desktop Build** (Weeks 1-3)
1. Port Python logic to GDScript
2. Build basic UI (Control nodes, scene tree)
3. Test all game mechanics (two win paths)
4. Add placeholder art (colored panels)

### Phase 2: **Polish & Assets** (Weeks 4-5)
5. Commission/create Bronze Age art
6. Add sound effects (UI clicks, event chimes)
7. Implement save/load
8. Write in-game tutorial

### Phase 3: **Web Export** (Week 6)
9. Export to HTML5
10. Optimize for web (compress assets, lazy loading)
11. Test on Itch.io
12. Add analytics (optional - track playthroughs)

### Phase 4: **Mobile Port** (Weeks 7-9)
13. Redesign UI for touch
14. Test on iOS and Android devices
15. Submit to App Store / Play Store
16. Add cloud saves

### Phase 5: **Unreal Showcase** (Weeks 10-14, optional)
17. Create 3D city visualization
18. Record cinematic trailer
19. Use for marketing / portfolio

---

## File Structure for Godot Port

```
bronze_1177bc_godot/
├── project.godot
├── scenes/
│   ├── main_menu.tscn
│   ├── game_board.tscn
│   ├── hud.tscn
│   └── victory_screen.tscn
├── scripts/
│   ├── game_state.gd         # Core game logic (resources, stability, etc.)
│   ├── turn_manager.gd       # Turn progression, event system
│   ├── action_handler.gd     # Player actions (Harvest, Build, etc.)
│   └── ui_controller.gd      # UI updates, button handling
├── data/
│   ├── buildings.json        # Building definitions
│   ├── technologies.json     # Tech tree
│   └── events.json           # Random events
└── assets/
    ├── art/                  # Sprites, backgrounds
    ├── fonts/                # Custom fonts
    └── audio/                # SFX, music
```

---

## Asset Needs

### Art
- Background: Bronze Age palace/city vista
- Icons: Grain, Timber, Bronze, Military, Stability, Prestige
- Building portraits (6 buildings)
- Event illustrations (optional - 8-10 events)

### Audio
- Menu click/hover SFX
- Action confirmation sounds
- Crisis warning chime
- Victory/defeat stings
- Ambient music (optional - lyre/flute instrumental)

### Fonts
- Ancient-themed display font (titles)
- Clean sans-serif for body text (readability)

---

## Technical Milestones

| Milestone | Platform | Status | Target Date |
|-----------|----------|--------|-------------|
| Python CLI v1.2.6 | Terminal | ✅ Complete | Oct 25, 2025 |
| Godot MVP | Desktop | 📋 Planned | Nov 15, 2025 |
| Godot Web Export | Browser | 📋 Planned | Nov 22, 2025 |
| Godot Mobile | iOS/Android | 📋 Planned | Dec 15, 2025 |
| Unreal Showcase | Desktop | 🎯 Stretch | Jan 2026 |

---

## Next Steps

1. **Set up Godot project structure**
2. **Port core game logic** to GDScript (start with GameState class)
3. **Build basic UI** (single scene with all panels)
4. **Playtest** - ensure parity with Python version
5. **Export to Web** - publish on Itch.io for early feedback

---

## Platform Comparison Summary

| Feature | Godot | Unreal | Python CLI |
|---------|-------|--------|------------|
| Development Speed | ⚡⚡⚡ | ⚡ | ⚡⚡⚡⚡ |
| Visual Quality | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Multi-Platform | ✅ All | ✅ All | ❌ Desktop only |
| Learning Curve | Easy | Moderate | N/A |
| File Size | ~20 MB | ~100+ MB | <1 MB |
| Best For | Production | Showcase | Prototyping |

---

**Recommendation:** Start with **Godot** for production release (desktop + web + mobile). Use **Unreal** for a cinematic trailer or future 3D expansion.
