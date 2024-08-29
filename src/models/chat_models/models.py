import os
import time
from openai import OpenAI
import google.generativeai as genai
from  database.interaction_history import get_history
from  database.users import get_user_api_keys, decrypt_api_key
from streamlit_server_state import server_state
from groq import Groq
import anthropic

session = server_state.get('session')

# Global dictionary to store clients and their API keys
clients = {
    'openai': {'client': None, 'api_key': None, 'decrypted_key': None},
    'gemini': {'client': None, 'api_key': None, 'decrypted_key': None},
    'groq': {'client': None, 'api_key': None, 'decrypted_key': None},
    'claude': {'client': None, 'api_key': None, 'decrypted_key': None}
}

def reset_clients():
    clients['openai']['client'], clients['openai']['api_key'], clients['openai']['decrypted_key']= None, None, None
    clients['gemini']['client'], clients['gemini']['api_key'], clients['gemini']['decrypted_key'] = None, None, None
    clients['groq']['client'], clients['groq']['api_key'], clients['groq']['decrypted_key'] = None, None, None
    clients['claude']['client'], clients['claude']['api_key'], clients['claude']['decrypted_key'] = None, None, None

def initialize_clients(user_id, client_type=None):
    api_keys = get_user_api_keys(user_id)
    openai_api_key = api_keys.get('openai_api')
    gemini_api_key = api_keys.get('gemini_api')
    groq_api_key = api_keys.get('groq_api')
    claude_api_key = api_keys.get('claude_api')

    if client_type == 'openai' or client_type is None:
        if openai_api_key is not None and clients['openai']['api_key'] != openai_api_key:
            openai_api_key_decrypted = decrypt_api_key(openai_api_key).decode('utf-8')
            clients['openai']['api_key'] = openai_api_key
            clients['openai']['decrypted_key'] = openai_api_key_decrypted
            print("HITTING OPENAI")
            clients['openai']['client'] = OpenAI(api_key=openai_api_key_decrypted) if openai_api_key_decrypted else None
    if client_type == 'gemini' or client_type is None:
        if gemini_api_key is not None and clients['gemini']['api_key'] != gemini_api_key:
            gemini_api_key_decrypted = decrypt_api_key(gemini_api_key)
            clients['gemini']['api_key'] = gemini_api_key
            print("HITTING GEMINI")
            clients['gemini']['decrypted_key'] = gemini_api_key_decrypted
            genai.configure(api_key=gemini_api_key_decrypted)
    if client_type == 'groq' or client_type is None:
        if groq_api_key is not None and clients['groq']['api_key'] != groq_api_key:
            groq_api_key_decrypted = decrypt_api_key(groq_api_key).decode('utf-8')
            clients['groq']['api_key'] = groq_api_key
            print("HITTING GROQ")
            clients['groq']['decrypted_key'] = groq_api_key_decrypted
            clients['groq']['client'] = Groq(
                api_key=groq_api_key_decrypted
            ) if groq_api_key_decrypted else None
    if client_type == 'claude' or client_type is None:
        if claude_api_key is not None and clients['claude']['api_key'] != claude_api_key:
            claude_api_key_decrypted = decrypt_api_key(claude_api_key).decode('utf-8')
            clients['claude']['api_key'] = claude_api_key
            print("HITTING CLAUDE")
            clients['claude']['decrypted_key'] = claude_api_key_decrypted
            clients['claude']['client'] = anthropic.Anthropic(
                api_key=claude_api_key_decrypted
            ) if claude_api_key_decrypted else None

    if client_type == 'openai' and clients['openai']['decrypted_key'] is None:
        return clients['openai']['client'], "Please validate the OpenAI API key"
    elif client_type == 'gemini' and clients['gemini']['decrypted_key'] is None:
        return clients['gemini']['client'], "Please validate the Gemini API key"
    elif client_type == 'groq' and clients['groq']['decrypted_key'] is None:
        return clients['groq']['client'], "Please validate the Groq API key"
    elif client_type == 'claude' and clients['claude']['decrypted_key'] is None:
        return clients['claude']['client'], "Please validate the Claude API key"
    else:
        return clients[client_type]['client'], ""

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

def gemini_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens):

    client, message = initialize_clients(user_id, client_type='gemini')
    if message:
        return None, None, message, 0

    start_time = time.time()

    chat_history_for_model = get_history(user_id, model_id, 5, model_name)
    

    modelg = genai.GenerativeModel('gemini-pro',generation_config=genai.types.GenerationConfig(
        temperature=temperature,
        top_p=p_value,
        max_output_tokens=max_tokens,
    ))
    chat_history = modelg.start_chat(history=chat_history_for_model)

    response = chat_history.send_message(prompt, stream=True)

    end_time = time.time()
    response_time = end_time - start_time
    return modelg, response, chat_history_for_model, response_time

# def llama_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens):
#     api_key = os.environ.get('CLOUDBASE_API_KEY')
#     account_id = os.environ.get('CLOUDBASE_ID')

#     if model_name != 'llama-2-13b-chat-awq':
#         url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/{model_name}"
#     else:
#         url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@hf/thebloke/{model_name}"
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#     }

#     chat_history_for_model = get_history(user_id, model_id, 5, model_name)
#     messages = chat_history_for_model + [
#                 {"role": "user", "content": prompt}
#                 ]
#     data = {
#         "messages": messages,
#         "max_tokens":max_tokens,
#         "temperature":temperature,
#         "p_value":p_value
#     }

#     start_time = time.time()
#     with requests.Session() as session:
#         response = session.post(url, headers=headers, data=json.dumps(data), stream=True)
#     end_time = time.time()
#     response_time = end_time - start_time

#     response = json.loads(response.text)['result']['response']

#     return response, messages, response_time

def mistral_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens):

    # client, message = initialize_clients(user_id, client_type='openai')
    # if client is None:
    #     return None, message, 0

    client_groq, message = initialize_clients(user_id, client_type='groq')
    if client_groq is None:
        return None, message, 0

    modelName = f'{model_name}-32768'

    start_time = time.time()
    chat_history_for_model = get_history(user_id, model_id, 5, model_name)
    messages = chat_history_for_model + [
                {"role": "user", "content": prompt}
                ]

    response = client_groq.chat.completions.create(
            model=modelName,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=p_value,
            stream=True,

        )
    
    end_time = time.time()
    response_time = end_time - start_time
    return response, messages, response_time

def llama_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens):

    client_groq, message = initialize_clients(user_id, client_type='groq')
    if client_groq is None:
        return None, message, 0
    
    modelName = f'{model_name}-8192'
    

    start_time = time.time()
    chat_history_for_model = get_history(user_id, model_id, 5, model_name)
    messages = chat_history_for_model + [
                {"role": "user", "content": prompt}
                ]

    response = client_groq.chat.completions.create(
            model=modelName,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=p_value,
            stream=True,

        )
    
    end_time = time.time()
    response_time = end_time - start_time
    return response, messages, response_time

def gemma_model(model_name, model_id, user_id, prompt, temperature, p_value, max_tokens):

    client_groq, message = initialize_clients(user_id, client_type='groq')
    if client_groq is None:
        return None, message, 0
    
    modelName = f'{model_name}-it'
    

    start_time = time.time()
    chat_history_for_model = get_history(user_id, model_id, 5, model_name)
    messages = chat_history_for_model + [
                {"role": "user", "content": prompt}
                ]

    response = client_groq.chat.completions.create(
            model=modelName,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=p_value,
            stream=True,

        )
    
    end_time = time.time()
    response_time = end_time - start_time
    return response, messages, response_time

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