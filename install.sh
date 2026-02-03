#!/bin/bash
# Full Claude Code installer: installs Claude Code + applies personal settings
# Usage: curl -fsSL https://raw.githubusercontent.com/sam-pich/claude-settings/main/install.sh | bash
#   or: git clone https://github.com/sam-pich/claude-settings.git && cd claude-settings && ./install.sh

set -e

REPO_URL="https://github.com/sam-pich/claude-settings.git"
CLAUDE_DIR="$HOME/.claude"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail()  { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }

# --- Step 1: Install Claude Code ---
echo ""
echo "====================================="
echo "  Claude Code Installer + Settings"
echo "====================================="
echo ""

if command -v claude &>/dev/null; then
    CURRENT_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    ok "Claude Code already installed (${CURRENT_VERSION})"
else
    info "Installing Claude Code..."

    OS="$(uname -s)"
    case "$OS" in
        Linux|Darwin)
            curl -fsSL https://claude.ai/install.sh | bash
            ;;
        MINGW*|MSYS*|CYGWIN*)
            fail "On Windows, run in PowerShell: irm https://claude.ai/install.ps1 | iex"
            ;;
        *)
            fail "Unsupported OS: $OS"
            ;;
    esac

    # Ensure claude is on PATH for the rest of this script
    export PATH="$HOME/.local/bin:$PATH"

    if command -v claude &>/dev/null; then
        ok "Claude Code installed successfully"
    else
        fail "Claude Code installation failed. Install manually: https://code.claude.com/docs/en/setup"
    fi
fi

# --- Step 2: Clone settings repo (if not already in it) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" 2>/dev/null)" && pwd 2>/dev/null || echo "")"

# Check if we're already inside the cloned repo
if [ -f "$SCRIPT_DIR/settings.json" ] && [ -f "$SCRIPT_DIR/CLAUDE.md" ]; then
    SETTINGS_DIR="$SCRIPT_DIR"
    ok "Running from settings repo"
else
    TEMP_DIR=$(mktemp -d)
    info "Cloning settings from $REPO_URL..."

    if command -v git &>/dev/null; then
        git clone --depth 1 "$REPO_URL" "$TEMP_DIR/claude-settings"
        SETTINGS_DIR="$TEMP_DIR/claude-settings"
        ok "Settings cloned"
    else
        fail "git is required but not installed"
    fi
fi

# --- Step 3: Backup existing config ---
if [ -d "$CLAUDE_DIR" ]; then
    BACKUP_DIR="${CLAUDE_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    warn "Existing ~/.claude found - backing up to $BACKUP_DIR"
    cp -r "$CLAUDE_DIR" "$BACKUP_DIR"
    ok "Backup created"
fi

# --- Step 4: Apply settings ---
info "Applying settings..."

mkdir -p "$CLAUDE_DIR/hooks"
mkdir -p "$CLAUDE_DIR/agents"
mkdir -p "$CLAUDE_DIR/skills"

# Copy core config
cp "$SETTINGS_DIR/CLAUDE.md" "$CLAUDE_DIR/"
ok "Copied CLAUDE.md"

cp "$SETTINGS_DIR/settings.json" "$CLAUDE_DIR/"
ok "Copied settings.json"

# Copy hooks
if [ -d "$SETTINGS_DIR/hooks" ] && [ "$(ls -A "$SETTINGS_DIR/hooks" 2>/dev/null)" ]; then
    cp -r "$SETTINGS_DIR/hooks/"* "$CLAUDE_DIR/hooks/"
    chmod +x "$CLAUDE_DIR/hooks/"*.sh 2>/dev/null || true
    ok "Copied hooks"
fi

# Copy agents
if [ -d "$SETTINGS_DIR/agents" ] && [ "$(ls -A "$SETTINGS_DIR/agents" 2>/dev/null)" ]; then
    cp -r "$SETTINGS_DIR/agents/"* "$CLAUDE_DIR/agents/"
    ok "Copied agents"
fi

# Copy skills
if [ -d "$SETTINGS_DIR/skills" ] && [ "$(ls -A "$SETTINGS_DIR/skills" 2>/dev/null)" ]; then
    cp -r "$SETTINGS_DIR/skills/"* "$CLAUDE_DIR/skills/"
    ok "Copied skills"
fi

# --- Step 5: Clean up temp dir ---
if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# --- Step 6: Summary ---
echo ""
echo "====================================="
echo "  Setup Complete"
echo "====================================="
echo ""
echo "  Installed:"
echo "    - CLAUDE.md (personal instructions)"
echo "    - settings.json (model, plugins, hooks, MCP)"
echo "    - hooks/block-dangerous-bash.sh"
echo "    - agents/code-reviewer.md, debugger.md"
echo "    - skills/ (dcf-model, docx, pdf, pptx, ...)"
echo ""
echo "  Next steps:"
echo "    1. Run 'claude' to start Claude Code"
echo "    2. Authenticate when prompted"
echo "    3. Plugins will auto-install on first launch"
echo ""
if command -v claude &>/dev/null; then
    echo "  Version: $(claude --version 2>/dev/null)"
fi
echo ""
