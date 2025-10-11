# GitHub Codespaces Guide: Viewing Your Repository Files

## Quick Answer

If you opened a Codespace and don't see your repository files, here's what to check:

### 1. **File Explorer in VS Code**
The file explorer should be visible on the left side of your browser-based IDE:
- Look for the **Explorer icon** (📁) in the left sidebar (Activity Bar)
- Click it to show/hide the file tree
- Keyboard shortcut: `Ctrl+Shift+E` (Windows/Linux) or `Cmd+Shift+E` (Mac)

### 2. **Check Your Current Branch**
You might be on a branch with minimal files. To check and switch branches:

```bash
# See which branch you're on
git branch

# List all available branches
git branch -a

# Switch to main branch to see all files
git checkout main
```

### 3. **Verify Repository Contents**
Run these commands in the integrated terminal (`Ctrl+` ` or `Cmd+` `) to see what files exist:

```bash
# List files in current directory
ls -la

# Show directory tree structure
tree -L 2 || find . -maxdepth 2 -type d

# List all files tracked by git
git ls-tree -r HEAD --name-only
```

## Understanding Your Current Situation

Based on your repository context, you're currently on branch `copilot/fix-codespace-file-visibility` which appears to have minimal files. The main branch (`origin/main`) contains the full project with:

- `src/agentic_datasets/` - Core package code
- `tests/` - Test suite
- `examples/` - Example configurations
- `docs/` - Documentation
- `.github/workflows/` - CI/CD workflows
- `pyproject.toml` - Project configuration
- And many more files...

## Step-by-Step: How to Access All Your Files

### Option 1: Switch to Main Branch (Recommended)

```bash
# Switch to main branch
git checkout main

# Verify you can see the files
ls -la
```

After switching to main, refresh the File Explorer in VS Code, and you should see all your repository files.

### Option 2: Merge Main into Your Current Branch

If you want to keep your current branch but get all the files:

```bash
# Fetch latest changes
git fetch origin

# Merge main branch into your current branch
git merge origin/main

# Or rebase your branch on top of main
git rebase origin/main
```

### Option 3: Create a New Branch from Main

```bash
# Switch to main first
git checkout main

# Create and switch to a new branch
git checkout -b my-feature-branch

# Push the new branch
git push -u origin my-feature-branch
```

## Common Codespace Issues and Solutions

### Issue: "I don't see the sidebar with files"

**Solution:**
1. Click the Explorer icon (📁) in the Activity Bar (leftmost vertical bar)
2. Or press `Ctrl+Shift+E` (Windows/Linux) or `Cmd+Shift+E` (Mac)
3. If the Activity Bar is hidden, press `Ctrl+B` or `Cmd+B` to toggle the sidebar

### Issue: "Terminal is not showing"

**Solution:**
1. Press `Ctrl+` ` (backtick) or `Cmd+` ` to toggle terminal
2. Or go to: View → Terminal
3. Or use menu: Terminal → New Terminal

### Issue: "I see only a few files but my repo has many"

**Solution:**
- You're likely on a branch with limited content
- Switch to `main` branch: `git checkout main`
- Check the branch: `git branch`
- List remote branches: `git branch -r`

### Issue: "Files appear but are grayed out or not loading"

**Solution:**
1. Check if you have internet connectivity
2. Reload the window: `Ctrl+R` or `Cmd+R`
3. Or: Press `F1` → type "Reload Window" → press Enter

### Issue: "Codespace is in safe mode or restricted"

**Solution:**
- GitHub may have loaded the Codespace in restricted mode
- Look for a banner at the top saying "Restricted Mode"
- Click "Trust" or "Manage" to allow full access

## Navigating the VS Code Interface in Codespaces

### Activity Bar (Left Side)
- **Explorer** (📁): Browse files and folders
- **Search** (🔍): Search across files
- **Source Control** (Git icon): Git operations
- **Run and Debug** (▶️): Debug tools
- **Extensions** (blocks icon): VS Code extensions

### Key Shortcuts
- `Ctrl+P` / `Cmd+P`: Quick file open
- `Ctrl+Shift+F` / `Cmd+Shift+F`: Search in files
- `Ctrl+` ` / `Cmd+` `: Toggle terminal
- `Ctrl+B` / `Cmd+B`: Toggle sidebar
- `Ctrl+Shift+E` / `Cmd+Shift+E`: Focus on Explorer

### Using the Integrated Terminal

The terminal at the bottom is a full Bash shell where you can:
- Run git commands
- Execute CLI tools
- Build and test your code
- Install dependencies

```bash
# Example commands
pwd                    # Show current directory
ls -la                 # List all files
git status            # Check git status
python --version      # Check Python version
pip install -e .      # Install package in dev mode
```

## Your Repository Structure

Once you're on the main branch, you should see this structure:

```
datasets/
├── .devcontainer/          # Codespace configuration
├── .github/
│   ├── workflows/          # CI/CD pipelines
│   └── instructions/       # Agent instructions
├── src/
│   └── agentic_datasets/   # Main package code
│       ├── cli.py          # CLI commands
│       ├── pipeline.py     # Core pipeline
│       ├── schemas/        # Data models
│       ├── stages/         # Pipeline stages
│       ├── transforms/     # Data transformations
│       └── ...
├── tests/                  # Test suite
├── examples/               # Example configs
├── docs/                   # Documentation
├── pyproject.toml          # Project config
├── README.md              # Main documentation
└── ...
```

## Working with the Repository

### Installing Dependencies

```bash
# Create and activate virtual environment (optional in Codespaces)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[dev]
```

### Running CLI Commands

```bash
# List available commands
agentic-datasets --help

# Run a pipeline
agentic-datasets run-config examples/pipeline.example.yaml

# List transforms
agentic-datasets transforms

# View catalog
agentic-datasets catalog:list
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/agentic_datasets

# Run specific test file
pytest tests/test_pipeline.py
```

## Verifying Your Setup

Run these commands to verify everything is working:

```bash
# 1. Check you're in the right directory
pwd
# Should show: /workspaces/datasets or similar

# 2. Check your branch
git branch
# Should show: * main (or your feature branch)

# 3. List files
ls -la
# Should show many files: src/, tests/, examples/, etc.

# 4. Check Python
python --version
# Should show: Python 3.11 or similar

# 5. Check if package is installed
pip show agentic-datasets
# Should show package info if installed
```

## Need More Help?

### Repository Documentation
- **README.md** - Main project documentation
- **README_AGENTIC.md** - Agentic CLI reference
- **IMPLEMENTATION_STATUS.md** - Current implementation status
- **MIGRATION_PLAN.md** - Technical architecture
- **PROJECT_STATUS.md** - Project status and roadmap

### Useful Commands
```bash
# View a file
cat README.md

# View with pagination
less README.md
# (Press 'q' to quit)

# Search for text in files
grep -r "search term" src/

# Find files by name
find . -name "*.py" | grep pipeline
```

### Getting Back to Main Branch

If you're ever lost or on the wrong branch:

```bash
# Discard any local changes (be careful!)
git reset --hard

# Switch to main
git checkout main

# Update from remote
git pull origin main

# List files to confirm
ls -la
```

## Summary

**The most common reason for not seeing files in Codespaces is being on a branch with limited content.**

**Quick fix:**
1. Open the terminal (`Ctrl+` `)
2. Run: `git checkout main`
3. Refresh the Explorer view (`Ctrl+Shift+E`)
4. You should now see all repository files

If you still have issues, check the Activity Bar on the left side of VS Code to ensure the Explorer panel is visible.
