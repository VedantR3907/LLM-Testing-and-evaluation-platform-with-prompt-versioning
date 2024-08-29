import time
import google.generativeai as genai
from  database.interaction_history import get_history
from .config import initialize_clients

def gemini_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens):

    client, message = initialize_clients(user_id, client_type='gemini')
    if message:
        return None, None, message, 0

    start_time = time.time()

    chat_history_for_model = get_history(user_id, model_id, 5, model_name)
    

    modelg = genai.GenerativeModel('gemini-pro',generation_config=genai.types.GenerationConfig(
        temperature=temperature,
        top_p=p_value,
        max_output_tokens=max_tokens
    ))
    chat_history = modelg.start_chat(history=chat_history_for_model)

    response = chat_history.send_message(prompt, stream=True)

    end_time = time.time()
    response_time = end_time - start_time
    return modelg, response, chat_history_for_model, response_time