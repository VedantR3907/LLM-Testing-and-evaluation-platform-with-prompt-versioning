import sys
import os
import time
import threading
import streamlit as st
import concurrent.futures
from navigation import make_sidebar
from models.chat_models.openai import openai_model
from models.chat_models.gemini import gemini_model
from models.chat_models.claude import claude_model
from models.chat_models.llama import llama_model
from models.chat_models.mixrtal import mistral_model
from models.chat_models.gemma import gemma_model
from evaluation.all_evaluation.openai import OPENAI_EVAL
from evaluation.all_evaluation.gemini import GOOGLE_EVAL
from evaluation.all_evaluation.claude import CLAUDE_EVAL
from evaluation.all_evaluation.llama import LLAMA_EVAL
from evaluation.all_evaluation.gemma import GEMMA_EVAL
from evaluation.all_evaluation.mixtral import MISTRAL_EVAL
from streamlit_extras.grid import grid
from streamlit_server_state import server_state
SCRIPT_DIR = os.path.dirname(os.path.abspath('assests'))
sys.path.append(os.path.dirname(SCRIPT_DIR))
sys.path.append('./version_control')
from streamlit.runtime.scriptrunner import add_script_run_ctx  # noqa: E402
from database.interaction_history import append_message  # noqa: E402
from database.models_db import fetch_model_details  # noqa: E402
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx  # noqa: E402
from dotenv import load_dotenv # noqa: E402
from model_calling.history import display_chat_history, display_message # noqa: E402
from model_calling.popovers import display_popovers # noqa: E402
from model_calling.bottom_container import create_bottom_container # noqa: E402
################################################################################################################
MAX_HISTORY_LENGTH = 5

st.set_page_config(layout='wide')

session = server_state.get('session')

make_sidebar(session)

EVAL_CLASSES = {
    "openai": OPENAI_EVAL,
    "gemini": GOOGLE_EVAL,
    "llama": LLAMA_EVAL,
    "mistral": MISTRAL_EVAL,
    "gemma": GEMMA_EVAL,
    "claude": CLAUDE_EVAL
}

# Initialize MODEL_DETAILS and MODEL_CHOICES if they are not in the session state
if "MODEL_DETAILS" not in st.session_state:
    st.session_state["MODEL_DETAILS"] = fetch_model_details()

MODEL_DETAILS = st.session_state["MODEL_DETAILS"]

if "MODEL_CHOICES" not in st.session_state:
    st.session_state["MODEL_CHOICES"] = list(MODEL_DETAILS.keys())

MODEL_CHOICES = st.session_state["MODEL_CHOICES"]

# Initialize the evaluation object for each model
for model_name, eval_class in EVAL_CLASSES.items():
    if f"{model_name}_eval" not in st.session_state:
        st.session_state[f"{model_name}_eval"] = eval_class()

openai_eval = st.session_state["openai_eval"]
google_eval = st.session_state["gemini_eval"]
claude_eval = st.session_state["claude_eval"]
gemma_eval = st.session_state["gemma_eval"]
llama_eval = st.session_state["llama_eval"]
mistral_eval = st.session_state["mistral_eval"]

load_dotenv()
################################################################################################################

