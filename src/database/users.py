from supabase_config import supabase
from encrypt_keys.encrypting_keys import encrypt_data, decrypt_data
import base64
import os
from dotenv import load_dotenv

load_dotenv()


encrypt_api_key = os.environ.get('ENCRYPTION_KEY').encode()
key_hex = os.environ.get('ENCRYPTION_KEY')
encrypt_api_key = bytes.fromhex(key_hex)

def fetch_user_prompts(user_id):
    """Fetches all prompts written by a given user from the chat_history table, excluding the current prompt."""
    response = supabase.table("chat_history")\
                  .select("user_message")\
                  .eq("user_id", user_id)\
                  .execute()
    return response

def delete_chat_history(user_id):
    try:
        # Replace 'chat_history_table' with the actual name of your chat history table
        response = supabase.from_("chat_history").delete().eq("user_id", user_id).execute()
        return response
    except Exception as e:
        return f"Error deleting chat history: {e}"
    

def verify_api_key(user_id, api_key_type, api_key):
    try:
        api_key_bytes = api_key.encode()  # Convert api_key to bytes
        encrypt_key = encrypt_data(api_key_bytes, encrypt_api_key)  # Pass bytes-like data to encrypt_data
        encrypted_key_base64 = base64.b64encode(encrypt_key).decode()  # Encode encrypted key to Base64

        if api_key_type == 'openai':
            response = supabase.table("users").update({"openai_api": encrypted_key_base64}).eq("id", user_id).execute()
        elif api_key_type == 'gemini':
            response = supabase.table("users").update({"gemini_api": encrypted_key_base64}).eq("id", user_id).execute()
        elif api_key_type == 'groq':
            response = supabase.table("users").update({"groq_api": encrypted_key_base64}).eq("id", user_id).execute()
        elif api_key_type == 'claude':
            response = supabase.table("users").update({"claude_api": encrypted_key_base64}).eq("id", user_id).execute()
        
        return response
    except Exception as e:
        print(f"Error updating API key: {e}")
        return f"Error updating API key: {e}"

def get_user_api_keys(user_id):
    try:
        response = supabase.table("users").select("openai_api", "gemini_api", "groq_api", "claude_api").eq("id", user_id).execute()
        if response.data:
            return response.data[0]
        else:
            print(f"No API keys found for user with id: {user_id}")
            return {}
    except Exception as e:
        print(f"Error fetching API keys: {e}")
        return {}
    
def decrypt_api_key(encrypt_api_keys):
    encrypted_key_bytes = base64.b64decode(encrypt_api_keys)
    decrypted_key = decrypt_data(encrypted_key_bytes, encrypt_api_key)
    return decrypted_key

def reset_openai_key(user_id):
    try:
        response = supabase.table("users").update({"openai_api": None}).eq("id", user_id).execute()
        return response
    except Exception as e:
        return f"Error resetting OpenAI key: {e}"
    