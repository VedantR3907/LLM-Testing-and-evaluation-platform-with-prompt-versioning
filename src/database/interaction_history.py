from supabase_config import supabase

def format_interaction_history(data):
    """
    Format a list of interaction dictionaries into a chat history for a chat model.

    Args:
    data (list of dicts): List containing interaction data where each dictionary has
                          'user_message' and 'ai_message' keys.

    Returns:
    list: Formatted chat history list suitable for models.
    """
    if not data.data:
         return [{"role": "user", "content": ''}]
    else:
        chat_history_for_model = []
        for interaction in data.data[::-1]:
            chat_history_for_model.append({"role": "user", "content": interaction["user_message"]})
            chat_history_for_model.append({"role": "assistant", "content": interaction["ai_message"]})
        return chat_history_for_model

def format_interaction_history_gemini(data):
     if not data.data:
         return []
     else:
        chat_history_for_model = []
        for interaction in data.data[::-1]:
            chat_history_for_model.append({"parts": [{"text": interaction['user_message']}], "role": "user"})
            chat_history_for_model.append({"parts": [{"text": interaction['ai_message']}], "role": "model"})
        return chat_history_for_model
     
def format_interaction_history_claude(data):
    """
    Format a list of interaction dictionaries into a chat history for a Claude model.

    Args:
    data (list of dicts): List containing interaction data where each dictionary has
                          'user_message' and 'ai_message' keys.

    Returns:
    list: Formatted chat history list suitable for Claude models.
    """
    if not data.data:
         return [{"role": "user", "content": 'Hi dummyved3907'}]
    else:
        chat_history_for_model = []
        if data.data:
            for interaction in data.data[::-1]:
                chat_history_for_model.append({"role": "user", "content": interaction["user_message"]})
                chat_history_for_model.append({"role": "assistant", "content": interaction["ai_message"]})
            return chat_history_for_model
             
def append_message(user_id, model_id, user_message, ai_message):
        data = {
            "user_id": user_id,
            "model_id": model_id,
            "user_message": user_message,
            "ai_message": ai_message
        }
        response = supabase.table("chat_history").insert(data).execute()
        return response

def get_history(user_id, model_id,MAX_HISTORY_LENGTH, model_name):
    messages = supabase.table("chat_history")\
        .select("user_message", "ai_message").eq("user_id", user_id)\
        .eq("model_id", model_id)\
        .order("created_at", desc=True)\
        .limit(MAX_HISTORY_LENGTH)\
        .execute()
    
    if 'gpt' in model_name or 'llama' in model_name or 'mixtral' in model_name or 'gemma' in model_name:
        return format_interaction_history(messages)
    elif 'gemini' in model_name:
        return format_interaction_history_gemini(messages)
    elif 'claude' in model_name:
        return format_interaction_history_claude(messages)
    
