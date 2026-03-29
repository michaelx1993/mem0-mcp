#!/bin/bash
set -e

# Mem0 MCP Client Installer
# Usage: ./install.sh

INSTALL_DIR="$HOME/.mem0-mcp"
CLAUDE_CONFIG="$HOME/.claude.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Default config
DEFAULT_API_URL=""
DEFAULT_USER_ID=""

echo "================================"
echo "  Mem0 MCP Client Installer"
echo "================================"
echo

# Prompt for config
read -p "API URL [$DEFAULT_API_URL]: " API_URL
API_URL="${API_URL:-$DEFAULT_API_URL}"

read -p "Username [$DEFAULT_USER_ID]: " USERNAME
USERNAME="${USERNAME:-$DEFAULT_USER_ID}"

read -sp "Password: " PASSWORD
echo

read -p "User ID (your memory namespace) [$USERNAME]: " USER_ID
USER_ID="${USER_ID:-$USERNAME}"

# Install MCP client script
mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/mem0-mcp-client.py" "$INSTALL_DIR/mem0-mcp-client.py"
chmod +x "$INSTALL_DIR/mem0-mcp-client.py"
echo
echo "[OK] Installed to $INSTALL_DIR/mem0-mcp-client.py"

# Update ~/.claude.json
MCP_ENTRY=$(cat <<EOF
{
  "command": "python3",
  "args": ["$INSTALL_DIR/mem0-mcp-client.py"],
  "env": {
    "MEM0_API_URL": "$API_URL",
    "MEM0_USERNAME": "$USERNAME",
    "MEM0_PASSWORD": "$PASSWORD",
    "MEM0_USER_ID": "$USER_ID"
  }
}
EOF
)

if [ -f "$CLAUDE_CONFIG" ]; then
    # Check if python3 is available for JSON manipulation
    if command -v python3 &>/dev/null; then
        python3 -c "
import json, sys

config_path = '$CLAUDE_CONFIG'
with open(config_path) as f:
    config = json.load(f)

config.setdefault('mcpServers', {})
config['mcpServers']['mem0'] = json.loads('''$MCP_ENTRY''')

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
print('[OK] Updated', config_path)
"
    else
        echo "[WARN] python3 not found, cannot auto-update $CLAUDE_CONFIG"
        echo "       Manually add the following to mcpServers in $CLAUDE_CONFIG:"
        echo "       \"mem0\": $MCP_ENTRY"
    fi
else
    # Create new config
    python3 -c "
import json
config = {'mcpServers': {'mem0': json.loads('''$MCP_ENTRY''')}}
with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
print('[OK] Created', '$CLAUDE_CONFIG')
"
fi

# Verify
echo
echo "================================"
echo "  Installation Complete!"
echo "================================"
echo
echo "  API URL:   $API_URL"
echo "  Username:  $USERNAME"
echo "  User ID:   $USER_ID"
echo "  Script:    $INSTALL_DIR/mem0-mcp-client.py"
echo "  Config:    $CLAUDE_CONFIG"
echo
echo "Restart Claude Code to activate."
echo "Tools available: add_memories, search_memory, list_memories, delete_memories, delete_all_memories"
