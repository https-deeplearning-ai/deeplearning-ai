import streamlit as st

# Create tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

with tab1:
    st.title("Welcome to Tab 1")
    st.write("This is the content of the first tab.")

with tab2:
    st.title("Welcome to Tab 2")
    st.write("This is the content of the second tab.")
