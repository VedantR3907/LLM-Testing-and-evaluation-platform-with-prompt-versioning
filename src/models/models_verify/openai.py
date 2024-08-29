from openai import OpenAI
import time

def openai_verify(api_key):
    client = OpenAI(api_key=api_key)
    start_time = time.time()

    messages = [{"role": "user", "content": "Hi"}]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100,
        temperature=0.5,
        top_p=0.5,
        stream=True,
    )

    end_time = time.time()
    
    response_time = end_time - start_time
    return response, messages, response_time