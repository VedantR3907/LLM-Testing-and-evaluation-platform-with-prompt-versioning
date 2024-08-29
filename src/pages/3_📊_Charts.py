import time
import streamlit as st
import plotly.graph_objects as go
from navigation import make_sidebar
from  database.models_db import fetch_model_details, fetch_model_votes
from streamlit_server_state import server_state
import json
session = server_state.get('session')


make_sidebar(session)
def create_bar_chart(data, y_key, title, num_steps=50, step_delay=0.005, highlight_max=True):
    if not data:
        st.warning(f"No data available for {title}.")
        return
    
    model_names = [model['model_name'] for model in data]
    final_values = [model[y_key] for model in data]

    highlight_value = max(final_values) if highlight_max else min(final_values) if final_values else 0

    non_zero_values = [value for value in final_values if value != 0]
    highlight_value = min(non_zero_values) if non_zero_values else 0

    placeholder = st.empty()
    fig = go.Figure(layout={
        "title": title,
        "xaxis": {"title": "Models"},
        "yaxis": {"range": [0, max(final_values) * 1.1] if final_values else [0, 1]},
        "template": "plotly_dark"
    })
    
    for step in range(1, num_steps + 1):
        current_values = [(value * (step / num_steps)) for value in final_values]
        colors = ['green' if value == highlight_value and value != 0 and step == num_steps else 'lightslategray' for value in final_values]
        
        # Enhanced format for display
        if 'cost' in y_key:
            # Format for cost metrics with a dollar sign and to two decimal places
            text_format = [f"${value:.6f}" if step == num_steps else "" for value in current_values]
        elif 'time' in y_key:
            # Format for time metrics with an 's' at the end and to two decimal places
            text_format = [f"{value:.2f}s" if step == num_steps else "" for value in current_values]
        else:
            # Default format to two decimal places
            text_format = [f"{value:.2f}" if step == num_steps else "" for value in current_values]
        
        fig.data = []  # Clear the existing data
        fig.add_trace(
            go.Bar(
                x=model_names,
                y=current_values,
                marker_color=colors,
                text=[text_format[i] if step == num_steps else "" for i, value in enumerate(final_values)],
                textposition='auto'
            )
        )
        placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(step_delay)

