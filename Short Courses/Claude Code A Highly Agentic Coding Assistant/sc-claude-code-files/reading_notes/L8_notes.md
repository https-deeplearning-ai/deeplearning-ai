# Lesson 8: Creating Web App based on a Figma Mockup

## Figma Design

Here's the [Figma design mockup](https://github.com/https-deeplearning-ai/sc-claude-code-files/blob/main/additional_files/key-indicators.fig) that you can open with [Figma desktop app](https://www.figma.com/downloads/). 

In the terminal, initialize your `next.js` application using this command:
`npx create-next-app@latest .`

## Figma Official MCP Server (Dev Mode MCP Server)

Note: The official MCP server provided by Figma requires [Dev or Full seat](https://help.figma.com/hc/en-us/articles/27468498501527-Updates-to-Figma-s-pricing-seats-and-billing-experience#h_01JCPBM8X2MBEXTABDM92HWZG4) on the [Professional, Organization, or Enterprise plans](https://help.figma.com/hc/en-us/articles/360040328273-Figma-plans-and-features). You can check [this guide](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server) for more details. There's another Figma MCP server provided by framelinks that you can use for free. Please check the last section of this note for more details. 

### Enable MCP Server

- Open the [Figma design](https://github.com/https-deeplearning-ai/sc-claude-code-files/blob/main/additional_files/key-indicators.fig) in Figma desktop app. 
- In the upper-left corner, open the Figma menu.
- Under Preferences, select Enable Dev Mode MCP Server (as shown [here](https://help.figma.com/hc/article_attachments/33880427925271)).
 
You should see a confirmation message at the bottom of the screen letting you know the server is enabled and running locally at `http://127.0.0.1:3845/mcp` (remote server running locally using http transport). 

### Configure the MCP Server for Claude Code

- In the terminal, type: `claude mcp add --transport http figma-dev-mode-mcp-server http://127.0.0.1:3845/mcp`.

- Also add MCP playwright server: `claude mcp add playwright npx @playwright/mcp@latest`.

- Launch Claude Code and verify that you're connected to both MCP servers (using `/mcp`).


## Prompt 

- To copy the Figma design, in Figma desktop select the design and then click on `Ctrl`+ `L` or `cmd` + `L`.

- Here's the prompt:

  ```
  Using the following figma mockup (paste the link) use the figma dev MCP server to analyze the mockup and build the underlying code in this next.js application. Use the recharts library for creating charts to make this a web application. Check how this application looks using the playwright MCP server and verify it looks as close to the mock as possible.
  ```   

- Follow-up request:

  ``` 
  populate these charts with real-world data from FRED
  ```

  If you'd like to connect the dashboard to real data, then you need at get an API key from FRED [here](https://fred.stlouisfed.org/docs/api/api_key.html).



## Alternative to Figma Official MCP server - Framelink Figma MCP server 

Here's a [guide](https://www.framelink.ai/docs/quickstart?utm_source=github&utm_medium=referral&utm_campaign=readme) on how to configure the Framelink Figma MCP server (as well as some [best practices](https://www.framelink.ai/docs/best-practices) for using it)

You can configure it for Claude Code using: 

`claude mcp add "Framelink Figma MCP" -- npx -y figma-developer-mcp --figma-api-key=YOUR-KEY --stdio`

Or this command:

`claude mcp add-json "Framelink-Figma-MCP" '{"command": "npx", "args": ["-y", "figma-developer-mcp", "--figma-api-key=YOUR-KEY","--stdio"]}'`
