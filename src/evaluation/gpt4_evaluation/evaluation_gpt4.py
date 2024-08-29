from openai import OpenAI
from  database.users import get_user_api_keys, decrypt_api_key
from .prompts import create_system_prompt, create_user_prompt

def gpt4_eval(models, category, prompt_given, model_responses, user_id):
            api_key = get_user_api_keys(user_id).get('openai_api')
            api_key = decrypt_api_key(api_key).decode('utf-8')
            client = OpenAI(api_key=api_key)
            messages = [
                {"role": "system", "content": create_system_prompt(category)},
                {"role": "user", "content": create_user_prompt(models, model_responses, prompt_given)}
            ]
            response = client.chat.completions.create(
            model="gpt-4",  # You can specify different GPT models here
            messages=messages
            )
            return response.choices[0].message.content