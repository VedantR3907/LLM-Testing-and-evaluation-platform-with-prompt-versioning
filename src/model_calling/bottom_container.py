from streamlit_extras.bottom_container import bottom
from version_control.SaveVersion import Saving_Version
from database.interaction_history import append_message, get_history  # noqa: F401
from database.models_db import fetch_model_details, update_model_uservotes # noqa: F401
from database.users import fetch_user_prompts # noqa: F401
from database.prompts import insert_saved_prompt, insert_version_prompt, fetch_saved_prompt_titles
from evaluation.gpt4_evaluation.evaluation_gpt4 import gpt4_eval
from evaluation.custom_evaluation.custom_eval import custom_eval
from model_calling.fetch_data import get_prompts, submitted_user_vote
import streamlit as st
import os
from streamlit_server_state import server_state # noqa: F401
from dotenv import load_dotenv

load_dotenv()

def create_bottom_container(user_id, MODEL_CHOICES):
    with bottom():
        
        popover_col, input_col, select_col = st.columns([1, 9, 1])



        with input_col:
            user_prompt = st.chat_input("Write a question")
            if user_prompt:
                st.session_state["current_prompt"] = user_prompt  # Update current prompt in session state

        

        with popover_col:
            with st.popover("📖"):
                st.header("Save Prompts")
                # Add your popover menu content here
                options = ["Save Current Prompt", "Save Previous Prompt"]
                selected_option = st.selectbox("\u00A0", options, index=0)  # Set default value to "Save Current Prompt"
                all_prompts = get_prompts(user_id)
                
                if all_prompts:
                    current_prompt = st.session_state.get("current_prompt")
                    if all_prompts and all_prompts[-1] == current_prompt:
                        previous_prompts = all_prompts[:-1] if len(all_prompts) > 1 else []
                    else:
                        previous_prompts = all_prompts
                else:
                    current_prompt = ''
                    previous_prompts = []

                if selected_option == options[0]:  # Save Current Prompt
                    prompt_to_save = current_prompt
                elif selected_option == options[1]:  # Save Previous Prompt
                    prompt_to_save = st.selectbox("Select a previous prompt to save:", previous_prompts)

                version_options = ["Save Prompt as New Version", "Add to Existing Version"]
                selected_version_option = st.selectbox("\u00A0", version_options)
                if st.session_state.get('current_prompt') is None:
                    st.warning("Please write a prompt to save it.")
                else:
                    if selected_version_option == version_options[0]:  # Save Prompt as New Version
                        if prompt_to_save:
                            prompt_title = st.text_input("Enter Prompt Title:", disabled=st.session_state.get('current_prompt') is None)
                            if st.button('Save as New Version'):
                                try:
                                    insert_saved_prompt(user_id, prompt_title, prompt_to_save)  # Save the prompt in the Saved_Prompts table
                                    # Refresh the saved prompt titles in the session state
                                    st.session_state["saved_prompt_titles"] = fetch_saved_prompt_titles(user_id)
                                    st.toast(f'Prompt saved with prompt title: - {prompt_title}', icon='✅')

                                    if 'check_rerun_prompts' not in st.session_state:
                                        st.session_state['check_rerun_prompts'] = True
                                    st.session_state['check_rerun_prompts'] = True
                                except Exception as e:
                                    st.warning("Prompt Already Saved or error saving version")

                    elif selected_version_option == version_options[1]:  # Add to Existing Version
                        # Check if saved_prompt_titles is already in session state
                        if "saved_prompt_titles" not in st.session_state:
                            # If not, fetch the saved prompt titles and store them in session state
                            st.session_state["saved_prompt_titles"] = fetch_saved_prompt_titles(user_id)
                        # Use the saved prompt titles from session state to populate the selectbox
                        existing_version = st.selectbox("Select existing version:", st.session_state["saved_prompt_titles"], format_func=lambda x: x['title'], disabled=st.session_state.get('current_prompt') is None)
                        if st.button('Add to Existing Version'):

                            new_version_number = Saving_Version(existing_version['id'], prompt_to_save)
                            insert_version_prompt(existing_version['id'], prompt_to_save, new_version_number)
                            st.session_state["saved_prompt_titles"] = fetch_saved_prompt_titles(user_id)
                            st.toast(f'Prompt saved with verison: - {new_version_number}', icon='✅')

                            if 'check_rerun_prompts' not in st.session_state:
                                st.session_state['check_rerun_prompts'] = True
                            st.session_state['check_rerun_prompts'] = True

        with select_col:
            with st.popover("🤖"):
                selected_models = st.multiselect("Select models:", MODEL_CHOICES, default=st.session_state["selected_models"], placeholder='Choose models', max_selections=4)
                if selected_models != st.session_state["selected_models"]:
                    st.session_state["selected_models"] = selected_models  # Update session state
                    st.rerun()  # Manually trigger a rerun
                if len(selected_models) < 1:
                    st.write("SELECT AT LEAST ONE MODEL")
        
        # Check if the user has written a prompt and not voted for it yet
        vote, menu = st.columns([30, 4])

        with vote.popover("🗳️ Vote"):
        # Check if the user has written a prompt and not voted for it yet
            if 'current_prompt' in st.session_state and st.session_state['current_prompt'] and ('last_voted_prompt' not in st.session_state or st.session_state['last_voted_prompt'] != st.session_state['current_prompt']) and ('submit_clicked' not in st.session_state) and len(selected_models) >= 2:
                # Get the models selected by the user
                selected_models = st.session_state["selected_models"]
                
                # Create radio buttons for the selected models
                model_vote = st.radio("Vote for a model:", options=selected_models, key='model_vote')
                
                # Create a submit button
                if st.button('Submit Vote'):
                    # Store the voted model and the current prompt in the session state when the submit button is clicked
                    st.session_state['voted_model'] = model_vote
                    submitted_user_vote(model_vote, st.session_state['current_prompt'])
                    st.session_state['last_voted_prompt'] = st.session_state['current_prompt']
                    
                    st.rerun()
            elif 'submit_clicked' in st.session_state:
                st.write("Already Voted for the current prompt")  # Empty content
            elif len(selected_models) < 2:
                st.write("Please select at least two models before voting.")
            else:
                st.write("Please write a prompt before voting.")
        
        with menu.popover("🖥️ Eval"):
        # Check if the user has written a prompt and not voted for it yet
            # Check if the user has written a prompt and not voted for it yet
             # Get the categories from the session state
            current_selected_models = st.session_state.get("selected_models", [])
            previous_selected_models = st.session_state.get("previous_selected_models", [])
            if set(current_selected_models) != set(previous_selected_models):
                st.warning("The models selected for evaluation have changed. Please generate new responses before performing the evaluation.")
            else:
                if "categories" not in st.session_state:
                    st.session_state["categories"] = ["General_Knowledge", "Code_Generation", "Translation", "Text_Generation"]
                categories = st.session_state["categories"]

                eval_method = st.selectbox("Select Category", ['Custom_Evaluation', 'GPT4_Evaluation'])

                selected_category = st.selectbox("Select a category", categories)

                st.session_state['selected_category'] = selected_category

                ref_sentence = ""
                if selected_category == "Translation" and eval_method == "Custom_Evaluation":
                    ref_sentence = st.text_input("Enter reference sentence:")

                if st.button('Submit Menu'):

                    if 'current_prompt' in st.session_state and st.session_state['current_prompt']:
                    
                        

                        # Create a submit button
                        # Store the voted model and the current prompt in the session state when the submit button is clicked
                        if eval_method == 'GPT4_Evaluation':
                            st.session_state['prompt_gpt4'] = st.session_state['current_prompt']
                            st.session_state['submit_clicked_eval_gpt4'] = True  # Track GPT-4 evaluation submission
                        else:
                            st.session_state['prompt_custom'] = st.session_state['current_prompt']
                            st.session_state['submit_clicked_eval_custom'] = True  # Track custom evaluation submission
                        st.session_state['last_eval_prompt'] = st.session_state['current_prompt']
                        model_responses = [st.session_state.get(f'{model}_response', '') for model in selected_models]
                        models_with_output = [model for model, response in zip(selected_models, model_responses) if response]
                        if eval_method == 'Custom_Evaluation':
                            response_custom_eval = custom_eval(models_with_output, model_responses, ref_sentence, st.session_state['current_prompt'], selected_category, os.environ.get("GROQ_API_KEY"))
                            st.session_state['response_custom_eval'] = response_custom_eval
                        else:
                            response_gpt4_eval = gpt4_eval(models_with_output, selected_category, st.session_state['current_prompt'], model_responses, user_id)
                            st.session_state['response_gpt4_eval'] = response_gpt4_eval
                        st.warning("Evaluation can take few seconds for the respond")
                        st.rerun()
                    else:
                        st.write("Please write a prompt before voting.")
                
    return user_prompt, selected_models