import anthropic

def claude_verify(api_key):
    client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=api_key,
    )


    message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=10,
    messages=[
        {"role": "user", "content": "Hi"}
    ],
    )

    return message.content[0].text