from supabase_config import supabase

def insert_saved_prompt(user_id, prompt_title, prompt):
    """Inserts a new record into the Saved_Prompts table."""
    data = {
        "user_id": user_id,
        "prompt_title": prompt_title,
        "prompt": prompt
    }
    response = supabase.table("saved_prompts").insert(data).execute()
    return response

def fetch_saved_prompts(user_id):
    response = supabase.table("saved_prompts").select("*").eq("user_id", user_id).execute()
    return response

def fetch_all_versions_prompt(prompt_id):
    """Fetches all versions of a given prompt from the Version_Prompts table."""
    response = supabase.table("version_prompts")\
                  .select("*")\
                  .eq("prompt_id", prompt_id)\
                  .order("version", desc=True)\
                  .execute()
    return response

def get_latest_version_prompt(prompt_id):
    response = supabase.table("version_prompts")\
                  .select("*")\
                  .eq("prompt_id", prompt_id)\
                  .order("version", desc=True)\
                  .order("created_at", desc=True)\
                  .limit(1)\
                  .execute()
    return response

def get_latest_version_from_view(prompt_id):
    response = supabase.from_("saved_prompt_titles")\
                  .select("*")\
                  .eq("prompt_id", prompt_id)\
                  .execute()
    return response

def insert_version_prompt(prompt_id, prompt, version):
    data = {
        'prompt_id':prompt_id,
        "prompt": prompt,
        "version": version
    }
    response = supabase.table("version_prompts").insert(data).execute()
    return response

def delete_version_prompt(prompt_id, version):
    response = supabase.from_("version_prompts")\
                       .delete()\
                       .eq('prompt_id', prompt_id)\
                       .eq('version', version)\
                       .execute()
    return response

def delete_saved_prompt(prompt_id):
    response = supabase.from_("saved_prompts")\
                       .delete()\
                       .eq('id', prompt_id)\
                       .execute()
    return response

def delete_all_version_prompts(prompt_id):
    response = supabase.from_("version_prompts")\
                       .delete()\
                       .eq('prompt_id', prompt_id)\
                       .execute()
    return response

def fetch_saved_prompt_titles(user_id):
    response = supabase.from_("saved_prompt_titles")\
                       .select('prompt_title, prompt_id, last_version')\
                       .eq('user_id', user_id)\
                       .execute()
    return [{'title': f"{record['prompt_title']} (Last Version {record['last_version']})", 'id': record['prompt_id']} for record in response.data]
