import streamlit as st
import requests
import json
import time

OLLAMA_API_URL = "http://localhost:11434/api/generate"
HEADERS = {"Content-Type": "application/json"}

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""
if "mode" not in st.session_state:
    st.session_state["mode"] = "Code Generation"

def query_ollama_api(prompt):
    """
    Sends a prompt to the Ollama API and returns the response.
    """
    payload = {
        "model": "CodeAssist",
        "prompt": prompt,
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_API_URL, headers=HEADERS, data=json.dumps(payload))
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response received.")
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def send_message():
    """
    Handles sending a message and getting a response from the API.
    """
    if st.session_state.user_input.strip():

        st.session_state["chat_history"].append({"role": "user", "content": st.session_state.user_input})

        # Creates the appropriate prompt based on the selected mode
        if st.session_state["mode"] == "Code Generation":
            prompt = f"Write Approach and Generate Python code for the following request:\n\n{st.session_state.user_input}\n\nInclude comments, test cases, and expected output."
        else:  # Debug Code
            prompt = f"Debug the following Python code:\n\n{st.session_state.user_input}\n\nEnsure the corrected code runs without errors and explain changes."

        with st.spinner("Generating response..."):
            assistant_response = query_ollama_api(prompt)

        # Adds assistant response to chat history
        st.session_state["chat_history"].append({"role": "assistant", "content": assistant_response})

        # Clear the user input field
        st.session_state.user_input = ""

def display_chat():
    """
    Displays the conversation history with proper formatting for user and assistant responses.
    """
    for chat in st.session_state["chat_history"]:
        if chat["role"] == "user":
            st.markdown(
                f"""
                <div style='text-align: right; background-color: #f1f1f1; color: #666666; padding: 10px; margin: 5px 0; border-radius: 15px; display: inline-block;'>
                    {chat["content"]}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            response = chat["content"]
            # Split the response into text and code segments
            if "```" in response:
                parts = response.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # Non-code parts
                        st.markdown(
                            f"""
                            <div style='text-align: left; background-color: #ffffff; color: #333333; padding: 10px; margin: 5px 0; border-radius: 15px; display: inline-block;'>
                                {part.strip()}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:  # Code parts
                        st.code(part.strip(), language="python")
            else:
                st.markdown(
                    f"""
                    <div style='text-align: left; background-color: #ffffff; color: #333333; padding: 10px; margin: 5px 0; border-radius: 15px; display: inline-block;'>
                        {response.strip()}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# Sidebar for mode selection
st.sidebar.title("Code Assist")
if st.sidebar.button("Code Generation", use_container_width=True):
    st.session_state["mode"] = "Code Generation"
if st.sidebar.button("Debug Code", use_container_width=True):
    st.session_state["mode"] = "Debug Code"

# Main App
st.title("Code Assist")
st.write("Chat with the assistant about coding tasks, and get Python code snippets or explanations!")

# Display chat history
st.markdown("<hr>", unsafe_allow_html=True)
display_chat()

# Footer container for input and button
footer_container = st.container()
with footer_container:
    footer_container.markdown(
        """
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #f0f0f0;
            padding: 10px;
            box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([4, 1])
    with col1:
        placeholder_text = (
            "Enter your code here..." if st.session_state["mode"] == "Debug Code" else "Enter your prompt here..."
        )
        st.text_input(
            "Your Message",
            placeholder=placeholder_text,
            key="user_input",
            label_visibility="collapsed",
        )
    with col2:
        button_text = "Debug" if st.session_state["mode"] == "Debug Code" else "Send"
        st.button(button_text, use_container_width=True, on_click=send_message)
