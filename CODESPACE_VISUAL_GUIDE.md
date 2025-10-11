# Codespace File Visibility - Visual Guide

## The Problem: Why Can't I See My Files?

### What You're Seeing (Current Branch)
```
📁 datasets/
├── 📄 README.md
└── 📁 .github/
    └── 📁 instructions/
```
**Only 2-3 files visible!** 😟

### What You Should See (Main Branch)
```
📁 datasets/
├── 📄 README.md
├── 📄 pyproject.toml
├── 📄 Dockerfile
├── 📄 catalog.yaml
├── 📁 .github/
│   ├── 📁 workflows/     (10+ CI/CD files)
│   └── 📁 instructions/
├── 📁 src/
│   └── 📁 agentic_datasets/
│       ├── 📄 cli.py
│       ├── 📄 pipeline.py
│       ├── 📁 schemas/
│       ├── 📁 stages/
│       ├── 📁 transforms/
│       └── ... (30+ files)
├── 📁 tests/            (20+ test files)
├── 📁 examples/         (Example configs)
├── 📁 docs/            (Documentation)
└── ... (100+ total files)
```
**Full project structure!** 🎉

---

## VS Code Interface Overview

```
┌─────────────────────────────────────────────────────────────┐
│  VS Code in Browser (GitHub Codespace)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──┬──────────────────────────────────────────────────┐   │
│  │  │  README.md                                       │   │
│  │A │                                                  │   │
│  │c │  # datasets                                      │   │
│  │t │  A project to help you...                        │   │
│  │i │                                                  │   │
│  │v │                                                  │   │
│  │i │                                                  │   │
│  │t │  Editor Area (Your Code Here)                   │   │
│  │y │                                                  │   │
│  │  │                                                  │   │
│  │B │                                                  │   │
│  │a │                                                  │   │
│  │r │                                                  │   │
│  └──┴──────────────────────────────────────────────────┘   │
│      ┌──────────────────────────────────────────────┐       │
│      │  TERMINAL                                    │       │
│      │  $ pwd                                       │       │
│      │  /workspaces/datasets                        │       │
│      │  $ git branch                                │       │
│      │  * copilot/fix-codespace-file-visibility    │       │
│      │  $ git checkout main                         │       │
│      └──────────────────────────────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Activity Bar Icons (Left Side):
📁 Explorer    - File tree (Ctrl+Shift+E)
🔍 Search      - Search files (Ctrl+Shift+F)
🌿 Git         - Source control (Ctrl+Shift+G)
▶️ Debug       - Run and debug
🧩 Extensions  - VS Code extensions
```

### Key Areas Explained:

1. **Activity Bar (Left)**: The thin vertical bar with icons
   - Click 📁 to show/hide file tree
   - Click 🌿 for git operations

2. **Explorer Panel**: Shows your file tree
   - If hidden: Click 📁 or press `Ctrl+Shift+E`
   - Might be collapsed - look for a thin bar

3. **Editor Area**: Where you edit files
   - Multiple tabs for different files
   - Can split into multiple panes

4. **Terminal Panel (Bottom)**: Command line interface
   - If hidden: Press `Ctrl+` ` (backtick)
   - This is where you run git commands

---

## Step-by-Step: Fixing the Issue

### Step 1: Open Terminal
```
┌─────────────────────┐
│ Look at bottom of   │
│ screen for:         │
│                     │
│ TERMINAL  ▼        │
└─────────────────────┘

If not visible:
- Press: Ctrl+` (backtick)
- Or: Menu → View → Terminal
```

### Step 2: Check Your Branch
```bash
$ git branch
* copilot/fix-codespace-file-visibility  # ← You're here (minimal files)
  main                                    # ← Need to go here (all files)
```

### Step 3: Switch to Main
```bash
$ git checkout main
Switched to branch 'main'
Your branch is up to date with 'origin/main'.

$ ls -la
# Now you'll see 100+ files!
```

### Step 4: Refresh File Explorer
```
Click the 📁 Explorer icon or press Ctrl+Shift+E

You should now see:
📁 datasets/
├── src/          ← New!
├── tests/        ← New!
├── examples/     ← New!
├── docs/         ← New!
└── ... (many more)
```

---

## Common Issues - Visual Guide

