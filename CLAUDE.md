# Personal Claude Code Instructions

## Git Commits
Do not include "Co-Authored-By" lines in commit messages.

## Code Style
- No emojis in codebase
- Prioritize modular code over mega-files

## Frontend
- Refrain from purple hues in frontend designs

## Quality & Deployment
- Always test code before deployment
- Never commit console.logs

# Bash Guidelines

## IMPORTANT: Avoid commands that cause output buffering issues
- DO NOT pipe output through `head`, `tail`, `less`, or `more` when monitoring or checking command output
- DO NOT use `| head -n X` or `| tail -n X` to truncate output - these cause buffering problems
- Instead, let commands complete fully, or use `--max-lines` flags if the command supports them
- For log monitoring, prefer reading files directly rather than piping through filters

## When checking command output:
- Run commands directly without pipes when possible
- If you need to limit output, use command-specific flags (e.g., `git log -n 10` instead of `git log | head -10`)
- Avoid chained pipes that can cause output to buffer indefinitely