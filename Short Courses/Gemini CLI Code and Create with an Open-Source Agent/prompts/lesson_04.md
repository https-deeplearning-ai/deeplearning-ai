# Lesson 4: Context is Key: GEMINI.md

## Memory Commands

| Command | Description |
|---------|-------------|
| `/memory show` | Combine all context files and show the aggregated view |
| `/memory add <text>` | Save a memory for the agent to remember |
| `/init` | Automatically create a GEMINI.md context file for your project |

## Prompts

### Prompt 1: Test Agent Memory (Before)
```
What is my name?
```
> The agent has no memory, so it can't know personal information.

### Adding Memory
```
/memory add My name is Jack and I only like Purple on Tuesdays
```

Then run `/memory show` to verify the memory was saved.

### Prompt 2: Test Agent Memory (After)
```
What is my name?
```
> Now the agent uses its context to answer the query correctly.

## Creating Project Context with GEMINI.md

For Gemini CLI to work efficiently in an existing project, create a `GEMINI.md` context file per project. This file provides:

- General knowledge on the technologies being used
- Overview of the project structure
- Information about where certain files are located

This guidance helps the agent work more efficiently without needing to explore your code every time you start a new session.

### Prompt 3: Initialize Context File
```
/init
```
> This command looks through your code and initializes a context file for you.

**Demo Note:** Use the `website/` folder (conference website) to demonstrate `/init`. Ensure no extensions are installed and no `GEMINI.md` exists in `~/.gemini` folder.