### Issue 1: Explorer Panel Hidden

**What you see:**
```
┌──┐
│📁│ ← Click this!
│🔍│
│🌿│
│▶️│
└──┘
(No file list visible)
```

**Solution:** Click 📁 icon or press `Ctrl+Shift+E`

---

### Issue 2: Explorer Panel Collapsed

**What you see:**
```
┌──┬─┐
│📁│E│ ← Very thin panel
│🔍│x│
│🌿│p│
│▶️│l│
└──┴─┘
```

**Solution:** Drag the edge to widen it

---

### Issue 3: Wrong Branch (Most Common!)

**What you see in Explorer:**
```
📁 datasets
├── 📄 README.md
└── 📁 .github
    └── 📁 instructions

Where's everything else?! 🤔
```

**Solution:** 
```bash
# In terminal:
git checkout main

# Now you see:
📁 datasets
├── 📄 README.md
├── 📁 src/           ← Appears!
├── 📁 tests/         ← Appears!
├── 📁 examples/      ← Appears!
└── ... (more)
```

---

## Branch Comparison Visual

### Branch: `copilot/fix-codespace-file-visibility` (Current)
```
datasets/
├── README.md                    ✓ (3 files only)
└── .github/instructions/

Status: 📊 Minimal branch for documentation work
```

### Branch: `main` (Target)
```
datasets/
├── README.md                    ✓
├── pyproject.toml              ✓
├── Dockerfile                  ✓
├── src/agentic_datasets/       ✓ (30+ files)
│   ├── cli.py
│   ├── pipeline.py
│   ├── schemas/
│   ├── stages/
│   └── transforms/
├── tests/                      ✓ (20+ files)
├── examples/                   ✓ (configs)
├── .github/workflows/          ✓ (10+ CI files)
└── docs/                       ✓

Status: 🎯 Full project with all source code
```

**To switch:** `git checkout main`

---

## Quick Command Reference with Visual Feedback

### Command: `git branch`
```
$ git branch
* copilot/fix-codespace-file-visibility  ← * means "you are here"
  main
  
Legend:
* = Current branch
```

### Command: `git checkout main`
```
$ git checkout main
Switched to branch 'main'
Your branch is up to date with 'origin/main'.

$ git branch
  copilot/fix-codespace-file-visibility
* main                                    ← * moved here!
```

### Command: `ls -la`
```bash
# Before (on feature branch):
$ ls -la
drwxr-xr-x  .git/
drwxr-xr-x  .github/
-rw-r--r--  README.md
# Total: 3 items

# After (on main branch):
$ ls -la
drwxr-xr-x  .git/
drwxr-xr-x  .github/
drwxr-xr-x  src/             ← New!
drwxr-xr-x  tests/           ← New!
drwxr-xr-x  examples/        ← New!
drwxr-xr-x  docs/            ← New!
-rw-r--r--  README.md
-rw-r--r--  pyproject.toml   ← New!
-rw-r--r--  Dockerfile       ← New!
-rw-r--r--  catalog.yaml     ← New!
# Total: 100+ items
```

---

## Verification Checklist

After running `git checkout main`, verify you can see:

- [ ] `src/` directory with agentic_datasets package
- [ ] `tests/` directory with test files
- [ ] `examples/` directory with YAML configs
- [ ] `pyproject.toml` file
- [ ] `Dockerfile`
- [ ] `.github/workflows/` with CI files

**If you see all these ✓ - Success!** You're now on the right branch with all files visible.

---

## Still Having Issues?

### Try This Checklist:

1. **Terminal visible?**
   - Press `Ctrl+` `

2. **On main branch?**
   - Run: `git checkout main`

3. **Explorer visible?**
   - Press `Ctrl+Shift+E`

4. **Files still not showing?**
   - Reload window: `Ctrl+R` or `F1` → "Reload Window"

5. **Codespace in safe mode?**
   - Look for banner at top
   - Click "Trust" to enable full features

---

## For More Help

- **Quick Reference**: See `CODESPACE_QUICKSTART.md`
- **Complete Guide**: See `CODESPACE_GUIDE.md`
- **Repository Docs**: See `README.md`

**Remember:** The most common issue is being on the wrong branch!
```bash
git checkout main  # ← This fixes 90% of "can't see files" issues
```
