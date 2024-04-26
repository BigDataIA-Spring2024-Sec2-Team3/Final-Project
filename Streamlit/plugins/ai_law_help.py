import datetime
import json
import openai
from dotenv import load_dotenv
import pandas as pd
import re
from typing import List, Union
import streamlit as st
import requests
import os
import boto3

def ai_law_help():
    # load_dotenv()
    # number_of_files = st.number_input("Please enter the number of PDF files", min_value=1, max_value=10, step=1)

    # uploaded_files = None

    # if number_of_files > 0:
    #     uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    #     if uploaded_files is not None and len(uploaded_files) == number_of_files:
    #         st.success("Uploading files...")
            
    #         # Create an S3 resource
    #         s3_resource = boto3.resource('s3',aws_access_key_id = aki, aws_secret_access_key =ak)

    #         # Iterate through the uploaded files and upload to S3
    #         s3_urls = []  # Store S3 URLs
    #         for file in uploaded_files:
    #             file_bytes = file.read()
    #             file_name = file.name  # Get the original file name

    #             # Upload the file to S3
    #             s3_resource.Bucket(BUCKET_NAME).put_object(
    #                 Key=file_name,
    #                 Body=file_bytes
    #             )
                
    #             # Construct S3 URL
    #             s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"
    #             s3_urls.append(s3_url)

    #         st.success("All files uploaded!")

    # BUCKET_NAME = os.getenv('KB_BUCKET_NAME')
    # BUCKET_NAME = os.getenv("BUCKET_NAME")
    # aki = os.getenv("AWS_AK")
    # ak = os.getenv("AWS_SK")

    st.title("ChatGPT-like clone")
    FASTAPI_URL= 'http://0.0.0.0:8000/chat/'
    
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


if __name__ == '__main__':
    ai_law_help()