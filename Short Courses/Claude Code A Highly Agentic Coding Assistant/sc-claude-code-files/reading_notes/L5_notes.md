# Lesson 5: Adding Multiple Features Simultaneously - Using Git Worktrees

## Custom Slash Commands

- Inside the `.claude` folder of your project directory, create a folder `commands`
- Inside the `commands` folder, create a markdown file: `implement-feature.md`
- Copy the following to the markdown file: 
```
You will be implementing a new feature in this codebase

$ARGUMENTS

IMPORTANT: Only do this for front-end features.
Once this feature is built, make sure to write the changes you made to file called frontend-changes.md
Do not ask for permissions to modify this file, assume you can always do it.
```   
- Launch again Claude Code, you can now use the command as any other built-in command with Claude Code.


## What are git Worktrees?

Git worktrees allow you to check out multiple branches from the same repository into separate directories. Each worktree represents a copy of your working directory with isolated files but shares the same Git history.

## Workflow

- Make sure first that you've added and committed any previous changes to the codebase.
- Create the folder .trees: `mkdir .trees`.
- For each feature you want to implement, create a worktree:
   - `git worktree add .trees/ui_feature`
   - `git worktree add .trees/testing_feature`
   - `git worktree add .trees/quality_feature`
- From each worktree, open an integrated terminal, launch Claude code in each terminal, and ask it to implement each feature.
- For each worktree, add and commit the changes in each worktree.
- Close claude terminals.
- In the main terminal: ask Claude Code to git merge the worktrees and resolve any merge conflicts (```use the git merge command to merge in all the worktrees of the .trees folder into main and fix any conflicts if there are any```)


## Prompt Used for each feature


### UI Feature

```
Add a toggle button that allows users to switch between dark and light themes.

1. Toggle Button Design
    - Create a toggle button that fits the existing design aesthetic
    - Position it in the top-right
    - Use an icon-based design (sun/moon icons or similar)
    - Smooth transition animation when toggling
    - Button should be accessible and keyboard-navigable

2. Light Theme CSS Variables
    Add a light theme variant with appropriate colors:
    - Light background colors
    - Dark text for good contrast
    - Adjusted primary and secondary colors
    - Proper border and surface colors
    - Maintain good accessibility standards

3. JavaScript Functionality
    - Toggle between themes on button click
    - Smooth transitions between themes

4. Implementation Details
    - Use CSS custom properties (CSS variables) for theme switching
    - Add a `data-theme` attribute to the body or html element
    - Ensure all existing elements work well in both themes
    - Maintain the current visual hierarchy and design language

```

### Testing Feature

```
Enhance the existing testing framework for the RAG system in @backend/tests. The current tests cover unit components but are missing essential API testing infrastructure:

- API endpoint tests - Test the FastAPI endpoints (/api/query, /api/courses, /) for proper request/response handling
- pytest configuration - Add pytest.ini_options in pyproject.toml for cleaner test execution
- Test fixtures - Create conftest.py with shared fixtures for mocking and test data setup

The FastAPI app in backend/app.py mounts static files that don't exist in the test environment. Either create a separate test app or define the API endpoints inline in the test file to avoid import issues.
```

### Quality Feature

```
Add essential code quality tools to the development workflow. Set up black for automatic code formatting. Add proper formatting consistency throughout the codebase and create development scripts for running quality checks.
```

## Summary of Claude Code Features

**Custom Slash Commands**

- Inside the `.claude` folder of your project directory, create a folder `commands`
- Inside the `commands` folder, create a markdown file: `implement-feature.md`
- Copy the following to the markdown file: 
   ```
   You will be implementing a new feature in this codebase
   
   $ARGUMENTS
   
   IMPORTANT: Only do this for front-end features.
   Once this feature is built, make sure to write the changes you made to file called frontend-changes.md
   Do not ask for permissions to modify this file, assume you can always do it.
   ```   
- Launch again Claude Code, you can now use the command as any other built-in command with Claude Code.