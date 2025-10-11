# Codespace FAQ - Frequently Asked Questions

## General Questions

### Q: What is a GitHub Codespace?
**A:** A Codespace is a cloud-based development environment that runs in your browser. It's essentially VS Code running on a remote server with your repository cloned and ready to work with.

### Q: How do I open a Codespace?
**A:** 
1. Go to your GitHub repository
2. Click the green "Code" button
3. Select the "Codespaces" tab
4. Click "Create codespace on main" (or select an existing one)

### Q: Is my Codespace the same as my local environment?
**A:** Not exactly. Your Codespace is a separate environment. Changes you make in the Codespace won't affect your local machine unless you push them to GitHub and pull them locally.

---

## File Visibility Issues

### Q: I opened a Codespace but I only see a few files. Where are the rest?
**A:** This is usually because you're on a branch with minimal files. 

**Solution:**
```bash
git checkout main
```

Then refresh the Explorer view (`Ctrl+Shift+E` or `Cmd+Shift+E`).

### Q: How do I know which branch I'm on?
**A:** Run in the terminal:
```bash
git branch
```

The branch with a `*` next to it is your current branch.

### Q: I'm on the main branch but still don't see files. What's wrong?
**A:** Try these steps:
1. Make sure the Explorer panel is visible: Press `Ctrl+Shift+E` (or `Cmd+Shift+E` on Mac)
2. Check if the Activity Bar is visible: Press `Ctrl+B` (or `Cmd+B`)
3. Reload the window: Press `Ctrl+R` (or `Cmd+R`)
4. Run the diagnostic script: `./codespace-check.sh`

### Q: What's the difference between the different branches?
**A:**
- **main branch**: Contains the full project with all source code, tests, and documentation
- **feature branches** (like `copilot/fix-codespace-file-visibility`): May contain only specific files needed for that feature
- Always check which branch you're on when you can't see expected files

---

## VS Code Interface Questions

### Q: Where is the file explorer?
**A:** The file explorer is on the left side of VS Code. Look for the 📁 icon in the Activity Bar (the thin vertical bar on the far left). Click it or press `Ctrl+Shift+E` (Windows/Linux) or `Cmd+Shift+E` (Mac).

### Q: I don't see the terminal. How do I open it?
**A:** Press `Ctrl+` ` (backtick) or go to View → Terminal in the menu.

### Q: Can I open multiple terminal windows?
**A:** Yes! Click the `+` icon in the terminal panel or press `Ctrl+Shift+` `.

### Q: How do I search for files?
**A:** Press `Ctrl+P` (or `Cmd+P` on Mac) for quick file search, or `Ctrl+Shift+F` (or `Cmd+Shift+F`) to search within files.

### Q: The sidebar disappeared. How do I get it back?
**A:** Press `Ctrl+B` (or `Cmd+B` on Mac) to toggle the sidebar visibility.

---

## Git and Branch Questions

### Q: How do I switch branches?
**A:** 
```bash
git checkout branch-name
```

For example:
```bash
git checkout main
```

### Q: How do I see all available branches?
**A:**
```bash
# Local branches
git branch

# All branches (including remote)
git branch -a
```

### Q: I switched branches but the Explorer didn't update. What do I do?
**A:** 
1. Click away from the Explorer and back to it
2. Press `Ctrl+Shift+E` twice to hide and show it
3. If that doesn't work, reload the window: `Ctrl+R` or `Cmd+R`

### Q: Can I create a new branch in Codespaces?
**A:** Yes!
```bash
git checkout -b my-new-branch
```

### Q: How do I know if my branch is up to date with main?
**A:**
```bash
git fetch origin
git status
```

This will show if your branch is ahead, behind, or up to date.

---

## Working with Files

### Q: How do I create a new file?
**A:** 
- Right-click in the Explorer and select "New File"
- Or press `Ctrl+N` (or `Cmd+N` on Mac)
- Or use terminal: `touch filename.txt`

### Q: How do I delete a file?
**A:**
- Right-click the file in Explorer and select "Delete"
- Or use terminal: `rm filename.txt`

### Q: I made changes but want to discard them. How?
**A:**
```bash
# Discard changes to a specific file
git checkout -- filename

# Discard all changes (be careful!)
git reset --hard
```

### Q: How do I save my work?
**A:** Files auto-save in VS Code, but you should commit and push your changes:
```bash
git add .
git commit -m "Describe your changes"
git push
```

---

## Codespace-Specific Questions

