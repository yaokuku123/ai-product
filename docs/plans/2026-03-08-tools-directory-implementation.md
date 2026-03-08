# Tools Directory Structure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a unified root tools directory and migrate the bilibili_downloader tool from deepsearch-fire directory while preserving full git history and functionality.

**Architecture:** Flat structure where each independent tool resides in its own top-level directory under /tools/, with fully independent dependencies and no shared configuration.

**Tech Stack:** Git, Python

---

### Task 1: Create root tools directory
**Files:**
- Create: `/tools/`

**Step 1: Create the directory**
Run: `mkdir -p tools`
Expected: Empty directory created at project root

**Step 2: Verify directory exists**
Run: `ls -la | grep tools`
Expected: Shows the tools directory with correct permissions

---

### Task 2: Move bilibili_downloader with git mv to preserve history
**Files:**
- Move: `deepsearch-fire/bilibili_downloader/` → `tools/bilibili_downloader/`

**Step 1: Execute git mv command**
Run: `git mv deepsearch-fire/bilibili_downloader tools/`
Expected: No errors, files are moved with git tracking preserved

**Step 2: Verify the move**
Run: `ls tools/bilibili_downloader/`
Expected: Shows all existing files: cli.py, core.py, etc.

Run: `git status`
Expected: Shows "renamed: deepsearch-fire/bilibili_downloader/... -> tools/bilibili_downloader/..."

---

### Task 3: Verify git history is preserved for moved files
**Files:**
- Check: `tools/bilibili_downloader/core.py`

**Step 1: Check git log for moved file**
Run: `git log --oneline -- tools/bilibili_downloader/core.py`
Expected: Shows the full commit history for the file, same as before the move

---

### Task 4: Test bilibili_downloader still works correctly after move
**Files:**
- Test: `tools/bilibili_downloader/`

**Step 1: Navigate to the tool directory and check dependencies**
Run: `cd tools/bilibili_downloader && ls -la pyproject.toml`
Expected: pyproject.toml exists with all required dependencies

**Step 2: Verify CLI runs without import errors**
Run: `cd tools/bilibili_downloader && python cli.py --help`
Expected: Shows help output without any import errors or missing module issues

---

### Task 5: Update any references to the old bilibili_downloader path
**Files:**
- Check: `deepsearch-fire/pyproject.toml`, `deepsearch-fire/README.md`

**Step 1: Search for references to old path**
Run: `grep -r "bilibili_downloader" deepsearch-fire/ --include="*.py" --include="*.md" --include="*.toml"`
Expected: If any references are found, update them to point to the new path `/tools/bilibili_downloader/`

---

### Task 6: Commit the changes
**Step 1: Stage all changes**
Run: `git add .`

**Step 2: Create commit**
Run: `git commit -m "feat: move bilibili_downloader to unified tools directory

Moved from deepsearch-fire/bilibili_downloader to tools/bilibili_downloader
Full git history preserved

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"`

**Step 3: Verify commit**
Run: `git log --oneline -1`
Expected: Shows the new commit
