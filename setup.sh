#!/bin/bash
# Setup script for Claude Code settings

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Setting up Claude Code configuration..."

# Backup existing config if present
if [ -d "$CLAUDE_DIR" ]; then
    BACKUP_DIR="$CLAUDE_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backing up existing config to $BACKUP_DIR"
    cp -r "$CLAUDE_DIR" "$BACKUP_DIR"
fi

# Create directories
mkdir -p "$CLAUDE_DIR/hooks"
mkdir -p "$CLAUDE_DIR/agents"
mkdir -p "$CLAUDE_DIR/skills"

# Copy files
echo "Copying CLAUDE.md..."
cp "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/"

echo "Copying settings.json..."
cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/"

echo "Copying hooks..."
cp -r "$SCRIPT_DIR/hooks/"* "$CLAUDE_DIR/hooks/" 2>/dev/null || true

echo "Copying agents..."
cp -r "$SCRIPT_DIR/agents/"* "$CLAUDE_DIR/agents/" 2>/dev/null || true

echo "Copying skills..."
cp -r "$SCRIPT_DIR/skills/"* "$CLAUDE_DIR/skills/" 2>/dev/null || true

# Make hooks executable
chmod +x "$CLAUDE_DIR/hooks/"*.sh 2>/dev/null || true

echo ""
echo "Setup complete!"
echo ""
echo "Note: Plugins will be automatically downloaded when you start Claude Code."
echo "Note: You'll need to authenticate Claude Code separately on this machine."
