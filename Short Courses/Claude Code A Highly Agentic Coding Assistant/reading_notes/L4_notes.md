# Lesson 4: Testing, Error Debugging and Code Refactoring

## Error Debugging

To create the error, we intentionally set `MAX_RESULTS: int = 0` in backend/config.py. 

Here's the prompt used with Plan mode:

```
The RAG chatbot returns 'query failed' for any content-related questions. I need you to:
1. Write tests to evaluate the outputs of the execute method of the CourseSearchTool in @backend/search_tools.py 
2. Write tests to evaluate if @backend/ai_generator.py correctly calls for the CourseSearchTool 
3. Write tests to evaluate how the RAG system is handling the content-query related questions. 

Save the tests in a tests folder within @backend. Run those tests against the current system to identify which components are failing. Propose fixes based on what the tests reveal is broken.

Think.
```

## Code Refactoring

In backend/ai_generator.py of the starting codebase, the chatbot is designed to use one tool call per query. To handle more complex queries, you can ask Claude 
Code to refactor it so it can handle sequential tool calls. 

Prompt:

```
Refactor @backend/ai_generator.py to support sequential tool calling where Claude can make up to 2 tool calls in separate API rounds.

Current behavior:
- Claude makes 1 tool call → tools are removed from API params → final response
- If Claude wants another tool call after seeing results, it can't (gets empty response)

Desired behavior:
- Each tool call should be a separate API request where Claude can reason about previous results
- Support for complex queries requiring multiple searches for comparisons, multi-part questions, or when information from different courses/lessons is needed

Example flow:
1. User: "Search for a course that discusses the same topic as lesson 4 of course X"
2. Claude: get course outline for course X → gets title of lesson 4
3. Claude: uses the title to search for a course that discusses the same topic → returns course information
4. Claude: provides complete answer

Requirements:
- Maximum 2 sequential rounds per user query
- Terminate when: (a) 2 rounds completed, (b) Claude's response has no tool_use blocks, or (c) tool call fails
- Preserve conversation context between rounds
- Handle tool execution errors gracefully

Notes: 
- Update the system prompt in @backend/ai_generator.py 
- Update the test @backend/tests/test_ai_generator.py
- Write tests that verify the external behavior (API calls made, tools executed, results returned) rather than internal state details. 

Use two parallel subagents to brainstorm possible plans. Do not implement any code.

```

## Summary of Claude Features

- **Extended Thinking Mode**

   For complex tasks (e.g., complex architectural changes, debugging complicated issues), you can use the word "think" to trigger [extended thinking mode](https://docs.anthropic.com/en/docs/claude-code/common-workflows#use-extended-thinking). There are several levels of thinking: "think" < "think hard" < "think harder" < "ultrathink." Each level allocates more thinking budget for Claude.

- **Use of subagents**

   You've learned that one of the out-of-the-box tools for Claude Code is **Task**, which Claude Code can use to launch subagents for complex multi-step tasks. You can explicitly ask Claude Code to use subagents to brainstorm ideas or to investigate multiple aspects of a question or a problem you want to solve. These built-in agents are of general purpose. 

   You can also create your customized specialized subagents. Each subagent has its own context window, and you can define a custom system prompt and specific tools for each subagent. This part is not covered in this course, but you can check the details in the documentation [here](https://docs.anthropic.com/en/docs/claude-code/sub-agents).  

