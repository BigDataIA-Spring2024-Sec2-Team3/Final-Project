import datetime
import json
import openai
import os
import datetime
import json
import openai
import os
from dotenv import load_dotenv
import pandas as pd
from pinecone import Pinecone, ServerlessSpec
import re
from typing import List, Union
import streamlit as st
import requests

st.title("ChatGPT-like clone")
FASTAPI_URL= 'http://fastapi2:8000/chat/'
 
 
# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
 
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
 
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
 
# Accept user input
user_input = st.chat_input("What is up?")
if user_input:
    with st.spinner("Loading"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)
    
        # Get the previous conversation history (including both user and assistant messages)
        history_content = "\n".join([message["content"] for message in st.session_state.messages])
        st.write(history_content)
    
        # Execute the agent
        try:
            chat = {
                'user_input': user_input,
                'history': history_content,
            }

            response = requests.post(FASTAPI_URL, json=chat)
            # st.write(response)

            if response.status_code == 200:
                # get response
                agent_output = response.json()['response']
                st.write("Response:", agent_output)
            else:
                st.error("Failed to get response from the server")
        
        except requests.exceptions.HTTPError as err:
            error_detail = err.response.json().get('detail', 'Unknown error')
            st.error(f"HTTP Error: {error_detail}")  # Display HTTP error details

    
        # Add agent response to chat history
        st.session_state.messages.append({"role": "assistant", "content": agent_output})
    
        # Display agent response in chat message container
        with st.chat_message("assistant"):
            st.markdown(agent_output)
