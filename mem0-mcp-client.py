#!/usr/bin/env python3
"""
Mem0 MCP Server (stdio mode) — connects to remote Mem0 HTTP API with Basic Auth.

Usage in ~/.claude.json:
{
  "mcpServers": {
    "mem0": {
      "command": "python3",
      "args": ["/path/to/mem0-mcp-client.py"],
      "env": {
        "MEM0_API_URL": "http://host:8889",
        "MEM0_USERNAME": "frank",
        "MEM0_PASSWORD": "aiwozhonghua",
        "MEM0_USER_ID": "frank"
      }
    }
  }
}
"""
import json
import os
import sys
import urllib.request
import urllib.error
import base64

API_URL = os.environ.get("MEM0_API_URL", "http://192.168.12.226:8889")
USERNAME = os.environ.get("MEM0_USERNAME", "")
PASSWORD = os.environ.get("MEM0_PASSWORD", "")
USER_ID = os.environ.get("MEM0_USER_ID", "default")

AUTH_HEADER = "Basic " + base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()


def api_request(method, path, body=None):
    url = f"{API_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", AUTH_HEADER)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()}"}
    except Exception as e:
        return {"error": str(e)}


# --- MCP Protocol (JSON-RPC over stdio) ---

TOOLS = [
    {
        "name": "add_memories",
        "description": "Add a new memory. Call this when the user shares information worth remembering.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to remember"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "search_memory",
        "description": "Search through stored memories. Call this when the user asks anything.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "list_memories",
        "description": "List all memories.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "delete_memories",
        "description": "Delete specific memories by their IDs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of memory IDs to delete",
                },
            },
            "required": ["memory_ids"],
        },
    },
    {
        "name": "delete_all_memories",
        "description": "Delete all memories.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def handle_request(req):
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mem0-remote", "version": "1.0.0"},
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        tool_name = params.get("name", "")
        args = params.get("arguments", {})
        result = call_tool(tool_name, args)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
            },
        }

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def call_tool(name, args):
    if name == "add_memories":
        text = args.get("text", "")
        return api_request("POST", "/memories", {
            "messages": [{"role": "user", "content": text}],
            "user_id": USER_ID,
        })

    if name == "search_memory":
        query = args.get("query", "")
        return api_request("POST", "/search", {
            "query": query,
            "user_id": USER_ID,
        })

    if name == "list_memories":
        return api_request("GET", f"/memories?user_id={USER_ID}")

    if name == "delete_memories":
        results = []
        for mid in args.get("memory_ids", []):
            results.append(api_request("DELETE", f"/memories/{mid}"))
        return results

    if name == "delete_all_memories":
        return api_request("DELETE", f"/memories?user_id={USER_ID}")

    return {"error": f"Unknown tool: {name}"}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        resp = handle_request(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
