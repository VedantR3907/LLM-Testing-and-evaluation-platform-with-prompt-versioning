from groq import Groq

def groq_verify(api_key):
    client = Groq(
    api_key=api_key,
)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Hi",
            }
        ],
        model="llama3-8b-8192",
        temperature=0.1,
        max_tokens=10,
        top_p=0.1
    )

    return chat_completion.choices[0].message.content