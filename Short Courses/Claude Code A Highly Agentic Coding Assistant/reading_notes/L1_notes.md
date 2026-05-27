# Installing Claude Code

1. Check system requirements [here](https://docs.anthropic.com/en/docs/claude-code/setup#system-requirements).
    - Main prerequisites: [Node.js 18 or newer](https://nodejs.org/en/download/)
    - For Windows:
        - Option 1: Claude Code on native Windows using Git Bash (requires [Git for Windows](https://git-scm.com/downloads/win))
        - Option 2: Claude Code within WSL (Window Subsystem for Linux) (requires [installation of WSL 1 or 2](https://learn.microsoft.com/en-us/windows/wsl/install)) 

2. Install Claude Code using this command in your terminal:
    `npm install -g @anthropic-ai/claude-code`

3. If you run into installation issues or permission issues, check this [troubleshooting guide](https://docs.anthropic.com/en/docs/claude-code/troubleshooting#linux-and-mac-installation-issues%3A-permission-or-command-not-found-errors).

4. Once you have Claude Code installed, you can:
   - launch it from your terminal: navigate to your project folder & then type `claude`
   - launch it from the terminal integrated within VS Code by typing `claude` (the extension will auto-install). If you run into issues with the installation with the VS Code extension:
       - Ensure you’re running Claude Code from VS Code’s integrated terminal
       - Ensure that `code` command is available: if not installed, use Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux) and search for “Shell Command: Install ‘code’ command in PATH”  
    
    For more info, check [Claude Code IDE Integrations](https://docs.anthropic.com/en/docs/claude-code/ide-integrations).

# Visualization File

Here's [the html file](https://github.com/https-deeplearning-ai/sc-claude-code-files/blob/main/additional_files/visualization.html) of the visualization generated in lesson 1. 
