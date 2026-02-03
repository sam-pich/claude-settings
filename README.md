# Claude Code Settings

Personal Claude Code configuration for quick setup on new machines.

## Contents

- `CLAUDE.md` - Personal instructions and preferences
- `settings.json` - Model preference, enabled plugins, hooks, MCP servers
- `hooks/` - Custom hooks (e.g., block-dangerous-bash.sh)
- `agents/` - Custom agents (code-reviewer, debugger)
- `skills/` - Custom skills (dcf-model, doc-coauthoring, docx, pdf, pptx, etc.)

## One-Liner Install (New Machine)

Installs Claude Code + applies all settings in one command:

```bash
rm -rf /tmp/claude-settings && git clone https://github.com/sam-pich/claude-settings.git /tmp/claude-settings && /tmp/claude-settings/install.sh
```

## Quick Setup (Claude Code Already Installed)

```bash
git clone https://github.com/sam-pich/claude-settings.git
cd claude-settings
./setup.sh
```

## Manual Setup

If you prefer to set things up manually:

```bash
# Backup existing config (if any)
[ -d ~/.claude ] && cp -r ~/.claude ~/.claude.backup

# Create ~/.claude if it doesn't exist
mkdir -p ~/.claude

# Copy configuration files
cp CLAUDE.md ~/.claude/
cp settings.json ~/.claude/
cp -r hooks ~/.claude/
cp -r agents ~/.claude/
cp -r skills ~/.claude/

# Make hooks executable
chmod +x ~/.claude/hooks/*.sh
```

## Notes

- **Plugins**: The `settings.json` references official plugins by marketplace ID. They will be automatically downloaded when Claude Code starts.
- **MCP Servers**: The `d2l` MCP server requires the `d2l-mcp` command to be installed separately.
- **Credentials**: Authentication credentials are NOT included and will need to be set up on each machine.

## Updating

After making changes to your Claude settings on any machine:

```bash
# From your home directory
cd ~/claude-settings

# Copy updated files
cp ~/.claude/CLAUDE.md .
cp ~/.claude/settings.json .
cp -r ~/.claude/hooks .
cp -r ~/.claude/agents .
cp -r ~/.claude/skills .

# Commit and push
git add -A && git commit -m "Update Claude settings" && git push
```
