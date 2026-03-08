# Tools Directory Structure Design
Date: 2026-03-08

## Overview
This design establishes a unified directory for independent tools in the ai-product project, to organize scattered utilities and make them easier to find and maintain.

## Design Decisions
1. **Root tools directory**: Created at `/tools/` as the home for all independent utilities
2. **Structure**: Flat structure where each tool has its own top-level directory under `/tools/`
3. **Dependency handling**: Each tool maintains fully independent dependencies (own requirements.txt/pyproject.toml)
4. **Git history**: Preserve full git history when moving existing tools using `git mv`

## Migration Plan
- First migration: Move `deepsearch-fire/bilibili_downloader/` to `tools/bilibili_downloader/`
- No changes to existing main project directories (`baicizhan-mvp/`, `deepsearch-fire/`, `remote_computer_use/`)

## Future Standards
All new independent tools should be added to the `/tools/` directory with their own self-contained structure.
