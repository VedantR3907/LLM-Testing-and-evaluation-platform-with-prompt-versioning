import streamlit as st
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx

def display_popovers(ctx, col, model_name, model_data=None):
    """
    Display popovers for model metadata and properties.
    
    Parameters:
        col (Column): Streamlit column object for layouts.
        model_data (dict, optional): Data about the model including tokens and cost. Defaults to None.
    """
    add_script_run_ctx(threading.current_thread(), ctx)
    default_data = {'prompt_token': 0, 'response_token': 0, 'cost': 0, 'total_cost':0, 'total_tokens':0, 'time_taken': 0}
    data = model_data if model_data else default_data
    
    with col.container():
        col1, col3 = st.columns([2,1])
        with col1.popover("💰"):
            st.markdown(f"**Prompt Tokens**: {data['prompt_token']}")
            st.markdown(f"**Response Tokens**: {data['response_token']}")
            st.markdown(f"**Total Tokens**: {int(data['total_tokens'])}")
            st.markdown(f"**Cost**: ${data['cost']:.4f}")
            st.markdown(f"**Total Cost**: ${data['total_cost']:.4f}")
            st.markdown(f"**Time Taken**: {data['time_taken']:.4f}s")
        with col3.popover("⛭ Param"):
            temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=st.session_state[f'{model_name}_temperature'], step=0.01, key = f'{model_name}_temperature_slider')
            p_value = st.slider("P Value:", min_value=0.0, max_value=1.0, value=st.session_state[f'{model_name}_p_value'], step=0.01, key = f'{model_name}_p_value_slider')
            max_tokens = st.slider("Max Output Tokens:", min_value=16, max_value=1000, value=st.session_state[f'{model_name}_max_output_tokens'], step=10, key=f'{model_name}_max_output_tokens_slider')

            # Submit button outside the form
            if st.button(f"Submit {model_name} Settings"):
                st.session_state[f'{model_name}_temperature'] = temperature
                st.session_state[f'{model_name}_p_value'] = p_value
                st.session_state[f'{model_name}_max_output_tokens'] = max_tokens
                st.rerun()