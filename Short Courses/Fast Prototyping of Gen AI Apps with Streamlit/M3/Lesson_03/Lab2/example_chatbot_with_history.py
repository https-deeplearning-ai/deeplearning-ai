import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# --- Constants and Configuration ---
MODELS = ['claude-3-5-sonnet', 'mistral-large', 'gemma-7b', 'llama3-8b']
CONTEXT_TABLE = "AVALANCHE_DB.AVALANCHE_SCHEMA.MERGED_REVIEWS"
DEFAULT_HISTORY_LENGTH = 5

# --- Data Loading (Cached) ---
@st.cache_data
def load_context_dataframe(table_name: str) -> pd.DataFrame:
    """Loads the specified Snowflake table into a Pandas DataFrame."""
    try:
        return session.sql(f"SELECT * FROM {table_name}").to_pandas()
    except Exception as e:
        st.error(f"Error loading data from {table_name}: {e}")
        return pd.DataFrame()

# --- Session State Initialization ---
def initialize_session_state():
    """Initializes required session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model_name" not in st.session_state:
        st.session_state.model_name = MODELS[0]
    if "use_chat_history" not in st.session_state:
        st.session_state.use_chat_history = True
    if "debug" not in st.session_state:
         st.session_state.debug = False

# --- UI Setup ---
def setup_sidebar():
    """Sets up the sidebar widgets."""
    st.sidebar.button("Clear conversation", on_click=lambda: st.session_state.update({"messages": []}))
    st.sidebar.toggle("Debug", key="debug")
    st.sidebar.toggle("Use chat history", key="use_chat_history")

    with st.sidebar.expander("Model and Context Options"):
        st.selectbox("Select model:", MODELS, key="model_name")
        st.number_input(
            "Max messages to use in chat history",
            key="num_chat_messages",
            min_value=1,
            max_value=25,
            value=DEFAULT_HISTORY_LENGTH,
            step=1,
        )

    if st.session_state.debug:
        st.sidebar.expander("Session State").write(st.session_state)


# --- Helper Functions ---
def get_formatted_chat_history() -> str:
    """Retrieves and formats the recent chat history."""
    if not st.session_state.use_chat_history:
        return "Chat history is disabled."

    num_messages = st.session_state.num_chat_messages
    messages = st.session_state.messages
    relevant_messages = messages[max(0, len(messages) - num_messages) : -1]

    if not relevant_messages:
        return "No prior chat history available or used."

    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in relevant_messages])


def complete(model: str, prompt: str) -> str:
    """Calls the Snowflake Cortex complete function using parameterized query."""
    try:
        result = session.sql(
            "SELECT snowflake.cortex.complete(?, ?)",
            params=[model, prompt]
        ).collect()
        if not result:
            return "Sorry, received no response from the model."
        return result[0][0]
    except Exception as e:
        st.error(f"Error calling Cortex complete function: {e}")
        return "Sorry, I encountered an error trying to generate a response."

def format_dataframe_context(df: pd.DataFrame) -> str:
    """Formats the DataFrame into a string for the prompt context."""
    if df.empty:
        return "No DataFrame context provided."
    return df.to_string(index=False)


# --- Prompt Generation ---
def create_prompt(user_question: str, dataframe_context: str, chat_history: str) -> str:
    """Creates the prompt for the LLM."""
    prompt_template = f"""
[INST]
You are a helpful AI chat assistant. Answer the user's question based on the provided
chat history and the context data from customer reviews provided below.

Use the data in the <context> section to inform your answer about customer reviews or sentiments
if the question relates to it. If the question is general and not answerable from the context
or chat history, answer naturally. Do not explicitly mention "based on the context" unless necessary for clarity.

<chat_history>
{chat_history}
</chat_history>

<context>
{dataframe_context}
</context>

<question>
{user_question}
</question>
[/INST]

Answer:
"""
    prompt = prompt_template.strip()

    if st.session_state.debug:
        st.sidebar.text_area("Generated Prompt", prompt, height=400)
    return prompt

# --- Main Application Logic ---
def main():
    st.title("💬 Chatbot Augmented with DataFrame Context")

    initialize_session_state()
    setup_sidebar()

    context_df = load_context_dataframe(CONTEXT_TABLE)
    if context_df.empty and CONTEXT_TABLE:
        st.warning(f"Could not load data from {CONTEXT_TABLE} or it is empty. No DataFrame context will be used.")

    icons = {"assistant": "❄️", "user": "👤"}
    for message in st.session_state.messages:
        avatar = icons.get(message["role"])
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if user_input := st.chat_input("Ask something (e.g., about customer reviews)..."):
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user", avatar=icons["user"]):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar=icons["assistant"]):
            message_placeholder = st.empty()
            with st.spinner("Thinking..."):
                dataframe_context_str = format_dataframe_context(context_df)
                chat_history_str = get_formatted_chat_history()
                full_prompt = create_prompt(user_input, dataframe_context_str, chat_history_str)
                model_to_use = st.session_state.model_name
                generated_response = complete(model_to_use, full_prompt)
                message_placeholder.markdown(generated_response)

        st.session_state.messages.append({"role": "assistant", "content": generated_response})

# --- Entry Point ---
if __name__ == "__main__":
    try:
        session = get_active_session()
        main()
    except Exception as e:
        st.error(f"Failed to get active Snowflake session: {e}")
        st.info("Please ensure you are running this Streamlit app within a Snowflake environment.")
