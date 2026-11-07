import os

import streamlit as st
from dotenv import load_dotenv

from anthropic import Anthropic

MODEL_NAME = "claude-sonnet-5-5"

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("Anthropic api key is missing")
client = Anthropic(api_key=api_key)

st.set_page_config(page_tile="Claude streaming chat", page_icon=" ")

st.title("Claude Streaming UI (streamlit)")
st.write("Real time token by token streaming  using Claude API and Streamlit")

## Session state

if "message" not in st.session_state:
    st.session_state.messages =[]

## show chat history

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): 
        st.markdown(msg["content"])

# Streaming function

def stream_claude(messages_for_model):
    # Calls Claude with streaming an yields text chunks
    with client.messages.stream(
        model = MODEL_NAME,
        max_tokens = 500,
        messages = messages_for_model,
    ) as stream:
        for text in stream.text_stream:
            yield text
        _ = stream.get_final_message()

# input
prompt = st.chat_input("Send a message")

if prompt: 
    st.session_state.messages.append({"role":"user","content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response =""

        messages_for_model = [
        {"role":m["role"],"content" : m["content"]}
        for m in st.session_state.messages
        ]

        for chunk in stream_claude(messages_for_model):
            full_response += chunk
            message_placeholder.markdown(full_response)

    st.session_state.message.append({"role": "assistant","content": full_response})        

        
        