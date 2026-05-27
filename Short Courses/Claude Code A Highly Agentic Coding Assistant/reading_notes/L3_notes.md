# Lesson 3: Adding Features

## Prompt Used for each feature

### Feature 1 - Embed links in the source citations

For each response, the chatbot returns the lesson that it used to answer the query. The vector store has two collections: one for the lesson chunks and another for the course metadata, which includes a link to each lesson. So assume you want to embed the links of the returned sources in the UI and you want Claude Code to help with that:

Here's a sample prompt (used with plan mode):
 ```
The chat interface displays query responses with source citations. I need to modify it so each source becomes a clickable link that opens the corresponding lesson video in a new tab:
- When courses are processed into chunks in @backend/document_processor.py, the link of each lesson is stored in the course_catalog collection
- Modify _format_results in @backend/search_tools.py so that the lesson links are  also returned
- The links should be embedded invisibly (no visible URL text)
```

Follow-up request:
```
[Ctrl + V to paste the screenshot] these links are hard to read. Make them more visually appealing.
```

### Feature 2 - Add '+ New Chat' Feature

Here's the prompt:
```
Add a '+ NEW CHAT' button to the left sidebar above the courses section. When clicked, it should:
- Clear the current conversation in the chat window
- Start a new session without page reload
- Handle proper cleanup on both @frontend and @backend
- Match the styling of existing sections (Courses, Try asking) - same font size, color, and uppercase formatting
```

Configuration of [Playwright MCP server](https://github.com/microsoft/playwright-mcp):
- exit Claude Code
- in the terminal, type: `claude mcp add playwright npx @playwright/mcp@latest` 
- open Claude Code again and verify you are connected to the MCP server using `/mcp` command

Here's the followup request:
```
Using the playwright MCP server, visit 127.0.0.1:8000 and view the '+ New Chat' button. I want that button to look the same as the other links below for Courses and Try Asking. Make sure this is left aligned and that the border is removed.
```
*Side note*: By default, Claude Code will ask you for your permission to use the "take a screenshot tool" of playwright. You can choose to always allow it when asked by Claude Code or you can manually configure this setting: type `/permissions` command -> Add a new rule (make sure that 'Allow' is highlighted) -> then you specify the full name of the tool. To type the full name of the screenshot tool, in Claude Code terminal, you can type `/mcp` -> choose your MCP server (in this case playwright) -> view tools -> 14. Take a screenshot -> you'll see the full name "mcp__playwright__browser_take_screenshot".



### Feature 3 - Adding a tool to the chatbot

If you check the [search_tools.py](https://github.com/https-deeplearning-ai/starting-ragchatbot-codebase/blob/main/backend/search_tools.py) in the starting codebase, you will see that there is one tool defined for the RAG chatbot. Assume you now want to define another tool for the RAG chatbot to handle outline-related questions. So instead of relying on the content received to answer outline questions, you want the exact outline to be returned (title of each lesson, course link, course title). The course_metadata collection in the vector database has this info. You can ask Claude Code to implement this tool for you:

Here's the prompt used:

```
In @backend/search_tools.py, add a second tool alongside the existing content-related tool. This new tool should handle course outline queries.
- Functionality:
   - Input: Course title
   - Output: Course title, course link, and complete lesson list
   - For each lesson: lesson number, lesson title
- Data source: Course metadata collection of the vector store
- Update the system prompt in @backend/ai_generator so that the course title, course link, the number and title of each lesson are all returned to address an outline-related queries.
- Make sure that the new tool is registered in the system. 
```


## Summary of Claude Features / Commands


| Command | Description |
|---------|-------------|
| `@` | Mention files with `@` to include its content in your request|
| `/mcp` | Manage MCP connection & check available MCP servers with their provided tools ([MCP with Claude Code](https://docs.anthropic.com/en/docs/claude-code/mcp))|

| Shortcuts | Description |
|---------|-------------|
| `shift`+`tab` | switch between planning and auto-accept mode |
| take a screenshot|  `cmd`+ `shift`+ `ctrl` + `4` (Mac) or `Win` + `Shift` + `S` (Windows) |
|paste a screenshot |  `Ctrl` + `V` (might not work on Windows)|


