#!/bin/bash
# Setup script for D&D session log linting

echo "🎲 Setting up D&D Session Log Linting..."

# Make scripts executable
chmod +x session_log_auto_fixer.py
chmod +x lint_session_logs.py

# Copy the intelligent line wrapper (assumes it exists)
if [ -f "intelligent_line_wrapper.py" ]; then
    echo "✅ Found intelligent_line_wrapper.py"
else
    echo "⚠️  intelligent_line_wrapper.py not found - please copy from adventure project"
fi

echo ""
echo "🔧 Available Commands:"
echo ""
echo "  # Check all session logs for issues:"
echo "  python lint_session_logs.py quest_logs/ --check --recursive"
echo ""
echo "  # Fix all issues automatically:"
echo "  python lint_session_logs.py quest_logs/ --fix --recursive"
echo ""
echo "  # Check specific file:"
echo "  python lint_session_logs.py quest_logs/friday/session_recap.md --check"
echo ""
echo "  # Fix specific file:"
echo "  python lint_session_logs.py quest_logs/friday/session_recap.md --fix"
echo ""

# Optional: Create a git pre-commit hook
read -p "Would you like to set up a git pre-commit hook? (y/N): " setup_hook

if [[ $setup_hook =~ ^[Yy]$ ]]; then
    if [ -d ".git" ]; then
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for D&D session logs

echo "🎲 Checking session logs..."

# Run linter on staged markdown files
staged_md_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' | grep -E '(quest_log|session_recap)' || true)

if [ -n "$staged_md_files" ]; then
    echo "Checking staged session log files..."
    python lint_session_logs.py $staged_md_files --check
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Session log formatting issues found!"
        echo "Run 'python lint_session_logs.py quest_logs/ --fix --recursive' to fix them."
        echo "Or add --no-verify to skip this check."
        exit 1
    fi
    
    echo "✅ Session logs look good!"
else
    echo "No session log files staged for commit."
fi
EOF
        chmod +x .git/hooks/pre-commit
        echo "✅ Pre-commit hook installed!"
    else
        echo "❌ Not a git repository - skipping pre-commit hook"
    fi
fi

echo ""
echo "🎉 Setup complete! Try running:"
echo "  python lint_session_logs.py quest_logs/ --check --recursive" 