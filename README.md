# Mem0 MCP Client

Connect Claude Code to a remote [Mem0](https://github.com/mem0ai/mem0) memory service via MCP (Model Context Protocol).

Pure Python, zero dependencies.

## Quick Install

```bash
git clone https://github.com/michaelx1993/mem0-mcp.git
cd mem0-mcp
./install.sh
```

The installer will prompt for:
- **API URL** — Mem0 API endpoint
- **Username / Password** — HTTP Basic Auth credentials
- **User ID** — your memory namespace

It auto-configures `~/.claude.json` and installs the script to `~/.mem0-mcp/`.

Restart Claude Code after installation.

## Manual Setup

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "python3",
      "args": ["/path/to/mem0-mcp-client.py"],
      "env": {
        "MEM0_API_URL": "http://your-server:8889",
        "MEM0_USERNAME": "your-username",
        "MEM0_PASSWORD": "your-password",
        "MEM0_USER_ID": "your-user-id"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `add_memories` | Store new memories |
| `search_memory` | Search through memories |
| `list_memories` | List all memories |
| `delete_memories` | Delete specific memories by ID |
| `delete_all_memories` | Delete all memories |

## Requirements

- Python 3.6+
- Claude Code
