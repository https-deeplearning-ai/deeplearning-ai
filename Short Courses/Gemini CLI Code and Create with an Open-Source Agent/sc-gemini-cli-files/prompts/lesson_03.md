# Lesson 3: A Tour of Gemini CLI

## Getting Started

### Installation

```bash
npm install -g @google/gemini-cli
```

## Important Slash Commands

| Command | Description |
|---------|-------------|
| `/auth` | View authentication methods and login (e.g., Google auth) |
| `/help` | View a list of all built-in commands and shortcuts |
| `/theme` | Customize the look and feel of Gemini CLI |
| `/settings` | See all the different areas of Gemini CLI you can customize |
| `/model` | Change different modes and models for your requests |
| `/clear` | Wipe history and reset conversation |
| `/stats` | Track model calls and token usage |
| `/docs` | View the documentation |
| `/quit` or `/exit` | Exit Gemini CLI |

**Tip:** Double escape to clear input prompt.

## Prompts

### Prompt 1: Reading Suggestions
```
Last year's organizers of the 2025 TechStack conference left some suggestions, can you read them to me from @suggestions.md
```

### Prompt 2: Research Best Practices
```
Can you see if this matches with online best practices for organizing a tech conference?
```

### Prompt 3: Update Documentation
```
Add the new findings to our suggestions doc.
```

> **Note:** This prompt will show tool call and requirement to accept writing/editing to files.
