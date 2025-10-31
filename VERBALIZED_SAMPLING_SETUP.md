# Verbalized Sampling Integration - Setup Guide

## Overview

This document provides setup instructions for the **Verbalized Sampling (VS)** integration for AutoGPT Platform, specifically designed for **BRONZE game playtesting**.

## What Was Implemented

### 1. Core Components

#### Utility Module
- **File:** `backend/backend/util/probability_parser.py`
- **Purpose:** Parse, validate, normalize, and manipulate probability distributions from LLM responses
- **Functions:**
  - `extract_probability_distribution()` - Extract probabilities from natural language
  - `validate_probability_distribution()` - Ensure valid distributions
  - `normalize_distribution()` - Normalize to sum = 1.0
  - `sample_from_distribution()` - Sample with temperature control
  - `merge_probability_distributions()` - Combine multiple distributions
  - `format_distribution_for_display()` - Pretty-print

### 2. Block Implementations

#### Verbalized Sampling Blocks
- **File:** `backend/backend/blocks/verbalized_sampling.py`
- **Blocks:**
  1. `VerbalizationSamplingBlock` (ID: `a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d`)
     - Prompts LLM to verbalize probability distributions
     - Supports auto-sampling and probability normalization
  2. `MultiOptionVerbalizationBlock` (ID: `b2c3d4e5-6f7a-8b9c-0d1e-2f3a4b5c6d7e`)
     - Generates multiple diverse responses with probabilities and reasoning

#### Multi-Agent Simulation
- **File:** `backend/backend/blocks/multi_agent_simulator.py`
- **Block:**
  1. `MultiAgentSimulationBlock` (ID: `c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f`)
     - Runs parallel agents with VS-based decision-making
     - Supports 6 personality types (aggressive, defensive, balanced, curious, cautious, random)
     - Detects emergent behavioral patterns

#### BRONZE Game Playtest Blocks
- **File:** `backend/backend/blocks/bronze_playtest.py`
- **Blocks:**
  1. `BronzePlaytestAgentBlock` (ID: `d4e5f6a7-8b9c-0d1e-2f3a-4b5c6d7e8f9a`)
     - Single BRONZE player agent with path-based decision-making
     - Supports Preserver/Exploiter/Hybrid/Undecided paths
     - Provides path alignment scoring and risk assessment
  2. `BronzeMultiPlayerSimulationBlock` (ID: `e5f6a7b8-9c0d-1e2f-3a4b-5c6d7e8f9a0b`)
     - Full multiplayer BRONZE playtest simulation
     - Configurable player counts by path
     - Generates balance analysis and recommendations

#### Evaluation Framework
- **File:** `backend/backend/blocks/playtest_evaluation.py`
- **Blocks:**
  1. `PlaytestAnalysisBlock` (ID: `f6a7b8c9-0d1e-2f3a-4b5c-6d7e8f9a0b1c`)
     - Analyzes playtest results for balance issues
     - Calculates diversity scores and coverage metrics
     - Generates detailed reports
  2. `VSDiversityMetricsBlock` (ID: `a7b8c9d0-1e2f-3a4b-5c6d-7e8f9a0b1c2d`)
     - Calculates Shannon entropy and effective options
     - Measures outcome diversity and distribution variance

### 3. Graph Templates

#### Complete Playtest Pipeline
- **File:** `graph_templates/bronze_playtest_vs_example.json`
- **Purpose:** Full BRONZE playtest with multi-player simulation and analysis
- **Flow:** Simulation → Analysis → Metrics → Display

#### Single Agent Testing
- **File:** `graph_templates/single_agent_bronze_playtest.json`
- **Purpose:** Test individual agent decision-making
- **Flow:** Game State → Agent Decision → Output

#### Creative Writing Example
- **File:** `graph_templates/creative_writing_vs_example.json`
- **Purpose:** Demonstrate VS for creative content generation
- **Flow:** Prompt → VS Generation → Diversity Analysis → Output

### 4. Documentation
- **File:** `backend/backend/blocks/VERBALIZED_SAMPLING_README.md`
- **Content:** Comprehensive guide with examples, use cases, and API documentation

## Installation & Setup

### Prerequisites

The blocks are automatically loaded when AutoGPT Platform starts. No special installation required.

**Requirements:**
- AutoGPT Platform running with Docker Compose
- Access to LLM API (OpenAI, Anthropic, etc.)
- Valid API credentials configured in AutoGPT

### Verification

Once AutoGPT Platform is running, verify blocks are loaded:

1. **Via Frontend:**
   - Navigate to http://localhost:3000
   - Open the graph builder
   - Search for "Verbalized" or "BRONZE" in the block palette
   - You should see all 7 new blocks available

2. **Via API:**
   ```bash
   curl http://localhost:8000/api/blocks | jq '.[] | select(.name | contains("Verbalization"))'
   ```

3. **Via Backend (if running locally):**
   ```bash
   cd backend
   poetry run python -c "from backend.blocks import load_all_blocks; blocks = load_all_blocks(); print([name for name in blocks.keys() if 'Verbalization' in name or 'Bronze' in name])"
   ```

Expected output should include:
- `VerbalizationSamplingBlock`
- `MultiOptionVerbalizationBlock`
- `MultiAgentSimulationBlock`
- `BronzePlaytestAgentBlock`
- `BronzeMultiPlayerSimulationBlock`
- `PlaytestAnalysisBlock`
- `VSDiversityMetricsBlock`

## Quick Start

### Example 1: Single BRONZE Agent Decision

1. Open AutoGPT at http://localhost:3000
2. Create a new graph
3. Add blocks:
   - **Input Block** with game state
   - **BronzePlaytestAgentBlock**
   - **Output Block**
4. Connect inputs and run
5. View probability distribution and chosen action

