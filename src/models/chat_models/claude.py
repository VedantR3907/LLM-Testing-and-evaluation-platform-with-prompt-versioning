import time
from  database.interaction_history import get_history
from .config import initialize_clients

def claude_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens):

    client_claude, message = initialize_clients(user_id, client_type='claude')
    if client_claude is None:
        return None, message, 0
    
    if 'haiku' in model_name:
        modelName = f'{model_name}-20240307'
    else:
        modelName = f'{model_name}-20240229'

    start_time = time.time()
    chat_history_for_model = get_history(user_id, model_id, 5, model_name)
    # Check if the last message in the chat history is from the "user"
    if chat_history_for_model and chat_history_for_model[-1]['role'] == 'user':
        # Append a dummy "assistant" message
        chat_history_for_model.append({"role": "assistant", "content": "Hi"})

    messages = chat_history_for_model + [
                {"role": "user", "content": prompt}
                ]
    
    response = client_claude.messages.create(
    model=modelName,
    max_tokens=max_tokens,
    top_p=p_value,
    temperature = temperature,
    messages=messages,
    stream=True
    )

    end_time = time.time()
    response_time = end_time - start_time
    return response, messages, response_time