def main():
    model_name = fetch_model_details().keys()
    data = []

    model_votes = fetch_model_votes()
    
    for i in model_name:
        if i in st.session_state and i in st.session_state['selected_models']:
            model_data = st.session_state[i]
            data.append({
                "model_name": i,
                "prompt_tokens": model_data['prompt_token'],
                "response_tokens": model_data['response_token'],
                "total_tokens": model_data['total_tokens'],
                "current_cost": model_data['cost'],
                "total_cost": model_data['total_cost'],
                "time_taken": model_data['time_taken']
            })

    st.title('Model Metrics Visualization')
    # Main Tabs for Token Metrics and Cost Metrics
    main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs(["Token Metrics", "Cost and Time Metrics", "Users Votings", "Evaluation"])
    
    with main_tab1:
        st.info(f"**Prompt:** {st.session_state.get('current_prompt', 'No prompt available')}")
        token_metric = st.selectbox(
            "Choose a token metric:",
            options=["prompt_tokens", "response_tokens", "total_tokens"],
            index=0,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        create_bar_chart(data, token_metric, f'{token_metric.replace("_", " ").title()} per Model', highlight_max=False)
    
    with main_tab2:
        st.info(f"**Prompt:** {st.session_state.get('current_prompt', 'No prompt available')}")
        cost_time_metric = st.selectbox(
            "Choose a cost metric:",
            options=["current_cost", "total_cost", "time_taken"],
            index=0,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        create_bar_chart(data, cost_time_metric, f'{cost_time_metric.replace("_", " ").title()} per Model', highlight_max=False)
    
    with main_tab3:
        st.info(f"**Prompt:** {st.session_state.get('current_prompt', 'No prompt available')}")
        st.header("User Votes for Models")
        create_bar_chart(model_votes, 'total_votes', 'Total Votes per Model', highlight_max=True)

    #Mainting session state between pages.
    if len(data) != 0:
        st.session_state['selected_models'] = [i['model_name'] for i in data]
    
    with main_tab4:
        st.info(f"**Prompt:** {st.session_state.get('current_prompt', 'No prompt available')}")
        mini_tab4_1, mini_tab4_2 = st.tabs(["GPT4 Evaluation", "Custom Evaluation"])

        with mini_tab4_1:

            st.header("GPT-4 Evaluation Results")
            response_gpt4_eval = st.session_state.get('response_gpt4_eval', None)
            prompt_gpt4 = st.session_state.get('prompt_gpt4', None)  # Get the prompt from the session state
            if response_gpt4_eval is None:
                st.warning('No data available')
            else:
                

                response_gpt4_eval = json.loads(response_gpt4_eval)  # Convert string to dictionary
                for model, evaluation in response_gpt4_eval.items():
                    st.subheader(model)
                    
                    # Exclude 'reason' from the metrics to be plotted
                    metrics = {k: v for k, v in evaluation.items() if k != 'reason'}
                    fig = go.Figure(data=[
                        go.Bar(name=metric, x=[model], y=[value], text=[value], textposition='auto') for metric, value in metrics.items()
                    ])
                    # Change the bar mode
                    fig.update_layout(barmode='group')
                    st.plotly_chart(fig)
                    
                    # Display the 'reason' separately
                    st.info(f"Reason: {evaluation.get('reason', '')}")
                    st.write("---")
        
        with mini_tab4_2:
            st.header("Custom Evaluation Results")
            response_custom_eval = st.session_state.get('response_custom_eval', None)
            prompt_custom = st.session_state.get('prompt_custom', None)  # Get the prompt from the session state
            selected_category = st.session_state.get('selected_category', None)  # Get the selected category from the session state

            if response_custom_eval is None:
                st.warning('No data available')
            else:

                response_custom_eval = json.loads(response_custom_eval)  # Convert string to dictionary
                for model, evaluation in response_custom_eval.items():
                    st.subheader(model)
                    
                    if selected_category == "Translation":
                        # Handle Translation category
                        # Exclude 'translation_scores' from the metrics to be plotted
                        metrics = {k: v for k, v in evaluation.items() if k != 'translation_scores'}
                        # Display the 'rougue' scores separately
                        if 'translation_scores' in evaluation:
                            translation_scores = evaluation.get('translation_scores', {})
                            if 'rougue' in translation_scores:
                                rouge_scores = translation_scores.get('rougue', [{}])[0]
                                for rouge_type, rouge_values in rouge_scores.items():
                                    metrics[f"{rouge_type}_f1"] = rouge_values.get('f', 0) * 10  # Scale the score
                    elif selected_category == "Text_Generation" or selected_category == "General_Knowledge":
                        # Handle Text_Generation and General_Knowledge categories
                        # Exclude 'toxicity_scores' from the metrics to be plotted
                        metrics = {k: v for k, v in evaluation.items() if k != 'toxicity_scores'}
                        # Display the 'toxicity_scores' as a grouped bar chart
                        if 'toxicity_scores' in evaluation:
                            toxicity_scores = evaluation.get('toxicity_scores', {})
                            for score_name, score_value in toxicity_scores.items():
                                metrics[score_name] = score_value * 10  # Scale the score
                    else:
                        # Default handling for other categories
                        if len(evaluation) == 0 or evaluation == None:
                            evaluation = {k: 0 for k in ['Conciseness', 'Relevance', 'Correctness', 'Harmfulness', 'Helpfulness', 'Insensitivity']}  # Set all points to zero
                        
                        metrics = evaluation
                    
                    # Scale the similarity_score
                    if 'similarity_score' in metrics:
                        metrics['similarity_score'] *= 10
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            name=metric, 
                            x=[model], 
                            y=[value], 
                            text=[f"{value:.2f}" if isinstance(value, (int, float)) else str(value)] * len(model), 
                            textposition='auto'
                        ) for metric, value in metrics.items()
                    ])
                    # Change the bar mode
                    fig.update_layout(barmode='group')
                    st.plotly_chart(fig)
                    
                    st.write("---")

if __name__ == "__main__":
    main()