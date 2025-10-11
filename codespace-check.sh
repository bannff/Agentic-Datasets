#!/bin/bash
# Codespace Diagnostics Script
# Run this to diagnose file visibility issues

echo "=================================="
echo "Codespace Diagnostics Tool"
echo "=================================="
echo ""

# Check 1: Current directory
echo "✓ Check 1: Current Directory"
echo "----------------------------"
pwd
echo ""

# Check 2: Current branch
echo "✓ Check 2: Current Git Branch"
echo "----------------------------"
current_branch=$(git branch --show-current)
echo "Current branch: $current_branch"

if [ "$current_branch" != "main" ]; then
    echo "⚠️  WARNING: You are NOT on the main branch!"
    echo "   This might be why you can't see all files."
    echo "   Run: git checkout main"
else
    echo "✓ You are on the main branch."
fi
echo ""

# Check 3: File count
echo "✓ Check 3: File Count"
echo "----------------------------"
file_count=$(find . -type f | wc -l)
echo "Total files in current directory: $file_count"

if [ "$file_count" -lt 10 ]; then
    echo "⚠️  WARNING: Very few files detected!"
    echo "   Expected: 100+ files on main branch"
    echo "   Found: $file_count files"
    echo "   Recommendation: Switch to main branch"
else
    echo "✓ Good! Found many files."
fi
echo ""

# Check 4: Key directories
echo "✓ Check 4: Key Directories Present"
echo "----------------------------"
directories=("src" "tests" "examples" ".github/workflows")
missing_dirs=0

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/ exists"
    else
        echo "✗ $dir/ NOT FOUND"
        missing_dirs=$((missing_dirs + 1))
    fi
done

if [ $missing_dirs -gt 0 ]; then
    echo ""
    echo "⚠️  WARNING: $missing_dirs key directories are missing!"
    echo "   You might be on a branch with minimal files."
fi
echo ""

# Check 5: Key files
echo "✓ Check 5: Key Files Present"
echo "----------------------------"
files=("pyproject.toml" "Dockerfile" "catalog.yaml" "README.md")
missing_files=0

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file NOT FOUND"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo ""
    echo "⚠️  WARNING: $missing_files key files are missing!"
fi
echo ""

# Check 6: Git status
echo "✓ Check 6: Git Status"
echo "----------------------------"
git status -sb
echo ""

# Check 7: Available branches
echo "✓ Check 7: Available Branches"
echo "----------------------------"
echo "Local branches:"
git branch
echo ""
echo "Remote branches:"
git branch -r | head -10
echo ""

# Summary and Recommendations
echo "=================================="
echo "SUMMARY & RECOMMENDATIONS"
echo "=================================="
echo ""

if [ "$current_branch" != "main" ] || [ $missing_dirs -gt 0 ] || [ $missing_files -gt 0 ]; then
    echo "❌ ISSUES DETECTED!"
    echo ""
    echo "Most likely cause: You're on a branch with minimal files."
    echo ""
    echo "RECOMMENDED FIX:"
    echo "  1. Run: git checkout main"
    echo "  2. Refresh VS Code Explorer (Ctrl+Shift+E or Cmd+Shift+E)"
    echo "  3. Run this script again to verify"
    echo ""
    echo "To switch branches:"
    echo "  git checkout main"
else
    echo "✓ ALL CHECKS PASSED!"
    echo ""
    echo "Your Codespace appears to be set up correctly."
    echo ""
    echo "If you still can't see files in VS Code:"
    echo "  1. Press Ctrl+Shift+E (or Cmd+Shift+E on Mac) to show Explorer"
    echo "  2. Click the 📁 icon in the left Activity Bar"
    echo "  3. Reload window: Press Ctrl+R (or Cmd+R on Mac)"
fi

echo ""
echo "=================================="
echo "For more help, see:"
echo "  - CODESPACE_QUICKSTART.md"
echo "  - CODESPACE_GUIDE.md"
echo "  - CODESPACE_VISUAL_GUIDE.md"
echo "=================================="