def call_chain(ctx, model_name, prompt):
    if prompt != '':
        model_id = MODEL_DETAILS.get(model_name)
        add_script_run_ctx(threading.current_thread(), ctx)
        try:
            temperature = st.session_state.get(f"{model_name}_temperature", 0.5)
            p_value = st.session_state.get(f"{model_name}_pvalue", 0.5)
            max_tokens = st.session_state.get(f"{model_name}_max_output_tokens", 150)

            # Pass these settings to the model function call
            response_content = ""  # Initialize to accumulate streamed response
                    
            if 'gpt' in model_name:
                response, messages, response_time = openai_model(model_name, model_id, user_id, prompt, temperature=temperature, p_value=p_value, max_tokens=max_tokens)
                if response is None:
                    st.error(messages)
                    return

                for i in response:
                    res = i.choices[0].delta.content
                    if res is not None:
                        response_content += res  # Accumulate response
                        yield res

                st.session_state[f'{model_name}_response'] = response_content        
                prompt_token = openai_eval.openai_token_count(model_name, prompt)
                response_token = openai_eval.openai_token_count(model_name, response_content)
                cost = openai_eval.cal_pricing_token(model_name, prompt_token, response_token)
                
            elif 'gemini' in model_name:
                gemini_models, response, messages, response_time = gemini_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens)

                if response is None:
                    st.error(messages)
                    return
                try:
                    for chunk in response:
                        for j in chunk.text:
                            res = j
                            if res is not None:
                                response_content += res  # Accumulate response
                                yield res
                                time.sleep(0.001)


                    st.session_state[f'{model_name}_response'] = response_content
                    prompt_token = google_eval.gemini_token_count(gemini_models, prompt)
                    response_token = google_eval.gemini_token_count(gemini_models, response_content)
                    cost = 0

                except Exception as e:  # noqa: F841
                    st.warning("Low Max_Output_Tokens")
                    prompt_token = 0
                    response_token = 0
                    cost = 0
                    response_time = 0
            
            elif 'llama' in model_name:


                response, messages, response_time = llama_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens)
                if response is None:
                    st.error(messages)
                    return
                
                if response is None:
                    st.error(messages)
                    return

                for i in response:
                    res = i.choices[0].delta.content
                    if res is not None:
                        response_content += res  # Accumulate response
                        yield res
                    else:
                        prompt_token = llama_eval.llama_token_count(prompt)
                        response_token = i.x_groq.usage.completion_tokens
                        cost = 0
                
                st.session_state[f'{model_name}_response'] = response_content
                prompt_token = llama_eval.llama_token_count(prompt)
                response_token = llama_eval.llama_token_count(response_content)
                cost = 0
            
            elif 'mixtral' in model_name:

                response, messages, response_time = mistral_model(model_name, model_id, user_id, prompt, temperature=temperature, p_value=p_value, max_tokens=max_tokens)
                if response is None:
                    st.error(messages)
                    return

                for i in response:
                    res = i.choices[0].delta.content
                    if res is not None:
                        response_content += res  # Accumulate response
                        yield res
                    else:
                        prompt_token = mistral_eval.mistral_token_count(prompt)
                        response_token = i.x_groq.usage.completion_tokens
                        cost = 0

                st.session_state[f'{model_name}_response'] = response_content

            elif 'gemma' in model_name:
                response, messages, response_time = gemma_model(model_name, model_id, user_id, prompt, temperature=temperature, p_value=p_value, max_tokens=max_tokens)
                if response is None:
                    st.error(messages)
                    return

                for i in response:
                    res = i.choices[0].delta.content
                    if res is not None:
                        response_content += res  # Accumulate response
                        yield res
                    else:
                        prompt_token = gemma_eval.gemma_token_count(prompt)
                        response_token = i.x_groq.usage.completion_tokens
                        cost = 0
                
                st.session_state[f'{model_name}_response'] = response_content

            elif 'claude' in model_name:
                response, messages, response_time = claude_model(model_name, model_id, user_id, prompt, temperature=temperature, p_value=p_value, max_tokens=max_tokens)
                if response is None:
                    st.error(messages)
                    return
                
                for i in response:
                    if getattr(i, 'type', None) == 'content_block_delta':
                        res = i.delta.text
                        response_content += i.delta.text
                        yield res
                    elif getattr(i, 'type', None) == 'message_start':
                        prompt_token = i.message.usage.input_tokens
                    elif getattr(i, 'type', None) == 'message_delta':
                        response_token = i.usage.output_tokens
                    
                st.session_state[f'{model_name}_response'] = response_content
                cost = claude_eval.cal_pricing_token(model_name, prompt_token, response_token)

            
        
            if model_name in st.session_state:
                print(model_name)
                st.session_state[model_name] = {
                    'prompt_token': prompt_token,
                    'response_token': response_token,
                    'cost': cost,
                    'total_cost':  st.session_state[model_name]['total_cost'] + cost,
                    'total_tokens':  st.session_state[model_name]['total_cost'] + prompt_token + response_token,
                    'time_taken': response_time
                }
            else:
                st.session_state[model_name] = {
                    'prompt_token': prompt_token,
                    'response_token': response_token,
                    'cost': cost,
                    'total_cost':  cost,
                    'total_tokens': prompt_token + response_token,
                    'time_taken': response_time
                }

            append_message(user_id, model_id, prompt, response_content)
        except Exception as e:
            yield f"Error: {str(e)}"

        return [prompt_token, response_token, cost]
