#!/bin/bash
# PreToolUse hook: Block dangerous bash commands
# Reads tool call JSON from stdin, outputs block decision if dangerous

# Read JSON input from stdin
input=$(cat)

# Extract the command from the JSON
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Exit silently (allow) if no command found
[ -z "$command" ] && exit 0

# Define dangerous patterns
dangerous_patterns=(
    ":(){:|:&};:"      # Fork bomb
    "mkfs\."
    "dd if=/dev/zero of=/dev/"
    "chmod -R 777 /"
    "> /dev/sda"
    "mv /* /dev/null"
)

# Check for dangerous patterns
for pattern in "${dangerous_patterns[@]}"; do
    if [[ "$command" == *"$pattern"* ]]; then
        # Output JSON to block the command
        echo "{\"decision\": \"block\", \"reason\": \"Blocked dangerous command pattern: $pattern\"}"
        exit 0
    fi
done

# Check for sudo (optional - remove if you want to allow sudo)
if [[ "$command" =~ ^sudo[[:space:]] ]]; then
    echo "{\"decision\": \"block\", \"reason\": \"sudo commands require manual execution\"}"
    exit 0
fi

# No output = allow the command to proceed
exit 0
