import streamlit as st
from database.users import fetch_user_prompts
from database.models_db import update_model_uservotes

def get_prompts(user_id):
        if "all_prompts" not in st.session_state:
            all_prompts = fetch_user_prompts(user_id)
            all_prompts = [prompt['user_message'] for prompt in all_prompts.data]
            st.session_state['all_prompts'] = all_prompts
        if 'current_prompt' in st.session_state and st.session_state['current_prompt'] != None and (not st.session_state['all_prompts'] or st.session_state['all_prompts'][-1] != st.session_state['current_prompt']):
            st.session_state['all_prompts'].append(st.session_state['current_prompt'])
        return st.session_state['all_prompts']

def submitted_user_vote(model_name, user_prompt):
    update_model_uservotes(model_name)
    st.session_state['last_voted_prompt'] = user_prompt