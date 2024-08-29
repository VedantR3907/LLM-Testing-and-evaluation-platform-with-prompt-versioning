import time
from  database.interaction_history import get_history
from .config import initialize_clients

def openai_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens):

    client, message = initialize_clients(user_id, client_type='openai')
    if client is None:
        return None, message, 0

    start_time = time.time()
    chat_history_for_model = get_history(user_id, model_id, 5, model_name)
    messages = chat_history_for_model + [
                {"role": "user", "content": prompt}
                ]

    response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=p_value,
            stream=True,

        )
    
    end_time = time.time()
    response_time = end_time - start_time
    return response, messages, response_time