### Q: Will my Codespace save my work if I close my browser?
**A:** Yes! Your Codespace and all your changes are saved on GitHub's servers. When you reopen the Codespace, everything will be as you left it.

### Q: How long does my Codespace stay active?
**A:** Codespaces automatically stop after 30 minutes of inactivity by default. Your files and changes are saved, but running processes will stop.

### Q: Can I have multiple Codespaces for the same repository?
**A:** Yes! You can create multiple Codespaces, even on different branches.

### Q: How do I delete a Codespace?
**A:** 
1. Go to github.com
2. Click your profile icon → "Your codespaces"
3. Find the Codespace and click the "..." menu
4. Select "Delete"

### Q: Does using Codespaces cost money?
**A:** GitHub provides free hours of Codespace usage per month. Check GitHub's pricing page for current limits and pricing.

---

## Development Questions

### Q: How do I install Python packages in my Codespace?
**A:**
```bash
pip install package-name

# Or install project dependencies
pip install -e .[dev]
```

### Q: How do I run Python code?
**A:**
```bash
# Run a Python file
python filename.py

# Or run the CLI
agentic-datasets --help
```

### Q: How do I run tests?
**A:**
```bash
pytest
```

### Q: Can I install additional software in my Codespace?
**A:** Yes, if you have sudo privileges:
```bash
sudo apt-get update
sudo apt-get install package-name
```

However, these changes won't persist if the Codespace is rebuilt. For permanent changes, modify the `.devcontainer/devcontainer.json` file.

---

## Troubleshooting

### Q: My Codespace is running slow. What can I do?
**A:**
1. Close unnecessary browser tabs
2. Stop any running processes you don't need
3. Restart the Codespace
4. Create a new Codespace if the problem persists

### Q: I get a "Permission denied" error. What's wrong?
**A:** You might not have write permissions. Check:
1. Are you working in the correct directory?
2. Is the file or directory owned by you? Run `ls -la` to check
3. Try: `sudo chown -R $(whoami) .` to take ownership

### Q: Commands aren't working. What should I check?
**A:**
1. Make sure you're in the right directory: `pwd`
2. Check if the command is installed: `which command-name`
3. Check your PATH: `echo $PATH`

### Q: I accidentally deleted something important. Can I get it back?
**A:** If you committed it before:
```bash
git reflog
git checkout commit-hash -- filename
```

If you never committed it, it might be unrecoverable.

### Q: The diagnostic script says I have issues. What do I do?
**A:** Follow the recommendations in the script output. Most commonly:
1. Switch to main branch: `git checkout main`
2. Refresh the Explorer: `Ctrl+Shift+E`
3. Reload the window if needed: `Ctrl+R`

---

## Getting More Help

### Q: Where can I find more documentation?
**A:**
- **CODESPACE_QUICKSTART.md** - Quick reference guide
- **CODESPACE_GUIDE.md** - Comprehensive guide
- **CODESPACE_VISUAL_GUIDE.md** - Visual step-by-step guide
- **README.md** - Project documentation

### Q: How do I run the diagnostic tool?
**A:**
```bash
./codespace-check.sh
```

This will check your setup and provide specific recommendations.

### Q: What if none of these solutions work?
**A:**
1. Try creating a fresh Codespace
2. Check GitHub Status (status.github.com) for service issues
3. Review GitHub's Codespaces documentation
4. Ask for help in your repository's issues or discussions

---

## Quick Command Reference

### File Operations
```bash
ls -la              # List files
pwd                 # Current directory
cd directory/       # Change directory
cat filename        # View file contents
tree -L 2           # Show directory tree
```

### Git Operations
```bash
git status          # Check status
git branch          # List branches
git checkout main   # Switch to main
git pull            # Update from remote
git add .           # Stage all changes
git commit -m "msg" # Commit changes
git push            # Push to remote
```

### VS Code Shortcuts
```
Ctrl+P or Cmd+P           # Quick file open
Ctrl+Shift+E or Cmd+Shift+E   # Toggle Explorer
Ctrl+` or Cmd+`           # Toggle Terminal
Ctrl+B or Cmd+B           # Toggle Sidebar
Ctrl+Shift+F or Cmd+Shift+F   # Search in files
Ctrl+Shift+P or Cmd+Shift+P   # Command Palette
```

---

## Remember

**The #1 most common issue is being on a branch with minimal files.**

**Solution:**
```bash
git checkout main
```

Then refresh your Explorer view and you should see all your files!
