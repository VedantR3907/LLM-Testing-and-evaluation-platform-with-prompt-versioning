import google.generativeai as genai

def gemini_verify(api_key):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-pro')

    response = model.generate_content('Hi')

    return response
