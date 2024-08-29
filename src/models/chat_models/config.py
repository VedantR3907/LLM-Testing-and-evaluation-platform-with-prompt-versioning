from openai import OpenAI
import google.generativeai as genai
from groq import Groq
import anthropic
from database.users import get_user_api_keys, decrypt_api_key

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