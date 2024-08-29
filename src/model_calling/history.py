import streamlit as st
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from database.interaction_history import get_history

def display_chat_history(ctx, col, model_id, model_name, user_id):
    add_script_run_ctx(threading.current_thread(), ctx)

    with col.container():
        st.header(model_name, divider='green')
    
    chat_history_for_model = get_history(user_id, model_id, 50, model_name)

    for message in chat_history_for_model:

        if 'gpt' in model_name:
            role, content = message["role"], message["content"]
            avatar_path = '../assests/openai.png'
        
        elif 'gemini' in model_name:
            role, content = message['role'], message['parts'][0]['text']
            avatar_path = '../assests/google.png'
        
        elif 'llama' in model_name:
            role, content = message["role"], message["content"]
            avatar_path = '../assests/meta.png'
        
        elif 'mixtral' in model_name:
            role, content = message["role"], message["content"]
            avatar_path = '../assests/mistral.png'
        
        elif 'gemma' in model_name:
            role, content = message["role"], message["content"]
            avatar_path = '../assests/gemma.png'
        
        elif 'claude' in model_name:
            role, content = message["role"], message["content"]
            if content == 'Hi dummyved3907':
                content = ''
            avatar_path = '../assests/claude.png'
            
        if role == "user" and content != '':
            with col.chat_message("Human", avatar='../assests/user.png'):
                st.markdown(content)
        elif role == 'assistant' or role == 'model':
            with col.chat_message("AI",avatar=avatar_path):
                st.markdown(content)

def display_message(ctx, col, prompt, generator, model_name):
    add_script_run_ctx(threading.current_thread(), ctx)

    if prompt != '':
        if 'gpt' in model_name:
            avatar_path = '../assests/openai.png'
        elif 'gemini' in model_name:
            avatar_path = '../assests/google.png'
        elif 'llama' in model_name:
            avatar_path = '../assests/meta.png'
        elif 'mixtral' in model_name:
            avatar_path = '../assests/mistral.png'
        elif 'gemma' in model_name:
            avatar_path = '../assests/gemma.png'
        elif 'claude' in model_name:
            avatar_path = '../assests/claude.png'

        with col.chat_message("HUMAN", avatar='../assests/user.png'):
            st.markdown(prompt)
        with col.chat_message("AI",avatar=avatar_path):
            st.write(generator)

