import streamlit as st
import pyperclip
from st_keyup import st_keyup
from version_control.VersionData import fetch_all_prompt_versions
from navigation import make_sidebar
from  database.prompts import fetch_saved_prompt_titles
from  database.prompts import delete_version_prompt, delete_saved_prompt, delete_all_version_prompts
from streamlit_server_state import server_state

session = server_state.get('session')

make_sidebar(session)
# Title for the Streamlit app
st.title("Saved Prompts")

userid =  session.user.id 

if 'userid' in st.session_state and st.session_state['userid'] != userid:
    st.session_state['check_rerun_prompts'] = True

st.session_state['userid'] = userid

if 'check_rerun_prompts' in st.session_state and st.session_state['check_rerun_prompts'] == True:
    data = fetch_all_prompt_versions(userid)
    st.session_state['version_prompts_data'] = data
    st.session_state['check_rerun_prompts'] = False
else:
    if 'version_prompts_data' not in st.session_state:
        data = fetch_all_prompt_versions(userid)
        st.session_state['version_prompts_data'] = data
    else:
        data = st.session_state['version_prompts_data']

with open("styles/prompts.css") as f:
        css = f.read()

# Adding custom CSS to style the containers and make them scrollable
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Container for the entire UI
with st.container() as main_container:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Container for the search bar to make it prominent
    with st.container():
        search_query = st_keyup(label="Search",key="search_query", placeholder="Write your prompt...")

    # Container for the selection box and the prompts
    with st.container():
        # Custom layout to make search bar more prominent
        col1, col2 = st.columns([1, 3])

        # Convert data keys (base prompts) to a list for selectbox
        base_prompts = sorted(list(data.keys()))
        # Selection box for base prompts
        with col1:
            if 'selected_prompt_title' not in st.session_state and len(base_prompts) != 0:
                st.session_state.selected_prompt_title = base_prompts[0]
            st.session_state.selected_prompt_title = st.selectbox("Select a Base Prompt", base_prompts)

        # Function to display version prompts
        def display_version_prompts(version_prompts):
            filtered_version_prompts = version_prompts.copy()

            if search_query:
                # Filter base prompt
                if search_query.lower() not in version_prompts["prompt"].lower():
                    filtered_version_prompts["prompt"] = ""

                # Filter version prompts
                filtered_version_prompts['versions'] = [vp for vp in version_prompts['versions'] if search_query.lower() in vp["Version"].lower() or search_query.lower() in vp["Prompt"].lower()]

            # If both base prompt and versions are empty, display a warning message
            if not filtered_version_prompts["prompt"] and not filtered_version_prompts['versions']:
                st.info("No Prompt with search results", icon="💡")
                return

            # Display the base_prompt alone if it's not empty
            if filtered_version_prompts["prompt"]:
                container_col, basebutton_col, delete_button_col = st.columns([5, 1, 1])
                with container_col:
                    st.markdown(f'<div class="scrollable-container small-container"><strong>Base Prompt:</strong> {filtered_version_prompts["prompt"]}</div>', unsafe_allow_html=True)
                with basebutton_col:
                    if st.button(f"📋"):
                        # Copy the base prompt to the clipboard
                        pyperclip.copy(data[st.session_state.selected_prompt_title]['prompt'])
                        st.toast("Prompt Copied", icon='✅')

            for vp in filtered_version_prompts['versions']:
                container_col, button_col, delete_button_col = st.columns([10.5, 1, 1])
                container_height_class = "large-container" if len(vp["Prompt"]) > 100 else "small-container"
                with container_col:
                    # Display the version prompts
                    st.markdown(f'<div class="scrollable-container {container_height_class}"><strong>Version {vp["Version"]}:</strong> {vp["Prompt"]}</div>', unsafe_allow_html=True)
                with button_col:
                    if st.button("📋", key=f'copy-{vp["Version"]}'):
                        pyperclip.copy(vp["Prompt"])
                        st.toast("Prompt Copied", icon='✅')
                
                with delete_button_col:
                    if st.button("🗑️", key=f'delete-{vp["Version"]}'):
                        delete_version_prompt(data[st.session_state.selected_prompt_title]['prompt_id'], vp["Version"])
                        st.toast("Prompt Deleted", icon='✅')
                        st.session_state['check_rerun_prompts'] = True
                        st.rerun()

        # When a base prompt is selected, display its version prompts in a container format with copy buttons
        if st.session_state.selected_prompt_title:
            with col2:
                # Create two columns: one for the base prompt and one for the copy button
                prompt_col, button_col = st.columns([5, 1])
                
                with prompt_col:
                    st.markdown(f'<div class="base-prompt-container"><h1>{st.session_state.selected_prompt_title}</h1></div>', unsafe_allow_html=True)

                with button_col:
                    if st.button("🗑️"):
                        # Get the id of the selected prompt
                        prompt_id = data[st.session_state.selected_prompt_title]['prompt_id']
                        
                        delete_all_version_prompts(prompt_id)
                        delete_saved_prompt(prompt_id)

                        st.session_state["saved_prompt_titles"] = fetch_saved_prompt_titles(userid)

                        st.session_state['check_rerun_prompts'] = True
                        st.rerun()
                
                version_prompts = data[st.session_state.selected_prompt_title]
                if version_prompts:
                    display_version_prompts(version_prompts)
                else:
                    st.warning("There are no version prompts for this base prompt.")
                    

    st.markdown('</div>', unsafe_allow_html=True)