################################################################################################################

def threading_output(prompt):
    ctx = get_script_run_ctx()
    
    # Assuming model settings keys are prefixed with 'model_'
    models_to_remove = [key for key in st.session_state.keys() if key.startswith('model_') and key.split('_')[1] not in selected_models]
    for key in models_to_remove:
        del st.session_state[key]

    if len(selected_models) > 1:
        # Create a list of containers with fixed height for scrollable content
        my_grid = grid(2, 2)
        scroll_containers = [my_grid.container(border=True, height=400) for _ in range(len(selected_models))]
    else:
        # If only one model is selected, use a single scrollable container
        scroll_containers = [st.container(border=True, height=500)]


    with concurrent.futures.ThreadPoolExecutor(max_workers=len(selected_models)) as executor:
        future_to_col = {}  # Map futures to corresponding scrollable container

        for i, model in enumerate(selected_models):
            model_id = MODEL_DETAILS.get(model)
            generator = call_chain(ctx, model, prompt)
            # Submit task to executor, mapping it to the corresponding scrollable container
            future = executor.submit(give_output, ctx, generator, scroll_containers[i], model_id, prompt, model)
            future_to_col[future] = scroll_containers[i]
        
        # Handle completed futures
        for future in concurrent.futures.as_completed(future_to_col):
            col = future_to_col[future]
            try:
                future.result()  # We are just calling result to trigger exception handling if any
            except Exception as exc:
                col.error(f'Generator raised an exception: {exc}')
            except BaseException as exc:  # BaseException to capture other potential system-level exceptions
                col.error(f'Unhandled exception in the generator: {exc}')

################################################################################################################
def give_output(ctx, generator, col, model_id, prompt, model_name):
    display_chat_history(ctx, col, model_id, model_name, user_id)

    if prompt!='':
        display_message(ctx,col, prompt, generator, model_name)

    # Check if the selected models have changed
    current_selected_models = st.session_state.get("selected_models", [])
    previous_selected_models = st.session_state.get("previous_selected_models", [])  # noqa: F841

    if model_name in st.session_state:
        model_data = st.session_state[model_name]
        display_popovers(ctx, col, model_name, model_data)
    else:
        display_popovers(ctx, col, model_name)

    # Update the previous selected models
    st.session_state["previous_selected_models"] = current_selected_models
################################################################################################################
# Sidebar Creation

if "selected_models" not in st.session_state:
    # Default model selection (you can set it to empty if you want no defaults)
    st.session_state["selected_models"] = ["gpt-4o-mini"]

for model_name in MODEL_CHOICES:
    if f'{model_name}_temperature' not in st.session_state:
        st.session_state[f'{model_name}_temperature'] = 0.5
        st.session_state[f'{model_name}_p_value'] = 0.5
        st.session_state[f'{model_name}_max_output_tokens'] = 150

user_id = session.user.id 

user_prompt, selected_models = create_bottom_container(user_id, MODEL_CHOICES)


if user_prompt and selected_models:
    # Store user input into each model's history
    for model in selected_models:
        model_id = MODEL_DETAILS[model]
    threading_output(user_prompt)
elif not selected_models:
    st.warning("Please select at least one model before proceeding.")
else:
    threading_output('')