# Codespace Quick Reference

## 🚀 Can't See Your Files? Start Here!

### Most Common Issue: Wrong Branch
```bash
# Check current branch
git branch

# Switch to main to see all files
git checkout main

# Refresh Explorer: Ctrl+Shift+E (or Cmd+Shift+E on Mac)
```

---

## 📁 File Explorer

**Show/Hide Explorer:**
- Click 📁 icon in left sidebar
- Or: `Ctrl+Shift+E` (Windows/Linux)
- Or: `Cmd+Shift+E` (Mac)

---

## ⌨️ Essential Shortcuts

| Action | Windows/Linux | Mac |
|--------|--------------|-----|
| Quick Open File | `Ctrl+P` | `Cmd+P` |
| Toggle Terminal | `Ctrl+` ` | `Cmd+` ` |
| Toggle Sidebar | `Ctrl+B` | `Cmd+B` |
| File Explorer | `Ctrl+Shift+E` | `Cmd+Shift+E` |
| Search Files | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| Command Palette | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| Git Panel | `Ctrl+Shift+G` | `Cmd+Shift+G` |

---

## 🔍 Quick Commands

```bash
# Where am I?
pwd

# What files are here?
ls -la

# What branch am I on?
git branch

# Switch to main branch
git checkout main

# Show directory tree
tree -L 2 || find . -maxdepth 2 -type d

# Git status
git status
```

---

## 🛠️ Development Commands

```bash
# Install dependencies
pip install -e .[dev]

# Run CLI
agentic-datasets --help

# Run tests
pytest

# Run pipeline
agentic-datasets run-config examples/pipeline.example.yaml
```

---

## 🆘 Troubleshooting

### No files visible?
1. Check branch: `git branch`
2. Switch to main: `git checkout main`
3. Show Explorer: `Ctrl+Shift+E`

### Terminal not showing?
- Press `Ctrl+` ` (backtick)
- Or: View → Terminal

### Sidebar hidden?
- Press `Ctrl+B` (Windows/Linux)
- Or: `Cmd+B` (Mac)

### Need to reload?
- Press `Ctrl+R` (Windows/Linux)
- Or: `Cmd+R` (Mac)
- Or: `F1` → "Reload Window"

---

## 📚 Full Documentation

See **CODESPACE_GUIDE.md** for comprehensive instructions.

---

## 💡 Pro Tips

1. **Quick file open**: `Ctrl+P` then start typing filename
2. **Command palette**: `Ctrl+Shift+P` for all VS Code commands
3. **Git operations**: Use Source Control panel (Git icon in Activity Bar)
4. **Multiple terminals**: Click `+` in terminal panel
5. **Split editor**: `Ctrl+\` to split view

---

## 🎯 Your Repository on Main Branch

```
datasets/
├── src/agentic_datasets/    # Core code
├── tests/                   # Tests
├── examples/                # Example configs
├── .github/workflows/       # CI/CD
├── pyproject.toml          # Config
└── README.md               # Docs
```

**To see this structure:**
```bash
git checkout main
ls -la
```
