# Lesson 6: Customization with Gemini CLI Extensions

## What is a Gemini CLI Extension?

Gemini CLI extensions build on top of MCP. There is an ecosystem of over 200 extensions you can browse at [geminicli.com/extensions](https://geminicli.com/extensions).

### What Extensions Bundle
- One or more MCP servers
- A context file
- Custom commands

### Extensions vs MCP

| MCP | Extensions |
|-----|------------|
| Tells the model what tools are available | Teaches the model *how* to use tools together |
| Describes what tools do | Provides workflows and combinations |
| Limited context | Custom context file for debugging, documentation, best practices |

### Custom Commands
Extensions can provide pre-populated prompts for complex workflows. For example, a `/generate-campaign` command could:

1. Pull ad campaign briefing and target audience from a Google doc
2. Generate detailed campaign descriptions of visual assets required
3. Generate 5 visual assets for ads

## Working with Extensions

### Exploring Extensions
```
/extensions explore
```

### Installing an Extension
```bash
gemini extensions install https://github.com/gemini-cli-extensions/workspace
```

### Extension Commands

| Command | Description |
|---------|-------------|
| `/extensions list` | View configured extensions |
| `/extensions explore` | Browse available extensions |
| `/mcp` | View MCP servers (including those from extensions) |
| `/memory show` | View context files (including extension context) |

## Prompts

### Prompt 1: Read Conference Schedule
```
Can you read my "Conference Schedule" doc and list me the current schedule for the TechStack conference
```

### Prompt 2: Create Calendar Holds
```
Can you go ahead and put a hold for me on my calendar for each session? With the title being [HOLD]: title of session.
```

> **Note:** For extensions with remote MCP servers, you may need to run `/mcp auth <serverName>` for authentication.