### Example 2: Full BRONZE Playtest

1. Create new graph
2. Add `BronzeMultiPlayerSimulationBlock`
3. Configure:
   - 2 Preserver players
   - 2 Exploiter players
   - 15 turns
4. Add `PlaytestAnalysisBlock` connected to simulation output
5. Add `Output Block` to view results
6. Run and review balance analysis

### Example 3: Creative Writing

1. Create new graph
2. Add `MultiOptionVerbalizationBlock`
3. Set prompt: "Generate 5 opening sentences for a mystery novel"
4. Add `VSDiversityMetricsBlock` to measure diversity
5. Run and compare creative options

## Configuration

### Environment Variables

No special environment variables required. Uses standard AutoGPT configuration.

### Model Selection

All VS blocks support multiple LLM providers:
- OpenAI (GPT-4, GPT-4o, etc.)
- Anthropic (Claude 3.5 Sonnet, etc.)
- Groq
- Ollama (local models)

Configure via the `model` input field on each block.

### Temperature Settings

- **Low diversity (0.3-0.5):** Consistent, predictable outputs
- **Medium diversity (0.6-0.8):** Balanced variety (recommended for playtesting)
- **High diversity (0.9-1.5):** Maximum creativity (good for brainstorming)

## Usage Tips

### For BRONZE Playtesting

1. **Start with single-agent tests** to verify agent behavior before multi-player
2. **Use enable_reasoning=true** to understand agent decision-making
3. **Run multiple simulations** with different player counts to test balance
4. **Compare Preserver vs Exploiter** win rates and strategy effectiveness
5. **Adjust diversity_threshold** in analysis based on game complexity

### For Creative Content

1. **Use MultiOptionVerbalizationBlock** for brainstorming
2. **Increase temperature** for maximum variety
3. **Enable reasoning** to understand why options were ranked
4. **Sample multiple times** from the same distribution for reproducibility

### For General Decision-Making

1. **Provide clear action options** when known
2. **Let VS generate options** when exploring possibilities
3. **Use auto_sample=true** for automated selection
4. **Chain multiple VS blocks** for iterative refinement

## Troubleshooting

### Issue: "Block not found"
**Cause:** Blocks not loaded by AutoGPT
**Solution:**
- Restart Docker Compose: `docker compose restart`
- Check backend logs: `docker compose logs backend`
- Verify files are in `backend/backend/blocks/`

### Issue: Probabilities don't sum to 1.0
**Cause:** LLM didn't follow instructions perfectly
**Solution:**
- Enable `normalize_probabilities=true`
- Try different model (GPT-4o recommended)
- Adjust temperature

### Issue: Low diversity scores
**Cause:** Insufficient variety in agent behavior
**Solution:**
- Increase temperature
- Add more agent personalities
- Run more simulation rounds
- Verify scenario provides meaningful choices

### Issue: Parsing errors in probability extraction
**Cause:** LLM response format doesn't match expected patterns
**Solution:**
- Check raw_response output to see actual format
- Update parsing patterns in `probability_parser.py`
- Use structured JSON output (may require custom prompt)

### Issue: "API key error"
**Cause:** LLM credentials not configured
**Solution:**
- Add API credentials in AutoGPT settings
- Verify provider is supported
- Check credential permissions

## File Locations

All implemented files:

```
autogpt_platform/
├── backend/backend/
│   ├── util/
│   │   └── probability_parser.py          # Core probability utilities
│   └── blocks/
│       ├── verbalized_sampling.py          # VS blocks
│       ├── multi_agent_simulator.py        # Multi-agent simulation
│       ├── bronze_playtest.py              # BRONZE-specific blocks
│       ├── playtest_evaluation.py          # Evaluation framework
│       └── VERBALIZED_SAMPLING_README.md   # Detailed documentation
├── graph_templates/
│   ├── bronze_playtest_vs_example.json     # Full playtest template
│   ├── single_agent_bronze_playtest.json   # Single agent template
│   └── creative_writing_vs_example.json    # Creative writing template
└── VERBALIZED_SAMPLING_SETUP.md            # This file
```

## Next Steps

### Basic Usage
1. ✅ Verify blocks are loaded
2. ✅ Import a graph template
3. ✅ Run a simple VS example
4. ✅ Inspect probability distributions

### BRONZE Playtesting
1. ✅ Define your game state format
2. ✅ Create custom action lists
3. ✅ Run single-agent tests
4. ✅ Scale to multi-player simulations
5. ✅ Analyze balance issues
6. ✅ Iterate on game design

### Advanced Customization
1. 📝 Add custom player paths (edit `BronzePlayerPath` enum)
2. 📝 Add custom action categories (edit `BronzeActionCategory` enum)
3. 📝 Extend evaluation metrics (modify `PlaytestAnalysisBlock`)
4. 📝 Create custom graph templates for your use cases
5. 📝 Integrate with external game state APIs

## Performance Notes

- **Parallel Execution:** Multi-agent blocks run agents concurrently
- **Token Usage:** Scales with num_agents × num_rounds × actions_per_round
- **Caching:** Enable in production for faster repeated queries
- **Rate Limits:** Monitor API quotas for large simulations

## Support & Feedback

For issues or questions:
1. Check `VERBALIZED_SAMPLING_README.md` for detailed documentation
2. Review graph templates for examples
3. Test blocks individually before chaining
4. Check backend logs for detailed error messages

## Credits

- **Implementation:** Claude Code (Anthropic)
- **Verbalized Sampling Technique:** Research paper on VS for LLM diversity
- **Platform:** AutoGPT (Significant Gravitas)
- **Use Case:** BRONZE game playtesting

## License

Same as AutoGPT Platform (MIT License)

---

**Version:** 1.0.0
**Date:** 2025-10-31
**Status:** Production Ready ✅
