# GitHub Codespaces Guide

Welcome to GitHub Codespaces! This guide will help you navigate the IDE and access your repository files.

## 🚀 Getting Started

When you click "Codespaces" from your GitHub repository, you'll see a browser-based VS Code IDE. Here's how to view and work with your files:

## 📁 Viewing Your Files

### Option 1: File Explorer Panel (Recommended)

The **File Explorer** is the primary way to view your repository files:

1. **Look at the left sidebar** - You should see several icons vertically aligned
2. **Click the top icon** (looks like two overlapping documents 📄) - This is the File Explorer
3. **Your repository files will appear** in a tree view on the left side

**If you don't see the sidebar:**
- Press `Ctrl+B` (Windows/Linux) or `Cmd+B` (Mac) to toggle the sidebar visibility
- Or click `View` → `Appearance` → `Show Primary Side Bar` from the menu

### Option 2: Using the Terminal

You can also navigate and view files using the integrated terminal:

1. **Open the Terminal:**
   - Press `Ctrl+`` (backtick) or `Cmd+`` (Mac)
   - Or click `View` → `Terminal` from the menu

2. **List files:**
   ```bash
   ls -la
   ```

3. **View directory structure:**
   ```bash
   tree -L 2  # Show 2 levels deep
   # or
   find . -type f | head -20  # List first 20 files
   ```

4. **Open a file in the editor:**
   ```bash
   code README.md
   ```

### Option 3: Quick Open (Fastest)

Press `Ctrl+P` (Windows/Linux) or `Cmd+P` (Mac) to:
- Open a quick file search
- Type the filename you want to open
- Press Enter to open it

## 🛠️ Common Codespaces Tasks

### Opening This Repository

Your repository is automatically cloned to `/workspaces/datasets/` (or similar path). The Codespace opens in this directory by default.

### Installing Dependencies

The devcontainer is configured to automatically run:
```bash
pip install --upgrade pip && pip install -e .[dev]
```

This happens after the Codespace is created. Check the terminal output to see if it completed successfully.

### Running Commands

Use the integrated terminal to run any command:

```bash
# List CLI commands
agentic-datasets --help

# Run a pipeline
agentic-datasets run-config examples/pipeline.example.yaml

# List transforms
agentic-datasets transforms

# View catalog
agentic-datasets catalog:list
```

## 🔍 Troubleshooting

### "I don't see any files!"

**Solution 1: Check if the Codespace finished loading**
- Look at the bottom status bar - it should say "Codespace: Ready"
- Wait for the postCreateCommand to complete (check the terminal)

**Solution 2: Verify you're in the right directory**
```bash
pwd  # Should show /workspaces/datasets or similar
ls -la  # Should list your repository files
```

**Solution 3: Refresh the File Explorer**
- Right-click in the File Explorer panel
- Select "Refresh"

**Solution 4: Check the workspace folder**
- Click `File` → `Open Folder`
- Navigate to `/workspaces/datasets`
- Click "OK"

### "The sidebar disappeared!"

Press `Ctrl+B` (Windows/Linux) or `Cmd+B` (Mac) to toggle it back.

### "Codespace is slow or unresponsive"

1. Check your internet connection
2. Try reloading the browser page
3. Stop and restart the Codespace from GitHub:
   - Go to your repository on GitHub
   - Click the green "Code" button
   - Under "Codespaces" tab, click the three dots next to your Codespace
   - Select "Stop codespace" then "Start codespace"

### "I get permission errors"

The Codespace runs as the `vscode` user. If you need to install system packages:
```bash
sudo apt-get update
sudo apt-get install <package-name>
```

## 📚 Useful Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|--------------|-----|
| Toggle sidebar | `Ctrl+B` | `Cmd+B` |
| Toggle terminal | `Ctrl+`` | `Cmd+`` |
| Quick open file | `Ctrl+P` | `Cmd+P` |
| Command palette | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| Find in files | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| New terminal | `Ctrl+Shift+`` | `Cmd+Shift+`` |
| Split editor | `Ctrl+\` | `Cmd+\` |
| Close editor | `Ctrl+W` | `Cmd+W` |

## 🎯 Next Steps

1. **Explore the codebase**: Click through the File Explorer to familiarize yourself with the project structure
2. **Read the documentation**: Open `README.md` and `README_AGENTIC.md`
3. **Try running a command**: Use the terminal to run `agentic-datasets --help`
4. **Make your first edit**: Modify a file and see the changes reflected

## 📖 Additional Resources

- **VS Code Documentation**: [code.visualstudio.com/docs](https://code.visualstudio.com/docs)
- **GitHub Codespaces Docs**: [docs.github.com/codespaces](https://docs.github.com/codespaces)
- **Project README**: See `README.md` for project-specific setup instructions
- **CLI Reference**: See `README_AGENTIC.md` for command usage examples

## 💡 Tips

- **Auto-save**: Enable auto-save by clicking `File` → `Auto Save`
- **Extensions**: The devcontainer includes useful extensions like Python, Ruff, and GitHub Copilot
- **Git integration**: Use the Source Control panel (third icon in sidebar) to commit and push changes
- **Ports**: If your app runs on a port, Codespaces will automatically forward it and show a notification

---

**Still having trouble?** Open an issue in the repository with details about your problem!
