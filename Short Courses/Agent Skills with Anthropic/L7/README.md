# L7 Agent

A multi-agent system built with the Claude Agent SDK that includes documentation research, repository analysis, and web research capabilities.

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Create a `.env` file in the project root:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key
   NOTION_TOKEN=your_notion_integration_token
   ```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key for Claude access |
| `NOTION_TOKEN` | Your Notion integration token for local MCP server access |

You can skip definining the `NOTION_TOKEN` if you choose not to try the MCP server.

### Getting an Anthropic API Key

1. Go to the <a href="https://console.anthropic.com/" target="_blank">Anthropic Console</a>
2. Sign up or log in to your account
3. Navigate to **API Keys** in the settings
4. Click **Create Key** and copy the generated key

### Optional - Getting a Notion Token
This is to run the Notion local MCP server.

**Note:** Node.js must be installed since the MCP server runs via `npx`. Download Node.js <a href="https://nodejs.org/" target="_blank">here</a>. 

1. Create an account with Notion (using the free plan) <a href="https://www.notion.so/signup" target="_blank">here</a> 
2. Go to <a href="https://www.notion.so/my-integrations" target="_blank">Notion Integrations</a>
3. Click **New integration**
4. Give it a name and select the workspace
5. Click on **Configure Internal Settings**
6. Copy the **Internal Integration Secret**
7. Share the Notion pages you want to access with your integration:
    - Navigate to **Access** tab
    - Click on **Edit Access**
    - Search for the pages you want to include

For more details, check the installation details <a href="https://github.com/makenotion/notion-mcp-server?tab=readme-ov-file#installation" target="_blank">here</a>.

## Running the Agent

```bash
uv run python agent.py
```

Once running, type your messages and press Enter. Type `exit` to quit.
