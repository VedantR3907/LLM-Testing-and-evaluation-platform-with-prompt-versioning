import streamlit as st
from streamlit_server_state import server_state
from navigation import make_sidebar
from models.models_verify.claude import claude_verify
from models.models_verify.openai import openai_verify
from models.models_verify.gemini import gemini_verify
from models.models_verify.groq import groq_verify

from  database.users import verify_api_key
from  models.chat_models.config import reset_clients
import time
session = server_state.get('session')

make_sidebar(session)

user_id = session.user.id

st.header("🔐 API Keys")

# CSS to style the button and subheaders
with open("src/styles/settings.css") as f:
        css = f.read()

# Adding custom CSS to style the containers and make them scrollable
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
# OpenAI API Key

col1, col2 = st.columns([1, 1])
openai_key = col1.text_input("OPENAI", placeholder='*********************', type='password')
col2.markdown('<span id="openai-button-after"></span>', unsafe_allow_html=True)
if col2.button("Verify →", key='openai'):
    try:
        if len(openai_key) > 3:
            # Get the current time
            current_time = time.time()

            # Check if 'openai_last_verify_time' is in the session state and if less than 60 seconds have passed since the last verification attempt
            if 'openai_last_verify_time' in st.session_state and current_time - st.session_state['openai_last_verify_time'] < 1:
                remaining_time = 60 - (current_time - st.session_state['openai_last_verify_time'])
                st.toast(f"Wait for {remaining_time:.0f} seconds until you can verify again.", icon='❌')
            else:
                # Store the current time as the time of the last verification attempt
                # Initialize session state for API key verification
                if 'openai_verify_apikey' not in st.session_state:
                    st.session_state['openai_verify_apikey'] = [0, False]
                st.session_state['openai_last_verify_time'] = current_time

                st.session_state['openai_verify_apikey'][0] += 1
                response, messages, response_time = openai_verify(api_key=openai_key)
                if response:
                    if st.session_state['openai_verify_apikey'][1] == False:  # noqa: E712
                        verify_api_key(user_id, 'openai', openai_key)
                        st.session_state['openai_verify_apikey'][1] = True
                        reset_clients()
                        st.toast("Key verified", icon='✅')
        else:
            st.toast("Please enter a valid key before verifying", icon='❌')
    except Exception:
        st.toast("API KEY is not valid", icon='❌')

st.write('')
st.write('')
# Gemini API Key

col3, col4 = st.columns([1, 1])
gemini_key = col3.text_input("GEMINI", placeholder='*********************', type='password')
col4.markdown('<span id="gemini-button-after"></span>', unsafe_allow_html=True)
if col4.button("Verify →", key='gemini'):
    try:
        if len(gemini_key) > 3:
            # Get the current time
            current_time = time.time()

            # Check if 'gemini_last_verify_time' is in the session state and if less than 60 seconds have passed since the last verification attempt
            if 'gemini_last_verify_time' in st.session_state and current_time - st.session_state['gemini_last_verify_time'] < 60:
                remaining_time = 60 - (current_time - st.session_state['gemini_last_verify_time'])
                st.toast(f"Wait for {remaining_time:.0f} seconds until you can verify again.", icon='❌')
            else:
                # Store the current time as the time of the last verification attempt
                if 'gemini_verify_apikey' not in st.session_state:
                    st.session_state['gemini_verify_apikey'] = [0, False]
                st.session_state['gemini_last_verify_time'] = current_time

                st.session_state['gemini_verify_apikey'][0] += 1
                response = gemini_verify(api_key=gemini_key)
                if response:
                    if st.session_state['gemini_verify_apikey'][1] == False:  # noqa: E712
                        verify_api_key(user_id, 'gemini', gemini_key)
                        st.session_state['gemini_verify_apikey'][1] = True
                        reset_clients()
                        st.toast("Key verified", icon='✅')
        else:
            st.toast("Please enter a valid key before verifying", icon='❌')
    except Exception:
        st.toast("API KEY is not valid", icon='❌')

st.write('')
st.write('')

col5, col6 = st.columns([1, 1])
groq_key = col5.text_input("GROQ", placeholder='*********************', type='password')
col6.markdown('<span id="groq-button-after"></span>', unsafe_allow_html=True)
if col6.button("Verify →", key='groq'):
    try:
        if len(groq_key) > 3:
            # Get the current time
            current_time = time.time()

            # Check if 'groq_last_verify_time' is in the session state and if less than 60 seconds have passed since the last verification attempt
            if 'groq_last_verify_time' in st.session_state and current_time - st.session_state['groq_last_verify_time'] < 10:
                remaining_time = 60 - (current_time - st.session_state['groq_last_verify_time'])
                st.toast(f"Wait for {remaining_time:.0f} seconds until you can verify again.", icon='❌')
            else:
                # Store the current time as the time of the last verification attempt
                if 'groq_verify_apikey' not in st.session_state:
                    st.session_state['groq_verify_apikey'] = [0, False]
                st.session_state['groq_last_verify_time'] = current_time
                st.session_state['groq_verify_apikey'][0] += 1

                response = groq_verify(api_key=groq_key)
                if response:
                    if st.session_state['groq_verify_apikey'][1] == False:  # noqa: E712
                        verify_api_key(user_id, 'groq', groq_key)
                        st.session_state['groq_verify_apikey'][1] = True
                        reset_clients()
                        st.toast("Key verified", icon='✅')
        else:
            st.toast("Please enter a valid key before verifying", icon='❌')
    except Exception:
        st.toast("API KEY is not valid", icon='❌')

st.write('')
st.write('')

col7, col8 = st.columns([1, 1])
claude_key = col7.text_input("CLAUDE", placeholder='*********************', type='password')
col8.markdown('<span id="claude-button-after"></span>', unsafe_allow_html=True)
if col8.button("Verify →", key='claude'):
    try:
        if len(claude_key) > 3:
            # Get the current time
            current_time = time.time()

            # Check if 'claude_last_verify_time' is in the session state and if less than 60 seconds have passed since the last verification attempt
            if 'claude_last_verify_time' in st.session_state and current_time - st.session_state['claude_last_verify_time'] < 60:
                remaining_time = 60 - (current_time - st.session_state['claude_last_verify_time'])
                st.toast(f"Wait for {remaining_time:.0f} seconds until you can verify again.", icon='❌')
            else:
                # Store the current time as the time of the last verification attempt
                if 'claude_verify_apikey' not in st.session_state:
                    st.session_state['claude_verify_apikey'] = [0, False]
                st.session_state['claude_last_verify_time'] = current_time
                st.session_state['claude_verify_apikey'][0] += 1

                response = claude_verify(api_key=claude_key)
                if response:
                    if st.session_state['claude_verify_apikey'][1] == False:  # noqa: E712
                        verify_api_key(user_id, 'claude', claude_key)
                        st.session_state['claude_verify_apikey'][1] = True
                        reset_clients()
                        st.toast("Key verified", icon='✅')
        else:
            st.toast("Please enter a valid key before verifying", icon='❌')
    except Exception:
        st.toast("API KEY is not valid", icon='❌')