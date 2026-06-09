import json
import sys

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text


# --- Global Theme Configuration ---
THEME_SYNTAX = "fruity"

# --- Global Color Configuration ---

# --- SYSTEM_MESSAGES: ---
SYSTEM_MESSAGES = "#327EFF"
# Being used in function "print_system_message"
COLOR_SYSTEM_PROMPT = SYSTEM_MESSAGES

# --- USER_MESSAGES: ---
USER_MESSAGES = "#FFB800"
# Being used in function "print_user_message"
COLOR_USER_PROMPT = USER_MESSAGES

# --- TOOL_INPUT: ---
TOOL_INPUT = "#FF5534"
# Being used in function "print_tool_input"
# Being used in function "print_previous_tool_calls"
COLOR_TOOL_INPUT = TOOL_INPUT

# --- TOOL_OUTPUT: ---
TOOL_OUTPUT = "#00855D"
# Being used in function "print_tool_output"
# Being used in function "print_previous_tool_calls"
COLOR_TOOL_OUTPUT = TOOL_OUTPUT

# --- HISTORY: ---
HISTORY = "#FF00FF"
# Being used in function "print_final_answer"
# Being used in function "print_history"
COLOR_FINAL_ANSWER = COLOR_HISTORY = HISTORY

# --- OTHERS ---

# Being used in function "print_iteration"
COLOR_ITERATION = "black on blue"

# Being used in function "print_alert"
COLOR_ALERT = "black on red"

# Being used in function "print_tool_error"
# Being used in function "print_alert"
COLOR_TOOL_ERROR = COLOR_ALERT_MSG = "red"



