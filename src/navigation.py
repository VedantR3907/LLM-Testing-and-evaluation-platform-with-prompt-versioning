import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
from streamlit_server_state import server_state
from database.users import delete_chat_history
from models.chat_models.config import reset_clients
import time

def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]


def make_sidebar(session):
    if get_current_page_name() == "1_🙎‍♂️_UserLogin.py":
        return
    with st.sidebar:
        if session:
            st.title("🤖 LLM EVALUATION")
            st.write("")
            st.write("")

            st.page_link("./pages/2_🌍_Main.py", label="Chat_Models", icon="🌍")
            st.page_link("./pages/3_📊_Charts.py", label="Charts", icon="📊")
            st.page_link("./pages/4_📝_Prompts.py", label="Saved_Prompts", icon="📝")

            st.write("")
            st.write("")

            cont = st.container()
            script = """<div id = 'chat_outer'></div>"""
            st.markdown(script, unsafe_allow_html=True)

            with cont:
                script = """<div id = 'chat_inner'></div>"""
                st.page_link("pages/5_📒_Settings.py", label="Settings", icon="⚙️")
                st.markdown(script, unsafe_allow_html=True)
                st.write(session.user.email)
                if st.button("Log out"):
                    delete_chat_history(session.user.id)
                    st.session_state.clear()
                    st.toast('Logged out successfully', icon='✅')
                    reset_clients()
                    time.sleep(1)
                    server_state['session'] = None
            styling = """<style>
                div[data-testid='stVerticalBlock']:has(div#chat_inner):not(:has(div#chat_outer)) {border-radius: 10px;
                padding: 10px;
                position:fixed;
                bottom:15px};
                </style>
                """
            st.markdown(styling, unsafe_allow_html=True) 

        elif not session:
            st.switch_page("1_🙎‍♂️_UserLogin.py")