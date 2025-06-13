# LegalMCP – SAOS Judgments MCP Server

LegalMCP provides a [Model Context Protocol (MCP)](https://docs.mcp.dev) interface to the public API of the Court Judgment Analysis System (SAOS).
It allows searching for judgments and retrieving full justifications directly from AI tools (e.g., Cascade) or your own scripts.

---

## Features

| MCP Tool           | Description |
|--------------------|-------------|
| **`search_judgments`** | Search for judgments in the SAOS database using any string and optional filters (court type, judgment type, date range, pagination). |
| **`get_judgment`**     | Retrieve the full content of a single judgment by its `id`. |

---

## Quick Start

### Requirements
* Python ≥ 3.10
* Internet access (SAOS API)

### Installation
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running the MCP Server
In default mode (streamable HTTP on port 8000):
```bash
python server.py
```

In development mode with MCP inspector:
```bash
mcp dev server.py
```

After starting, the server will print the address it is listening on (e.g., `http://127.0.0.1:8000`).

---

## Integration with Cascade / Windsurf

If you use Cascade (Windsurf) and want the server to start automatically together with the editor, add an entry to the configuration file `~/.codeium/windsurf/mcp_config.json` (Windows: `C:\Users\<user>\.codeium\windsurf\mcp_config.json`). For example:

```json
{
  "mcpServers": {
    "saos-search": {
      "command": "python",
      "args": [
        "C:/path/to/LegalMCP/server.py"
      ],
      "cwd": "C:/path/to/LegalMCP"
    }
  }
}
```

After saving the file, restart Cascade or run **Reload MCP Servers** from the command palette so the server appears in the list of available tools.

---

## Usage Examples

### 1. Searching for judgments on Swiss franc loans from February 2025
```python
from datetime import date
import asyncio, json, mcp.client

client = mcp.client.AsyncClient("http://127.0.0.1:8000")

async def main():
    results = await client.search_judgments(
        query="kredyt frankowy", # "Swiss franc loan"
        dateFrom=date(2025, 2, 1),
        dateTo=date(2025, 2, 28),
        page=0,
        pageSize=20,
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))

asyncio.run(main())
```

### 2. Retrieving the full justification of a selected judgment
```python
judgment = await client.get_judgment(judgment_id=522718)
print(judgment["textContent"])
```

---

## Repository Structure
```
LegalMCP/
├── server.py          # Main FastMCP server with two tools
├── requirements.txt   # Project dependencies
├── README.md          # This file
```

---

## License
This project is licensed under the MIT License.

---

## Authors
* **Kamil Dobrowolski** – initial author and project maintainer.

Happy legal coding!