class AgentVisualizer:
    """
    Handles all formatted terminal output for the agent execution.
    """

    @property
    def console(self):
        """
        Configures and returns the rich console instance.

        Returns:
            console_instance (Console): The configured rich console object.
        """
        # Initialize the console object with specific configurations
        console_instance = Console(force_terminal=True, force_jupyter=False, file=sys.stdout, width=85)
        
        # Return the configured console instance
        return console_instance

    
    def print_system_message(self, prompt):
        """
        Prints the system message to the console.

        Args:
            prompt (str): The text content of the system message.
        """
        # Output a blank line for visual spacing
        self.console.print()
        
        # Encapsulate the prompt text within a styled panel
        panel = Panel(
            prompt,
            title=f"[bold {COLOR_SYSTEM_PROMPT}]System Message[/bold {COLOR_SYSTEM_PROMPT}]",
            border_style=COLOR_SYSTEM_PROMPT
        )
        
        # Display the panel on the console
        self.console.print(panel)

        
    def print_user_message(self, prompt):
        """
        Prints the user query to the console.

        Args:
            prompt (str): The text content of the user message.
        """
        # Output a blank line for visual spacing
        self.console.print()
        
        # Encapsulate the user query within a styled panel
        panel = Panel(
            prompt,
            title=f"[bold {COLOR_USER_PROMPT}]User Message[/bold {COLOR_USER_PROMPT}]",
            border_style=COLOR_USER_PROMPT
        )
        
        # Display the panel on the console
        self.console.print(panel)

        
    def print_iteration(self, iteration, max_iterations):
        """
        Prints the current agent loop iteration.

        Args:
            iteration (int): The current loop iteration number.
            max_iterations (int): The maximum number of allowed iterations.
        """
        # Create the core iteration text string
        core_text = f"Agent Loop — Iteration {iteration} / {max_iterations}"
        
        # Pad the text to match the console width, centering the core text
        padded_text = core_text.center(self.console.width)
        
        # Output the formatted, full-width iteration counter to the console
        self.console.print(
            f"\n[bold {COLOR_ITERATION}]{padded_text}[/bold {COLOR_ITERATION}]"
        )

        
    def print_tool_input(self, tool_name, args):
        """
        Renders tool inputs as a formatted block.

        Args:
            tool_name (str): The identifier of the tool being executed.
            args (str or dict): The input arguments provided to the tool.
        """
        # Check if args is a JSON string and parse it for pretty printing
        if isinstance(args, str):
            # Attempt to parse the string arguments as JSON
            try:
                # Load the JSON string into a dictionary structure
                args = json.loads(args)
            # Handle cases where the string is not valid JSON
            except json.JSONDecodeError:
                # Proceed without modifying the original arguments
                pass
        
        # Format the arguments if they are currently a dictionary
        if isinstance(args, dict):
            # Serialize the dictionary to a formatted JSON string
            json_str = json.dumps(args, indent=2)
            
            # Apply syntax highlighting to the resulting JSON string
            content = Syntax(json_str, "json", theme=THEME_SYNTAX, background_color="default", line_numbers=False, word_wrap=True)
        # Handle the arguments if they are not a dictionary
        else:
            # Convert the arguments directly into a standard string
            content = str(args)

        # Wrap the formatted content within a visual panel component
        panel = Panel(
            content,
            title=f"[bold {COLOR_TOOL_INPUT}]Tool Input:[/bold {COLOR_TOOL_INPUT}] [{COLOR_TOOL_INPUT}]{tool_name}[/{COLOR_TOOL_INPUT}]",
            border_style=COLOR_TOOL_INPUT,
            expand=False
        )
        
        # Output a blank line for visual spacing
        self.console.print()
        
        # Render the constructed panel to the console
        self.console.print(panel)
        
        
    def print_tool_output(self, tool_name, output):
        """
        Renders the tool output as a formatted block.

        Args:
            tool_name (str): The identifier of the tool that was executed.
            output (Any): The resulting output from the executed tool.
        """
        # Attempt to extract dictionary if it's a Pydantic model
        if hasattr(output, 'model_dump'):
            # Extract the dictionary data using the model_dump method
            output_data = output.model_dump()
        # Attempt to extract dictionary using the legacy dict method
        elif hasattr(output, 'dict'):
            # Extract the dictionary data using the dict method
            output_data = output.dict()
        # Handle standard outputs without special extraction needs
        else:
            # Assign the raw output directly to the data variable
            output_data = output
        
        # Check if the output data is a dictionary or a list
        if isinstance(output_data, (dict, list)):
            # Serialize the structure to a formatted JSON string
            json_str = json.dumps(output_data, indent=2)
            
            # Apply syntax highlighting to the JSON output string
            content = Syntax(json_str, "json", theme=THEME_SYNTAX, background_color="default", line_numbers=False, word_wrap=True)
        # Handle other types of output data
        else:
            # Convert the output data directly into a standard string
            content = str(output_data)

        # Enclose the formatted content within a visual panel component
        panel = Panel(
            content,
            title=f"[bold {COLOR_TOOL_OUTPUT}]Tool Output:[/bold {COLOR_TOOL_OUTPUT}] [{COLOR_TOOL_OUTPUT}]{tool_name}[/{COLOR_TOOL_OUTPUT}]",
            border_style=COLOR_TOOL_OUTPUT,
            expand=False
        )
        
        # Output a blank line for visual spacing
        self.console.print()
        
        # Render the constructed panel to the console
        self.console.print(panel)

        
    def _clip_line(self, text, limit=80):
        """
        Collapses whitespace and clips text to a single, length-limited line.

        Args:
            text (str): The text to collapse and clip.
            limit (int): The maximum allowed line length. Defaults to 80.

        Returns:
            clipped_line (str): A single-line string no longer than the given limit.
        """
        # Collapse all runs of whitespace (including newlines) into spaces
        single_line = " ".join(str(text).split())

        # Clip the line and add an ellipsis when it exceeds the limit
        if len(single_line) > limit:
            # Generate the truncated string and store it in a variable
            clipped_line = single_line[:limit - 1] + "…"
            
            # Return the resulting clipped string variable
            return clipped_line

        # Return the collapsed line unchanged when within the limit
        return single_line


    def print_previous_tool_calls(self, calls):
        """
        Renders all resolved tool calls from prior iterations as a single
        compact panel. Each call line is tinted with the tool-input color and
        each output line with the tool-output color.

        Args:
            calls (list): A list of dicts, each with 'name', 'arguments', and
                          'output' keys describing a resolved tool call.
        """
        # Validate whether there are calls to process
        if not calls:
            # Exit the execution flow early if the calls list is empty
            return

        # Initialize a list to hold the formatted lines
        entries = []
        
        # Iterate over each resolved tool call
        for call in calls:
            # Format and clip the tool call name and arguments
            call_line = self._clip_line(f"→ {call['name']} {call['arguments']}")
            
            # Append the formatted line alongside its designated input color
            entries.append((call_line, COLOR_TOOL_INPUT))

            # Format and clip the tool output result
            output_line = self._clip_line(f"← {call['output']}")
            
            # Append the output line alongside its designated output color
            entries.append((output_line, COLOR_TOOL_OUTPUT))

        # Initialize a counter for entries that exceed the display limit
        hidden = 0
        
        # Check if the number of entries surpasses the limit
        if len(entries) > 5:
            # Calculate how many entries will be hidden from the view
            hidden = len(entries) - 5
            
            # Truncate the list to retain only the most recent five entries
            entries = entries[:5]

        # Initialize a text container for the structured output
        content = Text()
        
        # Loop through the retained entries with their indices
        for index, (line, color) in enumerate(entries):
            # Append the formatted line to the text container with the appropriate color style
            content.append(line, style=color)
            
            # Add a newline character unless it is the final visible entry without hidden items
            if index < len(entries) - 1 or hidden:
                # Insert the newline
                content.append("\n")

        # Verify if any calls were truncated
        if hidden:
            # Append a truncation notice to the text container
            content.append(f"… (+{hidden} more, truncated)", style="dim")

        # Encapsulate the formatted content within a visual panel component
        panel = Panel(
            content,
            title=f"[bold {COLOR_TOOL_INPUT}]{len(calls)} Previous Tool Calls[/bold {COLOR_TOOL_INPUT}]",
            border_style=COLOR_TOOL_INPUT,
            expand=False
        )

        # Output a blank line for visual spacing
        self.console.print()

        # Render the constructed panel to the console
        self.console.print(panel)


    def print_tool_error(self, error_msg):
        """
        Prints an error message from a failed tool execution.

        Args:
            error_msg (str): The description of the error to be displayed.
        """
        # Output a blank line to provide visual separation
        self.console.print()
        
        # Print the styled error message text to the console
        self.console.print(f"    [bold {COLOR_TOOL_ERROR}]⚠ Tool Error:[/bold {COLOR_TOOL_ERROR}] {error_msg}")
        
        
    def print_alert(self, label, message):
        """
        Prints a formatted message or alert to the console.

        Args:
            label (str): The prefix header for the alert (e.g., 'LIMIT REACHED', 'TIMEOUT').
            message (str): The descriptive text detailing the specific event or state.
        """
        # Output a blank line for visual spacing
        self.console.print()
        
        # Display the warning text with the specified colors and formatting
        self.console.print(
            f"[{COLOR_ALERT}][bold]{label}:[/bold][/{COLOR_ALERT}] "
            f"[{COLOR_ALERT_MSG}]{message}[/{COLOR_ALERT_MSG}]"
        )
        
        
    def print_history(self, history_text):
        """
        Prints the conversation history or context, truncating it if it
        exceeds five lines.

        Args:
            history_text (str): The full text of the history to be displayed.
        """
        # Split the incoming text into a list of individual lines
        lines = str(history_text).split('\n')

        # Check if the total number of lines exceeds five
        if len(lines) > 5:
            # Extract and join only the first five lines
            display_text = '\n'.join(lines[:5])
            
            # Append a clear truncation message separated by a blank line
            display_text += "\n\n(truncated to show first 5 lines)"
            
        # Handle cases where the text is five lines or fewer
        else:
            # Use the original text without any modifications
            display_text = str(history_text)

        # Output a blank line for visual spacing
        self.console.print()
        
        # Encapsulate the resulting text within a styled panel
        panel = Panel(
            display_text,
            title=f"[bold {COLOR_HISTORY}]History[/bold {COLOR_HISTORY}]",
            border_style=COLOR_HISTORY
        )
        
        # Display the formatted panel on the console
        self.console.print(panel)

     
    def print_final_answer(self, answer):
        """
        Prints the conclusive final answer from the agent.

        Args:
            answer (str): The text of the final generated answer.
        """
        # Output a blank line for visual spacing
        self.console.print()
        
        # Encapsulate the final answer text within a styled panel
        panel = Panel(
            answer,
            title=f"[bold {COLOR_FINAL_ANSWER}]FINAL ANSWER[/bold {COLOR_FINAL_ANSWER}]",
            border_style=COLOR_FINAL_ANSWER
        )
        
        # Display the panel on the console
        self.console.print(panel)


# Instantiate the global visualizer object
viz = AgentVisualizer()